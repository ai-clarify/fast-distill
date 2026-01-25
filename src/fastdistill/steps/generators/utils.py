# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import pandas as pd
from datasets import Dataset

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.base import StepResources

if TYPE_CHECKING:
    from fastdistill.pipeline.base import BasePipeline
    from fastdistill.steps import GeneratorStep


def make_generator_step(
    dataset: Union[Dataset, pd.DataFrame, List[Dict[str, str]]],
    pipeline: Union["BasePipeline", None] = None,
    batch_size: int = 50,
    input_mappings: Optional[Dict[str, str]] = None,
    output_mappings: Optional[Dict[str, str]] = None,
    resources: StepResources = StepResources(),
    repo_id: Optional[str] = "default_name",
) -> "GeneratorStep":
    """Helper method to create a `GeneratorStep` from a dataset, to simplify

    Args:
        dataset: The dataset to use in the `Pipeline`.
        batch_size: The batch_size, will default to the same used by the `GeneratorStep`s.
            Defaults to `50`.
        input_mappings: Applies the same as any other step. Defaults to `None`.
        output_mappings: Applies the same as any other step. Defaults to `None`.
        resources: Applies the same as any other step. Defaults to `StepResources()`.
        repo_id: The repository ID to use in the `LoadDataFromHub` step.
            This shouldn't be necessary, but in case of error, the dataset will try to be loaded
            using `load_dataset` internally. If that case happens, the `repo_id` will be used.

    Raises:
        ValueError: If the format is different from the ones supported.

    Returns:
        A `LoadDataFromDicts` if the input is a list of dicts, or `LoadDataFromHub` instance
        if the input is a `pd.DataFrame` or a `Dataset`.
    """
    from fastdistill.steps import LoadDataFromDicts, LoadDataFromHub

    if isinstance(dataset, list):
        return LoadDataFromDicts(
            pipeline=pipeline,
            data=dataset,
            batch_size=batch_size,
            input_mappings=input_mappings or {},
            output_mappings=output_mappings or {},
            resources=resources,
        )

    if isinstance(dataset, pd.DataFrame):
        dataset = Dataset.from_pandas(dataset, preserve_index=False)

    if not isinstance(dataset, Dataset):
        raise FastDistillUserError(
            f"Dataset type not allowed: {type(dataset)}, must be one of: "
            "`datasets.Dataset`, `pd.DataFrame`, `List[Dict[str, str]]`",
            page="sections/how_to_guides/basic/pipeline/?h=make_#__tabbed_1_2",
        )

    loader = LoadDataFromHub(
        pipeline=pipeline,
        repo_id=repo_id,
        batch_size=batch_size,
        input_mappings=input_mappings or {},
        output_mappings=output_mappings or {},
        resources=resources,
    )
    super(loader.__class__, loader).load()  # Ensure the logger is loaded
    loader._dataset = dataset
    loader.num_examples = len(dataset)
    loader._dataset_info = {"default": dataset.info}
    return loader
