# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.config import deep_merge_dicts, load_layered_config
from fastdistill.utils.serialization import write_yaml


def test_deep_merge_dicts_overrides() -> None:
    base = {"pipeline": {"name": "base", "steps": {"step1": {"a": 1}}}}
    override = {"pipeline": {"name": "override", "steps": {"step1": {"b": 2}}}}

    merged = deep_merge_dicts(base, override)

    assert merged["pipeline"]["name"] == "override"
    assert merged["pipeline"]["steps"]["step1"] == {"a": 1, "b": 2}


def test_load_layered_config(tmp_path) -> None:
    base_path = tmp_path / "base.yaml"
    env_path = tmp_path / "env.yaml"
    run_path = tmp_path / "run.yaml"

    write_yaml(
        base_path,
        {
            "pipeline": {"name": "base", "steps": {"step1": {"a": 1}}},
            "requirements": ["fastdistill"],
        },
    )
    write_yaml(env_path, {"pipeline": {"steps": {"step1": {"b": 2}}}})
    write_yaml(run_path, {"pipeline": {"name": "run"}})

    merged = load_layered_config(
        str(base_path), env_path=str(env_path), run_path=str(run_path)
    )

    assert merged["pipeline"]["name"] == "run"
    assert merged["pipeline"]["steps"]["step1"] == {"a": 1, "b": 2}
    assert merged["requirements"] == ["fastdistill"]
