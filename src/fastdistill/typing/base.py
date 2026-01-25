# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List, Literal, Union

from typing_extensions import Required, TypedDict


class TextContent(TypedDict, total=False):
    type: Required[Literal["text"]]
    text: Required[str]


class ImageUrl(TypedDict):
    url: Required[str]
    """Either a URL of the image or the base64 encoded image data."""


class ImageContent(TypedDict, total=False):
    """Type alias for the user's message in a conversation that can include text or an image.
    It's the standard type for vision language models:
    https://platform.openai.com/docs/guides/vision
    """

    type: Required[Literal["image_url"]]
    image_url: Required[ImageUrl]


class ChatItem(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: Union[str, list[Union[TextContent, ImageContent]]]


ChatType = List[ChatItem]
"""ChatType is a type alias for a `list` of `dict`s following the OpenAI conversational format."""
