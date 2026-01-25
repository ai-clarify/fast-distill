# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING
from unittest import mock

from fastdistill.pipeline import Pipeline
from fastdistill.steps import LoadDataFromDicts, StepInput, step

if TYPE_CHECKING:
    from fastdistill.typing import StepOutput


@step(inputs=["instruction"], outputs=["instruction2"])
def DummyStep(inputs: StepInput) -> "StepOutput":
    for input in inputs:
        input["instruction2"] = "miau"
    yield inputs


@step(inputs=["instruction"], outputs=["instruction2"])
def DummyStep2(*inputs: StepInput) -> "StepOutput":
    outputs = []
    for rows in zip(*inputs):
        combined = {}
        for row in rows:
            combined.update(row)
        outputs.append(combined)
    yield outputs


@step(inputs=["instruction"], outputs=["instruction2"], step_type="global")
def GlobalDummyStep(inputs: StepInput) -> "StepOutput":
    for input in inputs:
        input["instruction2"] = "miau"
    yield inputs


def test_load_groups() -> None:
    with Pipeline() as pipeline:
        generator = LoadDataFromDicts(data=[{"instruction": "Hi"}] * 50)
        dummy_step_0 = DummyStep()
        dummy_step_1 = DummyStep()
        dummy_step_2 = DummyStep2()
        global_dummy_step = GlobalDummyStep()
        dummy_step_3 = DummyStep()
        dummy_step_4 = DummyStep()
        dummy_step_5 = DummyStep()

        (
            generator
            >> [dummy_step_0, dummy_step_1]
            >> dummy_step_2
            >> global_dummy_step
            >> dummy_step_3
            >> [dummy_step_4, dummy_step_5]
        )

    with mock.patch.object(
        pipeline, "_run_stage_steps_and_wait", wraps=pipeline._run_stage_steps_and_wait
    ) as run_stage_mock:
        # `dummy_step_0` should be executed in isolation
        pipeline.run(load_groups=[[dummy_step_0.name], [dummy_step_3.name]])

    assert run_stage_mock.call_count == 6


def test_load_groups_sequential_step_execution() -> None:
    with Pipeline() as pipeline:
        generator = LoadDataFromDicts(data=[{"instruction": "Hi"}] * 50)
        dummy_step_0 = DummyStep()
        dummy_step_1 = DummyStep()
        dummy_step_2 = DummyStep2()
        global_dummy_step = GlobalDummyStep()
        dummy_step_3 = DummyStep()
        dummy_step_4 = DummyStep()
        dummy_step_5 = DummyStep()

        (
            generator
            >> [dummy_step_0, dummy_step_1]
            >> dummy_step_2
            >> global_dummy_step
            >> dummy_step_3
            >> [dummy_step_4, dummy_step_5]
        )

    with mock.patch.object(
        pipeline, "_run_stage_steps_and_wait", wraps=pipeline._run_stage_steps_and_wait
    ) as run_stage_mock:
        # `dummy_step_0` should be executed in isolation
        pipeline.run(load_groups="sequential_step_execution")

    assert run_stage_mock.call_count == 8
