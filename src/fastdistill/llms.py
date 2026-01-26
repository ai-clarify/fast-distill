# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: E402,F401

import warnings
from typing import TYPE_CHECKING

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.models.llms.anthropic import AnthropicLLM
    from fastdistill.models.llms.anyscale import AnyscaleLLM
    from fastdistill.models.llms.azure import AzureOpenAILLM
    from fastdistill.models.llms.base import LLM, AsyncLLM
    from fastdistill.models.llms.cohere import CohereLLM
    from fastdistill.models.llms.groq import GroqLLM
    from fastdistill.models.llms.huggingface.inference_endpoints import (
        InferenceEndpointsLLM,
    )
    from fastdistill.models.llms.huggingface.transformers import TransformersLLM
    from fastdistill.models.llms.litellm import LiteLLM
    from fastdistill.models.llms.llamacpp import LlamaCppLLM
    from fastdistill.models.llms.mistral import MistralLLM
    from fastdistill.models.llms.mlx import MlxLLM
    from fastdistill.models.llms.moa import MixtureOfAgentsLLM
    from fastdistill.models.llms.ollama import OllamaLLM
    from fastdistill.models.llms.openai import OpenAILLM
    from fastdistill.models.llms.sglang import SGLangLLM
    from fastdistill.models.llms.together import TogetherLLM
    from fastdistill.models.llms.vertexai import VertexAILLM
    from fastdistill.models.llms.vllm import ClientvLLM, vLLM
    from fastdistill.models.mixins.cuda_device_placement import CudaDevicePlacementMixin
    from fastdistill.typing import GenerateOutput, HiddenState

deprecation_message = (
    "Importing from 'fastdistill.llms' is deprecated and will be removed in a version 1.7.0. "
    "Import from 'fastdistill.models' instead."
)

warnings.warn(deprecation_message, DeprecationWarning, stacklevel=2)

_LAZY_IMPORTS = {
    "LLM": "fastdistill.models.llms.base:LLM",
    "AsyncLLM": "fastdistill.models.llms.base:AsyncLLM",
    "AnthropicLLM": "fastdistill.models.llms.anthropic:AnthropicLLM",
    "AnyscaleLLM": "fastdistill.models.llms.anyscale:AnyscaleLLM",
    "AzureOpenAILLM": "fastdistill.models.llms.azure:AzureOpenAILLM",
    "CohereLLM": "fastdistill.models.llms.cohere:CohereLLM",
    "GroqLLM": "fastdistill.models.llms.groq:GroqLLM",
    "InferenceEndpointsLLM": "fastdistill.models.llms.huggingface.inference_endpoints:InferenceEndpointsLLM",
    "TransformersLLM": "fastdistill.models.llms.huggingface.transformers:TransformersLLM",
    "LiteLLM": "fastdistill.models.llms.litellm:LiteLLM",
    "LlamaCppLLM": "fastdistill.models.llms.llamacpp:LlamaCppLLM",
    "MistralLLM": "fastdistill.models.llms.mistral:MistralLLM",
    "MlxLLM": "fastdistill.models.llms.mlx:MlxLLM",
    "MixtureOfAgentsLLM": "fastdistill.models.llms.moa:MixtureOfAgentsLLM",
    "OllamaLLM": "fastdistill.models.llms.ollama:OllamaLLM",
    "OpenAILLM": "fastdistill.models.llms.openai:OpenAILLM",
    "SGLangLLM": "fastdistill.models.llms.sglang:SGLangLLM",
    "TogetherLLM": "fastdistill.models.llms.together:TogetherLLM",
    "VertexAILLM": "fastdistill.models.llms.vertexai:VertexAILLM",
    "ClientvLLM": "fastdistill.models.llms.vllm:ClientvLLM",
    "vLLM": "fastdistill.models.llms.vllm:vLLM",
    "CudaDevicePlacementMixin": "fastdistill.models.mixins.cuda_device_placement:CudaDevicePlacementMixin",
    "GenerateOutput": "fastdistill.typing:GenerateOutput",
    "HiddenState": "fastdistill.typing:HiddenState",
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _lazy_imports.load_by_name(name, _LAZY_IMPORTS, globals())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
