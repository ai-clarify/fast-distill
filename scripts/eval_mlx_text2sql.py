# Copyright 2026 cklxx
#
# Licensed under the MIT License.

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable, List, Optional

from mlx_lm.sample_utils import make_sampler
from mlx_lm.utils import load

from fastdistill.steps.fastdistill import (
    ScoreFromExecEval,
    SQLiteExecEval,
    WriteQualityReport,
    clean_sql_output,
)


def _iter_jsonl(path: Path, limit: Optional[int]) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            if limit is not None and idx >= limit:
                break
            if not line.strip():
                continue
            yield json.loads(line)


def _build_prompt(tokenizer, schema: str, instruction: str, system_prompt: str) -> List[int]:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append(
        {
            "role": "user",
            "content": f"Schema: {schema}\nQuestion: {instruction}\nSQL:",
        }
    )
    return tokenizer.apply_chat_template(messages, add_generation_prompt=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate MLX model on Text2SQL JSONL.")
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--adapter-path", type=str, default=None)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--stage", type=str, default="student_eval_post")
    parser.add_argument("--system-prompt", type=str, default="Return SQL only.")
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--temp", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=100)
    args = parser.parse_args()

    model, tokenizer = load(
        args.model,
        adapter_path=args.adapter_path,
        tokenizer_config={"trust_remote_code": True},
    )

    import importlib

    mlx_generate = importlib.import_module("mlx_lm.generate")
    sampler = make_sampler(args.temp, args.top_p)
    rows: List[dict] = []
    start = time.monotonic()
    for idx, row in enumerate(_iter_jsonl(args.data, args.limit), start=1):
        prompt = _build_prompt(
            tokenizer,
            row.get("schema", ""),
            row.get("instruction", ""),
            args.system_prompt,
        )
        output = mlx_generate.generate(
            model,
            tokenizer,
            prompt,
            max_tokens=args.max_tokens,
            sampler=sampler,
        )
        rows.append(
            {
                "task_id": row.get("task_id"),
                "schema": row.get("schema"),
                "instruction": row.get("instruction"),
                "gold_sql": row.get("gold_sql"),
                "student_generation": clean_sql_output(output or ""),
            }
        )
        if args.log_every and idx % args.log_every == 0:
            print(f"evaluated_rows={idx}")
    elapsed = time.monotonic() - start
    print(f"mlx_eval_generate_wall_time_s={elapsed:.3f}")

    evaluator = SQLiteExecEval(
        db_path=str(args.db),
        sql_field="student_generation",
        exec_pass_field="student_exec_pass",
        exec_error_field="student_exec_error",
        gold_match_field="student_gold_match",
        result_signature_field="student_result_signature",
    )
    scorer = ScoreFromExecEval(
        exec_pass_field="student_exec_pass",
        gold_match_field="student_gold_match",
        score_field="student_score",
    )
    report = WriteQualityReport(
        stage=args.stage,
        output_dir=str(args.output_dir),
        judge_score_field="student_score",
        exec_pass_field="student_exec_pass",
        exec_error_field="student_exec_error",
        gold_match_field="student_gold_match",
    )

    evaluator.load()
    rows = next(evaluator.process(rows))
    evaluator.unload()
    rows = next(scorer.process(rows))
    next(report.process(rows))

    pred_path = args.output_dir / args.stage / "predictions.jsonl"
    pred_path.parent.mkdir(parents=True, exist_ok=True)
    with pred_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    print("predictions_path=", pred_path)


if __name__ == "__main__":
    main()
