# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Any, Dict, Union

import pytest

from fastdistill.steps.tasks.clair import CLAIR
from tests.unit.conftest import DummyLLM


class TestCLAIR:
    def test_format_input(self) -> None:
        task = CLAIR(llm=DummyLLM())
        task.load()

        result = task.format_input(
            input={"task": "TASK", "student_solution": "SOLUTION"}
        )
        # System prompt
        assert (
            result[0]["content"]
            == "You are a teacher and your task is to minimally improve a student's answer. I will give you a {task} and a {student_solution}. Your job is to revise the {student_solution} such that it is clearer, more correct, and more engaging. Copy all non-corrected parts of the student's answer. Do not allude to the {corrected_student_solution} being a revision or a correction in your final solution."
        )
        # User prompt
        assert (
            result[1]["content"]
            == """\
{task}: TASK

{student_solution}: SOLUTION

-----------------

Let's first think step by step with a {teacher_reasoning} to decide how to improve the {student_solution}, then give the {corrected_student_solution}. Mention the {teacher_reasoning} and {corrected_student_solution} identifiers to structure your answer.
""".strip()
        )

    @pytest.mark.parametrize(
        "output, expected",
        [
            (None, {"revision": None, "rational": None}),
            ("WRONG", {"revision": None, "rational": None}),
            (
                "{teacher_reasoning}\n\nreasoning\n\n{corrected_student_solution}\n\ncorrected",
                {"revision": "corrected", "rational": "reasoning"},
            ),
        ],
    )
    def test_format_output(
        self,
        output: Union[str, None],
        expected: Dict[str, Any],
    ) -> None:
        task = CLAIR(llm=DummyLLM())
        task.load()

        result = task.format_output(
            output=output,
            input={},
        )

        assert result == expected
