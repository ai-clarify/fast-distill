# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.constants import FASTDISTILL_METADATA_KEY
from fastdistill.steps.columns.combine import CombineOutputs


class TestCombineOutputs:
    def test_process(self) -> None:
        combine = CombineOutputs()

        output = next(
            combine.process(
                [
                    {
                        "a": 1,
                        "b": 2,
                        FASTDISTILL_METADATA_KEY: {"model": "model-1", "a": 1},
                    }
                ],
                [
                    {
                        "c": 3,
                        "d": 4,
                        FASTDISTILL_METADATA_KEY: {"model": "model-2", "b": 1},
                    }
                ],
            )
        )

        assert output == [
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
                FASTDISTILL_METADATA_KEY: {
                    "model": ["model-1", "model-2"],
                    "a": 1,
                    "b": 1,
                },
            }
        ]
