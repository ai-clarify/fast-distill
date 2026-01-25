# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, List, Optional

from typing_extensions import override

from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.columns.utils import group_columns

if TYPE_CHECKING:
    from fastdistill.typing import StepOutput


class GroupColumns(Step):
    """Combines columns from a list of `StepInput`.

    `GroupColumns` is a `Step` that implements the `process` method that calls the `group_dicts`
    function to handle and combine a list of `StepInput`. Also `GroupColumns` provides two attributes
    `columns` and `output_columns` to specify the columns to group and the output columns
    which will override the default value for the properties `inputs` and `outputs`, respectively.

    Attributes:
        columns: List of strings with the names of the columns to group.
        output_columns: Optional list of strings with the names of the output columns.

    Input columns:
        - dynamic (determined by `columns` attribute): The columns to group.

    Output columns:
        - dynamic (determined by `columns` and `output_columns` attributes): The columns
            that were grouped.

    Categories:
        - columns

    Examples:

        Group columns of a dataset:

        ```python
        from fastdistill.steps import GroupColumns

        group_columns = GroupColumns(
            name="group_columns",
            columns=["generation", "model_name"],
        )
        group_columns.load()

        result = next(
            group_columns.process(
                [{"generation": "AI generated text"}, {"model_name": "my_model"}],
                [{"generation": "Other generated text", "model_name": "my_model"}]
            )
        )
        # >>> result
        # [{'merged_generation': ['AI generated text', 'Other generated text'], 'merged_model_name': ['my_model']}]
        ```

        Specify the name of the output columns:

        ```python
        from fastdistill.steps import GroupColumns

        group_columns = GroupColumns(
            name="group_columns",
            columns=["generation", "model_name"],
            output_columns=["generations", "generation_models"]
        )
        group_columns.load()

        result = next(
            group_columns.process(
                [{"generation": "AI generated text"}, {"model_name": "my_model"}],
                [{"generation": "Other generated text", "model_name": "my_model"}]
            )
        )
        # >>> result
        #[{'generations': ['AI generated text', 'Other generated text'], 'generation_models': ['my_model']}]
        ```
    """

    columns: List[str]
    output_columns: Optional[List[str]] = None

    @property
    def inputs(self) -> List[str]:
        """The inputs for the task are the column names in `columns`."""
        return self.columns

    @property
    def outputs(self) -> List[str]:
        """The outputs for the task are the column names in `output_columns` or
        `grouped_{column}` for each column in `columns`."""
        return (
            self.output_columns
            if self.output_columns is not None
            else [f"grouped_{column}" for column in self.columns]
        )

    @override
    def process(self, *inputs: StepInput) -> "StepOutput":
        """The `process` method calls the `group_dicts` function to handle and combine a list of `StepInput`.

        Args:
            *inputs: A list of `StepInput` to be combined.

        Yields:
            A `StepOutput` with the combined `StepInput` using the `group_dicts` function.
        """
        yield group_columns(
            *inputs,
            group_columns=self.inputs,
            output_group_columns=self.outputs,
        )
