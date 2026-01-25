# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import Any, List

from typing_extensions import override

from fastdistill.models.llms.base import LLM
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.structured_generation import StructuredGeneration
from fastdistill.typing import GenerateOutput, StructuredInput


class DummyStructuredLLM(LLM):
    def load(self) -> None:
        pass

    @property
    def model_name(self) -> str:
        return "test"

    @override
    def generate(  # type: ignore
        self, inputs: List["StructuredInput"], num_generations: int = 1, **kwargs: Any
    ) -> List["GenerateOutput"]:
        return [
            {
                "generations": [
                    json.dumps({"test": "output"}) for _ in range(num_generations)
                ],
                "statistics": {
                    "input_tokens": [12] * num_generations,
                    "output_tokens": [12] * num_generations,
                },
            }
            for _ in inputs
        ]


class TestStructuredGeneration:
    def test_format_input(self) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        llm = DummyStructuredLLM()
        task = StructuredGeneration(name="task", llm=llm, pipeline=pipeline)

        # 1. Including the `grammar` field within the input
        assert task.format_input(
            {
                "instruction": "test",
                "system_prompt": "test",
                "structured_output": {"format": "regex", "schema": r"[a-zA-Z]+"},
            }
        ) == (
            [{"role": "user", "content": "test"}],
            {"format": "regex", "schema": r"[a-zA-Z]+"},
        )

        # 2. Not including the `grammar` field within the input
        assert task.format_input({"instruction": "test", "system_prompt": "test"}) == (
            [{"role": "user", "content": "test"}],
            None,
        )

    def test_format_input_with_system_prompt(self) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        llm = DummyStructuredLLM()
        task = StructuredGeneration(
            name="task",
            llm=llm,
            pipeline=pipeline,
            use_system_prompt=True,
        )

        assert task.format_input({"instruction": "test", "system_prompt": "test"}) == (
            [
                {"role": "system", "content": "test"},
                {"role": "user", "content": "test"},
            ],
            None,
        )

    def test_process(self) -> None:
        pipeline = Pipeline(name="unit-test-pipeline")
        llm = DummyStructuredLLM()
        task = StructuredGeneration(
            name="task", llm=llm, pipeline=pipeline, add_raw_input=False
        )
        assert next(
            task.process(
                [
                    {
                        "instruction": "test",
                        "structured_output": {
                            "format": "json",
                            "schema": {
                                "properties": {
                                    "test": {"title": "Test", "type": "string"}
                                },
                                "required": ["test"],
                                "title": "Test",
                                "type": "object",
                            },
                        },
                    }
                ]
            )
        ) == [
            {
                "instruction": "test",
                "structured_output": {
                    "format": "json",
                    "schema": {
                        "properties": {"test": {"title": "Test", "type": "string"}},
                        "required": ["test"],
                        "title": "Test",
                        "type": "object",
                    },
                },
                "generation": '{"test": "output"}',
                "model_name": "test",
                "fastdistill_metadata": {
                    "raw_output_task": '{"test": "output"}',
                    "statistics_task": {"input_tokens": 12, "output_tokens": 12},
                },
            }
        ]
