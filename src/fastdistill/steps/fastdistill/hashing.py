# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import hashlib
from typing import List

from pydantic import Field
from typing_extensions import override

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.base import Step, StepInput
from fastdistill.steps.fastdistill.utils import stable_json_dumps


class ComputeHash(Step):
    """Compute a stable SHA256 hash from selected fields.

    Attributes:
        fields: Ordered list of fields to include in the hash payload.
        output_field: Column name for the hash.
        separator: Separator between field payloads.
        strict: If True, missing fields raise an error.
        include_field_names: If True, include field names in the payload.

    Input columns:
        - dynamic (determined by `fields` attribute)

    Output columns:
        - hash (or `output_field`)
    """

    fields: List[str] = Field(
        ..., description="Ordered list of fields to include in the hash payload."
    )
    output_field: str = Field(default="hash", description="Column name for the hash.")
    separator: str = Field(default="|", description="Separator between fields.")
    strict: bool = Field(
        default=True, description="Raise an error when a required field is missing."
    )
    include_field_names: bool = Field(
        default=False,
        description="Include field names in the hash payload to reduce collisions.",
    )

    @property
    def inputs(self) -> List[str]:
        return self.fields

    @property
    def outputs(self) -> List[str]:
        return [self.output_field]

    def _payload_for_row(self, row: dict) -> str:
        parts: List[str] = []
        for field in self.fields:
            if field not in row:
                if self.strict:
                    raise FastDistillUserError(
                        f"Missing required field '{field}' in ComputeHash."
                    )
                continue
            value = stable_json_dumps(row[field])
            if self.include_field_names:
                parts.append(f"{field}={value}")
            else:
                parts.append(value)
        return self.separator.join(parts)

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            payload = self._payload_for_row(row)
            row[self.output_field] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        yield inputs
