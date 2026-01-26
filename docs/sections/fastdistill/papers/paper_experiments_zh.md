# 论文驱动实验（本地 Ollama 教师）

这份清单把论文转成可执行实验，默认使用**本地 Ollama 的强教师模型**。

## 0) 前置条件
- 本地已启动 Ollama（默认 `http://localhost:11434`）。
- 安装 Ollama 依赖：`pip install -e ".[ollama]"`。
- 数据集与（Text2SQL 场景）SQLite DB。参见 `docs/sections/fastdistill/text2sql_wikisql_zh.md`。

## 1) 选择本地教师模型
优先选择**在你机器上能稳定运行的最大指令模型**。先用小模型做 smoke test，再切换到强模型做正式实验。

建议流程：
- 查看已安装模型：`ollama list`。
- 选择最强的 instruct/chat 模型。
- 通过 `OLLAMA_MODEL` 指定。

## 2) 基线运行（本地 Ollama 教师）
推荐用 Python 管线跑完整评测（包含执行评测与过滤）：

```bash
FASTDISTILL_PROVIDER=ollama \
OLLAMA_MODEL=your-ollama-teacher \
OLLAMA_HOST=http://localhost:11434 \
OLLAMA_TIMEOUT=240 \
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
python examples/fastdistill/fastdistill_pipeline.py
```

快速自检（YAML，小样本）：

```bash
fastdistill pipeline run --config examples/fastdistill/fastdistill_pipeline_ollama.yaml
```

> 需将 `examples/fastdistill/fastdistill_pipeline_ollama.yaml` 中的 `ollama-strong-model` 替换为本地模型名。

## 3) 论文 → 实验配方

### A) Distilling Step-by-Step（推理/解释监督）
**论文：** Distilling Step-by-Step!（可行性高）

目标：收集简短的 rationale 与最终答案。

最小改动：
- 在 `system_prompt` 或 `template` 中要求**短且结构化的解释** + 最终答案。
- 设定固定分隔符（如 `### RATIONALE` / `### ANSWER`）。
- 先保留原始输出，后续需要时再加解析步骤拆分字段。

### B) Data Distillation（多采样 + 过滤）
**论文：** Data Distillation（可行性高）

目标：每条输入多采样，再用现有 gate 过滤。

最小改动：
- 提高 `TextGeneration.num_generations`，并提高温度。
- 保留 `RuleFilter` + `SQLiteExecEval` 作为筛选。
- 用 `decode_profile` 或 `generation_kwargs.options` 调整多样性。

### C) Born Again（迭代教师替换）
**论文：** Born Again Neural Networks（可行性高）

目标：教师 → 学生 → 教师的迭代蒸馏。

最小改动：
- 先用强教师跑基线。
- 训练学生并部署到本地 Ollama。
- 复跑管线，将学生设为教师（`OLLAMA_MODEL=student-model`）。
- 记录 `run_id` 串联并对比指标。

### D) Preference KD（基于打分偏好）
**论文：** Direct Preference KD（可行性中）

目标：用 judge 打分构造偏好对。

最小改动：
- 使用已有分数挑选 top vs. bottom 候选。
- 增加一个轻量后处理步骤输出 `(chosen, rejected)` 对。

## 4) 记录与追踪
- 基线记录到 `docs/sections/fastdistill/baseline_zh.md`。
- 性能记录到 `docs/sections/fastdistill/performance_zh.md`。
- 运行笔记中写明 `run_id`、教师模型、提示词变化、门槛配置。

## 5) 下一步建议
- 添加 `split_rationale` 步骤，将解释与答案拆分存储。
- 添加偏好对导出步骤支撑 DPKD。
- 若模型支持 logprobs，再考虑 MiniLLM-style reverse-KL。
