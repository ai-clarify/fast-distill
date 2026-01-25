# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.formatting.conversation import ConversationTemplate


class TestConversationTemplate:
    def test_process(self) -> None:
        conversation_template = ConversationTemplate(
            name="conversation_template",
            pipeline=Pipeline(name="unit-test"),
        )

        result = next(
            conversation_template.process([{"instruction": "Hello", "response": "Hi"}])
        )

        assert result == [
            {
                "instruction": "Hello",
                "response": "Hi",
                "conversation": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ],
            }
        ]
