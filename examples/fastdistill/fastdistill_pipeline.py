import json
import os
import sqlite3
import time
from pathlib import Path

from fastdistill.models.llms import OllamaLLM, OpenAILLM, SGLangLLM
from fastdistill.pipeline import Pipeline
from fastdistill.steps import KeepColumns, LoadDataFromDicts, LoadDataFromFileSystem
from fastdistill.steps.fastdistill import (
    CanonicalizeFields,
    CleanSqlOutput,
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
from fastdistill.steps.tasks import TextGeneration


def _load_repo_dotenv() -> None:
    for parent in Path(__file__).resolve().parents:
        env_path = parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if not key or key in os.environ:
                    continue
                os.environ[key] = value.strip().strip("'").strip('"')
            break


def _ensure_sample_db(artifacts_root: str) -> str:
    db_path = os.getenv("FASTDISTILL_DB_PATH")
    if db_path:
        return db_path
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
    return db_path


def _parse_stop_sequences(value: str | None) -> str | list[str] | None:
    if not value:
        return None
    if "|" in value:
        return [item for item in (part.strip() for part in value.split("|")) if item]
    return value.strip() or None


def _openrouter_generation_kwargs() -> dict:
    kwargs: dict[str, object] = {}
    if (value := os.getenv("OPENROUTER_TEMPERATURE")):
        kwargs["temperature"] = float(value)
    if (value := os.getenv("OPENROUTER_TOP_P")):
        kwargs["top_p"] = float(value)
    if (value := os.getenv("OPENROUTER_MAX_TOKENS")):
        kwargs["max_new_tokens"] = int(value)
    if (value := _parse_stop_sequences(os.getenv("OPENROUTER_STOP"))):
        kwargs["stop"] = value
    return kwargs


def build_pipeline():
    _load_repo_dotenv()
    artifacts_root = os.getenv(
        "FASTDISTILL_ARTIFACTS_DIR",
        os.path.join(os.path.expanduser("~"), ".cache", "fastdistill", "artifacts"),
    )
    db_path = _ensure_sample_db(artifacts_root)

    provider = os.getenv("FASTDISTILL_PROVIDER", "openrouter")
    llm_batch_size = os.getenv("FASTDISTILL_LLM_BATCH_SIZE")
    llm_batch_size = int(llm_batch_size) if llm_batch_size else None
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
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        teacher_llm = OllamaLLM(model=model, host=host, timeout=timeout)
    else:
        # Env keys (OpenRouter):
        # - OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY (fallback)
        # - OPENROUTER_BASE_URL (default: https://openrouter.ai/api/v1)
        # - OPENROUTER_MODEL (default: deepseek/deepseek-v3.2)
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        timeout = int(os.getenv("OPENROUTER_TIMEOUT", "120"))
        generation_kwargs = _openrouter_generation_kwargs()
        teacher_llm = OpenAILLM(
            model=model,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            generation_kwargs=generation_kwargs,
        )

    with Pipeline(name="fastdistill-text2sql") as pipeline:
        data_path = os.getenv("FASTDISTILL_DATA_PATH")
        if data_path:
            data = LoadDataFromFileSystem(data_files=data_path)
        else:
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

        teacher_kwargs = {}
        if llm_batch_size:
            teacher_kwargs["input_batch_size"] = llm_batch_size
        teacher = TextGeneration(
            llm=teacher_llm,
            system_prompt="Return SQL only.",
            template="Schema: {{ schema }}\nQuestion: {{ instruction }}\nSQL:",
            columns=["schema", "instruction"],
            **teacher_kwargs,
        )

        clean_sql = CleanSqlOutput(input_field="generation", output_field="generation")
        rule_filter = RuleFilter(text_field="generation", min_chars=1, max_chars=512)
        sql_eval = SQLiteExecEval(db_path=db_path, sql_field="generation")
        teacher_score = ScoreFromExecEval(
            exec_pass_field="exec_pass",
            gold_match_field="gold_match",
            score_field="teacher_score",
        )
        teacher_report = WriteQualityReport(
            stage="teacher_eval",
            output_dir=os.path.join(artifacts_root, "reports"),
            judge_score_field="teacher_score",
            exec_pass_field="exec_pass",
            exec_error_field="exec_error",
            gold_match_field="gold_match",
        )
        filter_gold = FilterByBool(field="gold_match", value=True)
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
            >> clean_sql
            >> rule_filter
            >> sql_eval
            >> teacher_score
            >> teacher_report
            >> filter_gold
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
    run_kwargs = {"use_cache": False}
    dataset_batch_size = os.getenv("FASTDISTILL_DATASET_BATCH_SIZE")
    if dataset_batch_size:
        run_kwargs["dataset_batch_size"] = int(dataset_batch_size)
    pipeline.run(**run_kwargs)
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
