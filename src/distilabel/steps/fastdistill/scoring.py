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

from distilabel.errors import DistilabelUserError
from distilabel.steps.base import Step, StepInput


class ScoreFromExecEval(Step):
    """Compute a teacher score from exec/gold signals.

    - gold_match True -> gold_score
    - exec_pass True  -> exec_score
    - otherwise       -> fail_score
    """

    exec_pass_field: str = Field(default="exec_pass")
    gold_match_field: str = Field(default="gold_match")
    score_field: str = Field(default="teacher_score")
    exec_score: float = Field(default=0.5)
    gold_score: float = Field(default=1.0)
    fail_score: float = Field(default=0.0)

    @property
    def inputs(self) -> List[str]:
        return [self.exec_pass_field, self.gold_match_field]

    @property
    def outputs(self) -> List[str]:
        return [self.score_field]

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            if self.exec_pass_field not in row:
                raise DistilabelUserError(
                    f"ScoreFromExecEval requires field '{self.exec_pass_field}'."
                )
            exec_pass = bool(row[self.exec_pass_field])
            gold_match: Optional[bool] = row.get(self.gold_match_field)
            if gold_match is True:
                score = self.gold_score
            elif exec_pass:
                score = self.exec_score
            else:
                score = self.fail_score
            row[self.score_field] = score
        yield inputs


class KeepByScore(Step):
    """Update keep flag based on a score threshold."""

    score_field: str = Field(default="teacher_score")
    keep_field: str = Field(default="keep")
    min_score: float = Field(default=0.5)
    respect_existing_keep: bool = Field(default=True)

    @property
    def inputs(self) -> List[str]:
        return [self.score_field, self.keep_field]

    @property
    def outputs(self) -> List[str]:
        return [self.keep_field]

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        for row in inputs:
            if self.score_field not in row:
                raise DistilabelUserError(
                    f"KeepByScore requires field '{self.score_field}'."
                )
            base_keep = True
            if self.respect_existing_keep:
                base_keep = bool(row.get(self.keep_field))
            score = row.get(self.score_field)
            row[self.keep_field] = base_keep and score is not None and score >= self.min_score
        yield inputs
