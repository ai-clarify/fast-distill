# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.tasks.pair_rm import PairRM


@pytest.mark.skip(reason="Not maintained and to be deprecated.")
@patch("llm_blender.Blender")
class TestPairRM:
    def test_process(self, mocker: MagicMock) -> None:
        ranker = PairRM(
            name="pair_rm_ranker", pipeline=Pipeline(name="unit-test-pipeline")
        )
        ranker._blender = mocker
        ranker._blender.rank = MagicMock(return_value=np.array([[2, 1, 3], [2, 1, 3]]))

        result = ranker.process(
            [
                {"input": "Hello, how are you?", "candidates": ["fine", "good", "bad"]},
                {"input": "Anybody there?", "candidates": ["get out", "yep", "nope"]},
            ]
        )
        ranked = list(result)[0]

        assert ranked == [
            {
                "input": "Hello, how are you?",
                "candidates": ["fine", "good", "bad"],
                "ranks": [2, 1, 3],
                "ranked_candidates": ["good", "fine", "bad"],
                "model_name": "llm-blender/PairRM",
            },
            {
                "input": "Anybody there?",
                "candidates": ["get out", "yep", "nope"],
                "ranks": [2, 1, 3],
                "ranked_candidates": ["yep", "get out", "nope"],
                "model_name": "llm-blender/PairRM",
            },
        ]

    def test_serialization(self, _: MagicMock) -> None:
        ranker = PairRM(
            name="pair_rm_ranker", pipeline=Pipeline(name="unit-test-pipeline")
        )
        assert ranker.dump() == {
            "name": ranker.name,
            "input_mappings": {},
            "output_mappings": {},
            "resources": {
                "cpus": None,
                "gpus": None,
                "memory": None,
                "replicas": 1,
                "resources": None,
            },
            "input_batch_size": ranker.input_batch_size,
            "model": ranker.model,
            "instructions": None,
            "runtime_parameters_info": [
                {
                    "name": "resources",
                    "runtime_parameters_info": [
                        {
                            "description": "The number of replicas for the step.",
                            "name": "replicas",
                            "optional": True,
                        },
                        {
                            "description": "The number of CPUs assigned to each step replica.",
                            "name": "cpus",
                            "optional": True,
                        },
                        {
                            "description": "The number of GPUs assigned to each step replica.",
                            "name": "gpus",
                            "optional": True,
                        },
                        {
                            "description": "The memory in bytes required for each step replica.",
                            "name": "memory",
                            "optional": True,
                        },
                        {
                            "description": "A dictionary containing names of custom resources and the number of those resources required for each step replica.",
                            "name": "resources",
                            "optional": True,
                        },
                    ],
                },
                {
                    "description": "The number of rows that will contain the batches processed by the step.",
                    "name": "input_batch_size",
                    "optional": True,
                },
            ],
            "use_cache": True,
            "type_info": {
                "module": "fastdistill.steps.tasks.pair_rm",
                "name": "PairRM",
            },
        }
