# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Protocol

from fastdistill.providers.types import (
    ChatRequest,
    ChatResponse,
    EmbeddingsRequest,
    EmbeddingsResponse,
    ImageRequest,
    ImageResponse,
)


class ChatProvider(Protocol):
    def generate(self, request: ChatRequest) -> ChatResponse: ...


class EmbeddingsProvider(Protocol):
    def embed(self, request: EmbeddingsRequest) -> EmbeddingsResponse: ...


class ImageProvider(Protocol):
    def generate(self, request: ImageRequest) -> ImageResponse: ...


__all__ = [
    "ChatProvider",
    "EmbeddingsProvider",
    "ImageProvider",
]
