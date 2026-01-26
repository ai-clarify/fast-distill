# FastDistill 基线记录

## 运行（2026-01-25，OpenRouter WikiSQL 1k）

### 运行配置
- Pipeline：`scripts/run_ollama_mlx_e2e.py`
- Provider：OpenRouter（远程）
- Teacher 模型：`deepseek/deepseek-v3.2`
- 学生训练模型：`Qwen/Qwen3-0.6B`（MLX LoRA）
- 数据集规模：训练 1k + 评测 1k（WikiSQL 1k）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts`
- Gate 覆盖：`FASTDISTILL_TEACHER_EVAL_GATE=0`（完整 1k 触发 teacher gate 失败）

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`：
- total：1000
- exec_pass_rate：0.119
- gold_match_rate：0.062
- judge_score：min 0.0，max 1.0，mean 0.0905

来自 `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`：
- total：119
- kept：119
- rejected：881
- p_keep：0.119
- exec_pass_rate：1.0
- gold_match_rate：0.5210
- judge_score：min 0.0，max 1.0，mean 0.7605

### 学生评测（MLX）
来自 `~/.cache/fastdistill/artifacts/reports/student_eval_pre/quality_report.json`：
- total：1000
- exec_pass_rate：0.53
- gold_match_rate：0.0
- judge_score：min 0.0，max 1.0，mean 0.265

来自 `~/.cache/fastdistill/artifacts/reports/student_eval_post/quality_report.json`：
- total：1000
- exec_pass_rate：0.929
- gold_match_rate：0.309
- judge_score：min 0.0，max 1.0，mean 0.619

### 蒸馏耗时
- distillation_wall_time_s：1023.000（pipeline 日志，19:14:57 → 19:32:00）
- mlx_eval_pre_wall_time_s：889.301
- mlx_train_wall_time_s：294.597（mlx_train.yaml → adapters.safetensors）
- mlx_eval_post_wall_time_s：479.854

### 备注
- Teacher gate 失败（exec_pass_rate 0.119、gold_match_rate 0.062、judge_score mean 0.0905）。
- 关闭 gate 继续蒸馏，保留率 11.9%（119/1000）。

## 运行（2026-01-26，OpenRouter WikiSQL 1k，CleanSqlOutput）

### 运行配置
- Pipeline：`examples/fastdistill/fastdistill_pipeline.py`
- Provider：OpenRouter（远程）
- Teacher 模型：`deepseek/deepseek-v3.2`
- 学生训练模型：`Qwen/Qwen3-0.6B`（MLX LoRA）
- 数据集规模：训练 1k（WikiSQL 1k）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2`
- 数据路径：`~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
- DB 路径：`~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
- 生成参数：`temperature=0.2`、`max_new_tokens=128`、`timeout=240`、`input_batch_size=10`
- 输出清洗：启用 `CleanSqlOutput`（移除 fenced SQL）
- MLX 配置：`~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/mlx_train.yaml`
- MLX adapters：`~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/mlx/adapters`

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/teacher_eval/quality_report.json`：
- total：1000
- kept：995
- rejected：5
- p_keep：0.995
- exec_pass_rate：0.932
- gold_match_rate：0.45
- judge_score：min 0.0，max 1.0，mean 0.691

来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/distilled/quality_report.json`：
- total：927
- kept：927
- rejected：0
- p_keep：1.0
- exec_pass_rate：1.0
- gold_match_rate：0.4854
- judge_score：min 0.5，max 1.0，mean 0.7427

### 学生评测（MLX）
来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_pre/quality_report.json`：
- total：1000
- exec_pass_rate：0.529
- gold_match_rate：0.002
- judge_score：min 0.0，max 1.0，mean 0.2655

来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_post/quality_report.json`：
- total：1000
- exec_pass_rate：0.986
- gold_match_rate：0.449
- judge_score：min 0.0，max 1.0，mean 0.7175

### 学生评测（MLX，WikiSQL eval split）
评测数据：`~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl`  
评测 DB：`~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db`

来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_pre_eval/quality_report.json`：
- total：1000
- exec_pass_rate：0.53
- gold_match_rate：0.0
- judge_score：min 0.0，max 0.5，mean 0.265

来自 `~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26_v2/reports/student_eval_post_eval/quality_report.json`：
- total：1000
- exec_pass_rate：0.982
- gold_match_rate：0.394
- judge_score：min 0.0，max 1.0，mean 0.688

### 蒸馏耗时
- pipeline_wall_time_s：2688.739
- distilled_model_score_mean：0.7427184466019418
- mlx_eval_pre_wall_time_s：948.057
- mlx_train_wall_time_s：345.760
- mlx_eval_post_wall_time_s：448.192
- mlx_eval_pre_eval_wall_time_s：944.916
- mlx_eval_post_eval_wall_time_s：465.839

### 备注
- Teacher gate 通过，无需覆盖；其中 5 条样本因 `empty_output` 被剔除。
- Fenced SQL 执行错误为 0（CleanSqlOutput 已移除代码块）。

