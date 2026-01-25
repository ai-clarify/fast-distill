# FastDistill 基线记录

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
