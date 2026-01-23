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

import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Optional

from pydantic import Field

from distilabel.mixins.runtime_parameters import RuntimeParameter
from distilabel.steps.base import GlobalStep, StepInput
from distilabel.utils.serialization import write_json


class WriteQualityReport(GlobalStep):
    """Write a quality_report.json with basic metrics and reject reasons.

    This step is intentionally lightweight and only summarizes fields that exist
    in the dataset.
    """

    output_dir: RuntimeParameter[str] = Field(
        default="artifacts/reports",
        description="Base directory for quality report files.",
    )
    stage: RuntimeParameter[str] = Field(
        default="stage",
        description="Stage name (raw, canonical, filtered, distilled, etc.).",
    )
    run_id: Optional[RuntimeParameter[str]] = Field(
        default=None,
        description="Optional run identifier stored in the report.",
    )
    run_id_env: str = Field(
        default="FASTDISTILL_RUN_ID",
        description="Environment variable used as fallback for run_id.",
    )

    reject_reason_field: str = Field(default="reject_reason")
    exec_pass_field: str = Field(default="exec_pass")
    exec_error_field: str = Field(default="exec_error")
    gold_match_field: str = Field(default="gold_match")
    judge_score_field: str = Field(default="judge_score")
    keep_field: str = Field(default="keep")
    selected_field: str = Field(default="selected")

    def _rate_for_bool_field(self, inputs, field: str):
        if not inputs or field not in inputs[0]:
            return None
        values = [bool(row.get(field)) for row in inputs if field in row]
        if not values:
            return None
        return sum(1 for value in values if value) / len(values)

    def process(self, inputs: StepInput):  # type: ignore[override]
        total = len(inputs)
        run_id = self.run_id or os.getenv(self.run_id_env)

        reject_counts = None
        if total > 0 and self.reject_reason_field in inputs[0]:
            reject_counts = Counter(
                row.get(self.reject_reason_field) for row in inputs
            )
            reject_counts = {str(k): v for k, v in reject_counts.items()}

        exec_error_counts = None
        if total > 0 and self.exec_error_field in inputs[0]:
            exec_error_counts = Counter(
                row.get(self.exec_error_field)
                for row in inputs
                if row.get(self.exec_error_field)
            )
            exec_error_counts = {str(k): v for k, v in exec_error_counts.items()}

        exec_pass_rate = self._rate_for_bool_field(inputs, self.exec_pass_field)
        gold_match_rate = self._rate_for_bool_field(inputs, self.gold_match_field)

        judge_scores = [
            row.get(self.judge_score_field)
            for row in inputs
            if isinstance(row.get(self.judge_score_field), (int, float))
        ]
        judge_stats = None
        if judge_scores:
            judge_stats = {
                "min": min(judge_scores),
                "max": max(judge_scores),
                "mean": mean(judge_scores),
            }

        keep_rate = None
        kept_count = None
        rejected_count = None
        if total > 0:
            if self.keep_field in inputs[0]:
                kept_count = sum(
                    1 for row in inputs if bool(row.get(self.keep_field))
                )
                rejected_count = total - kept_count
                keep_rate = kept_count / total
            elif self.selected_field in inputs[0]:
                kept_count = sum(
                    1 for row in inputs if bool(row.get(self.selected_field))
                )
                rejected_count = total - kept_count
                keep_rate = kept_count / total
            elif reject_counts is not None:
                kept = reject_counts.get("None", 0) + reject_counts.get("", 0) + reject_counts.get("ok", 0)
                kept_count = kept
                rejected_count = total - kept
                keep_rate = kept / total

        report = {
            "run_id": run_id,
            "stage": self.stage,
            "total": total,
            "kept": kept_count,
            "rejected": rejected_count,
            "p_keep": keep_rate,
            "exec_pass_rate": exec_pass_rate,
            "gold_match_rate": gold_match_rate,
            "judge_score": judge_stats,
            "reject_reason_counts": reject_counts,
            "exec_error_counts": exec_error_counts,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        output_path = Path(self.output_dir) / str(self.stage) / "quality_report.json"
        write_json(output_path, report)
        yield inputs
