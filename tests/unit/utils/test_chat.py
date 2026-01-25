# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any

import pytest

from fastdistill.utils.chat import is_openai_format


@pytest.mark.parametrize(
    "input, expected",
    [
        (None, False),
        (1, False),
        ("Hello", False),
        (
            [
                {"role": "user", "content": "Hello!"},
            ],
            True,
        ),
        (
            [
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
            ],
            True,
        ),
        (
            [
                {"role": "system", "content": "You're a helpful assistant"},
                {"role": "user", "content": "Hello!"},
                {"role": "assistant", "content": "Hi! How can I help you?"},
            ],
            True,
        ),
        (
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                            },
                        },
                    ],
                }
            ],
            True,
        ),
    ],
)
def test_is_openai_format(input: Any, expected: bool) -> None:
    assert is_openai_format(input) == expected
