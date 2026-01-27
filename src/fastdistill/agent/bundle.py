# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastdistill.agent.utils import make_run_id


@dataclass(frozen=True)
class AgentBundle:
    root: Path
    run_id: str
    spec_path: Path
    pipeline_path: Path
    card_path: Path
    artifacts_root: Path
    reports_dir: Path
    manifests_dir: Path
    mlx_dir: Path
    train_config_path: Path


def build_agent_bundle(
    output_dir: str, *, name: Optional[str], run_id: Optional[str]
) -> AgentBundle:
    bundle_run_id = run_id or make_run_id(name)
    root = Path(output_dir).expanduser().resolve() / bundle_run_id
    artifacts_root = root / "artifacts"
    reports_dir = artifacts_root / "reports"
    manifests_dir = artifacts_root / "manifests"
    mlx_dir = artifacts_root / "mlx"
    return AgentBundle(
        root=root,
        run_id=bundle_run_id,
        spec_path=root / "spec.yaml",
        pipeline_path=root / "pipeline.yaml",
        card_path=root / "agent_card.md",
        artifacts_root=artifacts_root,
        reports_dir=reports_dir,
        manifests_dir=manifests_dir,
        mlx_dir=mlx_dir,
        train_config_path=mlx_dir / "mlx_train.yaml",
    )
