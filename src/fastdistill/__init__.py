# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

from typing import TYPE_CHECKING

from rich import traceback as rich_traceback

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.distiset import Distiset
    from fastdistill.models.embeddings.base import Embeddings
    from fastdistill.models.image_generation.base import ImageGenerationModel
    from fastdistill.models.llms.base import LLM, AsyncLLM
    from fastdistill.pipeline.base import BasePipeline
    from fastdistill.pipeline.local import Pipeline
    from fastdistill.pipeline.ray import RayPipeline
    from fastdistill.steps.base import (
        GeneratorStep,
        GlobalStep,
        Step,
        StepInput,
        StepResources,
    )
    from fastdistill.typing import GeneratorStepOutput, StepOutput

__version__ = "1.5.3"

rich_traceback.install(show_locals=True)

_LAZY_IMPORTS = {
    "AsyncLLM": "fastdistill.models.llms.base:AsyncLLM",
    "BasePipeline": "fastdistill.pipeline.base:BasePipeline",
    "Distiset": "fastdistill.distiset:Distiset",
    "Embeddings": "fastdistill.models.embeddings.base:Embeddings",
    "GeneratorStep": "fastdistill.steps.base:GeneratorStep",
    "GeneratorStepOutput": "fastdistill.typing:GeneratorStepOutput",
    "GlobalStep": "fastdistill.steps.base:GlobalStep",
    "ImageGenerationModel": "fastdistill.models.image_generation.base:ImageGenerationModel",
    "LLM": "fastdistill.models.llms.base:LLM",
    "Pipeline": "fastdistill.pipeline.local:Pipeline",
    "RayPipeline": "fastdistill.pipeline.ray:RayPipeline",
    "Step": "fastdistill.steps.base:Step",
    "StepInput": "fastdistill.steps.base:StepInput",
    "StepOutput": "fastdistill.typing:StepOutput",
    "StepResources": "fastdistill.steps.base:StepResources",
}

__all__ = ["__version__", *_LAZY_IMPORTS.keys()]


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _lazy_imports.load_by_name(name, _LAZY_IMPORTS, globals())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
