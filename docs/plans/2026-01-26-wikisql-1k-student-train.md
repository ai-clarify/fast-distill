# Plan: Train + evaluate student on WikiSQL 1k distilled set

Date: 2026-01-26

## Context
- Request: run student training + eval on the latest 1k distilled set.
- Constraints: follow engineering practices, update progress here, record baseline/performance, run full lint/tests after changes, and commit changes.

## Plan
1. Reuse the latest distillation artifacts and MLX export for training.
2. Run student eval pre, MLX training, and student eval post.
3. Record metrics + timings in baseline/performance docs.
4. Run full lint + tests and log any incidents.
5. Commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Ran student eval pre + MLX training + student eval post.
- [x] Updated baseline/performance docs with student metrics.
- [x] Ran full lint + tests.
- [x] Logged incidents (if any).
- [ ] Committed changes.

## Notes
- Target artifacts: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`.
- Run command:
  - `FASTDISTILL_SKIP_DISTILL=1`
  - `FASTDISTILL_ARTIFACTS_DIR=~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
  - `FASTDISTILL_EVAL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
  - `FASTDISTILL_EVAL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
  - `MLX_MODEL=Qwen/Qwen3-0.6B MLX_EVAL_MAX_TOKENS=128 MLX_EVAL_LOG_EVERY=100`
  - `python scripts/run_ollama_mlx_e2e.py`
- Outputs:
  - `mlx_eval_generate_wall_time_s` pre: 948.057
  - `mlx_train_wall_time_s`: 345.760
  - `mlx_eval_generate_wall_time_s` post: 448.192
- Student metrics (quality_report.json):
  - Pre: exec_pass_rate 0.529, gold_match_rate 0.002, judge_mean 0.2655.
  - Post: exec_pass_rate 0.986, gold_match_rate 0.449, judge_mean 0.7175.
- Test status:
  - `make lint`
  - `make unit-tests` (warnings)
  - `make integration-tests` (warnings, 4 xpassed)
- Incidents: none.
