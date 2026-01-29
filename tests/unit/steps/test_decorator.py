# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from unittest import mock

import pytest

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.base import (
    GeneratorStep,
    GlobalStep,
    Step,
    StepInput,
)
from fastdistill.steps.decorator import step
from fastdistill.typing import GeneratorStepOutput, StepOutput


class TestStepDecorator:
    def test_creating_step(self) -> None:
        @step(inputs=["instruction"], outputs=["generation"])
        def UnitTestStep(
            inputs: StepInput,
            runtime_param1: RuntimeParameter[int],
            runtime_param2: RuntimeParameter[float] = 5.0,
        ) -> StepOutput:
            """A dummy step for the unit test"""
            yield []

        assert issubclass(UnitTestStep, Step)
        assert UnitTestStep.__doc__ == "A dummy step for the unit test"
        assert UnitTestStep.__module__ == "tests.unit.steps.test_decorator"

        unit_test_step = UnitTestStep(
            name="unit_test_step", pipeline=Pipeline(name="unit-test-pipeline")
        )
        assert unit_test_step._built_from_decorator is True
        assert unit_test_step.inputs == ["instruction"]
        assert unit_test_step.outputs == ["generation"]
        assert unit_test_step.runtime_parameters_names == {
            "input_batch_size": True,
            "resources": {
                "cpus": True,
                "gpus": True,
                "replicas": True,
                "memory": True,
                "resources": True,
            },
            "runtime_param1": True,
            "runtime_param2": True,
        }

    def test_step_decoraror_raise_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid step type 'invalid'"):

            @step(step_type="invalid")
            def UnitTestStep(inputs: StepInput) -> StepOutput:
                yield []

    def test_creating_step_with_more_than_one_step_input(self) -> None:
        with pytest.raises(
            ValueError,
            match="Function 'UnitTestStep' has more than one parameter annotated with `StepInput`.",
        ):

            @step(inputs=["instruction"], outputs=["generation"])
            def UnitTestStep(inputs: StepInput, inputs2: StepInput) -> StepOutput:
                """A dummy step for the unit test"""
                yield []

    def test_creating_global_step(self) -> None:
        @step(inputs=["instruction"], outputs=["generation"], step_type="global")
        def UnitTestStep(
            inputs: StepInput,
            runtime_param1: RuntimeParameter[int],
            runtime_param2: RuntimeParameter[float] = 5.0,
        ) -> StepOutput:
            yield []

        assert issubclass(UnitTestStep, GlobalStep)

    def test_creating_generator_step(self) -> None:
        @step(outputs=["generation"], step_type="generator")
        def UnitTestStep(
            inputs: StepInput,
            runtime_param1: RuntimeParameter[int],
            runtime_param2: RuntimeParameter[float] = 5.0,
        ) -> GeneratorStepOutput:
            yield [], False

        assert issubclass(UnitTestStep, GeneratorStep)

    def test_processing(self) -> None:
        @step(inputs=["instruction"], outputs=["generation"])
        def UnitTestStep(
            inputs: StepInput,
            runtime_param1: RuntimeParameter[int],
            runtime_param2: RuntimeParameter[float] = 5.0,
        ) -> StepOutput:
            yield []

        inputs = [[{"instruction": "Build AGI please"}]]

        with mock.patch.object(
            UnitTestStep,
            "process",
            return_value=[[{"instruction": "Build AGI please", "generation": ""}]],
        ) as process_mock:
            unit_test_step = UnitTestStep(
                name="unit_test_step", pipeline=Pipeline(name="unit-test-pipeline")
            )
            next(
                unit_test_step.process_applying_mappings(
                    inputs, **unit_test_step._runtime_parameters
                )
            )

        process_mock.assert_called_once_with(
            inputs, **unit_test_step._runtime_parameters
        )
