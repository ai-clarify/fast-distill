# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import sys

import pytest

from fastdistill.steps.embeddings.nearest_neighbour import FaissNearestNeighbour

if sys.platform == "darwin":
    pytest.skip(
        "Faiss nearest-neighbour tests are unstable on macOS (segfault in faiss).",
        allow_module_level=True,
    )

pytest.importorskip("faiss")


class TestFaissNearestNeighbour:
    def test_process(self) -> None:
        step = FaissNearestNeighbour()

        step.load()

        results = next(
            step.process(
                inputs=[
                    {"embedding": [0.1, -0.4, 0.7, 0.2]},
                    {"embedding": [-0.3, 0.9, 0.1, -0.5]},
                    {"embedding": [0.6, 0.2, -0.1, 0.8]},
                    {"embedding": [-0.2, -0.6, 0.4, 0.3]},
                    {"embedding": [0.9, 0.1, -0.3, -0.2]},
                    {"embedding": [0.4, -0.7, 0.6, 0.1]},
                    {"embedding": [-0.5, 0.3, -0.2, 0.9]},
                    {"embedding": [0.7, 0.5, -0.4, -0.1]},
                    {"embedding": [-0.1, -0.9, 0.8, 0.6]},
                ]
            )
        )

        assert results == [
            {
                "embedding": [0.1, -0.4, 0.7, 0.2],
                "nn_indices": [5],
                "nn_scores": [0.19999998807907104],
            },
            {
                "embedding": [-0.3, 0.9, 0.1, -0.5],
                "nn_indices": [7],
                "nn_scores": [1.5699999332427979],
            },
            {
                "embedding": [0.6, 0.2, -0.1, 0.8],
                "nn_indices": [7],
                "nn_scores": [1.0000001192092896],
            },
            {
                "embedding": [-0.2, -0.6, 0.4, 0.3],
                "nn_indices": [0],
                "nn_scores": [0.23000000417232513],
            },
            {
                "embedding": [0.9, 0.1, -0.3, -0.2],
                "nn_indices": [7],
                "nn_scores": [0.2200000137090683],
            },
            {
                "embedding": [0.4, -0.7, 0.6, 0.1],
                "nn_indices": [0],
                "nn_scores": [0.19999998807907104],
            },
            {
                "embedding": [-0.5, 0.3, -0.2, 0.9],
                "nn_indices": [2],
                "nn_scores": [1.2400000095367432],
            },
            {
                "embedding": [0.7, 0.5, -0.4, -0.1],
                "nn_indices": [4],
                "nn_scores": [0.2200000137090683],
            },
            {
                "embedding": [-0.1, -0.9, 0.8, 0.6],
                "nn_indices": [3],
                "nn_scores": [0.3499999940395355],
            },
        ]
