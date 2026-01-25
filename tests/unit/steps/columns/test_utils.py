# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.constants import FASTDISTILL_METADATA_KEY
from fastdistill.steps.columns.utils import merge_fastdistill_metadata


def test_merge_fastdistill_metadata() -> None:
    rows = [
        {FASTDISTILL_METADATA_KEY: {"a": 1, "b": 1}},
        {FASTDISTILL_METADATA_KEY: {"a": 2, "b": 2}},
    ]
    result = merge_fastdistill_metadata(*rows)
    assert result == {"a": [1, 2], "b": [1, 2]}


def test_merge_fastdistill_metadata_list() -> None:
    rows = [
        {
            FASTDISTILL_METADATA_KEY: [
                {"a": 1.0, "b": 1.0},
                {"a": 1.1, "b": 1.1},
                {"a": 1.2, "b": 1.2},
            ]
        },
        {
            FASTDISTILL_METADATA_KEY: [
                {"a": 2.0, "b": 2.0},
                {"a": 2.1, "b": 2.1},
                {"a": 2.2, "b": 2.2},
            ]
        },
    ]
    result = merge_fastdistill_metadata(*rows)
    assert result == [
        {"a": 1.0, "b": 1.0},
        {"a": 1.1, "b": 1.1},
        {"a": 1.2, "b": 1.2},
        {"a": 2.0, "b": 2.0},
        {"a": 2.1, "b": 2.1},
        {"a": 2.2, "b": 2.2},
    ]
