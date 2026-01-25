# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import Dict, List, Union

import pandas as pd
import pytest
from datasets import Dataset

from fastdistill.pipeline.local import Pipeline
from fastdistill.steps.generators.utils import make_generator_step

data = [{"instruction": "Tell me a joke."}] * 10


@pytest.mark.parametrize("dataset", (data, Dataset.from_list(data), pd.DataFrame(data)))
def test_make_generator_step(
    dataset: Union[Dataset, pd.DataFrame, List[Dict[str, str]]],
) -> None:
    batch_size = 5
    load_dataset = make_generator_step(
        dataset, batch_size=batch_size, output_mappings={"instruction": "other"}
    )
    load_dataset.load()
    result = next(load_dataset.process())
    assert len(result[0]) == batch_size
    if isinstance(dataset, (pd.DataFrame, Dataset)):
        assert isinstance(load_dataset._dataset, Dataset)
    else:
        assert isinstance(load_dataset.data, list)

    assert load_dataset.output_mappings == {"instruction": "other"}


def test_make_generator_step_with_pipeline() -> None:
    pipeline = Pipeline()
    load_dataset = make_generator_step(data, pipeline=pipeline)
    assert load_dataset.pipeline == pipeline
