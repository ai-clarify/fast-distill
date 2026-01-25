# 2026-01-25 - Standard flow stopped at teacher eval gate (min_total)

## Context
- Command: `python scripts/run_ollama_mlx_e2e.py`
- Provider: Ollama (`qwen3:0.6b`)
- Dataset size: 2 samples (Text2SQL mini set).

## Symptoms
- Distillation ran and produced reports.
- Script aborted with: `Teacher eval gate failed: total 2 < min_total 50`.

## Likely cause
- Default `FASTDISTILL_TEACHER_EVAL_MIN_TOTAL=50` is higher than the smoke-test dataset size.

## Impact
- Standard flow cannot proceed to MLX training on the 2-sample dataset.

## Resolution
- Set `FASTDISTILL_TEACHER_EVAL_MIN_TOTAL=2` (or disable gate with `FASTDISTILL_TEACHER_EVAL_GATE=0`) for smoke tests.

## Follow-ups
- Consider documenting the gate override in the standard flow instructions.
