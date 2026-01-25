# FastDistill Performance Analysis

## Run (2026-01-25, OpenRouter quick distill)

### Key metrics (Text2SQL mini set)
- Distillation wall time: 35.798s for 1 kept sample (~100.56 samples/hour).
- 1k-sample distillation estimate: ~9.94 hours (linear extrapolation from kept samples).
- Teacher exec_pass_rate: 0.5 (one fenced-SQL response failed execution).
- Teacher gold_match_rate: 0.5.

### Notes
- Add `SqlOutputCleaner` before SQL exec to strip code fences and improve pass rate.

## Data sources (2026-01-24 baseline)
- Timing report: `~/.cache/fastdistill/artifacts/reports/timing_report.json` (2026-01-23, `examples/fastdistill/ollama_distill_e2e.py`)
- Baseline: `docs/sections/fastdistill/baseline.md` (2026-01-24, `scripts/run_ollama_mlx_e2e.py`)

## Key metrics (Text2SQL mini set)
- Distillation wall time: 20.930s for 2 samples (~344 samples/hour).
- 1k-sample distillation estimate: ~2.91 hours (linear extrapolation).
- MLX training wall time: 60.187s for 1k iters (smoke-test config, 2 samples).

## Stage timing breakdown (p50, 2026-01-23)
From the timing report, the top contributors are:
- `distilled -> student_gen`: 15.420s (61.9%)
- `hashed -> teacher`: 6.996s (28.1%)
- `filtered -> eval`: 0.578s (2.3%)
- `student_gen -> student_eval`: 0.450s (1.8%)
- `eval -> selected`: 0.436s (1.8%)
- Everything else: <1.2% each

## Bottlenecks
1. **LLM generation dominates**: teacher + student generation ~90% of runtime.
2. **SQL exec eval is not a bottleneck** in this workload (<3%).
3. **Training is separate**: MLX training cost is dominated by iters, not distillation stages.

## Optimization points (ranked)
1. **Reduce LLM tokens**: shorter prompts and responses reduce wall time and cost.
2. **Batch and parallelize**: increase provider concurrency for generation; use multiple workers.
3. **Early cheap filters**: reject malformed outputs before SQL eval and judge steps.
4. **Cache repeated gold SQL**: avoid re-executing the same gold query.

## Training speed levers
- Use `MLX_FAST=1` to reduce eval and checkpoint overhead.
- Increase `steps_per_eval` / `save_every` for long runs.
- Tune `batch_size` and `max_seq_length` to the smallest values that preserve quality.

## Implemented optimization
- **Gold SQL result caching** in `SQLiteExecEval`:
  - Adds in-memory caching of gold SQL results with an LRU cap (`max_cached_gold`).
  - Useful when many rows share the same gold SQL (e.g., templated tasks).
  - Default: enabled (`cache_gold_results=True`).
