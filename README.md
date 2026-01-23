# Fast Distill

面向 **高吞吐 + 质量不降** 的蒸馏流水线。核心目标是同时满足三条硬约束：
1) Teacher 生成吞吐拉满；
2) 过滤与选择锁死质量下限；
3) 训练端把每个 token 的学习效率吃到上限。

本仓库提供：
- **统一 Provider 接口**（OpenAI-compatible 语义层）
- **可重放数据合同**（manifest + sample_id）
- **分层质量闸门**（规则/执行/评测）
- **训练与数据解耦**（蒸馏管线不绑训练器）
- **分阶段耗时统计**（timing_report）

---

## 快速开始（Text2SQL + 自动评估）

### 1) 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[ollama]"
```

### 2) 运行 Text2SQL 蒸馏（本地 Ollama）
```bash
OLLAMA_MODEL=qwen3:0.6b python examples/fastdistill/ollama_distill_e2e.py
```

输出位置（默认写入缓存区，不污染仓库）：
- `~/.cache/fastdistill/artifacts/manifests/distilled/manifest.json`
- `~/.cache/fastdistill/artifacts/reports/quality_report.json`
- `~/.cache/fastdistill/artifacts/reports/timing_report.json`

### 3) 结果与耗时
脚本会打印 distilled 样本和 timing_report 汇总。
`timing_report.json` 包含各阶段耗时（p50/p90/p95）。

---

## Text2SQL 自动评估

内置 `SQLiteExecEval`：
- 执行生成 SQL，输出 `exec_pass` 和 `exec_error`
- 有 `gold_sql` 时进行结果一致性对比，输出 `gold_match`

脚本 `examples/fastdistill/ollama_distill_e2e.py` 会：
- 构造 SQLite 示例库（users 表）
- Teacher 生成 SQL
- 自动执行评估并产出质量报告

---

## 关键指标（硬约束）

**速度指标（可复核）：**
- `teacher_tokens_per_sec`
- `pipeline_kept_samples_per_hour`
- `train_tokens_per_sec`

**质量指标（可反驳）：**
- `test_exec_accuracy`
- `online_win_rate`

阈值写入配置，变更必须新 run_id + 新评测记录。

---

## 关键抽象与架构

**四个平面：**
- 控制平面：run_id、分片、背压、调度
- 数据平面：canonical + parquet + manifest + dedup
- 推理平面：teacher / judge 统一 Provider Gateway
- 训练平面：SFT / Distill 与数据解耦

**管线固定路径：**
Raw → Canonicalize → Dedup → Teacher → Parse/Exec → Judge → Select → Export → Train → Eval

---

## 目录结构
```
configs/fastdistill
  provider_gateway.sample.yaml
  quality_gates.sample.yaml
  run_config.sample.yaml

docs/sections/fastdistill
  plan.md
  provider_gateway_contract.yaml
  run_config.sample.yaml

examples/fastdistill
  fastdistill_pipeline.py
  fastdistill_pipeline.yaml
  ollama_distill_e2e.py

src/distilabel/steps/fastdistill
  canonicalize.py
  hashing.py
  filtering.py
  manifest.py
  quality_report.py
  sql_eval.py
  timing.py
  utils.py
```

---

## Provider Gateway（OpenAI-compatible）

统一对外：`/chat/completions`、`/embeddings`。
内部适配云 API 与自建引擎（vLLM / sglang），避免上层逻辑耦合。
接口定义见：`docs/sections/fastdistill/provider_gateway_contract.yaml`

---

## 贡献与测试

```bash
source .venv/bin/activate
pytest tests/unit/steps/fastdistill/test_fastdistill_steps.py
```

---

## License
Apache-2.0
