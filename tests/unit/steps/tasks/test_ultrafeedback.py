# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import importlib.util
from typing import Any, Dict, List, Union

import pytest

from fastdistill.models.llms.base import LLM
from fastdistill.steps.tasks.ultrafeedback import UltraFeedback
from fastdistill.typing import ChatType, GenerateOutput

pytest.importorskip("instructor")

requires_outlines = pytest.mark.skipif(
    not importlib.util.find_spec("outlines"),
    reason="outlines not installed",
)


class UltraFeedbackLLM(LLM):
    structured_output: Any = None

    def load(self) -> None:
        pass

    @property
    def model_name(self) -> str:
        return "ultrafeedback-model"

    def generate(
        self, inputs: List[ChatType], num_generations: int = 1, **kwargs: Any
    ) -> List[GenerateOutput]:
        return [
            {
                "generations": [
                    "Type: 1\nRationale: text\nRating: 1\nRationale: text\n\nType: 2\nRationale: text\nRating: 2\nRationale: text"
                    for i in range(num_generations)
                ],
                "statistics": {
                    "input_tokens": [12] * num_generations,
                    "output_tokens": [12] * num_generations,
                },
            }
        ] * len(inputs)


class TestUltraFeedback:
    def test_process_with_simple_aspect(self) -> None:
        task = UltraFeedback(
            name="ultrafeedback",
            aspect="instruction-following",
            llm=UltraFeedbackLLM(),
            use_default_structured_output=False,
            add_raw_input=False,
        )
        task.load()

        assert next(
            task.process([{"instruction": "test", "generations": ["A", "B"]}])
        ) == [
            {
                "instruction": "test",
                "generations": ["A", "B"],
                "ratings": [1, 2],
                "rationales": ["text", "text"],
                "model_name": "ultrafeedback-model",
                "fastdistill_metadata": {
                    "raw_output_ultrafeedback": "Type: 1\nRationale: text\nRating: 1\nRationale: text\n\nType: 2\nRationale: text\nRating: 2\nRationale: text",
                    "statistics_ultrafeedback": {
                        "input_tokens": 12,
                        "output_tokens": 12,
                    },
                },
            }
        ]

    def test_process_with_complex_aspect(self) -> None:
        task = UltraFeedback(
            name="ultrafeedback",
            aspect="truthfulness",
            llm=UltraFeedbackLLM(),
            use_default_structured_output=False,
            add_raw_input=False,
        )
        task.load()

        assert next(
            task.process([{"instruction": "test", "generations": ["A", "B"]}])
        ) == [
            {
                "instruction": "test",
                "generations": ["A", "B"],
                "types": [1, 2],
                "rationales": ["text", "text"],
                "ratings": [1, 2],
                "rationales-for-ratings": ["text", "text"],
                "model_name": "ultrafeedback-model",
                "fastdistill_metadata": {
                    "raw_output_ultrafeedback": "Type: 1\nRationale: text\nRating: 1\nRationale: text\n\nType: 2\nRationale: text\nRating: 2\nRationale: text",
                    "statistics_ultrafeedback": {
                        "input_tokens": 12,
                        "output_tokens": 12,
                    },
                },
            }
        ]

    @requires_outlines
    @pytest.mark.parametrize(
        "output, use_default_structured_output, aspect, expected",
        [
            (
                "{ \n   random\n}",
                True,
                "honesty",
                {"ratings": [None, None], "rationales": [None, None]},
            ),
            (
                '{ \n  "ratings": [\n    1,\n    5\n  ]\n ,\n  "rationales": [\n    "rationale1",\n    "rationale2"\n  ]}',
                True,
                "honesty",
                {"ratings": [1, 5], "rationales": ["rationale1", "rationale2"]},
            ),
            (
                "{ \n   random\n}",
                True,
                "helpfulness",
                {
                    "ratings": [None, None],
                    "rationales": [None, None],
                    "rationales-for-ratings": [None, None],
                    "types": [None, None],
                },
            ),
            (
                '{ \n  "ratings": [\n    1,\n    5\n  ]\n ,\n  "rationales": [\n    "rationale1",\n    "rationale2"\n  ], "rationales-for-ratings": [\n    "rationale1",\n    "rationale2"\n  ], "types": [\n    1,\n    2\n  ]}',
                True,
                "helpfulness",
                {
                    "ratings": [1, 5],
                    "rationales": ["rationale1", "rationale2"],
                    "rationales-for-ratings": ["rationale1", "rationale2"],
                    "types": [1, 2],
                },
            ),
        ],
    )
    def test_format_output(
        self,
        output: Union[str, None],
        use_default_structured_output: bool,
        aspect: str,
        expected: Dict[str, Any],
    ) -> None:
        task = UltraFeedback(
            llm=UltraFeedbackLLM(),
            aspect=aspect,
            use_default_structured_output=use_default_structured_output,
        )
        task.load()

        result = task.format_output(
            output=output,
            input={
                "instruction": "How much is 2+2?",
                "generations": ["4", "something weird"],
            },
        )

        assert result == expected
