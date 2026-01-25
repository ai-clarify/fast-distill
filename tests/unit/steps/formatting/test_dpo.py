# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline import Pipeline
from fastdistill.steps.formatting.dpo import (
    FormatChatGenerationDPO,
    FormatTextGenerationDPO,
)


class TestFormatTextGenerationDPO:
    def test_process(self) -> None:
        step = FormatTextGenerationDPO(name="dpo", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "instruction": "What's 2+2?",
                        "generations": ["4", "5", "6"],
                        "generation_models": ["A", "B", "C"],
                        "ratings": [1, 0, -1],
                    }
                ]
            )
        ) == [
            {
                "instruction": "What's 2+2?",
                "generations": ["4", "5", "6"],
                "generation_models": ["A", "B", "C"],
                "ratings": [1, 0, -1],
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
                "chosen": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
                "chosen_rating": 1,
                "chosen_model": "A",
                "rejected": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "6"},
                ],
                "rejected_rating": -1,
                "rejected_model": "C",
            }
        ]

    def test_process_with_system_prompt(self) -> None:
        step = FormatTextGenerationDPO(name="dpo", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "system_prompt": "You are a helpful assistant.",
                        "instruction": "What's 2+2?",
                        "generations": ["4", "5", "6"],
                        "generation_models": ["A", "B", "C"],
                        "ratings": [1, 0, -1],
                    }
                ]
            )
        ) == [
            {
                "system_prompt": "You are a helpful assistant.",
                "instruction": "What's 2+2?",
                "generations": ["4", "5", "6"],
                "generation_models": ["A", "B", "C"],
                "ratings": [1, 0, -1],
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
                "chosen": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
                "chosen_rating": 1,
                "chosen_model": "A",
                "rejected": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "6"},
                ],
                "rejected_rating": -1,
                "rejected_model": "C",
            }
        ]


class TestFormatChatGenerationdpo:
    def test_process(self) -> None:
        step = FormatChatGenerationDPO(name="dpo", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "messages": [{"role": "user", "content": "What's 2+2?"}],
                        "generations": ["4", "5", "6"],
                        "generation_models": ["A", "B", "C"],
                        "ratings": [1, 0, -1],
                    }
                ]
            )
        ) == [
            {
                "messages": [{"role": "user", "content": "What's 2+2?"}],
                "generations": ["4", "5", "6"],
                "generation_models": ["A", "B", "C"],
                "ratings": [1, 0, -1],
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
                "chosen": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
                "chosen_rating": 1,
                "chosen_model": "A",
                "rejected": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "6"},
                ],
                "rejected_rating": -1,
                "rejected_model": "C",
            }
        ]
