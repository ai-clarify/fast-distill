# Copyright 2026 cklxx
#
# Licensed under the MIT License.


import pytest

pytest.importorskip("sklearn")

from fastdistill.steps.clustering.dbscan import DBSCAN


class TestDBSCAN:
    def test_process(self) -> None:
        step = DBSCAN(n_jobs=1, eps=0.5, min_samples=5)
        step.load()

        results = next(
            step.process(
                inputs=[
                    {"projection": [0.1, -0.4]},
                    {"projection": [-0.3, 0.9]},
                    {"projection": [0.6, 0.2]},
                    {"projection": [-0.2, -0.6]},
                    {"projection": [0.9, 0.1]},
                    {"projection": [0.4, -0.7]},
                    {"projection": [-0.5, 0.3]},
                    {"projection": [0.7, 0.5]},
                    {"projection": [-0.1, -0.9]},
                ]
            )
        )
        assert all(result["cluster_label"] == -1 for result in results)
