# Copyright 2023-present, Argilla, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Optional

from pydantic import Field
from typing_extensions import override

from distilabel.steps.base import GlobalStep, Step, StepInput


class RuleFilter(Step):
    """Apply simple rule-based filtering to a text field.

    Adds `keep` and `reject_reason` fields so downstream steps can select rows.
    """

    text_field: str = Field(
        default="generation", description="Text field to validate."
    )
    min_chars: int = Field(default=1, description="Minimum char length to keep.")
    max_chars: Optional[int] = Field(
        default=None, description="Maximum char length to keep."
    )
    keep_field: str = Field(default="keep")
    reject_reason_field: str = Field(default="reject_reason")

    @property
    def inputs(self) -> List[str]:
        return [self.text_field]

    @property
    def outputs(self) -> List[str]:
        return [self.keep_field, self.reject_reason_field]

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            text = row.get(self.text_field) or ""
            if not isinstance(text, str):
                text = str(text)
            if len(text) == 0:
                row[self.keep_field] = False
                row[self.reject_reason_field] = "empty_output"
            elif len(text) < self.min_chars:
                row[self.keep_field] = False
                row[self.reject_reason_field] = "too_short"
            elif self.max_chars is not None and len(text) > self.max_chars:
                row[self.keep_field] = False
                row[self.reject_reason_field] = "too_long"
            else:
                row[self.keep_field] = True
                row[self.reject_reason_field] = "ok"
        yield inputs


class FilterByBool(Step):
    """Streamingly filter rows where the given field matches the expected value."""

    field: str = Field(default="keep")
    value: bool = Field(default=True)

    @property
    def inputs(self) -> List[str]:
        return [self.field]

    @property
    def outputs(self) -> List[str]:
        return []

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        filtered = [row for row in inputs if bool(row.get(self.field)) == self.value]
        yield filtered


class SelectByBool(GlobalStep):
    """Select rows where the given field matches the expected value.

    Useful as a final global step to keep only the accepted samples.
    """

    field: str = Field(default="keep")
    value: bool = Field(default=True)

    def process(self, inputs: StepInput):  # type: ignore[override]
        filtered = [row for row in inputs if bool(row.get(self.field)) == self.value]
        yield filtered
