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

from distilabel.steps.fastdistill.quality_gate import QualityGate, evaluate_quality_gate


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
