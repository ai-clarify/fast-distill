# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: E402

import warnings

deprecation_message = (
    "Importing from 'fastdistill.llms' is deprecated and will be removed in a version 1.7.0. "
    "Import from 'fastdistill.models' instead."
)

warnings.warn(deprecation_message, DeprecationWarning, stacklevel=2)

from fastdistill.models.llms.anthropic import AnthropicLLM
from fastdistill.models.llms.anyscale import AnyscaleLLM
from fastdistill.models.llms.azure import AzureOpenAILLM
from fastdistill.models.llms.base import LLM, AsyncLLM
from fastdistill.models.llms.cohere import CohereLLM
from fastdistill.models.llms.groq import GroqLLM
from fastdistill.models.llms.huggingface import InferenceEndpointsLLM, TransformersLLM
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

__all__ = [
    "LLM",
    "AnthropicLLM",
    "AnyscaleLLM",
    "AsyncLLM",
    "AzureOpenAILLM",
    "ClientvLLM",
    "CohereLLM",
    "CudaDevicePlacementMixin",
    "GenerateOutput",
    "GroqLLM",
    "HiddenState",
    "InferenceEndpointsLLM",
    "LiteLLM",
    "LlamaCppLLM",
    "MistralLLM",
    "MixtureOfAgentsLLM",
    "MlxLLM",
    "OllamaLLM",
    "OpenAILLM",
    "SGLangLLM",
    "TogetherLLM",
    "TransformersLLM",
    "VertexAILLM",
    "vLLM",
]
