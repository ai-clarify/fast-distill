# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List

from pydantic import Field
from typing_extensions import override

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.fastdistill.utils import stable_json_dumps


class CanonicalizeFields(Step):
    """Create a stable canonical string from selected fields.

    This step is used to enforce a deterministic representation of inputs prior to
    hashing, caching, or deduplication.

    Attributes:
        fields: Ordered list of fields to include in the canonical payload.
        output_field: Column name for the canonical string.
        drop_null_fields: Drop fields with None values.
        strict: If True, missing fields raise an error.

    Input columns:
        - dynamic (determined by `fields` attribute)

    Output columns:
        - canonical_input (or `output_field`)
    """

    fields: List[str] = Field(
        ..., description="Ordered list of fields to include in the canonical payload."
    )
    output_field: str = Field(
        default="canonical_input",
        description="Column name for the canonical string.",
    )
    drop_null_fields: bool = Field(
        default=True, description="Drop fields with None values."
    )
    strict: bool = Field(
        default=True, description="Raise an error when a required field is missing."
    )

    @property
    def inputs(self) -> List[str]:
        return self.fields

    @property
    def outputs(self) -> List[str]:
        return [self.output_field]

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            payload = {}
            for field in self.fields:
                if field not in row:
                    if self.strict:
                        raise FastDistillUserError(
                            f"Missing required field '{field}' in CanonicalizeFields."
                        )
                    continue
                value = row[field]
                if self.drop_null_fields and value is None:
                    continue
                payload[field] = value
            row[self.output_field] = stable_json_dumps(payload)
        yield inputs
