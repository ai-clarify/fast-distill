# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import Any, Dict, List

import pytest

pytest.importorskip("instructor")

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.argilla_labeller import ArgillaLabeller
from fastdistill.typing import ChatItem
from tests.unit.conftest import DummyAsyncLLM


@pytest.fixture
def fields() -> Dict[str, Any]:
    return [
        {
            "name": "text",
            "settings": {"type": "text"},
        }
    ]


@pytest.fixture
def questions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "label_selection",
            "settings": {
                "type": "label_selection",
                "options": [
                    {"value": "yes", "text": "Yes"},
                    {"value": "no", "text": "No"},
                ],
            },
        },
        {
            "name": "multi_label_selection",
            "settings": {
                "type": "multi_label_selection",
                "options": [
                    {"value": "yes", "text": "Yes"},
                    {"value": "no", "text": "No"},
                ],
            },
        },
        {
            "name": "rating",
            "settings": {
                "type": "rating",
                "options": [
                    {"value": "1", "text": "1"},
                ],
            },
        },
        {
            "name": "text",
            "settings": {
                "type": "text",
            },
        },
    ]


@pytest.fixture
def outputs() -> List[Dict[str, Any]]:
    return [
        {
            "label": "yes",
        },
        {
            "labels": ["yes", "no"],
        },
        {
            "rating": "1",
        },
        {
            "text": "yes",
        },
    ]


@pytest.fixture
def records() -> List[Dict[str, Any]]:
    return [
        {
            "fields": {
                "text": "What is the capital of France?",
            },
            "responses": [
                {
                    "quesion_name": "label_selection",
                    "value": "yes",
                }
            ],
        }
    ]


class TestArgillaLabeller:
    def test_format_input(
        self,
        questions: List[Dict[str, Any]],
        records: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
    ) -> None:
        task = ArgillaLabeller(
            name="argilla_labeller",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        for question in questions:
            result: List[ChatItem] = task.format_input(
                input={
                    "question": question,
                    "fields": fields,
                    "record": records[0],
                }
            )
            if question["settings"]["type"] in [
                "label_selection",
                "multi_label_selection",
                "rating",
            ]:
                assert (
                    question["settings"]["options"][0]["value"] in result[-1]["content"]
                )

    def test_format_output(
        self,
        questions: List[Dict[str, Any]],
        records: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
    ) -> None:
        task = ArgillaLabeller(
            name="argilla_labeller",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        for question, output in zip(questions, outputs):
            task.format_output(
                input={
                    "question": question,
                    "fields": fields,
                    "record": records[0],
                },
                output=json.dumps(output),
            )

    def test_fail_on_invalid_question_type(
        self, questions: List[Dict[str, Any]], records: List[Dict[str, Any]]
    ) -> None:
        task = ArgillaLabeller(
            name="argilla_labeller",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        fake_question = questions[0]
        fake_question["settings"]["type"] = "invalid_type"

        with pytest.raises(ValueError):
            task.format_input(
                input={
                    "record": records[0],
                    "question": fake_question,
                }
            )

    def test_fail_on_no_question(self, records: List[Dict[str, Any]]) -> None:
        task = ArgillaLabeller(
            name="argilla_labeller",
            llm=DummyAsyncLLM(),
            pipeline=Pipeline(name="unit-test-pipeline"),
        )
        task.load()

        with pytest.raises(ValueError):
            task.format_input(input={"record": records[0]})
