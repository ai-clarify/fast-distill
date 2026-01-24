# Plan: Handle <think> outputs in MLX Text2SQL eval

## Goal
Ensure MLX Text2SQL evaluation can safely consume model outputs that include reasoning tags and still extract executable SQL.

## Context
- `student_eval_pre/post` reported `near "<": syntax error` for all rows.
- `student_generation` contained `<think>` blocks and no SQL-only output.

## Plan
- [x] Add a reusable SQL output cleaner to strip reasoning tags and extract SQL.
- [x] Wire the cleaner into MLX eval before SQLite execution.
- [x] Add unit tests covering common reasoning and fenced SQL cases.
- [x] Document the behavior and log an error-experience entry.

## Notes
- If the model emits no SQL at all, exec will still fail (correct behavior); enforce SQL-only prompts to improve upstream generation.
