# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Union

import pytest

pytest.importorskip("instructor")

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.quality_scorer import QualityScorer
from tests.unit.conftest import DummyAsyncLLM


class TestQualityScorer:
    def test_format_input(self) -> None:
        task = QualityScorer(
            name="quality_scorer",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        result = task.format_input(
            input={
                "instruction": "instruction 1",
                "responses": ["response 1", "response 2", "response 3"],
            }
        )

        assert result == [
            {
                "role": "user",
                "content": "Rank the following pair of instructions and responses according to their quality. Your evaluation should consider factors such as helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response. Score 1-3.\nScore each response from 1 to 3, with 4 reserved for responses that are already very well written and cannot be improved further. You should respond with the format:\n[1] Score: 1\n[2] Score: 2\n...\n#Question#: instruction 1\n#Response List#:\n\n[1] response 1\n[2] response 2\n[3] response 3",
            }
        ]

    @pytest.mark.parametrize(
        "output, use_default_structured_output, expected",
        [
            (
                "[1] Score: 1\n[2] Score: 2\n[3] Score: 3\n",
                False,
                {"scores": [1.0, 2.0, 3.0]},
            ),
            (
                "[1] Score: 1\n[2] Score: 2\n[3] Score: 3\njfjfjfjjfjfjf this is noise from the llm\nlallalalala more noise\nand more noise",
                False,
                {"scores": [1.0, 2.0, 3.0]},
            ),
            (
                None,
                False,
                {"scores": [None, None, None]},
            ),
            (
                '{"scores":[1,2,3]}',
                True,
                {"scores": [1.0, 2.0, 3.0]},
            ),
            (
                "wrong",
                True,
                {"scores": [None, None, None]},
            ),
        ],
    )
    def test_format_output(
        self,
        output: Union[str, None],
        use_default_structured_output: bool,
        expected: Dict[str, Any],
    ) -> None:
        task = QualityScorer(
            llm=DummyAsyncLLM(),
            use_default_structured_output=use_default_structured_output,
        )
        task.load()

        result = task.format_output(
            output=output,
            input={
                "instruction": "instruction 1",
                "responses": ["response 1", "response 2", "response 3"],
            },
        )

        assert result == expected
