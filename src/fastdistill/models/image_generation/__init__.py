# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

from typing import TYPE_CHECKING

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.models.image_generation.base import (
        AsyncImageGenerationModel,
        ImageGenerationModel,
    )
    from fastdistill.models.image_generation.huggingface.inference_endpoints import (
        InferenceEndpointsImageGeneration,
    )
    from fastdistill.models.image_generation.openai import OpenAIImageGeneration

_LAZY_IMPORTS = {
    "AsyncImageGenerationModel": (
        "fastdistill.models.image_generation.base:AsyncImageGenerationModel"
    ),
    "ImageGenerationModel": "fastdistill.models.image_generation.base:ImageGenerationModel",
    "InferenceEndpointsImageGeneration": (
        "fastdistill.models.image_generation.huggingface.inference_endpoints:InferenceEndpointsImageGeneration"
    ),
    "OpenAIImageGeneration": "fastdistill.models.image_generation.openai:OpenAIImageGeneration",
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _lazy_imports.load_by_name(name, _LAZY_IMPORTS, globals())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
