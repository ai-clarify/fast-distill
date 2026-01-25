# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from fastdistill.steps.tasks.apigen.execution_checker import APIGenExecutionChecker

SAMPLE_LIB = Path(__file__).parent / "_sample_module.py"
SAMPLE_LIB_FOLDER = Path(__file__).parent / "_sample_lib"


class TestAPIGenExecutionChecker:
    @pytest.mark.parametrize("lib", (SAMPLE_LIB, SAMPLE_LIB_FOLDER))
    @pytest.mark.parametrize(
        "answers, expected",
        [
            (
                {
                    "query": "Whats the velocity of X?",
                    "answers": json.dumps(
                        [
                            {
                                "arguments": {
                                    "initial_velocity": 0.2,
                                    "acceleration": "0.1",
                                    "time": 5,
                                },
                                "name": "final_velocity",
                            }
                        ]
                    ),
                },
                [
                    {
                        "query": "Whats the velocity of X?",
                        "answers": json.dumps(
                            [
                                {
                                    "arguments": {
                                        "initial_velocity": 0.2,
                                        "acceleration": "0.1",
                                        "time": 5,
                                    },
                                    "name": "final_velocity",
                                }
                            ]
                        ),
                        "keep_row_after_execution_check": True,
                        "execution_result": ["0.7"],
                    }
                ],
            ),
            (
                {
                    "query": "Other query",
                    "answers": json.dumps(
                        [
                            {
                                "arguments": {
                                    "initial_velocity": 0.2,
                                    "acceleration": 0.1,
                                    "time": 0.5,
                                },
                                "name": "unknown_function",
                            }
                        ]
                    ),
                },
                [
                    {
                        "query": "Other query",
                        "answers": json.dumps(
                            [
                                {
                                    "arguments": {
                                        "initial_velocity": 0.2,
                                        "acceleration": 0.1,
                                        "time": 0.5,
                                    },
                                    "name": "unknown_function",
                                }
                            ]
                        ),
                        "keep_row_after_execution_check": False,
                        "execution_result": ["Function 'unknown_function' not found."],
                    }
                ],
            ),
            (
                {
                    "query": "Other query",
                    "answers": '[{"arguments": {"matrix": "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "indices": "[1, 2]"}, "name": "get_value"}]',
                },
                [
                    {
                        "query": "Other query",
                        "answers": '[{"arguments": {"matrix": "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "indices": "[1, 2]"}, "name": "get_value"}]',
                        "keep_row_after_execution_check": True,
                        "execution_result": ["6"],
                    }
                ],
            ),
            (
                {
                    "query": "Other query",
                    "answers": None,
                },
                [
                    {
                        "query": "Other query",
                        "answers": None,
                        "keep_row_after_execution_check": False,
                        "execution_result": ["No answers were provided."],
                    }
                ],
            ),
        ],
    )
    def test_process(
        self, lib: str, answers: Dict[str, str], expected: Dict[str, Any]
    ) -> None:
        task = APIGenExecutionChecker(libpath=str(lib))
        task.load()
        result = next(task.process([answers]))
        assert result == expected
