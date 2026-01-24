import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from distilabel.utils.serialization import read_yaml, write_yaml
from distilabel.steps.fastdistill import QualityGate, evaluate_quality_gate


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


def _env_int(env: dict, key: str) -> int | None:
    value = env.get(key)
    return int(value) if value is not None else None


def _env_float(env: dict, key: str) -> float | None:
    value = env.get(key)
    return float(value) if value is not None else None


def _apply_teacher_eval_gate(artifacts_root: Path, env: dict) -> None:
    if env.get("FASTDISTILL_TEACHER_EVAL_GATE", "1") != "1":
        print("teacher_eval_gate=disabled")
        return

    stage = env.get("FASTDISTILL_TEACHER_EVAL_STAGE", "teacher_eval")
    report_path = artifacts_root / "reports" / stage / "quality_report.json"
    if not report_path.exists():
        raise FileNotFoundError(
            f"Teacher eval report not found at {report_path}. "
            "Run the distillation pipeline to generate it or disable the gate "
            "with FASTDISTILL_TEACHER_EVAL_GATE=0."
        )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    gate = QualityGate(
        min_total=_env_int(env, "FASTDISTILL_TEACHER_EVAL_MIN_TOTAL") or 50,
        min_exec_pass_rate=_env_float(env, "FASTDISTILL_TEACHER_EVAL_MIN_EXEC_PASS_RATE")
        or 0.5,
        min_gold_match_rate=_env_float(env, "FASTDISTILL_TEACHER_EVAL_MIN_GOLD_MATCH_RATE")
        or 0.1,
        min_judge_score_mean=_env_float(env, "FASTDISTILL_TEACHER_EVAL_MIN_JUDGE_MEAN")
        or 0.4,
    )
    failures = evaluate_quality_gate(report, gate)
    if failures:
        details = "; ".join(failures)
        raise RuntimeError(f"Teacher eval gate failed: {details}")

    print(
        "teacher_eval_gate=passed",
        f"total={report.get('total')}",
        f"exec_pass_rate={report.get('exec_pass_rate')}",
        f"gold_match_rate={report.get('gold_match_rate')}",
        f"judge_score_mean={(report.get('judge_score') or {}).get('mean')}",
    )


