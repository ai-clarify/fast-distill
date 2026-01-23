import json
import os
import sqlite3

from distilabel.models.llms import OllamaLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import KeepColumns, LoadDataFromDicts
from distilabel.steps.fastdistill import (
    CanonicalizeFields,
    ComputeHash,
    DeduplicateByField,
    FilterByBool,
    KeepByScore,
    MarkTime,
    RuleFilter,
    ScoreFromExecEval,
    SQLiteExecEval,
    WriteManifest,
    WriteQualityReport,
    WriteTimingReport,
)
from distilabel.steps.tasks import TextGeneration


def run():
    model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
    student_model = os.getenv("OLLAMA_STUDENT_MODEL", model)
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    artifacts_root = os.getenv(
        "FASTDISTILL_ARTIFACTS_DIR",
        os.path.join(os.path.expanduser("~"), ".cache", "fastdistill", "artifacts"),
    )

    db_dir = os.path.join(artifacts_root, "db")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "text2sql.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    cur.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob"), (3, "Chloe")],
    )
    conn.commit()
    conn.close()

    llm = OllamaLLM(
        model=model,
        host=host,
        generation_kwargs={
            "options": {
                "num_gpu": 0,
            }
        },
    )
    student_llm = OllamaLLM(
        model=student_model,
        host=host,
        generation_kwargs={
            "options": {
                "num_gpu": 0,
            }
        },
    )

    with Pipeline(name="fastdistill-ollama-e2e") as pipeline:
        data = LoadDataFromDicts(
            data=[
                {
                    "task_id": "text2sql-001",
                    "schema": "users(id, name)",
                    "instruction": "List all user names ordered by id.",
                    "gold_sql": "SELECT name FROM users ORDER BY id;",
                },
                {
                    "task_id": "text2sql-002",
                    "schema": "users(id, name)",
                    "instruction": "Count total users.",
                    "gold_sql": "SELECT COUNT(*) FROM users;",
                },
            ]
        )

        mark_raw = MarkTime(label="raw")
        canonical = CanonicalizeFields(fields=["schema", "instruction"])
        mark_canonical = MarkTime(label="canonical")
        sample_id = ComputeHash(
            fields=["task_id", "canonical_input"], output_field="sample_id"
        )
        mark_hashed = MarkTime(label="hashed")
        dedup = DeduplicateByField(field="sample_id")
        teacher = TextGeneration(
            llm=llm,
            system_prompt="Return SQL only. Do not wrap in quotes.",
            template="Schema: {{ schema }}\nQuestion: {{ instruction }}\nSQL:",
            columns=["schema", "instruction"],
        )
        mark_teacher = MarkTime(label="teacher")
        rule_filter = RuleFilter(text_field="generation", min_chars=1, max_chars=512)
        mark_filtered = MarkTime(label="filtered")
        sql_eval = SQLiteExecEval(db_path=db_path, sql_field="generation")
        teacher_score = ScoreFromExecEval(
            exec_pass_field="exec_pass",
            gold_match_field="gold_match",
            score_field="teacher_score",
        )
        keep_by_score = KeepByScore(
            score_field="teacher_score",
            keep_field="keep",
            min_score=0.5,
        )
        mark_eval = MarkTime(label="eval")
        filter_keep = FilterByBool(field="keep", value=True)
        filter_exec = FilterByBool(field="exec_pass", value=True)
        mark_selected = MarkTime(label="selected")
        keep = KeepColumns(
            columns=[
                "sample_id",
                "schema",
                "instruction",
                "gold_sql",
                "generation",
                "timing",
            ]
        )
        mark_distilled = MarkTime(label="distilled")
        student = TextGeneration(
            llm=student_llm,
            system_prompt="Return SQL only. Do not wrap in quotes.",
            template="Schema: {{ schema }}\nQuestion: {{ instruction }}\nSQL:",
            columns=["schema", "instruction"],
            output_mappings={
                "generation": "student_generation",
                "model_name": "student_model_name",
            },
        )
        mark_student = MarkTime(label="student_gen")
        student_eval = SQLiteExecEval(
            db_path=db_path,
            sql_field="student_generation",
            exec_pass_field="student_exec_pass",
            exec_error_field="student_exec_error",
            gold_match_field="student_gold_match",
            result_signature_field="student_result_signature",
        )
        student_score = ScoreFromExecEval(
            exec_pass_field="student_exec_pass",
            gold_match_field="student_gold_match",
            score_field="student_score",
        )
        mark_student_eval = MarkTime(label="student_eval")
        manifest = WriteManifest(
            stage="distilled",
            output_dir=os.path.join(artifacts_root, "manifests"),
        )
        report = WriteQualityReport(
            stage="distilled",
            output_dir=os.path.join(artifacts_root, "reports"),
            judge_score_field="teacher_score",
        )
        student_report = WriteQualityReport(
            stage="student_eval",
            output_dir=os.path.join(artifacts_root, "reports"),
            judge_score_field="student_score",
            exec_pass_field="student_exec_pass",
            exec_error_field="student_exec_error",
            gold_match_field="student_gold_match",
        )
        timing_report = WriteTimingReport(
            output_dir=os.path.join(artifacts_root, "reports"),
            report_name="timing_report.json",
            ordered_labels=[
                "raw",
                "canonical",
                "hashed",
                "teacher",
                "filtered",
                "eval",
                "selected",
                "distilled",
                "student_gen",
                "student_eval",
            ],
        )

        (
            data
            >> mark_raw
            >> canonical
            >> mark_canonical
            >> sample_id
            >> mark_hashed
            >> dedup
            >> teacher
            >> mark_teacher
            >> rule_filter
            >> mark_filtered
            >> sql_eval
            >> teacher_score
            >> keep_by_score
            >> mark_eval
            >> filter_keep
            >> filter_exec
            >> mark_selected
            >> mark_distilled
            >> report
            >> keep
            >> manifest
            >> student
            >> mark_student
            >> student_eval
            >> student_score
            >> mark_student_eval
            >> student_report
            >> timing_report
        )

    load_groups = os.getenv("FASTDISTILL_LOAD_GROUPS")
    run_kwargs = {"use_cache": False}
    if load_groups:
        run_kwargs["load_groups"] = load_groups
    result = pipeline.run(**run_kwargs)
    ds = result["default"]["train"]
    print("distilled_rows=", len(ds))
    for row in ds:
        print(row)

    timing_path = os.path.join(artifacts_root, "reports", "timing_report.json")
    if os.path.exists(timing_path):
        with open(timing_path, "r", encoding="utf-8") as handle:
            timing_report = json.load(handle)
        print("timing_report=", timing_report.get("durations"))


if __name__ == "__main__":
    run()
