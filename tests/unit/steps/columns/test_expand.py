# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import Union

import pytest

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.columns.expand import ExpandColumns


class TestExpandColumns:
    def test_always_dict(self) -> None:
        expand_columns = ExpandColumns(
            name="expand_columns",
            columns=["column1", "column2"],
            pipeline=Pipeline(name="unit-test"),
        )

        assert expand_columns.columns == {"column1": "column1", "column2": "column2"}

    @pytest.mark.parametrize(
        "encoded, split_statistics, values, stats",
        [
            (
                False,
                False,
                [
                    {
                        "column1": [1, 2, 3],
                        "column2": ["a", "b", "c"],
                        "fastdistill_metadata": {
                            "statistics_column1": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                            "statistics_column2": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                        },
                    }
                ],
                [
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                ],
            ),
            (
                ["column1", "column2"],
                False,
                [
                    {
                        "column1": json.dumps([1, 2, 3]),
                        "column2": json.dumps(["a", "b", "c"]),
                        "fastdistill_metadata": {
                            "statistics_column1": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                            "statistics_column2": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                        },
                    }
                ],
                [
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                        "statistics_column2": {
                            "input_tokens": [12],
                            "output_tokens": [12],
                        },
                    },
                ],
            ),
            (
                False,
                True,
                [
                    {
                        "column1": [1, 2, 3],
                        "column2": ["a", "b", "c"],
                        "fastdistill_metadata": {
                            "statistics_column1": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                            "statistics_column2": {
                                "input_tokens": [12],
                                "output_tokens": [12],
                            },
                        },
                    }
                ],
                [
                    {
                        "statistics_column1": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                        "statistics_column2": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                        "statistics_column2": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                        "statistics_column2": {
                            "input_tokens": [4],
                            "output_tokens": [4],
                        },
                    },
                ],
            ),
            (
                False,
                True,
                [
                    {
                        "column1": [1, 2, 3],
                        "column2": ["a", "b", "c"],
                        "fastdistill_metadata": {
                            "statistics_column1": {
                                "input_tokens": [793],
                                "output_tokens": [361],
                            },
                            "statistics_column2": {
                                "input_tokens": [202],
                                "output_tokens": [100],
                            },
                        },
                    }
                ],
                [
                    {
                        "statistics_column1": {
                            "input_tokens": [264],
                            "output_tokens": [120],
                        },
                        "statistics_column2": {
                            "input_tokens": [67],
                            "output_tokens": [33],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [264],
                            "output_tokens": [120],
                        },
                        "statistics_column2": {
                            "input_tokens": [67],
                            "output_tokens": [33],
                        },
                    },
                    {
                        "statistics_column1": {
                            "input_tokens": [264],
                            "output_tokens": [120],
                        },
                        "statistics_column2": {
                            "input_tokens": [67],
                            "output_tokens": [33],
                        },
                    },
                ],
            ),
        ],
    )
    def test_process(
        self,
        encoded: Union[bool, list[str]],
        split_statistics: bool,
        values: list[dict[str, Union[list[int], list[str], str]]],
        stats: dict[str, dict[str, int]],
    ) -> None:
        expand_columns = ExpandColumns(
            columns=["column1", "column2"],
            encoded=encoded,
            split_statistics=split_statistics,
        )

        result = next(expand_columns.process(values))

        assert result == [
            {
                "column1": 1,
                "column2": "a",
                "fastdistill_metadata": stats[0],
            },
            {
                "column1": 2,
                "column2": "b",
                "fastdistill_metadata": stats[1],
            },
            {
                "column1": 3,
                "column2": "c",
                "fastdistill_metadata": stats[2],
            },
        ]
