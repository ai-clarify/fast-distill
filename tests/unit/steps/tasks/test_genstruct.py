# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Union

import pytest

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.genstruct import Genstruct
from tests.unit.conftest import DummyAsyncLLM


class TestGenstruct:
    def test_format_input(self) -> None:
        task = Genstruct(
            name="genstruct",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        result = task.format_input(
            input={"title": "This is the title.\n", "content": "This is the content.\n"}
        )

        assert result == [
            {
                "role": "user",
                "content": "[[[Title]]] This is the title.\n[[[Content]]] This is the content.\n\nThe following is an interaction between a user and an AI assistant that is related to the above text.\n\n[[[User]]] ",
            }
        ]

    @pytest.mark.parametrize(
        "output, expected",
        [
            (
                "This is the instruction.\n[[[Assistant]]] This is the response.\n",
                {
                    "user": "This is the instruction.",
                    "assistant": "This is the response.",
                },
            ),
            (
                None,
                {"user": None, "assistant": None},
            ),
        ],
    )
    def test_format_output(
        self, output: Union[str, None], expected: Dict[str, Any]
    ) -> None:
        task = Genstruct(
            name="genstruct",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        assert (
            task.format_output(
                output=output,
                input={
                    "title": "This is the title.\n",
                    "content": "This is the content.\n",
                },
            )
            == expected
        )
