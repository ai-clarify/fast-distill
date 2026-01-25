# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

from fastdistill.pipeline.batch import _Batch
from fastdistill.steps.base import GeneratorStep, GlobalStep, Step, StepInput
from fastdistill.typing import GeneratorStepOutput, StepOutput


class DummyGeneratorStep(GeneratorStep):
    def process(self, offset: int = 0) -> GeneratorStepOutput:  # type: ignore
        yield [{"instruction": "Generate an email..."}], False

    @property
    def outputs(self) -> List[str]:
        return ["instruction"]


class DummyGlobalStep(GlobalStep):
    @property
    def inputs(self) -> List[str]:
        return ["instruction"]

    def process(self) -> StepOutput:  # type: ignore
        yield [{"instruction": "Generate an email..."}]

    @property
    def outputs(self) -> List[str]:
        return []


class DummyStep1(Step):
    attr1: int = 5

    @property
    def inputs(self) -> List[str]:
        return ["instruction"]

    def process(self, input: StepInput) -> StepOutput:  # type: ignore
        yield [{"response": "response1"}]

    @property
    def outputs(self) -> List[str]:
        return ["response"]


class DummyStep2(Step):
    @property
    def inputs(self) -> List[str]:
        return ["response"]

    def process(self, *inputs: StepInput) -> StepOutput:  # type: ignore
        yield [{"response": "response1"}]

    @property
    def outputs(self) -> List[str]:
        return ["evol_response"]


def batch_gen(
    step_name: str,
    seq_no: int = 0,
    last_batch: bool = False,
    col_name: str = "a",
    num_rows: int = 5,
) -> _Batch:
    return _Batch(
        seq_no=seq_no,
        step_name=step_name,
        last_batch=last_batch,
        data=[[{col_name: i} for i in range(num_rows)]],
    )
