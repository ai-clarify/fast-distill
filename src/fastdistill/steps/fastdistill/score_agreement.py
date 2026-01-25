# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from pydantic import Field

from fastdistill.mixins.runtime_parameters import RuntimeParameter
from fastdistill.steps.base import GlobalStep, StepInput
from fastdistill.utils.serialization import write_json


def _rank(values: Sequence[float]) -> List[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    if len(xs) < 2:
        return None
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


class WriteScoreAgreementReport(GlobalStep):
    """Write score agreement metrics between teacher and student scores."""

    output_dir: RuntimeParameter[str] = Field(
        default="artifacts/reports",
        description="Base directory for score agreement reports.",
    )
    stage: RuntimeParameter[str] = Field(
        default="score_agreement",
        description="Stage name used in the output path.",
    )
    run_id: Optional[RuntimeParameter[str]] = Field(
        default=None,
        description="Optional run identifier stored in the report.",
    )
    run_id_env: str = Field(
        default="FASTDISTILL_RUN_ID",
        description="Environment variable used as fallback for run_id.",
    )
    teacher_score_field: str = Field(default="teacher_score")
    student_score_field: str = Field(default="student_score")
    agreement_epsilons: List[float] = Field(
        default_factory=lambda: [0.0, 0.05, 0.1, 0.2],
        description="Absolute error thresholds for agreement@epsilon.",
    )
    pass_threshold: Optional[float] = Field(
        default=None,
        description="Optional threshold to compute pass/fail agreement.",
    )

    def _pairs(self, inputs: StepInput) -> Tuple[List[float], List[float], int]:
        teacher_scores: List[float] = []
        student_scores: List[float] = []
        missing = 0
        for row in inputs:
            teacher = row.get(self.teacher_score_field)
            student = row.get(self.student_score_field)
            if isinstance(teacher, (int, float)) and isinstance(student, (int, float)):
                teacher_scores.append(float(teacher))
                student_scores.append(float(student))
            else:
                missing += 1
        return teacher_scores, student_scores, missing

    def _agreement(self, errors: Iterable[float]) -> dict:
        metrics = {}
        errors_list = list(errors)
        if not errors_list:
            return metrics
        for eps in self.agreement_epsilons:
            key = f"agreement_at_{eps}"
            metrics[key] = sum(1 for err in errors_list if err <= eps) / len(
                errors_list
            )
        return metrics

    def process(self, inputs: StepInput):  # type: ignore[override]
        run_id = self.run_id or os.getenv(self.run_id_env)
        teacher_scores, student_scores, missing = self._pairs(inputs)

        metrics = {
            "run_id": run_id,
            "stage": self.stage,
            "total": len(inputs),
            "matched": len(teacher_scores),
            "missing": missing,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if teacher_scores:
            errors = [abs(t - s) for t, s in zip(teacher_scores, student_scores)]
            metrics.update(
                {
                    "teacher_mean": sum(teacher_scores) / len(teacher_scores),
                    "student_mean": sum(student_scores) / len(student_scores),
                    "mae": sum(errors) / len(errors),
                    "rmse": math.sqrt(sum(err * err for err in errors) / len(errors)),
                }
            )
            metrics.update(self._agreement(errors))

            pearson = _pearson(teacher_scores, student_scores)
            metrics["pearson"] = pearson

            teacher_ranks = _rank(teacher_scores)
            student_ranks = _rank(student_scores)
            metrics["spearman"] = _pearson(teacher_ranks, student_ranks)

            if self.pass_threshold is not None:
                teacher_pass = [
                    score >= self.pass_threshold for score in teacher_scores
                ]
                student_pass = [
                    score >= self.pass_threshold for score in student_scores
                ]
                agree = sum(
                    1
                    for t_pass, s_pass in zip(teacher_pass, student_pass)
                    if t_pass == s_pass
                )
                metrics["pass_threshold"] = self.pass_threshold
                metrics["pass_agreement"] = agree / len(teacher_scores)

        output_path = Path(self.output_dir) / str(self.stage) / "score_agreement.json"
        write_json(output_path, metrics)
        yield inputs
