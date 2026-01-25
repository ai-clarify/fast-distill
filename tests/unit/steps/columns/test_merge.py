# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, List, Optional

import pytest

from fastdistill.steps.columns.merge import MergeColumns


class TestMergeColumns:
    @pytest.mark.parametrize(
        "output_column, expected",
        [
            (None, "merged_column"),
            ("queries", "queries"),
        ],
    )
    def test_init(self, output_column: Optional[str], expected: str) -> None:
        task = MergeColumns(columns=["query", "queries"], output_column=output_column)

        assert task.inputs == ["query", "queries"]
        assert task.outputs == [expected]

    @pytest.mark.parametrize(
        "columns",
        [
            [{"query": 1, "queries": 2}],
            [{"query": 1, "queries": [2]}],
            [{"query": [1], "queries": [2]}],
        ],
    )
    def test_process(self, columns: List[Dict[str, Any]]) -> None:
        combiner = MergeColumns(
            columns=["query", "queries"],
        )
        output: List[Dict[str, Any]] = next(combiner.process(columns))
        assert output == [{"merged_column": [1, 2]}]
