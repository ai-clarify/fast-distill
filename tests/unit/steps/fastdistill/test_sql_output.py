# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from distilabel.steps.fastdistill.sql_output import SqlOutputCleaner, clean_sql_output


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
