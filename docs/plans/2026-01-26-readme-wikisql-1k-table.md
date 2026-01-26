# Plan: README highlight WikiSQL 1k distillation results

Date: 2026-01-26

## Context
- Need a prominent table in README summarizing the 1k-sample distillation run.
- Emphasis: student model performance + teacher pass rates.

## Plan
1. Pull metrics from `docs/sections/fastdistill/baseline.md`.
2. Add a top-of-README table with teacher pass rate and student pre/post metrics.
3. Run lint + unit + integration tests.
4. Commit README + plan.

## Progress
- [x] Add README table.
- [x] Run lint + unit + integration tests (skipped: doc-only change per user).
- [x] Commit changes.

## Notes
- Lint/unit/integration runs were attempted but blocked by existing repo issues
  (e.g., `Optional` missing in `src/fastdistill/cli/pipeline/utils.py`).
