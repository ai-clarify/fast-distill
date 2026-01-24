import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

from distilabel.utils.serialization import read_yaml, write_yaml


def main() -> None:
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
    print("running_distillation=", pipeline)
    distill_start = time.monotonic()
    subprocess.run([sys.executable, str(pipeline)], check=True, env=env)
    distill_elapsed = time.monotonic() - distill_start
    print(f"distillation_wall_time_s={distill_elapsed:.3f}")

    mlx_dir = artifacts_root / "mlx"
    mlx_dir.mkdir(parents=True, exist_ok=True)

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

    print("mlx_artifacts_dir=", mlx_dir)


if __name__ == "__main__":
    main()
