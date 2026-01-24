# FastDistill + MLX 对接

FastDistill 可以把蒸馏数据导出成 MLX 友好的 JSONL 格式，然后在本地进行训练。

## 导出 MLX 数据集
参考管线会输出：

- `~/.cache/fastdistill/artifacts/mlx/train.jsonl`
- `~/.cache/fastdistill/artifacts/mlx/valid.jsonl`

文件内容为 `messages` 数组（system/user/assistant），由 `WriteMlxDataset` 步骤生成。

## 使用 mlx-lm-lora 训练（可选）
`mlx-lm-lora` 支持 YAML 配置训练，数据格式支持 `messages`、`prompt/completion` 或 `text`。

示例配置：
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

运行：
```bash
mlx_lm_lora.train --config configs/fastdistill/mlx_train.sample.yaml
```

## 备注
- MLX 训练需要 Apple Silicon；导出可以在任意环境完成。
- 训练完成后用 FastDistill 的 student_eval 继续做 SQL 执行评测。
