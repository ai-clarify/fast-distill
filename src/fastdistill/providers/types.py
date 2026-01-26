# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, List, TypedDict

from typing_extensions import NotRequired

from fastdistill.typing import ChatType


class ProviderTrace(TypedDict, total=False):
    run_id: str
    sample_id: str
    shard_id: int


class DecodeOptions(TypedDict, total=False):
    temperature: float
    top_p: float
    top_k: int
    max_tokens: int
    n: int
    seed: int


class ConstraintOptions(TypedDict, total=False):
    json_schema: Any
    stop: List[str]
    tool_spec: Any


class ChatRequest(TypedDict):
    provider_id: str
    model: str
    messages: ChatType
    decode: NotRequired[DecodeOptions]
    constraints: NotRequired[ConstraintOptions]
    trace: NotRequired[ProviderTrace]


class ChatResponse(TypedDict):
    generations: List[str]
    statistics: Dict[str, Any]
    raw: NotRequired[Any]


class EmbeddingsRequest(TypedDict):
    provider_id: str
    model: str
    inputs: List[str]
    trace: NotRequired[ProviderTrace]


class EmbeddingsResponse(TypedDict):
    embeddings: List[List[float]]
    raw: NotRequired[Any]


class ImageRequest(TypedDict):
    provider_id: str
    model: str
    inputs: List[str]
    trace: NotRequired[ProviderTrace]
    decode: NotRequired[DecodeOptions]


class ImageResponse(TypedDict):
    images: List[List[Dict[str, Any]]]
    raw: NotRequired[Any]


__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ConstraintOptions",
    "DecodeOptions",
    "EmbeddingsRequest",
    "EmbeddingsResponse",
    "ImageRequest",
    "ImageResponse",
    "ProviderTrace",
]
