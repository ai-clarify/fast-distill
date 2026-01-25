# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from typing import List, Optional

from pydantic import Field
from typing_extensions import override

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.base import Step, StepInput


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
                raise FastDistillUserError(
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
                raise FastDistillUserError(
                    f"KeepByScore requires field '{self.score_field}'."
                )
            base_keep = True
            if self.respect_existing_keep:
                base_keep = bool(row.get(self.keep_field))
            score = row.get(self.score_field)
            row[self.keep_field] = (
                base_keep and score is not None and score >= self.min_score
            )
        yield inputs
