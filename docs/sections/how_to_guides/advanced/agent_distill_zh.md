# 任务型 Agent 蒸馏

本指南演示如何用 Claude Agent SDK 把用户需求转换为可训练的 agent 蒸馏包。产物包含：
- `spec.yaml`（agent 规格）
- `pipeline.yaml`（FastDistill 流水线快照）
- `agent_card.md`（摘要）
- `artifacts/`（报告、清单、MLX 数据集、GGUF 模型）

## 前置条件

安装 Claude Agent SDK，并设置所需的环境变量。GGUF 导出还需要 MLX 与 transformers。

```bash
pip install -e ".[claude-agent]"
pip install -e ".[mlx,hf-transformers]"
# 训练需要 mlx-lm-lora
```

## 快速开始

```bash
fastdistill agent distill --task "为分析问题构建 SQL 查询助手"
```

默认输出在 `~/.cache/fastdistill/agents/<run_id>/`。

## YAML 配置

你可以通过 YAML 控制蒸馏流程，建议从示例配置开始：

```bash
fastdistill agent distill \
  --config configs/fastdistill/agent_distill.sample.yaml \
  --task "为分析问题构建 SQL 查询助手"
```

关键字段：
- `agent`：任务信息、输出路径、指令数量。
- `claude`：生成规格的最大轮次。
- `distill`：prompt 与过滤阈值。
- `teacher`：教师模型配置。
- `training`：可选的 MLX 训练设置。

## 产物结构

```text
<output_dir>/<run_id>/
  spec.yaml
  pipeline.yaml
  agent_card.md
  artifacts/
    reports/
    manifests/
    mlx/
    model/
```

如果 `training.enabled` 为 true，将自动写入 `artifacts/mlx/mlx_train.yaml` 并执行训练。
如果 `training.export_gguf` 为 true，将导出 GGUF 到 `artifacts/model/agent.gguf`。
