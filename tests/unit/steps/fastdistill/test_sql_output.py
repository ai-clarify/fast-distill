# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import pytest

from fastdistill.steps.fastdistill.sql_output import SqlOutputCleaner, clean_sql_output


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("SELECT * FROM t", "SELECT * FROM t"),
        ("sql: SELECT a FROM b", "SELECT a FROM b"),
        ("```sql\nSELECT a FROM b\n```", "SELECT a FROM b"),
        (
            "<think>hidden</think>\nSELECT a FROM b",
            "SELECT a FROM b",
        ),
        (
            "<analysis>hidden</analysis> SQL: SELECT a FROM b",
            "SELECT a FROM b",
        ),
        (
            "reasoning: ...\nSELECT a FROM b\nfinal: done",
            "SELECT a FROM b",
        ),
    ],
)
def test_clean_sql_output(text: str, expected: str) -> None:
    assert clean_sql_output(text) == expected


def test_clean_sql_output_requires_keyword() -> None:
    assert clean_sql_output("<think>only reasoning</think>") == ""


def test_clean_sql_output_allows_no_keyword_when_configured() -> None:
    cleaner = SqlOutputCleaner(require_sql_keyword=False)
    assert cleaner.clean("<think>only reasoning</think>") == ""
    assert cleaner.clean("result: ok") == "result: ok"
