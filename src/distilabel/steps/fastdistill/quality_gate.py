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

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class QualityGate:
    min_total: Optional[int] = None
    min_exec_pass_rate: Optional[float] = None
    min_gold_match_rate: Optional[float] = None
    min_judge_score_mean: Optional[float] = None


def evaluate_quality_gate(report: Dict[str, Any], gate: QualityGate) -> List[str]:
    failures: List[str] = []

    total = report.get("total")
    if gate.min_total is not None:
        if total is None:
            failures.append("missing total")
        elif total < gate.min_total:
            failures.append(f"total {total} < min_total {gate.min_total}")

    exec_pass_rate = report.get("exec_pass_rate")
    if gate.min_exec_pass_rate is not None:
        if exec_pass_rate is None:
            failures.append("missing exec_pass_rate")
        elif exec_pass_rate < gate.min_exec_pass_rate:
            failures.append(
                f"exec_pass_rate {exec_pass_rate:.4f} < min_exec_pass_rate {gate.min_exec_pass_rate:.4f}"
            )

    gold_match_rate = report.get("gold_match_rate")
    if gate.min_gold_match_rate is not None:
        if gold_match_rate is None:
            failures.append("missing gold_match_rate")
        elif gold_match_rate < gate.min_gold_match_rate:
            failures.append(
                f"gold_match_rate {gold_match_rate:.4f} < min_gold_match_rate {gate.min_gold_match_rate:.4f}"
            )

    judge_score = report.get("judge_score") or {}
    judge_mean = None
    if isinstance(judge_score, dict):
        judge_mean = judge_score.get("mean")
    if gate.min_judge_score_mean is not None:
        if judge_mean is None:
            failures.append("missing judge_score.mean")
        elif judge_mean < gate.min_judge_score_mean:
            failures.append(
                f"judge_score.mean {judge_mean:.4f} < min_judge_score_mean {gate.min_judge_score_mean:.4f}"
            )

    return failures
