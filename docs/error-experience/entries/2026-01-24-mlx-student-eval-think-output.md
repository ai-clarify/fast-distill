# 2026-01-24 - MLX student eval outputs contained reasoning tags

## Context
- Command: `python scripts/run_ollama_mlx_e2e.py`
- Evaluator: `scripts/eval_mlx_text2sql.py`

## Symptoms
- `student_eval_pre` and `student_eval_post` reported `exec_pass_rate=0.0`.
- `exec_error_counts` showed `near "<": syntax error` for every row.

## Likely cause
- Model responses included `<think>` reasoning blocks and no SQL-only output.
- The SQL executor tried to parse the leading `<` token and failed.

## Impact
- Exec/gold-match metrics were invalid (false negatives).

## Resolution
- Added `SqlOutputCleaner` (`src/fastdistill/steps/fastdistill/sql_output.py`).
- Updated MLX eval to strip reasoning tags and extract SQL via `clean_sql_output`.

## Follow-ups
- Keep SQL-only prompts in generation to reduce cleaning reliance.
