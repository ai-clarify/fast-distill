# Copyright 2026 cklxx
#
# Licensed under the MIT License.

import hashlib
import json
import math
import sqlite3
from pathlib import Path

import pytest

from fastdistill.errors import FastDistillUserError
from fastdistill.steps.fastdistill import (
    CanonicalizeFields,
    ComputeHash,
    DeduplicateByField,
    FilterByBool,
    KeepByScore,
    MarkTime,
    RuleFilter,
    ScoreFromExecEval,
    SelectByBool,
    SQLiteExecEval,
    WriteManifest,
    WriteMlxDataset,
    WriteQualityReport,
    WriteScoreAgreementReport,
    WriteTimingReport,
)
from fastdistill.utils.serialization import read_json


def test_canonicalize_fields_stable_json() -> None:
    step = CanonicalizeFields(fields=["b", "a"], output_field="canonical_input")
    output = next(step.process([{"a": 2, "b": 1}]))

    assert output[0]["canonical_input"] == json.dumps(
        {"a": 2, "b": 1},
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


def test_canonicalize_fields_missing_field_raises() -> None:
    step = CanonicalizeFields(fields=["a", "missing"], output_field="canonical_input")
    with pytest.raises(FastDistillUserError):
        next(step.process([{"a": 1}]))


def test_compute_hash_matches_expected() -> None:
    step = ComputeHash(fields=["a", "b"], output_field="sample_id")
    row = {"a": 1, "b": {"y": 1, "x": 2}}
    output = next(step.process([row]))

    payload = (
        json.dumps(1, ensure_ascii=True, separators=(",", ":"))
        + "|"
        + json.dumps(
            {"x": 2, "y": 1},
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert output[0]["sample_id"] == expected


def test_write_manifest(tmp_path: Path) -> None:
    step = WriteManifest(output_dir=str(tmp_path), stage="canonical")
    inputs = [
        {"sample_id": "a", "field": 1},
        {"sample_id": "b", "field": 2},
    ]
    next(step.process(inputs))

    manifest = read_json(tmp_path / "canonical" / "manifest.json")
    assert manifest["count"] == 2
    assert manifest["min_sample_id"] == "a"
    assert manifest["max_sample_id"] == "b"


def test_write_quality_report(tmp_path: Path) -> None:
    step = WriteQualityReport(output_dir=str(tmp_path), stage="filtered")
    inputs = [
        {
            "exec_pass": True,
            "gold_match": True,
            "judge_score": 0.9,
            "reject_reason": "ok",
            "exec_error": None,
            "keep": True,
        },
        {
            "exec_pass": False,
            "gold_match": False,
            "judge_score": 0.2,
            "reject_reason": "exec_error",
            "exec_error": "syntax error",
            "keep": False,
        },
    ]
    next(step.process(inputs))

    report = read_json(tmp_path / "filtered" / "quality_report.json")
    assert report["total"] == 2
    assert report["kept"] == 1
    assert report["rejected"] == 1
    assert report["exec_pass_rate"] == 0.5
    assert report["gold_match_rate"] == 0.5
    assert report["judge_score"]["min"] == 0.2
    assert report["judge_score"]["max"] == 0.9


def test_write_score_agreement_report(tmp_path: Path) -> None:
    step = WriteScoreAgreementReport(
        output_dir=str(tmp_path),
        stage="score_agreement",
        agreement_epsilons=[0.0, 0.1, 0.2],
        pass_threshold=0.5,
    )
    inputs = [
        {"teacher_score": 1.0, "student_score": 1.0},
        {"teacher_score": 0.5, "student_score": 0.6},
        {"teacher_score": 0.0, "student_score": 0.2},
    ]
    next(step.process(inputs))

    report = read_json(tmp_path / "score_agreement" / "score_agreement.json")
    assert report["total"] == 3
    assert report["matched"] == 3
    assert math.isclose(report["mae"], 0.1, rel_tol=1e-6)
    assert math.isclose(report["agreement_at_0.0"], 1 / 3, rel_tol=1e-6)
    assert math.isclose(report["agreement_at_0.1"], 2 / 3, rel_tol=1e-6)
    assert math.isclose(report["agreement_at_0.2"], 1.0, rel_tol=1e-6)
    assert math.isclose(report["pass_agreement"], 1.0, rel_tol=1e-6)


def test_rule_filter_rejects_and_keeps() -> None:
    step = RuleFilter(text_field="generation", min_chars=2, max_chars=5)
    outputs = next(
        step.process(
            [
                {"generation": ""},
                {"generation": "ok"},
                {"generation": "toolong"},
            ]
        )
    )
    assert outputs[0]["keep"] is False
    assert outputs[0]["reject_reason"] == "empty_output"
    assert outputs[1]["keep"] is True
    assert outputs[1]["reject_reason"] == "ok"
    assert outputs[2]["keep"] is False
    assert outputs[2]["reject_reason"] == "too_long"


def test_filter_by_bool() -> None:
    step = FilterByBool(field="keep", value=True)
    outputs = next(
        step.process(
            [
                {"keep": True, "value": 1},
                {"keep": False, "value": 2},
            ]
        )
    )
    assert outputs == [{"keep": True, "value": 1}]


def test_select_by_bool() -> None:
    step = SelectByBool(field="keep", value=True)
    outputs = next(
        step.process(
            [
                {"keep": True, "value": 1},
                {"keep": False, "value": 2},
            ]
        )
    )
    assert outputs == [{"keep": True, "value": 1}]


def test_deduplicate_by_field_drop_duplicates() -> None:
    step = DeduplicateByField(field="sample_id")
    outputs = next(
        step.process(
            [
                {"sample_id": "a", "value": 1},
                {"sample_id": "a", "value": 2},
                {"sample_id": "b", "value": 3},
            ]
        )
    )
    assert outputs == [
        {"sample_id": "a", "value": 1},
        {"sample_id": "b", "value": 3},
    ]


def test_deduplicate_by_field_emits_duplicate_flag() -> None:
    step = DeduplicateByField(
        field="sample_id", drop_duplicates=False, emit_duplicate_field=True
    )
    outputs = next(
        step.process(
            [
                {"sample_id": "a", "value": 1},
                {"sample_id": "a", "value": 2},
            ]
        )
    )
    assert outputs[0]["is_duplicate"] is False
    assert outputs[1]["is_duplicate"] is True


def test_score_from_exec_eval() -> None:
    step = ScoreFromExecEval()
    outputs = next(
        step.process(
            [
                {"exec_pass": True, "gold_match": True},
                {"exec_pass": True, "gold_match": False},
                {"exec_pass": False, "gold_match": False},
            ]
        )
    )
    assert outputs[0]["teacher_score"] == 1.0
    assert outputs[1]["teacher_score"] == 0.5
    assert outputs[2]["teacher_score"] == 0.0


def test_keep_by_score() -> None:
    step = KeepByScore(min_score=0.5)
    outputs = next(
        step.process(
            [
                {"teacher_score": 1.0, "keep": True},
                {"teacher_score": 0.3, "keep": True},
            ]
        )
    )
    assert outputs[0]["keep"] is True
    assert outputs[1]["keep"] is False


def test_mark_time_and_timing_report(tmp_path: Path) -> None:
    marker = MarkTime(label="stage_a")
    outputs = next(marker.process([{"value": 1}]))
    assert "timing" in outputs[0]
    assert "stage_a" in outputs[0]["timing"]

    report = WriteTimingReport(
        output_dir=str(tmp_path),
        report_name="timing.json",
        ordered_labels=["stage_a", "stage_b"],
    )
    outputs[0]["timing"]["stage_b"] = outputs[0]["timing"]["stage_a"] + 1.0
    next(report.process(outputs))


def test_write_mlx_dataset(tmp_path: Path) -> None:
    step = WriteMlxDataset(
        output_dir=str(tmp_path),
        train_ratio=1.0,
        system_prompt="Return SQL only.",
    )
    inputs = [
        {
            "sample_id": "a",
            "schema": "users(id, name)",
            "instruction": "Count total users.",
            "generation": "SELECT COUNT(*) FROM users;",
        }
    ]
    next(step.process(inputs))

    train_path = tmp_path / "train.jsonl"
    valid_path = tmp_path / "valid.jsonl"
    assert train_path.exists()
    assert valid_path.exists()

    with open(train_path, "r", encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle.readlines()]
    assert len(rows) == 1
    assert rows[0]["messages"][0]["role"] == "system"
    assert rows[0]["messages"][1]["role"] == "user"
    assert rows[0]["messages"][2]["role"] == "assistant"


def test_sqlite_exec_eval(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    cur.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob")],
    )
    conn.commit()
    conn.close()

    step = SQLiteExecEval(db_path=str(db_path), sql_field="generation")
    step.load()
    outputs = next(
        step.process(
            [
                {
                    "generation": "SELECT name FROM users ORDER BY id;",
                    "gold_sql": "SELECT name FROM users ORDER BY id;",
                }
            ]
        )
    )
    assert outputs[0]["exec_pass"] is True
    assert outputs[0]["gold_match"] is True


def test_sqlite_exec_eval_gold_cache(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    cur.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [(1, "Alice"), (2, "Bob")],
    )
    conn.commit()
    conn.close()

    step = SQLiteExecEval(
        db_path=str(db_path),
        sql_field="generation",
        cache_gold_results=True,
        max_cached_gold=1,
    )
    step.load()

    call_counter = {"count": 0}
    original_exec = step._exec_sql

    def wrapped_exec(sql: str):
        call_counter["count"] += 1
        return original_exec(sql)

    step._exec_sql = wrapped_exec  # type: ignore[assignment]

    outputs = next(
        step.process(
            [
                {
                    "generation": "SELECT name FROM users ORDER BY id;",
                    "gold_sql": "SELECT name FROM users ORDER BY id;",
                },
                {
                    "generation": "SELECT name FROM users ORDER BY id;",
                    "gold_sql": "SELECT name FROM users ORDER BY id;",
                },
            ]
        )
    )

    assert outputs[0]["gold_match"] is True
    assert outputs[1]["gold_match"] is True
    assert call_counter["count"] == 3
