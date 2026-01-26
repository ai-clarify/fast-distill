# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import importlib
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Dict, Iterable, Mapping, Optional

from fastdistill.errors import FastDistillUserError


def _load_import_path(import_path: str) -> Any:
    module_path, attr = import_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def _entry_points(group: str) -> Iterable[metadata.EntryPoint]:
    entry_points = metadata.entry_points()
    if hasattr(entry_points, "select"):
        return entry_points.select(group=group)
    return entry_points.get(group, [])


def _lazy_imports(module_path: str) -> Dict[str, str]:
    module = importlib.import_module(module_path)
    imports = getattr(module, "_LAZY_IMPORTS", None)
    if not isinstance(imports, Mapping):
        raise RuntimeError(f"{module_path} does not expose _LAZY_IMPORTS")
    return dict(imports)


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    import_path: str
    source: str
    entry_point: Optional[metadata.EntryPoint] = None

    def load(self) -> Any:
        if self.entry_point is not None:
            return self.entry_point.load()
        return _load_import_path(self.import_path)


class ComponentRegistry:
    def __init__(
        self,
        kind: str,
        builtin_imports: Mapping[str, str],
        entrypoint_group: str,
        *,
        exclude_names: Optional[Iterable[str]] = None,
    ) -> None:
        self.kind = kind
        self._builtin_imports = dict(builtin_imports)
        self._entrypoint_group = entrypoint_group
        self._exclude_names = set(exclude_names or ())
        self._specs: Optional[Dict[str, ComponentSpec]] = None
        self._loaded: Dict[str, Any] = {}

    def _build_specs(self) -> Dict[str, ComponentSpec]:
        specs: Dict[str, ComponentSpec] = {}
        for name, import_path in self._builtin_imports.items():
            if name in self._exclude_names:
                continue
            specs[name] = ComponentSpec(
                name=name,
                import_path=import_path,
                source="builtin",
            )
        for entry_point in _entry_points(self._entrypoint_group):
            if entry_point.name in specs:
                raise FastDistillUserError(
                    f"Duplicate {self.kind} component '{entry_point.name}' from entry point"
                    f" '{entry_point.value}'. Please rename the plugin entry or remove the"
                    " conflicting component."
                )
            specs[entry_point.name] = ComponentSpec(
                name=entry_point.name,
                import_path=entry_point.value,
                source="plugin",
                entry_point=entry_point,
            )
        return specs

    def specs(self) -> Dict[str, ComponentSpec]:
        if self._specs is None:
            self._specs = self._build_specs()
        return self._specs

    def names(self) -> list[str]:
        return sorted(self.specs().keys())

    def get(self, name: str) -> Any:
        if name in self._loaded:
            return self._loaded[name]
        spec = self.specs().get(name)
        if spec is None:
            raise FastDistillUserError(
                f"Unknown {self.kind} component '{name}'. Available: {', '.join(self.names())}"
            )
        try:
            value = spec.load()
        except Exception as exc:
            raise FastDistillUserError(
                f"Failed to load {self.kind} component '{name}' from '{spec.import_path}'."
            ) from exc
        self._loaded[name] = value
        return value


_LLM_EXCLUDES = {
    "LLM",
    "AsyncLLM",
    "CudaDevicePlacementMixin",
    "GenerateOutput",
    "HiddenState",
}
_EMBEDDINGS_EXCLUDES = {"Embeddings"}
_IMAGE_EXCLUDES = {"ImageGenerationModel", "AsyncImageGenerationModel"}
_STEP_EXCLUDES = {
    "Step",
    "StepInput",
    "StepOutput",
    "StepResources",
    "GeneratorStep",
    "GeneratorStepOutput",
    "GlobalStep",
    "make_generator_step",
    "step",
}
_TASK_EXCLUDES = {"Task", "GeneratorTask", "ImageTask", "ChatItem", "ChatType", "task"}


llm_registry = ComponentRegistry(
    kind="llm",
    builtin_imports=_lazy_imports("fastdistill.models.llms"),
    entrypoint_group="fastdistill.llms",
    exclude_names=_LLM_EXCLUDES,
)
embeddings_registry = ComponentRegistry(
    kind="embeddings",
    builtin_imports=_lazy_imports("fastdistill.models.embeddings"),
    entrypoint_group="fastdistill.embeddings",
    exclude_names=_EMBEDDINGS_EXCLUDES,
)
image_generation_registry = ComponentRegistry(
    kind="image_generation",
    builtin_imports=_lazy_imports("fastdistill.models.image_generation"),
    entrypoint_group="fastdistill.image_generation",
    exclude_names=_IMAGE_EXCLUDES,
)
step_registry = ComponentRegistry(
    kind="step",
    builtin_imports=_lazy_imports("fastdistill.steps"),
    entrypoint_group="fastdistill.steps",
    exclude_names=_STEP_EXCLUDES,
)
task_registry = ComponentRegistry(
    kind="task",
    builtin_imports=_lazy_imports("fastdistill.steps.tasks"),
    entrypoint_group="fastdistill.tasks",
    exclude_names=_TASK_EXCLUDES,
)


REGISTRIES = {
    "llm": llm_registry,
    "embeddings": embeddings_registry,
    "image_generation": image_generation_registry,
    "step": step_registry,
    "task": task_registry,
}


def get_registry(kind: str) -> ComponentRegistry:
    registry = REGISTRIES.get(kind)
    if registry is None:
        raise FastDistillUserError(
            f"Unknown registry kind '{kind}'. Available: {', '.join(sorted(REGISTRIES))}"
        )
    return registry


__all__ = [
    "REGISTRIES",
    "ComponentRegistry",
    "ComponentSpec",
    "embeddings_registry",
    "get_registry",
    "image_generation_registry",
    "llm_registry",
    "step_registry",
    "task_registry",
]
