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
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional

from pydantic import Field
from typing_extensions import override

from distilabel.mixins.runtime_parameters import RuntimeParameter
from distilabel.steps.base import GlobalStep, Step, StepInput
from distilabel.utils.serialization import write_json


class MarkTime(Step):
    """Attach a wall-clock timestamp to each row for a given stage label.

    Uses time.time() to ensure comparability across processes.
    """

    label: str = Field(..., description="Stage label to record under the timing map.")
    timing_field: str = Field(default="timing")

    @property
    def inputs(self) -> List[str]:
        return []

    @property
    def outputs(self) -> List[str]:
        return [self.timing_field]

    @override
    def process(self, inputs: StepInput):  # type: ignore[override]
        ts = time.time()
        for row in inputs:
            timing = row.get(self.timing_field)
            if not isinstance(timing, dict):
                timing = {}
            timing[self.label] = ts
            row[self.timing_field] = timing
        yield inputs


class WriteTimingReport(GlobalStep):
    """Aggregate per-stage durations from timing markers and write a JSON report."""

    output_dir: RuntimeParameter[str] = Field(
        default="artifacts/reports",
        description="Base directory for timing report files.",
    )
    report_name: RuntimeParameter[str] = Field(
        default="timing_report.json",
        description="Report filename.",
    )
    ordered_labels: List[str] = Field(
        ..., description="Stage labels in the order they should be diffed."
    )
    timing_field: str = Field(default="timing")
    run_id: Optional[RuntimeParameter[str]] = Field(default=None)
    run_id_env: str = Field(default="FASTDISTILL_RUN_ID")

    @property
    def inputs(self) -> List[str]:
        return [self.timing_field]

    @property
    def outputs(self) -> List[str]:
        return []

    def _compute_quantile(self, values: List[float], q: float) -> float:
        if not values:
            return 0.0
        values_sorted = sorted(values)
        idx = int(round((len(values_sorted) - 1) * q))
        return values_sorted[idx]

    def process(self, inputs: StepInput):  # type: ignore[override]
        durations: Dict[str, List[float]] = {}
        total_durations: List[float] = []

        for row in inputs:
            timing = row.get(self.timing_field)
            if not isinstance(timing, dict):
                continue
            for prev_label, next_label in zip(
                self.ordered_labels, self.ordered_labels[1:]
            ):
                if prev_label not in timing or next_label not in timing:
                    continue
                delta = timing[next_label] - timing[prev_label]
                durations.setdefault(f"{prev_label}__to__{next_label}", []).append(
                    delta
                )
            if (
                self.ordered_labels
                and self.ordered_labels[0] in timing
                and self.ordered_labels[-1] in timing
            ):
                total_durations.append(
                    timing[self.ordered_labels[-1]]
                    - timing[self.ordered_labels[0]]
                )

        summary = {}
        for label, values in durations.items():
            summary[label] = {
                "count": len(values),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "mean": mean(values) if values else None,
                "p50": self._compute_quantile(values, 0.5),
                "p90": self._compute_quantile(values, 0.9),
                "p95": self._compute_quantile(values, 0.95),
            }

        total_summary = None
        if total_durations:
            total_summary = {
                "count": len(total_durations),
                "min": min(total_durations),
                "max": max(total_durations),
                "mean": mean(total_durations),
                "p50": self._compute_quantile(total_durations, 0.5),
                "p90": self._compute_quantile(total_durations, 0.9),
                "p95": self._compute_quantile(total_durations, 0.95),
            }

        report = {
            "run_id": self.run_id or os.getenv(self.run_id_env),
            "labels": self.ordered_labels,
            "durations": summary,
            "total": total_summary,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        output_path = Path(self.output_dir) / self.report_name
        write_json(output_path, report)
        yield inputs