## 运行（2026-01-25，Ollama 标准流程）

### 运行配置
- Pipeline：`scripts/run_ollama_mlx_e2e.py`
- Provider：Ollama（本地）
- Teacher 模型：`qwen3:0.6b`
- 学生训练模型：`Qwen/Qwen3-0.6B`（MLX LoRA）
- 数据集规模：2 条样本（Text2SQL 迷你集）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts`

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`：
- total：2
- exec_pass_rate：1.0
- gold_match_rate：0.5
- judge_score：min 0.5，max 1.0，mean 0.75

来自 `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`：
- total：2
- kept：2
- rejected：0
- p_keep：1.0
- exec_pass_rate：1.0
- gold_match_rate：0.5
- judge_score：min 0.5，max 1.0，mean 0.75

### 蒸馏耗时
- pipeline_wall_time_s：31.817
- distillation_wall_time_s：35.200
- distilled_model_score_mean：0.75

### 备注
- Teacher 评测 gate 失败：`total 2 < min_total 50`。
- 可设置 `FASTDISTILL_TEACHER_EVAL_MIN_TOTAL=2` 或 `FASTDISTILL_TEACHER_EVAL_GATE=0` 继续流程。

## 运行（2026-01-26，Ollama 快速蒸馏）

### 运行配置
- Pipeline：`examples/fastdistill/fastdistill_pipeline.py`
- Provider：Ollama（本地）
- Teacher 模型：`lfm2.5-thinking:latest`
- 数据集规模：2 条样本（Text2SQL 迷你集）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts`

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`：
- total：2
- exec_pass_rate：1.0
- gold_match_rate：1.0
- judge_score：min 1.0，max 1.0，mean 1.0

来自 `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`：
- total：2
- kept：2
- rejected：0
- p_keep：1.0
- exec_pass_rate：1.0
- gold_match_rate：1.0
- judge_score：min 1.0，max 1.0，mean 1.0

### 蒸馏耗时
- pipeline_wall_time_s：41.012

### 备注
- 该运行用于验证本地 Ollama 模型接入，规模为 2 条样本。

## 运行（2026-01-25，OpenRouter 快速蒸馏）

### 运行配置
- Pipeline：`examples/fastdistill/fastdistill_pipeline.py`
- Provider：OpenRouter（远程）
- Teacher 模型：`deepseek/deepseek-v3.2`
- 数据集规模：2 条样本（Text2SQL 迷你集）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts`

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/reports/teacher_eval/quality_report.json`：
- total：2
- exec_pass_rate：0.5
- gold_match_rate：0.5
- judge_score：min 0.0，max 1.0，mean 0.5
- exec_error_counts：`{"near \"```sql\nSELECT name FROM users ORDER BY id;\n```\": syntax error": 1}`

来自 `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`：
- total：1
- kept：1
- rejected：0
- p_keep：1.0
- exec_pass_rate：1.0
- gold_match_rate：1.0
- judge_score：min 1.0，max 1.0，mean 1.0

### 蒸馏耗时
- pipeline_wall_time_s：35.798
- distilled_model_score_mean：1.0
- pipeline_kept_samples_per_hour：100.56
- 1000 样本蒸馏时间估算：9.94 小时（线性估算）

### 备注
- Teacher 输出包含 fenced SQL，导致 1 条执行失败。
- 建议在 SQL 执行前加入 `SqlOutputCleaner` 去除代码块。

## 运行（2026-01-24，Ollama + MLX e2e）

### 运行配置
- Pipeline：`examples/fastdistill/fastdistill_pipeline.py`
- Orchestrator：`scripts/run_ollama_mlx_e2e.py`
- Provider：Ollama（本地）
- Teacher 模型：`qwen3:0.6b`
- 学生训练模型：`Qwen/Qwen3-0.6B`（MLX LoRA）
- 数据集规模：2 条样本（Text2SQL 迷你集）
- Artifacts 根目录：`~/.cache/fastdistill/artifacts`
- MLX 配置：`~/.cache/fastdistill/artifacts/mlx/mlx_train.yaml`
- MLX iters：1000
- MLX batch size：1（随数据规模自动调整）

### 蒸馏质量结果
来自 `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`：
- total：2
- kept：2
- rejected：0
- p_keep：1.0
- exec_pass_rate：1.0
- gold_match_rate：1.0
- judge_score：min 1.0，max 1.0，mean 1.0
- reject_reason_counts：{"ok": 2}
- exec_error_counts：{}

### 蒸馏耗时
- distillation_wall_time_s：20.930
- distilled_model_score_mean：1.0
- pipeline_kept_samples_per_hour：344.00
- 1000 样本蒸馏时间估算：2.91 小时（线性估算）

### MLX 训练结果
- mlx_train_wall_time_s：60.187
- adapter 输出：`~/.cache/fastdistill/artifacts/mlx/adapters/adapters.safetensors`

### 备注
- 这是 smoke-test 数据集，耗时与 prompt 长度、模型速度、数据规模成比例。
- Ollama 客户端未提供 token 统计，无法给出 token 吞吐。
