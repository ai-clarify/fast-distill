# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: E402,F401

import warnings
from typing import TYPE_CHECKING

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.models.embeddings.base import Embeddings
    from fastdistill.models.embeddings.sentence_transformers import (
        SentenceTransformerEmbeddings,
    )
    from fastdistill.models.embeddings.vllm import vLLMEmbeddings

deprecation_message = (
    "Importing from 'fastdistill.embeddings' is deprecated and will be removed in a version 1.7.0. "
    "Import from 'fastdistill.models' instead."
)

warnings.warn(deprecation_message, DeprecationWarning, stacklevel=2)

_LAZY_IMPORTS = {
    "Embeddings": "fastdistill.models.embeddings.base:Embeddings",
    "SentenceTransformerEmbeddings": (
        "fastdistill.models.embeddings.sentence_transformers:SentenceTransformerEmbeddings"
    ),
    "vLLMEmbeddings": "fastdistill.models.embeddings.vllm:vLLMEmbeddings",
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> object:
    if name in _LAZY_IMPORTS:
        return _lazy_imports.load_by_name(name, _LAZY_IMPORTS, globals())
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_LAZY_IMPORTS.keys()))
