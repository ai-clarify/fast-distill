import json
import os
import sqlite3
import time

from distilabel.models.llms import OllamaLLM, OpenAILLM, SGLangLLM
from distilabel.pipeline import Pipeline
from distilabel.steps import KeepColumns, LoadDataFromDicts
from distilabel.steps.fastdistill import (
    CanonicalizeFields,
    ComputeHash,
    DeduplicateByField,
    FilterByBool,
    KeepByScore,
    RuleFilter,
    ScoreFromExecEval,
    SQLiteExecEval,
    WriteManifest,
    WriteMlxDataset,
    WriteQualityReport,
)
from distilabel.steps.tasks import TextGeneration


def build_pipeline():
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

    provider = os.getenv("FASTDISTILL_PROVIDER", "openrouter")
    if provider == "sglang":
        # Env keys (SGLang):
        # - SGLANG_BASE_URL (default: http://127.0.0.1:30000/v1)
        # - SGLANG_API_KEY (optional)
        # - SGLANG_MODEL (default: qwen/qwen2.5-0.5b-instruct)
        model = os.getenv("SGLANG_MODEL", "qwen/qwen2.5-0.5b-instruct")
        teacher_llm = SGLangLLM(model=model)
    elif provider == "ollama":
        # Env keys (Ollama):
        # - OLLAMA_MODEL (default: qwen3:0.6b)
        # - OLLAMA_HOST (default: http://localhost:11434)
        model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        teacher_llm = OllamaLLM(model=model, host=host)
    else:
        # Env keys (OpenRouter):
        # - OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY (fallback)
        # - OPENROUTER_BASE_URL (default: https://openrouter.ai/api/v1)
        # - OPENROUTER_MODEL (default: deepseek/deepseek-v3.2)
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        teacher_llm = OpenAILLM(
            model=model,
            base_url=base_url,
            api_key=api_key,
        )

    with Pipeline(name="fastdistill-text2sql") as pipeline:
        data = LoadDataFromDicts(
            data=[
                {
                    "task_id": "text2sql-001",
                    "schema": "users(id, name)",
                    "instruction": "List all user names ordered by id.",
                    "gold_sql": "SELECT name FROM users ORDER BY id;",
                    "decode_profile": {"temperature": 0.2, "max_tokens": 128, "n": 1},
                    "system_prompt": "Return SQL only.",
                },
                {
                    "task_id": "text2sql-002",
                    "schema": "users(id, name)",
                    "instruction": "Count total users.",
                    "gold_sql": "SELECT COUNT(*) FROM users;",
                    "decode_profile": {"temperature": 0.2, "max_tokens": 128, "n": 1},
                    "system_prompt": "Return SQL only.",
                },
            ]
        )

        canonical = CanonicalizeFields(fields=["schema", "instruction"])
        sample_id = ComputeHash(fields=["task_id", "canonical_input"], output_field="sample_id")
        dedup = DeduplicateByField(field="sample_id")

        teacher = TextGeneration(
            llm=teacher_llm,
            system_prompt="Return SQL only.",
            template="Schema: {{ schema }}\nQuestion: {{ instruction }}\nSQL:",
            columns=["schema", "instruction"],
        )

        rule_filter = RuleFilter(text_field="generation", min_chars=1, max_chars=512)
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
        filter_keep = FilterByBool(field="keep", value=True)
        filter_exec = FilterByBool(field="exec_pass", value=True)
        keep = KeepColumns(
            columns=[
                "sample_id",
                "schema",
                "instruction",
                "gold_sql",
                "generation",
                "teacher_score",
            ]
        )

        report = WriteQualityReport(
            stage="distilled",
            output_dir=os.path.join(artifacts_root, "reports"),
            judge_score_field="teacher_score",
        )
        manifest = WriteManifest(
            stage="distilled",
            output_dir=os.path.join(artifacts_root, "manifests"),
        )
        mlx_export = WriteMlxDataset(
            output_dir=os.path.join(artifacts_root, "mlx"),
        )

        (
            data
            >> canonical
            >> sample_id
            >> dedup
            >> teacher
            >> rule_filter
            >> sql_eval
            >> teacher_score
            >> keep_by_score
            >> filter_keep
            >> filter_exec
            >> report
            >> keep
            >> mlx_export
            >> manifest
        )

    return pipeline


if __name__ == "__main__":
    pipeline = build_pipeline()
    start = time.monotonic()
    pipeline.run(use_cache=False)
    elapsed = time.monotonic() - start
    print(f"pipeline_wall_time_s={elapsed:.3f}")

    artifacts_root = os.getenv(
        "FASTDISTILL_ARTIFACTS_DIR",
        os.path.join(os.path.expanduser("~"), ".cache", "fastdistill", "artifacts"),
    )
    report_path = os.path.join(
        artifacts_root, "reports", "distilled", "quality_report.json"
    )
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as handle:
            report = json.load(handle)
        judge_score = report.get("judge_score", {})
        print(
            "distilled_model_score_mean=",
            judge_score.get("mean"),
        )
