# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.deita import DeitaFiltering


class TestDeitaFiltering:
    def test_process(self) -> None:
        deita_filtering = DeitaFiltering(
            name="deita_filtering",
            data_budget=1,
            pipeline=Pipeline(name="unit-test"),
        )

        deita_filtering.load()

        result = next(
            deita_filtering.process(
                [
                    {
                        "evol_instruction_score": 0.5,
                        "evol_response_score": 0.5,
                        "embedding": [-8.12729941, -5.24642847, -6.34003029],
                    },
                    {
                        "evol_instruction_score": 0.6,
                        "evol_response_score": 0.6,
                        "embedding": [2.99329242, 0.7800932, 0.7799726],
                    },
                    {
                        "evol_instruction_score": 0.7,
                        "evol_response_score": 0.7,
                        "embedding": [10.29041806, 14.33088073, 13.00557506],
                    },
                ]
            )
        )

        assert result == [
            {
                "evol_instruction_score": 0.5,
                "evol_response_score": 0.5,
                "embedding": [-8.12729941, -5.24642847, -6.34003029],
                "deita_score": 0.25,
                "deita_score_computed_with": [
                    "evol_instruction_score",
                    "evol_response_score",
                ],
                "nearest_neighbor_distance": 1.9042812683723933,
            }
        ]
