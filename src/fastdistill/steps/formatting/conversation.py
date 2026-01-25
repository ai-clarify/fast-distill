# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING

from fastdistill.steps.base import Step, StepInput

if TYPE_CHECKING:
    from fastdistill.typing import StepColumns, StepOutput


class ConversationTemplate(Step):
    """Generate a conversation template from an instruction and a response.

    Input columns:
        - instruction (`str`): The instruction to be used in the conversation.
        - response (`str`): The response to be used in the conversation.

    Output columns:
        - conversation (`ChatType`): The conversation template.

    Categories:
        - format
        - chat
        - template

    Examples:
        Create a conversation from an instruction and a response:

        ```python
        from fastdistill.steps import ConversationTemplate

        conv_template = ConversationTemplate()
        conv_template.load()

        result = next(
            conv_template.process(
                [
                    {
                        "instruction": "Hello",
                        "response": "Hi",
                    }
                ],
            )
        )
        # >>> result
        # [{'instruction': 'Hello', 'response': 'Hi', 'conversation': [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi'}]}]
        ```
    """

    @property
    def inputs(self) -> "StepColumns":
        """The instruction and response."""
        return ["instruction", "response"]

    @property
    def outputs(self) -> "StepColumns":
        """The conversation template."""
        return ["conversation"]

    def process(self, inputs: StepInput) -> "StepOutput":  # type: ignore
        """Generate a conversation template from an instruction and a response.

        Args:
            inputs: The input data.

        Yields:
            The input data with the conversation template.
        """
        for input in inputs:
            input["conversation"] = [
                {"role": "user", "content": input["instruction"]},
                {"role": "assistant", "content": input["response"]},
            ]
        yield inputs
