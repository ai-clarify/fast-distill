# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

import pytest

from fastdistill.utils.lists import flatten_responses


@pytest.mark.parametrize(
    "input, expected",
    [
        ([["A"], ["B"]], ["A", "B"]),
        ([["A", "B"], ["C", "D"]], ["B", "D"]),
    ],
)
def test_flatten_responses(input: List[List[str]], expected: List[str]) -> None:
    assert flatten_responses(input) == expected
