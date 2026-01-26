# FastDistill Baselines

## Run (2026-01-25, OpenRouter WikiSQL 1k)

### Run configuration
- Pipeline: `scripts/run_ollama_mlx_e2e.py`
- Provider: OpenRouter (remote)
- Teacher model: `deepseek/deepseek-v3.2`
- Student training model: `Qwen/Qwen3-0.6B` (MLX LoRA)
- Dataset size: 1k train + 1k eval (WikiSQL 1k)
- Artifacts root: `~/.cache/fastdistill/artifacts`
- Gate override: `FASTDISTILL_TEACHER_EVAL_GATE=0` (teacher gate failed on full 1k)

### Distillation quality results
From `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`:
- total: 1000
- exec_pass_rate: 0.119
- gold_match_rate: 0.062
- judge_score: min 0.0, max 1.0, mean 0.0905

From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 119
- kept: 119
- rejected: 881
- p_keep: 0.119
- exec_pass_rate: 1.0
- gold_match_rate: 0.5210
- judge_score: min 0.0, max 1.0, mean 0.7605

### Student eval (MLX)
From `~/.cache/fastdistill/artifacts/reports/student_eval_pre/quality_report.json`:
- total: 1000
- exec_pass_rate: 0.53
- gold_match_rate: 0.0
- judge_score: min 0.0, max 1.0, mean 0.265

From `~/.cache/fastdistill/artifacts/reports/student_eval_post/quality_report.json`:
- total: 1000
- exec_pass_rate: 0.929
- gold_match_rate: 0.309
- judge_score: min 0.0, max 1.0, mean 0.619

### Distillation timing
- distillation_wall_time_s: 1023.000 (pipeline log, 19:14:57 → 19:32:00)
- mlx_eval_pre_wall_time_s: 889.301
- mlx_train_wall_time_s: 294.597 (mlx_train.yaml → adapters.safetensors)
- mlx_eval_post_wall_time_s: 479.854

### Notes
- Teacher eval gate failed at default thresholds (exec_pass_rate 0.119, gold_match_rate 0.062, judge_score mean 0.0905).
- Distillation continued with the gate disabled; the keep rate was 11.9% (119/1000).

## Run (2026-01-26, OpenRouter WikiSQL 1k, CleanSqlOutput)

### Run configuration
- Pipeline: `examples/fastdistill/fastdistill_pipeline.py`
- Provider: OpenRouter (remote)
- Teacher model: `deepseek/deepseek-v3.2`
- Student training model: `Qwen/Qwen3-0.6B` (MLX LoRA)
- Dataset size: 1k train (WikiSQL 1k)
- Artifacts root: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
- Data path: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
- DB path: `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
- Generation: `temperature=0.2`, `max_new_tokens=128`, `timeout=240`, `input_batch_size=10`
- Output cleaning: `CleanSqlOutput` enabled (strips fenced SQL)
- MLX config: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/mlx_train.yaml`
- MLX adapters: `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/adapters`

### Distillation quality results
From `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/teacher_eval/quality_report.json`:
- total: 1000
- kept: 995
- rejected: 5
- p_keep: 0.995
- exec_pass_rate: 0.932
- gold_match_rate: 0.45
- judge_score: min 0.0, max 1.0, mean 0.691

From `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/distilled/quality_report.json`:
- total: 927
- kept: 927
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 0.4854
- judge_score: min 0.5, max 1.0, mean 0.7427

### Student eval (MLX)
From `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_pre/quality_report.json`:
- total: 1000
- exec_pass_rate: 0.529
- gold_match_rate: 0.002
- judge_score: min 0.0, max 1.0, mean 0.2655

From `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_post/quality_report.json`:
- total: 1000
- exec_pass_rate: 0.986
- gold_match_rate: 0.449
- judge_score: min 0.0, max 1.0, mean 0.7175

### Distillation timing
- pipeline_wall_time_s: 2688.739
- distilled_model_score_mean: 0.7427184466019418
- mlx_eval_pre_wall_time_s: 948.057
- mlx_train_wall_time_s: 345.760
- mlx_eval_post_wall_time_s: 448.192

### Notes
- Teacher eval gate passed without overrides; 5 rows rejected as `empty_output`.
- Fenced SQL exec errors: 0 (CleanSqlOutput removed markdown fences).

## Run (2026-01-25, Ollama standard flow)

### Run configuration
- Pipeline: `scripts/run_ollama_mlx_e2e.py`
- Provider: Ollama (local)
- Teacher model: `qwen3:0.6b`
- Student training model: `Qwen/Qwen3-0.6B` (MLX LoRA)
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`

### Distillation quality results
From `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`:
- total: 2
- exec_pass_rate: 1.0
- gold_match_rate: 0.5
- judge_score: min 0.5, max 1.0, mean 0.75

From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 2
- kept: 2
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 0.5
- judge_score: min 0.5, max 1.0, mean 0.75

### Distillation timing
- pipeline_wall_time_s: 31.817
- distillation_wall_time_s: 35.200
- distilled_model_score_mean: 0.75

### Notes
- Run failed at teacher eval gate: `total 2 < min_total 50`.
- Override via `FASTDISTILL_TEACHER_EVAL_MIN_TOTAL=2` or disable with `FASTDISTILL_TEACHER_EVAL_GATE=0` to proceed.

## Run (2026-01-26, Ollama quick distill)

### Run configuration
- Pipeline: `examples/fastdistill/fastdistill_pipeline.py`
- Provider: Ollama (local)
- Teacher model: `lfm2.5-thinking:latest`
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`

### Distillation quality results
From `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`:
- total: 2
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0

From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 2
- kept: 2
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0

### Distillation timing
- pipeline_wall_time_s: 41.012

### Notes
- This is a 2-sample smoke test to validate local Ollama model wiring.

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
