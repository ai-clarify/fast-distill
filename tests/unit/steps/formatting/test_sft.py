# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline import Pipeline
from fastdistill.steps.formatting.sft import (
    FormatChatGenerationSFT,
    FormatTextGenerationSFT,
)


class TestFormatTextGenerationSFT:
    def test_process(self) -> None:
        step = FormatTextGenerationSFT(name="sft", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "instruction": "What's 2+2?",
                        "generation": "4",
                    }
                ]
            )
        ) == [
            {
                "instruction": "What's 2+2?",
                "generation": "4",
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
                "messages": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
            }
        ]

    def test_process_with_system_prompt(self) -> None:
        step = FormatTextGenerationSFT(name="sft", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "system_prompt": "You are a helpful assistant.",
                        "instruction": "What's 2+2?",
                        "generation": "4",
                    }
                ]
            )
        ) == [
            {
                "system_prompt": "You are a helpful assistant.",
                "instruction": "What's 2+2?",
                "generation": "4",
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
            }
        ]


class TestFormatChatGenerationSFT:
    def test_process(self) -> None:
        step = FormatChatGenerationSFT(name="sft", pipeline=Pipeline(name="pipeline"))
        step.load()

        assert next(
            step.process(
                [
                    {
                        "messages": [{"role": "user", "content": "What's 2+2?"}],
                        "generation": "4",
                    }
                ]
            )
        ) == [
            {
                "messages": [
                    {"role": "user", "content": "What's 2+2?"},
                    {"role": "assistant", "content": "4"},
                ],
                "generation": "4",
                "prompt": "What's 2+2?",
                "prompt_id": "7762ecf17ad41479767061a8f4a7bfa3b63d371672af5180872f9b82b4cd4e29",
            }
        ]
