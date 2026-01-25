# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING

from fastdistill.constants import FASTDISTILL_METADATA_KEY
from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.columns.utils import merge_fastdistill_metadata

if TYPE_CHECKING:
    from fastdistill.typing import StepOutput


class CombineOutputs(Step):
    """Combine the outputs of several upstream steps.

    `CombineOutputs` is a `Step` that takes the outputs of several upstream steps and combines
    them to generate a new dictionary with all keys/columns of the upstream steps outputs.

    Input columns:
        - dynamic (based on the upstream `Step`s): All the columns of the upstream steps outputs.

    Output columns:
        - dynamic (based on the upstream `Step`s): All the columns of the upstream steps outputs.

    Categories:
        - columns

    Examples:

        Combine dictionaries of a dataset:

        ```python
        from fastdistill.steps import CombineOutputs

        combine_outputs = CombineOutputs()
        combine_outputs.load()

        result = next(
            combine_outputs.process(
                [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
                [{"c": 5, "d": 6}, {"c": 7, "d": 8}],
            )
        )
        # [
        #   {"a": 1, "b": 2, "c": 5, "d": 6},
        #   {"a": 3, "b": 4, "c": 7, "d": 8},
        # ]
        ```

        Combine upstream steps outputs in a pipeline:

        ```python
        from fastdistill.pipeline import Pipeline
        from fastdistill.steps import CombineOutputs

        with Pipeline() as pipeline:
            step_1 = ...
            step_2 = ...
            step_3 = ...
            combine = CombineOutputs()

            [step_1, step_2, step_3] >> combine
        ```
    """

    def process(self, *inputs: StepInput) -> "StepOutput":
        combined_outputs = []
        for output_dicts in zip(*inputs):
            combined_dict = {}
            for output_dict in output_dicts:
                combined_dict.update(
                    {
                        k: v
                        for k, v in output_dict.items()
                        if k != FASTDISTILL_METADATA_KEY
                    }
                )

            if any(
                FASTDISTILL_METADATA_KEY in output_dict for output_dict in output_dicts
            ):
                combined_dict[FASTDISTILL_METADATA_KEY] = merge_fastdistill_metadata(
                    *output_dicts
                )
            combined_outputs.append(combined_dict)

        yield combined_outputs
