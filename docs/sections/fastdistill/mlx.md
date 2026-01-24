# FastDistill + MLX

FastDistill can export distilled rows into MLX-friendly JSONL files and then
train locally with MLX-based tooling.

## Export MLX dataset
The reference pipeline writes MLX datasets to:

- `~/.cache/fastdistill/artifacts/mlx/train.jsonl`
- `~/.cache/fastdistill/artifacts/mlx/valid.jsonl`

These files contain `messages` arrays (system/user/assistant) and are produced
by the `WriteMlxDataset` step in the pipeline.

## Local Ollama + MLX full run
```bash
FASTDISTILL_PROVIDER=ollama OLLAMA_MODEL=qwen3:0.6b \
python scripts/run_ollama_mlx_e2e.py
```

### Training speed knobs
Use environment overrides to speed up training without changing code:

- `MLX_FAST=1`: reduce eval/checkpoint frequency for faster runs
- `MLX_ITERS`: override training iterations
- `MLX_BATCH_SIZE`: override batch size (still capped by dataset size)
- `MLX_MAX_SEQ_LENGTH`: override max sequence length
- `MLX_SAVE_EVERY`: checkpoint interval
- `MLX_STEPS_PER_EVAL`: evaluation interval
- `MLX_VAL_BATCHES`: validation batch count
- `MLX_STEPS_PER_REPORT`: logging interval

## Train with mlx-lm-lora (optional)
`mlx-lm-lora` supports MLX fine-tuning using a YAML config. Dataset format
supports `messages`, `prompt/completion`, or `text` records.

Make sure the `mlx_lm_lora` module is installed and importable before running
the training command.

Example config:
```yaml
model: Qwen/Qwen3-0.6B
train: true
train_mode: sft
train_type: lora
data: ~/.cache/fastdistill/artifacts/mlx
iters: 1000
batch_size: 4
learning_rate: 1e-5
max_seq_length: 2048
```

Run:
```bash
mlx_lm_lora.train --config configs/fastdistill/mlx_train.sample.yaml
```

## Notes
- MLX training runs on Apple Silicon; export can run anywhere.
- Set `MLX_MODEL` to override the default student model (defaults to `Qwen/Qwen3-0.6B` in the e2e script).
- Keep student eval in FastDistill to verify SQL exec correctness after training.
- If eval outputs include `<think>` or other reasoning, the evaluator strips reasoning and extracts SQL automatically (see `clean_sql_output`).
