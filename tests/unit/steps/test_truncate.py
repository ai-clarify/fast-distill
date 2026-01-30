# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import importlib.util
from typing import Optional

import pytest

from fastdistill.steps.truncate import TruncateTextColumn

requires_transformers = pytest.mark.skipif(
    not importlib.util.find_spec("transformers"),
    reason="transformers not installed",
)


@pytest.mark.parametrize(
    "max_length, text, tokenizer, expected",
    [
        (
            10,
            "This is a sample text that is longer than 10 characters",
            None,
            "This is a ",
        ),
        pytest.param(
            4,
            "This is a sample text that is longer than 10 characters",
            "teknium/OpenHermes-2.5-Mistral-7B",
            "This is a sample",
            marks=requires_transformers,
        ),
    ],
)
def test_truncate_row(
    max_length: int, text: str, tokenizer: Optional[str], expected: str
) -> None:
    trunc = TruncateTextColumn(
        column="text", max_length=max_length, tokenizer=tokenizer
    )
    trunc.load()

    assert next(trunc.process([{"text": text}])) == [{"text": expected}]
