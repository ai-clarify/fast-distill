# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, List

import numpy as np
import pytest

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
                [{"array": np.random.randn(256)} for _ in range(self.batch_size)],  # type: ignore
                i == self.num_batches - 1,
            )  # type: ignore


@step(step_type="global")
def ReceiveArrays(inputs: StepInput) -> "StepOutput":
    yield inputs


@pytest.mark.benchmark
def test_cache_time(benchmark) -> None:
    def run_pipeline() -> None:
        with Pipeline(name="dummy") as pipeline:
            numpy_generator = NumpyBigArrayGenerator(num_batches=2, batch_size=100)

            receive_arrays = ReceiveArrays()

            numpy_generator >> receive_arrays

        pipeline.run(use_cache=False)

    benchmark(run_pipeline)
