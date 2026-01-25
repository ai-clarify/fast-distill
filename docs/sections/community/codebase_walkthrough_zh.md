---
description: FastDistill 代码库分层导读，从入口到执行内核逐层消除不确定性。
---

# 代码库导读（由浅入深）

这份文档按“由浅到深”的层次解释 FastDistill 代码库。你可以从上往下阅读，只在不确定的部分继续深挖。

## 第 0 层 — 运行 FastDistill 时到底发生了什么？

**目标：** 找到入口和最快的执行路径。

- **CLI 入口**：`src/fastdistill/__main__.py` → `src/fastdistill/cli/app.py` → `fastdistill pipeline run`（`src/fastdistill/cli/pipeline/app.py`）。
- **配置/脚本加载**：`src/fastdistill/cli/pipeline/utils.py` 读取 `.yaml` 配置或 Python 脚本并构建 `Pipeline`。
- **执行**：`Pipeline.run()`（`src/fastdistill/pipeline/base.py`）完成运行参数设置、DAG 校验、执行启动（本地 `pipeline/local.py` 或 Ray `pipeline/ray.py`）。
- **缓存与产物**：落在 `~/.cache/fastdistill/pipelines/<pipeline>/<signature>/...`（见 `src/fastdistill/constants.py`）。

如果只读一个文件，建议先看：
- `src/fastdistill/pipeline/base.py`（全流程主干）

## 第 1 层 — 核心抽象（代码里的“名词”）

**目标：** 搞清楚最重要的对象和职责。

| 概念 | 作用 | 关键文件 |
| --- | --- | --- |
| Pipeline | 执行调度与缓存，管理 DAG | `pipeline/base.py`, `pipeline/local.py` |
| DAG | 校验拓扑、输入输出、路由规则 | `pipeline/_dag.py` |
| Step | 批处理节点（输入/输出列） | `steps/base.py` |
| GeneratorStep | 根节点数据源 | `steps/base.py` |
| GlobalStep | 一次性接收全量数据 | `steps/base.py` |
| Task | 面向 LLM 的 Step（格式化输入输出） | `steps/tasks/base.py` |
| Distiset | 输出数据集封装（含 artifacts） | `distiset.py` |
| Batch | 步骤间数据流单位 | `pipeline/batch.py` |

### 关系简述
1. **Pipeline** 里挂着 **DAG**。
2. **GeneratorStep** 产生批次；普通 **Step** 消费并产出批次。
3. **GlobalStep** 等待全量数据。
4. **Distiset** 汇总叶子节点输出 + 产物 + 日志。

## 第 2 层 — 执行引擎（并发/调度）

**目标：** 理解批次如何流动、为何有 stage。

- **Batch 管理器**（`pipeline/batch_manager.py`）：
  - 累积上游数据直到满足 `input_batch_size`。
  - 维护 seq_no、offset 和缓存状态。
  - 支持路由批次与汇聚（convergence）逻辑。
- **Step Wrapper**（`pipeline/step_wrapper.py`）：
  - 进程内执行 `step.load()` → `process()` → `step.unload()`。
  - 非全局 step 出错会补空行，避免全局失败。
  - 离线批生成异常会触发“可恢复的停止”。
- **Stage 加载**（`pipeline/base.py` + `_dag.py`）：
  - `GlobalStep` 和 `load_groups` 会拆分成阶段。
  - 必须等一个 stage 全部完成才加载下一 stage。

**本地执行最短路径：**
1. `Pipeline.run()` 校验 + 缓存加载。
2. 多进程池启动（`pipeline/local.py`）。
3. output loop：接收 batch → 写 buffer → 触发下游。
4. 结束后从缓存构建 `Distiset`。

## 第 3 层 — 运行时参数与序列化

**目标：** 理解运行时参数如何注入与缓存如何命中。

- **运行时参数**（`mixins/runtime_parameters.py`）：
  - `RuntimeParameter[...]` 标注的字段可通过 `Pipeline.run(parameters={...})` 注入。
  - `Pipeline.run()` 会先设置参数，再决定缓存命中。
