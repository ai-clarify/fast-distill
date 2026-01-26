# Plan: Train small sample with gold_match-only teacher outputs

Date: 2026-01-26

## Context
- Request: enforce gold_match=True for teacher outputs and retrain on a small sample.
- Constraints: follow engineering practices, update progress here, record baseline/performance, run full lint/tests, and commit changes.

## Plan
1. Enforce gold_match filtering in the Text2SQL pipeline.
2. Run a 200-sample distillation + MLX train/eval on the small WikiSQL subset.
3. Record metrics and timings in baseline/performance docs (EN/ZH).
4. Run full lint + unit + integration tests.
5. Commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Enforced gold_match-only filter in the pipeline.
- [x] Ran 200-sample offline filter + MLX train/eval (reused cached teacher outputs).
- [x] Updated baseline/performance docs with small-sample metrics.
- [x] Ran full lint + tests.
- [x] Logged incidents (if any).
- [x] Committed changes.

## Notes
- Train data: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train_200.jsonl`
- Eval data: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval_200.jsonl`
- DBs: `train.db`, `eval.db` under `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/`
- Artifacts: `~/.cache/fastdistill/artifacts/openrouter_wikisql_200_goldmatch_2026-01-26`
- Teacher eval: exec_pass_rate 0.885, gold_match_rate 0.41, judge_score mean 0.6475.
- Distilled: 82/200 kept (gold_match-only), judge_score mean 1.0.
- Student eval pre/post: exec_pass_rate 0.545 → 0.885; gold_match_rate 0.0 → 0.29.
- MLX wall time: pre 173.679s, train 304.425s, post 92.768s.
- Incidents: none.
- Commits: `3e685ab`, `3b68979`.
