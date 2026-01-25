# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from fastdistill.steps.fastdistill.quality_gate import (
    QualityGate,
    evaluate_quality_gate,
)


def test_quality_gate_passes() -> None:
    report = {
        "total": 100,
        "exec_pass_rate": 0.9,
        "gold_match_rate": 0.4,
        "judge_score": {"mean": 0.7},
    }
    gate = QualityGate(
        min_total=50,
        min_exec_pass_rate=0.5,
        min_gold_match_rate=0.2,
        min_judge_score_mean=0.5,
    )
    assert evaluate_quality_gate(report, gate) == []


def test_quality_gate_missing_fields() -> None:
    report = {"total": 10}
    gate = QualityGate(min_exec_pass_rate=0.5, min_judge_score_mean=0.5)
    failures = evaluate_quality_gate(report, gate)
    assert "missing exec_pass_rate" in failures
    assert "missing judge_score.mean" in failures


def test_quality_gate_failures() -> None:
    report = {
        "total": 20,
        "exec_pass_rate": 0.1,
        "gold_match_rate": 0.05,
        "judge_score": {"mean": 0.2},
    }
    gate = QualityGate(
        min_total=50,
        min_exec_pass_rate=0.5,
        min_gold_match_rate=0.2,
        min_judge_score_mean=0.5,
    )
    failures = evaluate_quality_gate(report, gate)
    assert any("min_total" in failure for failure in failures)
    assert any("min_exec_pass_rate" in failure for failure in failures)
    assert any("min_gold_match_rate" in failure for failure in failures)
    assert any("min_judge_score_mean" in failure for failure in failures)
