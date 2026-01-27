# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastdistill.errors import FastDistillUserError
from fastdistill.utils.serialization import read_yaml, write_yaml


def _ensure_valid_split(mlx_dir: Path) -> None:
    train_path = mlx_dir / "train.jsonl"
    valid_path = mlx_dir / "valid.jsonl"
    if not train_path.exists() or not valid_path.exists():
        raise FastDistillUserError(
            "MLX dataset export missing train.jsonl or valid.jsonl in the mlx directory."
        )

    train_lines = train_path.read_text(encoding="utf-8").splitlines()
    valid_lines = valid_path.read_text(encoding="utf-8").splitlines()

    if not valid_lines and train_lines:
        valid_lines = [train_lines.pop()]
        train_path.write_text("\n".join(train_lines) + "\n", encoding="utf-8")
        valid_path.write_text("\n".join(valid_lines) + "\n", encoding="utf-8")

    if not train_lines:
        raise FastDistillUserError("MLX training set is empty after split adjustment.")


def prepare_mlx_train_config(
    *,
    mlx_dir: Path,
    base_config_path: Optional[Path],
    model: Optional[str],
    iters: Optional[int],
    batch_size: Optional[int],
    max_seq_length: Optional[int],
) -> Path:
    if base_config_path and base_config_path.exists():
        config = read_yaml(base_config_path)
    else:
        config = {}

    config["data"] = str(mlx_dir)
    config["adapter_path"] = str(mlx_dir / "adapters")
    if model:
        config["model"] = model
    if iters is not None:
        config["iters"] = iters
    if batch_size is not None:
        config["batch_size"] = batch_size
    if max_seq_length is not None:
        config["max_seq_length"] = max_seq_length

    train_config_path = mlx_dir / "mlx_train.yaml"
    write_yaml(train_config_path, config)
    return train_config_path


def run_mlx_training(train_config_path: Path) -> None:
    if importlib.util.find_spec("mlx_lm_lora") is None:
        raise FastDistillUserError(
            "mlx_lm_lora is not installed; install the MLX training package before training."
        )
    subprocess.run(
        [sys.executable, "-m", "mlx_lm_lora.train", "--config", str(train_config_path)],
        check=True,
    )


def run_mlx_pipeline(
    *,
    mlx_dir: Path,
    base_config_path: Optional[Path],
    model: Optional[str],
    iters: Optional[int],
    batch_size: Optional[int],
    max_seq_length: Optional[int],
) -> Path:
    _ensure_valid_split(mlx_dir)
    train_config_path = prepare_mlx_train_config(
        mlx_dir=mlx_dir,
        base_config_path=base_config_path,
        model=model,
        iters=iters,
        batch_size=batch_size,
        max_seq_length=max_seq_length,
    )
    run_mlx_training(train_config_path)
    return train_config_path
