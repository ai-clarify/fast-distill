# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, List

from typing_extensions import override

from fastdistill.steps.base import Step, StepInput

if TYPE_CHECKING:
    from fastdistill.typing import StepColumns, StepOutput


class KeepColumns(Step):
    """Keeps selected columns in the dataset.

    `KeepColumns` is a `Step` that implements the `process` method that keeps only the columns
    specified in the `columns` attribute. Also `KeepColumns` provides an attribute `columns` to
    specify the columns to keep which will override the default value for the properties `inputs`
    and `outputs`.

    Note:
        The order in which the columns are provided is important, as the output will be sorted
        using the provided order, which is useful before pushing either a `dataset.Dataset` via
        the `PushToHub` step or a `fastdistill.Distiset` via the `Pipeline.run` output variable.

    Attributes:
        columns: List of strings with the names of the columns to keep.

    Input columns:
        - dynamic (determined by `columns` attribute): The columns to keep.

    Output columns:
        - dynamic (determined by `columns` attribute): The columns that were kept.

    Categories:
        - columns

    Examples:
        Select the columns to keep:

        ```python
        from fastdistill.steps import KeepColumns

        keep_columns = KeepColumns(
            columns=["instruction", "generation"],
        )
        keep_columns.load()

        result = next(
            keep_columns.process(
                [{"instruction": "What's the brightest color?", "generation": "white", "model_name": "my_model"}],
            )
        )
        # >>> result
        # [{'instruction': "What's the brightest color?", 'generation': 'white'}]
        ```
    """

    columns: List[str]

    @property
    def inputs(self) -> "StepColumns":
        """The inputs for the task are the column names in `columns`."""
        return self.columns

    @property
    def outputs(self) -> "StepColumns":
        """The outputs for the task are the column names in `columns`."""
        return self.columns

    @override
    def process(self, *inputs: StepInput) -> "StepOutput":
        """The `process` method keeps only the columns specified in the `columns` attribute.

        Args:
            *inputs: A list of dictionaries with the input data.

        Yields:
            A list of dictionaries with the output data.
        """
        for input in inputs:
            outputs = []
            for item in input:
                outputs.append({col: item[col] for col in self.columns})
            yield outputs
