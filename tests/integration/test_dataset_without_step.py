# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Dict, List, Union

import pandas as pd
import pytest
from datasets import Dataset

from fastdistill.pipeline import Pipeline
from fastdistill.steps import make_generator_step
from fastdistill.steps.base import Step, StepInput
from fastdistill.typing import StepOutput

if TYPE_CHECKING:
    pass


class DummyStep(Step):
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


data = [{"instruction": "Tell me a joke."}] * 10


@pytest.mark.parametrize("dataset", (data, Dataset.from_list(data), pd.DataFrame(data)))
def test_pipeline_with_dataset_from_function(
    dataset: Union[Dataset, pd.DataFrame, List[Dict[str, str]]],
) -> None:
    with Pipeline(name="pipe-nothing") as pipeline:
        load_dataset = make_generator_step(dataset)
        if isinstance(dataset, (pd.DataFrame, Dataset)):
            assert isinstance(load_dataset._dataset, Dataset)

        dummy = DummyStep()
        load_dataset >> dummy

    distiset = pipeline.run(use_cache=False)
    assert len(distiset["default"]["train"]) == 10


@pytest.mark.parametrize("dataset", (data, Dataset.from_list(data), pd.DataFrame(data)))
def test_pipeline_run_without_generator_step(
    dataset: Union[Dataset, pd.DataFrame, List[Dict[str, str]]],
) -> None:
    with Pipeline(name="pipe-nothing") as pipeline:
        DummyStep()
        assert len(pipeline.dag) == 1

    distiset = pipeline.run(use_cache=False, dataset=dataset)
    assert len(distiset["default"]["train"]) == 10
    assert len(pipeline.dag) == 2


if __name__ == "__main__":
    with Pipeline(name="pipe-nothing") as pipeline:
        data = [{"instruction": "Tell me a joke."}] * 10
        load_dataset = make_generator_step(Dataset.from_list(data))

        dummy = DummyStep()
        load_dataset >> dummy

    distiset = pipeline.run(use_cache=False)
    print(distiset)
