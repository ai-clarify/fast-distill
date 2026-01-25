# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Union

import pytest

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.tasks.decorator import task
from tests.unit.conftest import DummyLLM


class TestTaskDecorator:
    def test_decoraror_raise_if_no_docstring(self) -> None:
        with pytest.raises(
            FastDistillUserError,
            match=r"When using the `task` decorator, including a docstring in the formatting function is mandatory",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                return {"response": output}

    def test_decorator_raise_if_docstring_invalid(self) -> None:
        with pytest.raises(
            FastDistillUserError,
            match=r"Formatting function decorated with `task` doesn't follow the expected format.",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """This is not valid"""
                return {"response": output}

        with pytest.raises(
            FastDistillUserError,
            match=r"Formatting function decorated with `task` doesn't follow the expected format.",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """
                ---
                - this
                - is
                - a
                - list
                ---
                """
                return {"response": output}

    def test_decorator_raise_if_no_system_prompt_or_user_message_template(self) -> None:
        with pytest.raises(
            FastDistillUserError,
            match=r"The formatting function decorated with `task` must include both the `system_prompt` and `user_message_template` keys in the docstring",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """
                ---
                system_prompt: prompt
                ---
                """
                return {"response": output}

        with pytest.raises(
            FastDistillUserError,
            match=r"The formatting function decorated with `task` must include both the `system_prompt` and `user_message_template` keys in the docstring",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """
                ---
                user_message_template: prompt
                ---
                """
                return {"response": output}

    def test_decorator_raise_if_template_invalid_placeholders(self) -> None:
        with pytest.raises(
            FastDistillUserError,
            match=r"The formatting function decorated with `task` includes invalid placeholders in the extracted `system_prompt`",
        ):

            @task(inputs=["instruction"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """
                ---
                system_prompt: |
                    You are an AI assistant designed to {task}

                user_message_template: |
                    {instruction}
                ---
                """
                return {"response": output}

        with pytest.raises(
            FastDistillUserError,
            match=r"The formatting function decorated with `task` includes invalid placeholders in the extracted `user_message_template`",
        ):

            @task(inputs=["task"], outputs=["response"])
            def MyTask(
                output: Union[str, None], input: Union[Dict[str, Any], None] = None
            ) -> Dict[str, Any]:
                """
                ---
                system_prompt: |
                    You are an AI assistant designed to {task}

                user_message_template: |
                    {instruction}
                ---
                """
                return {"response": output}

    def test_decorator_task(self) -> None:
        @task(inputs=["task", "instruction"], outputs=["response"])
        def MyTask(
            output: Union[str, None], input: Union[Dict[str, Any], None] = None
        ) -> Dict[str, Any]:
            """
            `MyTask` is a simple `Task` for bla bla bla

            ---
            system_prompt: |
                You are an AI assistant designed to {task}

            user_message_template: |
                Text: {instruction}
            ---
            """
            return {"response": output}

        my_task = MyTask(llm=DummyLLM())

        my_task.load()

        assert my_task.inputs == ["task", "instruction"]
        assert my_task.outputs == ["response"]
        assert my_task.format_input(
            {"task": "summarize", "instruction": "The cell..."}
        ) == [
            {
                "role": "system",
                "content": "You are an AI assistant designed to summarize",
            },
            {"role": "user", "content": "Text: The cell..."},
        ]
        assert next(
            my_task.process_applying_mappings(
                [{"task": "summarize", "instruction": "The cell..."}]
            )
        ) == [
            {
                "task": "summarize",
                "instruction": "The cell...",
                "response": "output 0",
                "model_name": "test",
                "fastdistill_metadata": {
                    "raw_input_my_task_0": [
                        {
                            "content": "You are an AI assistant designed to summarize",
                            "role": "system",
                        },
                        {
                            "content": "Text: The cell...",
                            "role": "user",
                        },
                    ],
                    "raw_output_my_task_0": "output 0",
                    "statistics_my_task_0": {
                        "input_tokens": 12,
                        "output_tokens": 12,
                    },
                },
            }
        ]
