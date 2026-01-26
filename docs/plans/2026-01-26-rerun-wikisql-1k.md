# Plan: Investigate low teacher pass rate + rerun WikiSQL 1k

Date: 2026-01-26

## Context
- Request: re-run the 1k Text2SQL distillation test, investigate why teacher exec pass rate is low (11.9%).
- Constraints: follow engineering practices, update progress here, record baselines + performance, run full lint/tests after changes.

## Plan
1. Inspect existing 1k baseline artifacts and pipeline config to understand sampling, prompts, and gates.
2. Identify likely causes for low teacher exec pass rate (prompt/formatting, sampling, model choice, gate overrides).
3. Propose and implement minimal adjustments (if warranted) to improve pass rate without overfitting.
4. Re-run 1k pipeline with OpenRouter teacher and record baseline/performance updates.
5. Run full lint + tests and log any incidents.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Inspected baseline artifacts and pipeline config.
- [x] Root-cause analysis for low teacher pass rate documented.
- [x] Adjustments implemented (if needed).
- [x] Re-ran 1k pipeline + updated baseline/performance docs.
- [x] Ran full lint + tests.
- [x] Logged incidents (if any).
- [ ] Committed changes.

## Notes
- 200-sample baseline (raw): `FASTDISTILL_ARTIFACTS_DIR=~/.cache/fastdistill/artifacts/openrouter_wikisql_200_raw`.
  - exec_pass_rate 0.165, gold_match_rate 0.06, judge_mean 0.1125 (teacher_eval).
  - exec_error_counts show 167 total errors; 161 (96.4%) include ``` fences.
- 200-sample with `CleanSqlOutput`: `FASTDISTILL_ARTIFACTS_DIR=~/.cache/fastdistill/artifacts/openrouter_wikisql_200_clean`.
  - exec_pass_rate 0.905, gold_match_rate 0.405, judge_mean 0.655 (teacher_eval).
  - fenced errors dropped to 0.
- 1k teacher run (attempt 1) aborted due to OpenRouter `JSONDecodeError` on batch 3 with `FASTDISTILL_LLM_BATCH_SIZE=20`. Will retry with smaller batch size.
- 1k teacher run (attempt 2) started 2026-01-26 18:18 local:
  - Command:
    - `FASTDISTILL_PROVIDER=openrouter OPENROUTER_MODEL=deepseek/deepseek-v3.2 OPENROUTER_TIMEOUT=240`
    - `OPENROUTER_TEMPERATURE=0.2 OPENROUTER_MAX_TOKENS=128 FASTDISTILL_LLM_BATCH_SIZE=10`
    - `FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
    - `FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
    - `FASTDISTILL_ARTIFACTS_DIR=~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
    - `python examples/fastdistill/fastdistill_pipeline.py`
- 1k teacher run (attempt 2) completed 2026-01-26 19:02 local:
  - Artifacts: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
  - Teacher eval: exec_pass_rate 0.932, gold_match_rate 0.45, judge_mean 0.691, kept 995/1000 (rejects: 5 empty_output).
  - Distilled: total 927, exec_pass_rate 1.0, gold_match_rate 0.4854, judge_mean 0.7427.
  - pipeline_wall_time_s: 2688.739, distilled_model_score_mean: 0.7427184466019418.
- Test status:
  - `make lint`
  - `make unit-tests` (warnings)
  - `make integration-tests` (warnings, 4 xpassed)
- Incidents: none.
