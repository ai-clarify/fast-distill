# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import json
from typing import TYPE_CHECKING

import pytest

pytest.importorskip("instructor")

from fastdistill.steps.clustering.text_clustering import TextClustering
from tests.unit.conftest import DummyAsyncLLM

if TYPE_CHECKING:
    from fastdistill.typing import FormattedInput, GenerateOutput


class ClusteringLLM(DummyAsyncLLM):
    n: int = 1

    async def agenerate(  # type: ignore
        self, input: "FormattedInput", num_generations: int = 1
    ) -> "GenerateOutput":
        if self.n == 1:
            text = json.dumps({"labels": "label"})
        else:
            text = json.dumps({"labels": ["label" for _ in range(self.n)]})
        return {
            "generations": [text] * num_generations,
            "statistics": {
                "input_tokens": [12] * num_generations,
                "output_tokens": [12] * num_generations,
            },
        }


class TestTextClustering:
    @pytest.mark.parametrize("n", [1, 3])
    def test_process(self, n: int) -> None:
        step = TextClustering(
            llm=ClusteringLLM(n=n),
            n=n,
            samples_per_cluster=2,
            savefig=False,
        )
        step.load()

        results = next(
            step.process(
                inputs=[
                    {"projection": [0.1, -0.4], "cluster_label": -1, "text": "hello"},
                    {"projection": [-0.3, 0.9], "cluster_label": -1, "text": "hello"},
                    {"projection": [0.6, 0.2], "cluster_label": 0, "text": "hello"},
                    {"projection": [-0.2, -0.6], "cluster_label": 0, "text": "hello"},
                    {"projection": [0.9, 0.1], "cluster_label": 0, "text": "hello"},
                    {"projection": [0.4, -0.7], "cluster_label": 1, "text": "hello"},
                    {"projection": [-0.5, 0.3], "cluster_label": 1, "text": "hello"},
                    {"projection": [0.7, 0.5], "cluster_label": 2, "text": "hello"},
                    {"projection": [-0.1, -0.9], "cluster_label": 2, "text": "hello"},
                ]
            )
        )
        for r in results:
            if r["cluster_label"] == -1:
                assert r["summary_label"] == json.dumps("Unclassified")
            else:
                if n == 1:
                    assert r["summary_label"] == json.dumps("label")
                else:
                    assert r["summary_label"] == json.dumps(["label"] * n)