def main() -> None:
    _load_repo_dotenv()
    repo_root = Path(__file__).resolve().parents[1]
    artifacts_root = Path(
        os.getenv(
            "FASTDISTILL_ARTIFACTS_DIR",
            Path.home() / ".cache" / "fastdistill" / "artifacts",
        )
    )

    env = os.environ.copy()
    env.setdefault("FASTDISTILL_PROVIDER", "ollama")
    env.setdefault("OLLAMA_MODEL", "qwen3:0.6b")
    env.setdefault("OLLAMA_HOST", "http://localhost:11434")
    env.setdefault("FASTDISTILL_ARTIFACTS_DIR", str(artifacts_root))
    env.setdefault("MLX_MODEL", "Qwen/Qwen3-0.6B")

    pipeline = repo_root / "examples" / "fastdistill" / "fastdistill_pipeline.py"
    distill_elapsed = 0.0
    if env.get("FASTDISTILL_SKIP_DISTILL") == "1":
        print("skip_distillation=1")
    else:
        print("running_distillation=", pipeline)
        distill_start = time.monotonic()
        subprocess.run([sys.executable, str(pipeline)], check=True, env=env)
        distill_elapsed = time.monotonic() - distill_start
        print(f"distillation_wall_time_s={distill_elapsed:.3f}")

    _apply_teacher_eval_gate(artifacts_root, env)

    mlx_dir = artifacts_root / "mlx"
    mlx_dir.mkdir(parents=True, exist_ok=True)

    eval_data = env.get("FASTDISTILL_EVAL_DATA_PATH")
    eval_db = env.get("FASTDISTILL_EVAL_DB_PATH")
    eval_limit = env.get("MLX_EVAL_LIMIT")
    eval_max_tokens = env.get("MLX_EVAL_MAX_TOKENS")
    eval_log_every = env.get("MLX_EVAL_LOG_EVERY")
    eval_system_prompt = env.get("MLX_EVAL_SYSTEM_PROMPT", "Return SQL only.")
    eval_script = repo_root / "scripts" / "eval_mlx_text2sql.py"

    if eval_data and eval_db:
        print("running_mlx_eval_pre=", eval_script)
        eval_args = [
            sys.executable,
            str(eval_script),
            "--model",
            env.get("MLX_MODEL", "Qwen/Qwen3-0.6B"),
            "--data",
            eval_data,
            "--db",
            eval_db,
            "--output-dir",
            str(artifacts_root / "reports"),
            "--stage",
            "student_eval_pre",
            "--system-prompt",
            eval_system_prompt,
        ]
        if eval_limit:
            eval_args += ["--limit", eval_limit]
        if eval_max_tokens:
            eval_args += ["--max-tokens", eval_max_tokens]
        if eval_log_every:
            eval_args += ["--log-every", eval_log_every]
        subprocess.run(eval_args, check=True, env=env)

    sample_config = repo_root / "configs" / "fastdistill" / "mlx_train.sample.yaml"
    config_path = Path(env.get("MLX_TRAIN_CONFIG", str(sample_config)))
    if config_path.exists():
        config = read_yaml(config_path)
        config["data"] = str(mlx_dir)
        config["adapter_path"] = str(mlx_dir / "adapters")
        if env.get("MLX_MODEL"):
            config["model"] = env["MLX_MODEL"]
        train_config_path = mlx_dir / "mlx_train.yaml"
    else:
        raise FileNotFoundError(f"MLX train config not found: {config_path}")

    train_path = mlx_dir / "train.jsonl"
    valid_path = mlx_dir / "valid.jsonl"
    if train_path.exists() and valid_path.exists():
        train_lines = train_path.read_text(encoding="utf-8").splitlines()
        valid_lines = valid_path.read_text(encoding="utf-8").splitlines()
        if not valid_lines and train_lines:
            valid_lines = [train_lines.pop()]
            train_path.write_text("\n".join(train_lines) + "\n", encoding="utf-8")
            valid_path.write_text("\n".join(valid_lines) + "\n", encoding="utf-8")
        if not train_lines:
            raise RuntimeError("MLX training set is empty after split.")
        batch_size = int(config.get("batch_size", 1))
        if batch_size > len(train_lines):
            config["batch_size"] = len(train_lines)
        if "MLX_ITERS" in env:
            config["iters"] = int(env["MLX_ITERS"])
        batch_override = _env_int(env, "MLX_BATCH_SIZE")
        if batch_override is not None:
            config["batch_size"] = batch_override
        max_seq_override = _env_int(env, "MLX_MAX_SEQ_LENGTH")
        if max_seq_override is not None:
            config["max_seq_length"] = max_seq_override
        save_every_override = _env_int(env, "MLX_SAVE_EVERY")
        if save_every_override is not None:
            config["save_every"] = save_every_override
        steps_eval_override = _env_int(env, "MLX_STEPS_PER_EVAL")
        if steps_eval_override is not None:
            config["steps_per_eval"] = steps_eval_override
        steps_report_override = _env_int(env, "MLX_STEPS_PER_REPORT")
        if steps_report_override is not None:
            config["steps_per_report"] = steps_report_override
        val_batches_override = _env_int(env, "MLX_VAL_BATCHES")
        if val_batches_override is not None:
            config["val_batches"] = val_batches_override
        if env.get("MLX_FAST") == "1":
            iters = config.get("iters")
            if iters is None:
                iters = 1000000
            config["steps_per_eval"] = max(int(iters), int(config.get("steps_per_eval", 200)))
            config["save_every"] = max(int(iters), int(config.get("save_every", 100)))
            config["val_batches"] = 1
            config["steps_per_report"] = max(int(config.get("steps_per_report", 10)), 50)
    else:
        raise FileNotFoundError("MLX dataset export missing train.jsonl or valid.jsonl")

    write_yaml(train_config_path, config)

    if importlib.util.find_spec("mlx_lm_lora") is None:
        raise RuntimeError(
            "mlx_lm_lora is not installed; install the MLX training package "
            "and ensure `python -m mlx_lm_lora.train` works before rerunning."
        )

    print("running_mlx_train=", train_config_path)
    train_start = time.monotonic()
    subprocess.run(
        [sys.executable, "-m", "mlx_lm_lora.train", "--config", str(train_config_path)],
        check=True,
        env=env,
    )
    train_elapsed = time.monotonic() - train_start
    print(f"mlx_train_wall_time_s={train_elapsed:.3f}")

    if eval_data and eval_db:
        print("running_mlx_eval_post=", eval_script)
        eval_args = [
            sys.executable,
            str(eval_script),
            "--model",
            env.get("MLX_MODEL", "Qwen/Qwen3-0.6B"),
            "--adapter-path",
            str(mlx_dir / "adapters"),
            "--data",
            eval_data,
            "--db",
            eval_db,
            "--output-dir",
            str(artifacts_root / "reports"),
            "--stage",
            "student_eval_post",
            "--system-prompt",
            eval_system_prompt,
        ]
        if eval_limit:
            eval_args += ["--limit", eval_limit]
        if eval_max_tokens:
            eval_args += ["--max-tokens", eval_max_tokens]
        if eval_log_every:
            eval_args += ["--log-every", eval_log_every]
        subprocess.run(eval_args, check=True, env=env)

    print("mlx_artifacts_dir=", mlx_dir)


if __name__ == "__main__":
    main()
