# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Union

import pytest

pytest.importorskip("instructor")

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.complexity_scorer import ComplexityScorer
from tests.unit.conftest import DummyAsyncLLM


class TestComplexityScorer:
    def test_format_input(self) -> None:
        task = ComplexityScorer(
            name="complexity_scorer",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        result = task.format_input(
            input={"instructions": ["instruction 1", "instruction 2", "instruction 3"]}
        )

        assert result == [
            {
                "role": "user",
                "content": "Ranking the following questions according to the difficulty and complexity. Score 1-3.\nYou can give a score of 4 if the question is too complex for you to answer it. You should\nrespond with the format:\n[1] Score: 1\n[2] Score: 2\n...\n\n[1] instruction 1\n[2] instruction 2\n[3] instruction 3",
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
        task = ComplexityScorer(
            llm=DummyAsyncLLM(),
            use_default_structured_output=use_default_structured_output,
        )
        task.load()

        result = task.format_output(
            output=output,
            input={"instructions": ["instruction 1", "instruction 2", "instruction 3"]},
        )

        assert result == expected
