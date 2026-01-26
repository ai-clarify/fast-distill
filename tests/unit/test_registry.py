from importlib import metadata

import pytest

from fastdistill.errors import FastDistillUserError
from fastdistill.registry import ComponentRegistry


def test_registry_gets_builtin_component() -> None:
    registry = ComponentRegistry(
        kind="llm",
        builtin_imports={"LLM": "fastdistill.models.llms.base:LLM"},
        entrypoint_group="fastdistill.llms",
    )

    component = registry.get("LLM")

    assert component.__name__ == "LLM"


def test_registry_loads_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    entry_point = metadata.EntryPoint(
        name="PluginLLM",
        value="fastdistill.models.llms.base:LLM",
        group="fastdistill.llms",
    )
    entry_points = metadata.EntryPoints([entry_point])
    monkeypatch.setattr(metadata, "entry_points", lambda: entry_points)

    registry = ComponentRegistry(
        kind="llm",
        builtin_imports={},
        entrypoint_group="fastdistill.llms",
    )

    component = registry.get("PluginLLM")

    assert component.__name__ == "LLM"


def test_registry_rejects_entry_point_collisions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry_point = metadata.EntryPoint(
        name="LLM",
        value="fastdistill.models.llms.base:LLM",
        group="fastdistill.llms",
    )
    entry_points = metadata.EntryPoints([entry_point])
    monkeypatch.setattr(metadata, "entry_points", lambda: entry_points)

    registry = ComponentRegistry(
        kind="llm",
        builtin_imports={"LLM": "fastdistill.models.llms.base:LLM"},
        entrypoint_group="fastdistill.llms",
    )

    with pytest.raises(FastDistillUserError, match="Duplicate llm component"):
        registry.names()


def test_registry_errors_on_unknown_component() -> None:
    registry = ComponentRegistry(
        kind="llm",
        builtin_imports={},
        entrypoint_group="fastdistill.llms",
    )

    with pytest.raises(FastDistillUserError, match="Unknown llm component"):
        registry.get("MissingLLM")
