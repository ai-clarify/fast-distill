# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import numpy as np
import pytest

from fastdistill.steps.clustering.umap import UMAP

pytest.importorskip("umap")


class TestUMAP:
    def test_process(self) -> None:
        n_components = 2
        step = UMAP(n_jobs=1, n_components=n_components)
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
        assert all(isinstance(result["projection"], np.ndarray) for result in results)
        assert all(len(result["projection"]) == n_components for result in results)
