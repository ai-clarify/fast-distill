# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING

from fastdistill.pipeline import Pipeline
from fastdistill.steps import GroupColumns, LoadDataFromDicts, StepInput, step

if TYPE_CHECKING:
    from fastdistill.steps import StepOutput


@step(inputs=["instruction"], outputs=["response"])
def FailAlways(_: StepInput) -> "StepOutput":
    raise Exception("This step always fails")


@step(inputs=["instruction"], outputs=["response"])
def SucceedAlways(inputs: StepInput) -> "StepOutput":
    for input in inputs:
        input["response"] = "This step always succeeds"
    yield inputs


def test_branching_missalignment_because_step_fails_processing_batch() -> None:
    with Pipeline(name="") as pipeline:
        load_data = LoadDataFromDicts(data=[{"instruction": i} for i in range(20)])

        fail = FailAlways()
        succeed = SucceedAlways()
        combine = GroupColumns(columns=["response"])

        load_data >> [fail, succeed] >> combine

    distiset = pipeline.run(use_cache=False)

    assert (
        distiset["default"]["train"]["grouped_response"]
        == [[None, "This step always succeeds"]] * 20
    )
