# FastDistill + MLX

FastDistill can export distilled rows into MLX-friendly JSONL files and then
train locally with MLX-based tooling.

## Export MLX dataset
The reference pipeline writes MLX datasets to:

- `~/.cache/fastdistill/artifacts/mlx/train.jsonl`
- `~/.cache/fastdistill/artifacts/mlx/valid.jsonl`

These files contain `messages` arrays (system/user/assistant) and are produced
by the `WriteMlxDataset` step in the pipeline.

## Train with mlx-lm-lora (optional)
`mlx-lm-lora` supports MLX fine-tuning using a YAML config. Dataset format
supports `messages`, `prompt/completion`, or `text` records.

Example config:
```yaml
model: Qwen/Qwen2.5-0.5B-Instruct
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
- Keep student eval in FastDistill to verify SQL exec correctness after training.