- **序列化**（`utils/serialization.py`）：
  - `Pipeline` 会写入 `pipeline.yaml`。
  - `DAG.dump()` 持久化 step 结构与路由。
- **签名与缓存**：
  - Step 签名 + DAG 签名用于定位缓存。
  - 发生签名变化时由 batch manager 负责失效。

## 第 4 层 — 模型与 Provider

**目标：** 找到 LLM/Embedding/Image 的实现位置。

- **LLM 基类**：`models/llms/base.py`（`generate` / 离线 batch）
- **Provider 实现**：`models/llms/`（OpenAI、vLLM、SGLang、Ollama 等）
- **Embedding**：`models/embeddings/`
- **Image Generation**：`models/image_generation/`
- **兼容入口**：`src/fastdistill/llms.py`（已废弃，指向 `models`）

## 第 5 层 — FastDistill 专用步骤（蒸馏流水线积木）

这些是“可审计、可复现”的核心积木：

| Step | 作用 | 文件 |
| --- | --- | --- |
| CanonicalizeFields | 稳定 canonical string | `steps/fastdistill/canonicalize.py` |
| ComputeHash | SHA256 哈希 | `steps/fastdistill/hashing.py` |
| DeduplicateByField | 去重或标注重复 | `steps/fastdistill/dedup.py` |
| RuleFilter / FilterByBool | 规则过滤 | `steps/fastdistill/filtering.py` |
| SQLiteExecEval | SQL 执行与对齐 | `steps/fastdistill/sql_eval.py` |
| ScoreFromExecEval | exec/gold → 分数 | `steps/fastdistill/scoring.py` |
| KeepByScore | 分数阈值过滤 | `steps/fastdistill/scoring.py` |
| WriteManifest | manifest.json | `steps/fastdistill/manifest.py` |
| WriteQualityReport | quality_report.json | `steps/fastdistill/quality_report.py` |
| MarkTime / WriteTimingReport | timing 报告 | `steps/fastdistill/timing.py` |
| SqlOutputCleaner | SQL 输出清洗 | `steps/fastdistill/sql_output.py` |
| evaluate_quality_gate | 质量门槛 | `steps/fastdistill/quality_gate.py` |

## 第 6 层 — Step/Task 生态与工具箱

- **Steps**：`steps/`（generators、columns、formatting、filtering、clustering、embeddings、argilla）
- **Tasks**：`steps/tasks/`（文本生成、评分、结构化输出、Evol 指令等）
- **模板**：`steps/tasks/templates/`（提示词与模板）
- **Utils**：`utils/`（序列化、日志、HF 辅助、模板、类型）
- **Typing**：`typing/`（公共类型定义）

## 第 7 层 — 不确定性消除清单（遇到问题去哪里）

- **“这个字段从哪来？”**
  - 看 `Step.inputs` / `Step.outputs` + `input_mappings` / `output_mappings`（`steps/base.py`）。
- **“为什么是 GlobalStep？”**
  - 全量处理需求或离线 batch 生成（`steps/tasks/base.py`）。
- **“批次为什么对不上？”**
  - 路由/汇聚约束在 `pipeline/_dag.py` 的 `validate()`。
- **“产物写在哪里？”**
  - `Step.save_artifact()`（`steps/base.py`，写入 `steps_artifacts`）。
- **“缓存为何失效？”**
  - Step 签名变化或 `use_cache=False`（`pipeline/base.py` + `batch_manager.py`）。
- **“日志在哪？”**
  - cache 目录下的 `pipeline.log`（见 `constants.py`）。

## 第 8 层 — 读代码建议路径

1. **改执行引擎**：`pipeline/base.py` → `_dag.py` → `batch_manager.py` → `step_wrapper.py`
2. **新增 Step**：`steps/base.py` → `steps/` 子类 → `tests/unit/steps/`
3. **新增 LLM provider**：`models/llms/base.py` → `models/llms/` 新实现
4. **搭 FastDistill pipeline**：`examples/fastdistill/` + `steps/fastdistill/`

---

如果你希望，我可以再补一个 **具体 pipeline 的调用链追踪** 或者对 `examples/fastdistill/fastdistill_pipeline.py` 做逐行讲解。
