from pathlib import Path

from fastdistill.agent.bundle import build_agent_bundle


def test_build_agent_bundle_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "agents"
    bundle = build_agent_bundle(str(output_dir), name="My Agent", run_id="run-1")

    assert bundle.root == output_dir.resolve() / "run-1"
    assert bundle.spec_path == bundle.root / "spec.yaml"
    assert bundle.pipeline_path == bundle.root / "pipeline.yaml"
    assert bundle.card_path == bundle.root / "agent_card.md"
    assert bundle.artifacts_root == bundle.root / "artifacts"
    assert bundle.reports_dir == bundle.artifacts_root / "reports"
    assert bundle.manifests_dir == bundle.artifacts_root / "manifests"
    assert bundle.mlx_dir == bundle.artifacts_root / "mlx"
    assert bundle.train_config_path == bundle.mlx_dir / "mlx_train.yaml"
