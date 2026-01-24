# Plan: Teacher eval gate for Text2SQL distillation

## Goal
Stop MLX training when teacher quality is below a minimum threshold, and document a standardized eval prompt/split for consistent reporting.

## Plan
- [x] Emit a teacher-eval quality report before filtering in the reference pipeline.
- [x] Add a reusable quality gate helper for reports.
- [x] Wire the gate into `scripts/run_ollama_mlx_e2e.py` with env thresholds.
- [x] Add unit tests for the gate logic.
- [x] Document standardized eval prompt/split in quality alignment docs.

## Notes
- Gate defaults: min_total=50, exec_pass_rate>=0.5, gold_match_rate>=0.1, judge_mean>=0.4 (override via env).
