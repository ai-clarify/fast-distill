# Copyright 2026 cklxx
#
# Licensed under the MIT License.

# ruff: noqa: F401

from typing import TYPE_CHECKING

from fastdistill.utils import lazy_imports as _lazy_imports

if TYPE_CHECKING:
    from fastdistill.models.embeddings.base import Embeddings
    from fastdistill.models.embeddings.llamacpp import LlamaCppEmbeddings
    from fastdistill.models.embeddings.sentence_transformers import (
        SentenceTransformerEmbeddings,
    )
    from fastdistill.models.embeddings.vllm import vLLMEmbeddings

_LAZY_IMPORTS = {
    "Embeddings": "fastdistill.models.embeddings.base:Embeddings",
    "LlamaCppEmbeddings": "fastdistill.models.embeddings.llamacpp:LlamaCppEmbeddings",
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
