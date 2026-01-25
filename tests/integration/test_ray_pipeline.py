# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Dict, List

import pytest

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.pipeline.ray import RayPipeline
from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.generators.data import LoadDataFromDicts

if TYPE_CHECKING:
    from fastdistill.typing import StepOutput

pytest.importorskip("ray")

DATA = [
    {"prompt": "Tell me a joke"},
    {"prompt": "Write a short haiku"},
    {"prompt": "Translate 'My name is Alvaro' to Spanish"},
    {"prompt": "What's the capital of Spain?"},
] * 8


class RenameColumns(Step):
    rename_mappings: RuntimeParameter[Dict[str, str]] = None

    @property
    def inputs(self) -> List[str]:
        return []

    @property
    def outputs(self) -> List[str]:
        return list(self.rename_mappings.values())  # type: ignore

    def process(self, inputs: StepInput) -> "StepOutput":  # type: ignore
        outputs = []
        for input in inputs:
            outputs.append(
                {self.rename_mappings.get(k, k): v for k, v in input.items()}  # type: ignore
            )
        yield outputs


class GenerateResponse(Step):
    @property
    def inputs(self) -> List[str]:
        return ["instruction"]

    def process(self, inputs: StepInput) -> "StepOutput":  # type: ignore
        for input in inputs:
            input["response"] = "I don't know"

        yield inputs

    @property
    def outputs(self) -> List[str]:
        return ["response"]


@pytest.mark.skip_python_versions(["3.12"])
def test_run_pipeline() -> None:
    import ray
    from ray.cluster_utils import Cluster

    # TODO: if we add more tests, this should be a fixture
    cluster = Cluster(initialize_head=True, head_node_args={"num_cpus": 4})
    ray.init(address=cluster.address, ignore_reinit_error=True)

    try:
        with RayPipeline(
            name="unit-test-pipeline", ray_init_kwargs={"ignore_reinit_error": True}
        ) as pipeline:
            load_dataset = LoadDataFromDicts(
                name="load_dataset", data=DATA, batch_size=8
            )
            rename_columns = RenameColumns(name="rename_columns", input_batch_size=12)
            generate_response = GenerateResponse(
                name="generate_response", input_batch_size=16
            )

            load_dataset >> rename_columns >> generate_response

        distiset = pipeline.run(
            parameters={
                "rename_columns": {
                    "rename_mappings": {
                        "prompt": "instruction",
                    },
                },
            }
        )
    finally:
        ray.shutdown()
        cluster.shutdown()

    assert len(distiset["default"]["train"]) == len(DATA)
