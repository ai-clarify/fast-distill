# Distilling Task Agents

This guide shows how to turn a user requirement into a distilled agent bundle using the Claude Agent SDK.
The bundle includes:
- `spec.yaml` (agent spec)
- `pipeline.yaml` (FastDistill pipeline dump)
- `agent_card.md` (quick summary)
- `artifacts/` (reports, manifests, MLX dataset, GGUF model)

## Prerequisites

Install the Claude Agent SDK extra and set the required environment variables for your Claude provider.
For GGUF export you also need the MLX stack and transformers.

```bash
pip install -e ".[claude-agent]"
pip install -e ".[mlx,hf-transformers]"
# plus mlx-lm-lora for training
```

## Quick start

```bash
fastdistill agent distill --task "Build a SQL query helper for analytics questions"
```

This will create a bundle under `~/.cache/fastdistill/agents/<run_id>/`.

## YAML config

You can control the distillation plan via YAML. Start from the sample config:

```bash
fastdistill agent distill \
  --config configs/fastdistill/agent_distill.sample.yaml \
  --task "Build a SQL query helper for analytics questions"
```

Key sections:
- `agent`: task metadata, output path, instruction count.
- `claude`: max turns for spec generation.
- `distill`: prompts and rule filter bounds.
- `teacher`: provider and model configuration.
- `training`: optional MLX training settings.

## Outputs

The bundle structure:

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

If `training.enabled` is true, the MLX training config is written to `artifacts/mlx/mlx_train.yaml` and training is executed automatically.
If `training.export_gguf` is true, the GGUF model is exported to `artifacts/model/agent.gguf` (requires training + MLX).
