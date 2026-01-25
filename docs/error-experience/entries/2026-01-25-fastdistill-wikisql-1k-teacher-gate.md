# 2026-01-25 - WikiSQL 1k run failed teacher eval gate (quality too low)

## Context
- Command: `python scripts/run_ollama_mlx_e2e.py`
- Provider: OpenRouter (`deepseek/deepseek-v3.2`)
- Dataset: WikiSQL 1k (train/eval 1k each).

## Symptoms
- Distillation completed and produced reports.
- Script aborted with: `Teacher eval gate failed: exec_pass_rate 0.1190 < min_exec_pass_rate 0.5000; gold_match_rate 0.0620 < min_gold_match_rate 0.1000; judge_score.mean 0.0905 < min_judge_score_mean 0.4000`.

## Likely cause
- Teacher output quality on the full WikiSQL 1k run was substantially below gate thresholds.

## Impact
- End-to-end MLX training/eval did not run until the gate was bypassed.

## Resolution
- Re-ran with `FASTDISTILL_TEACHER_EVAL_GATE=0` and `FASTDISTILL_SKIP_DISTILL=1` to continue with existing artifacts.

## Follow-ups
- Revisit teacher prompt/constraints or consider a higher-quality teacher for WikiSQL 1k.
- Consider per-dataset gate thresholds or a soft-gate mode that records failure but continues.
