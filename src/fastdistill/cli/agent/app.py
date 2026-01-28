# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from typing import Any, Dict, Optional

import typer
import yaml

from fastdistill.agent.config import load_agent_config
from fastdistill.agent.runner import distill_agent

app = typer.Typer(help="Distill task-specific agents using Claude Agent SDK.")


def _set_override(overrides: Dict[str, Any], *keys: str, value: Any) -> None:
    if value is None:
        return
    target = overrides
    for key in keys[:-1]:
        target = target.setdefault(key, {})
    target[keys[-1]] = value


@app.command(name="distill", help="Generate and distill an agent for a given task.")
def distill(
    task: Optional[str] = typer.Option(
        None, help="Task requirement to distill (overrides agent.task)."
    ),
    config: Optional[str] = typer.Option(
        None, help="Path to YAML agent config (agent/claude/teacher/training)."
    ),
    config_env: Optional[str] = typer.Option(
        None, help="Optional YAML config overlay applied after --config."
    ),
    config_run: Optional[str] = typer.Option(
        None, help="Optional YAML config overlay applied last."
    ),
    output_dir: Optional[str] = typer.Option(
        None, help="Override output directory for agent bundles."
    ),
    num_instructions: Optional[int] = typer.Option(
        None, help="Override number of instructions to generate."
    ),
    run_id: Optional[str] = typer.Option(
        None, help="Override run_id used in artifact paths."
    ),
    train: Optional[bool] = typer.Option(
        None,
        "--train/--no-train",
        help="Enable or disable MLX training step.",
    ),
    export_gguf: Optional[bool] = typer.Option(
        None,
        "--export-gguf/--no-export-gguf",
        help="Enable or disable GGUF export after training.",
    ),
    gguf_output: Optional[str] = typer.Option(None, help="Override GGUF output path."),
) -> None:
    overrides: Dict[str, Any] = {}
    _set_override(overrides, "agent", "task", value=task)
    _set_override(overrides, "agent", "output_dir", value=output_dir)
    _set_override(overrides, "agent", "num_instructions", value=num_instructions)
    _set_override(overrides, "agent", "run_id", value=run_id)
    if train is not None:
        _set_override(overrides, "training", "enabled", value=train)
    if export_gguf is not None:
        _set_override(overrides, "training", "export_gguf", value=export_gguf)
    _set_override(overrides, "training", "gguf_output", value=gguf_output)

    config_obj = load_agent_config(
        config,
        config_env=config_env,
        config_run=config_run,
        overrides=overrides or None,
    )
    bundle = distill_agent(task=task, config=config_obj)
    gguf_path = str(bundle.gguf_path) if bundle.gguf_path.exists() else None

    typer.echo(
        yaml.safe_dump(
            {
                "bundle_root": str(bundle.root),
                "spec_path": str(bundle.spec_path),
                "pipeline_path": str(bundle.pipeline_path),
                "agent_card": str(bundle.card_path),
                "artifacts_root": str(bundle.artifacts_root),
                "reports_dir": str(bundle.reports_dir),
                "manifests_dir": str(bundle.manifests_dir),
                "mlx_dir": str(bundle.mlx_dir),
                "gguf_path": gguf_path,
            },
            sort_keys=False,
        )
    )
