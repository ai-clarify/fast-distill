# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

import pytest

from fastdistill.pipeline import Pipeline
from fastdistill.steps import Step
from fastdistill.steps.base import StepInput
from fastdistill.typing import StepOutput
from fastdistill.utils.requirements import requirements

from ..pipeline.utils import DummyGeneratorStep


def test_add_requirements_decorator():
    @requirements(["fastdistill>=0.0.1"])
    class CustomStep(Step):
        @property
        def inputs(self) -> List[str]:
            return ["instruction"]

        @property
        def outputs(self) -> List[str]:
            return ["response"]

        def process(self, inputs: StepInput) -> StepOutput:  # type: ignore
            for input in inputs:
                input["response"] = "unit test"
            yield inputs

    assert CustomStep.requirements == ["fastdistill>=0.0.1"]


@pytest.mark.parametrize(
    "requirements_pipeline, expected",
    [
        ([], ["fastdistill>=0.0.1", "numpy"]),
        (["candle_holder"], ["candle_holder", "fastdistill>=0.0.1", "numpy"]),
    ],
)
def test_add_requirements_to_pipeline(
    requirements_pipeline: List[str], expected: List[str]
) -> None:
    # Check the pipeline has the requirements from the steps defined within it.

    @requirements(["fastdistill>=0.0.1"])
    class CustomStep(Step):
        @property
        def inputs(self) -> List[str]:
            return ["instruction"]

        @property
        def outputs(self) -> List[str]:
            return ["response"]

        def process(self, inputs: StepInput) -> StepOutput:  # type: ignore
            for input in inputs:
                input["response"] = "unit test"
            yield inputs

    @requirements(["numpy"])
    class OtherStep(Step):
        @property
        def inputs(self) -> List[str]:
            return ["instruction"]

        @property
        def outputs(self) -> List[str]:
            return ["response"]

        def process(self, inputs: StepInput) -> StepOutput:  # type: ignore
            for input in inputs:
                input["response"] = "unit test"
            yield inputs

    with Pipeline(
        name="unit-test-pipeline", requirements=requirements_pipeline
    ) as pipeline:
        generator = DummyGeneratorStep()
        step = CustomStep()
        global_step = OtherStep()

        generator >> [step, global_step]
    print("REQS", pipeline.requirements)
    print("REQS_PRIVATE", pipeline._requirements)
    assert pipeline.requirements == expected


def test_requirements_on_step_decorator() -> None:
    from fastdistill.mixins.runtime_parameters import RuntimeParameter
    from fastdistill.steps.decorator import step

    @requirements(["fastdistill>=0.0.1"])
    @step(inputs=["instruction"], outputs=["generation"])
    def UnitTestStep(
        inputs: StepInput,
        runtime_param1: RuntimeParameter[int],
        runtime_param2: RuntimeParameter[float] = 5.0,
    ) -> StepOutput:
        """A dummy step for the unit test"""
        yield []

    assert UnitTestStep.requirements == ["fastdistill>=0.0.1"]
