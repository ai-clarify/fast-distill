# Copyright 2026 cklxx
#
# Licensed under the MIT License.

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

    def check_min_int(name: str, value: Optional[int], minimum: Optional[int]) -> None:
        if minimum is None:
            return
        if value is None:
            failures.append(f"missing {name}")
        elif value < minimum:
            failures.append(f"{name} {value} < min_{name} {minimum}")

    def check_min_float(
        name: str,
        value: Optional[float],
        minimum: Optional[float],
        *,
        min_label: Optional[str] = None,
    ) -> None:
        if minimum is None:
            return
        if value is None:
            failures.append(f"missing {name}")
        elif value < minimum:
            label = min_label or f"min_{name}"
            failures.append(f"{name} {value:.4f} < {label} {minimum:.4f}")

    total = report.get("total")
    check_min_int("total", total, gate.min_total)

    exec_pass_rate = report.get("exec_pass_rate")
    check_min_float("exec_pass_rate", exec_pass_rate, gate.min_exec_pass_rate)

    gold_match_rate = report.get("gold_match_rate")
    check_min_float("gold_match_rate", gold_match_rate, gate.min_gold_match_rate)

    judge_score = report.get("judge_score") or {}
    judge_mean = judge_score.get("mean") if isinstance(judge_score, dict) else None
    check_min_float(
        "judge_score.mean",
        judge_mean,
        gate.min_judge_score_mean,
        min_label="min_judge_score_mean",
    )

    return failures
