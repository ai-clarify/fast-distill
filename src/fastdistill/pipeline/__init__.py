# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

from typing import TYPE_CHECKING

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.pipeline.local import Pipeline
    from fastdistill.pipeline.ray import RayPipeline
    from fastdistill.pipeline.routing_batch_function import (
        routing_batch_function,
        sample_n_steps,
    )
    from fastdistill.pipeline.templates.instruction import InstructionResponsePipeline

_LAZY_IMPORTS = {
    "InstructionResponsePipeline": (
        "fastdistill.pipeline.templates.instruction:InstructionResponsePipeline"
    ),
    "Pipeline": "fastdistill.pipeline.local:Pipeline",
    "RayPipeline": "fastdistill.pipeline.ray:RayPipeline",
    "routing_batch_function": "fastdistill.pipeline.routing_batch_function:routing_batch_function",
    "sample_n_steps": "fastdistill.pipeline.routing_batch_function:sample_n_steps",
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _lazy_imports.load_by_name(name, _LAZY_IMPORTS, globals())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
