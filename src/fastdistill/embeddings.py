# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: E402

import warnings

deprecation_message = (
    "Importing from 'fastdistill.embeddings' is deprecated and will be removed in a version 1.7.0. "
    "Import from 'fastdistill.models' instead."
)

warnings.warn(deprecation_message, DeprecationWarning, stacklevel=2)

from fastdistill.models.embeddings.base import Embeddings
from fastdistill.models.embeddings.sentence_transformers import (
    SentenceTransformerEmbeddings,
)
from fastdistill.models.embeddings.vllm import vLLMEmbeddings

__all__ = [
    "Embeddings",
    "SentenceTransformerEmbeddings",
    "vLLMEmbeddings",
]
