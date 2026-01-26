# Plan: Run student eval on WikiSQL eval split

Date: 2026-01-26

## Context
- Request: evaluate student on the separate WikiSQL eval split (avoid train leakage).
- Constraints: follow engineering practices, update progress here, record baseline/performance, run full lint/tests, and commit changes.

## Plan
1. Run student eval pre + post on WikiSQL eval split using MLX scripts.
2. Record eval metrics/timing and update baseline/performance docs (EN/ZH).
3. Run full lint + unit + integration tests.
4. Commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Ran eval split student eval pre/post.
- [x] Updated baseline/performance docs with eval split metrics.
- [x] Ran full lint + tests.
- [x] Logged incidents (if any).
- [ ] Committed changes.

## Notes
- Eval data: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl`
- Eval DB: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db`
- Artifacts: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
- Model: `Qwen/Qwen3-0.6B` (MLX LoRA)
- Adapter path: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/adapters`
- Commands:
  - `python scripts/eval_mlx_text2sql.py --model Qwen/Qwen3-0.6B --data ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl --db ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db --output-dir ~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports --stage student_eval_pre_eval --system-prompt "Return SQL only." --max-tokens 128 --log-every 100`
  - `python scripts/eval_mlx_text2sql.py --model Qwen/Qwen3-0.6B --adapter-path ~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/adapters --data ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl --db ~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db --output-dir ~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports --stage student_eval_post_eval --system-prompt "Return SQL only." --max-tokens 128 --log-every 100`
- Timings:
  - `mlx_eval_generate_wall_time_s` pre: 944.916
  - `mlx_eval_generate_wall_time_s` post: 465.839
- Test status:
  - `make lint`
  - `make unit-tests` (warnings)
  - `make integration-tests` (warnings, 4 xpassed)
- Incidents: none.
