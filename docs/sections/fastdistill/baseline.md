# FastDistill Baselines

## Run (2026-01-25, OpenRouter quick distill)

### Run configuration
- Pipeline: `examples/fastdistill/fastdistill_pipeline.py`
- Provider: OpenRouter (remote)
- Teacher model: `deepseek/deepseek-v3.2`
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`

### Distillation quality results
From `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`:
- total: 2
- exec_pass_rate: 0.5
- gold_match_rate: 0.5
- judge_score: min 0.0, max 1.0, mean 0.5
- exec_error_counts: `{"near \"```sql\nSELECT name FROM users ORDER BY id;\n```\": syntax error": 1}`

From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 1
- kept: 1
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0

### Distillation timing
- pipeline_wall_time_s: 35.798
- distilled_model_score_mean: 1.0
- pipeline_kept_samples_per_hour: 100.56
- 1000-sample distillation time estimate: 9.94 hours (linear extrapolation)

### Notes
- Teacher output included fenced SQL for one sample, causing an exec error.
- Add `SqlOutputCleaner` (or strip fences) before SQL exec to improve pass rate.

## Run (2026-01-24, Ollama + MLX e2e)

### Run configuration
- Pipeline: `examples/fastdistill/fastdistill_pipeline.py`
- Orchestrator: `scripts/run_ollama_mlx_e2e.py`
- Provider: Ollama (local)
- Teacher model: `qwen3:0.6b`
- Student training model: `Qwen/Qwen3-0.6B` (MLX LoRA)
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`
- MLX config: `~/.cache/fastdistill/artifacts/mlx/mlx_train.yaml`
- MLX iters: 1000
- MLX batch size: 1 (auto-adjusted to dataset size)

### Distillation quality results
From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 2
- kept: 2
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0
- reject_reason_counts: {"ok": 2}
- exec_error_counts: {}

### Distillation timing
- distillation_wall_time_s: 20.930
- distilled_model_score_mean: 1.0
- pipeline_kept_samples_per_hour: 344.00
- 1000-sample distillation time estimate: 2.91 hours (linear extrapolation)

### MLX training results
- mlx_train_wall_time_s: 60.187
- adapter outputs: `~/.cache/fastdistill/artifacts/mlx/adapters/adapters.safetensors`

### Notes
- This is a smoke-test dataset; timings scale with prompt length, model speed, and dataset size.
- Token-level throughput is not reported because the Ollama client did not emit token statistics in this run.
