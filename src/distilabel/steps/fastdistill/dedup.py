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

from typing import List, Set

from pydantic import Field, PrivateAttr
from typing_extensions import override

from distilabel.errors import DistilabelUserError
from distilabel.steps.base import Step, StepInput


class DeduplicateByField(Step):
    """Drop duplicate rows based on a single field value.

    Use this step before expensive generation stages to avoid repeated work.
    """

    field: str = Field(default="sample_id")
    drop_duplicates: bool = Field(default=True)
    emit_duplicate_field: bool = Field(default=False)
    duplicate_field: str = Field(default="is_duplicate")

    _seen: Set[object] = PrivateAttr(default_factory=set)

    @property
    def inputs(self) -> List[str]:
        return [self.field]

    @property
    def outputs(self) -> List[str]:
        return [self.duplicate_field] if self.emit_duplicate_field else []

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        output = []
        for row in inputs:
            if self.field not in row:
                raise DistilabelUserError(
                    f"DeduplicateByField requires field '{self.field}' in each row."
                )
            key = row[self.field]
            is_duplicate = key in self._seen
            if not is_duplicate:
                self._seen.add(key)
            if self.emit_duplicate_field:
                row[self.duplicate_field] = is_duplicate
            if is_duplicate and self.drop_duplicates:
                continue
            output.append(row)
        yield output
