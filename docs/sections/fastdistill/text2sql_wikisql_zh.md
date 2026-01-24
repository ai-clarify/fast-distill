# Text2SQL WikiSQL 1k

这里提供基于 WikiSQL 的 1k Text2SQL 数据构建与跑通流程。

## 数据来源
原始 WikiSQL 数据与 SQLite 数据库来自 Salesforce 官方发布版。

## 构建 1k 数据集
```bash
python scripts/prepare_wikisql_1k.py
```

默认输出：
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db`

## 运行蒸馏（教师）
如果 `OPENROUTER_API_KEY` 放在仓库根目录的 `.env`，示例会自动加载。

```bash
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
python examples/fastdistill/fastdistill_pipeline.py
```

## 运行教师 + 学生评测（Ollama）
```bash
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
OLLAMA_MODEL=qwen3:0.6b \
OLLAMA_STUDENT_MODEL=qwen3:0.6b \
python examples/fastdistill/ollama_distill_e2e.py
```

## 性能调参
- `FASTDISTILL_LLM_BATCH_SIZE`: LLM 任务批大小（默认 50）。
- `FASTDISTILL_DATASET_BATCH_SIZE`: Pipeline 数据集分批大小。
- `OPENROUTER_TIMEOUT` / `OLLAMA_TIMEOUT`: 请求超时时间（秒）。

## 备注
- `train.db` 与 `eval.db` 分别包含对应 split 的所有表。
- SQL 构造会将字符串字面量小写化以匹配 WikiSQL 数据库。
