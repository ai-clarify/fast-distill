# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, List

import numpy as np

from fastdistill.pipeline import Pipeline
from fastdistill.steps import GeneratorStep, StepInput, step

if TYPE_CHECKING:
    from fastdistill.steps import GeneratorStepOutput, StepOutput


class NumpyBigArrayGenerator(GeneratorStep):
    num_batches: int

    @property
    def outputs(self) -> List[str]:
        return ["array"]

    def process(self, offset: int = 0) -> "GeneratorStepOutput":
        for i in range(self.num_batches):
            yield (
                [{"array": np.random.randn(128)} for _ in range(self.batch_size)],  # type: ignore
                i == self.num_batches - 1,
            )  # type: ignore


@step(step_type="global")
def ReceiveArrays(inputs: StepInput) -> "StepOutput":
    yield inputs


def test_passing_data_through_fs_only_global_steps() -> None:
    with Pipeline(name="dummy") as pipeline:
        numpy_generator = NumpyBigArrayGenerator(num_batches=5, batch_size=100)

        receive_arrays = ReceiveArrays()

        numpy_generator >> receive_arrays

    distiset = pipeline.run(use_fs_to_pass_data=False, use_cache=False)

    assert len(distiset["default"]["train"]) == 500


def test_passing_data_through_fs() -> None:
    with Pipeline(name="dummy") as pipeline:
        numpy_generator = NumpyBigArrayGenerator(num_batches=2, batch_size=200)

        receive_arrays = ReceiveArrays()

        numpy_generator >> receive_arrays

    distiset = pipeline.run(use_fs_to_pass_data=True, use_cache=False)

    assert len(distiset["default"]["train"]) == 400
