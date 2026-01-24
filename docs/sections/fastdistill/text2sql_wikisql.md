# Text2SQL WikiSQL 1k

This repo includes a reproducible Text2SQL 1k dataset build based on WikiSQL.

## Dataset source
The raw WikiSQL data and SQLite databases come from the official
Salesforce WikiSQL release.

## Build the 1k dataset
```bash
python scripts/prepare_wikisql_1k.py
```

Outputs (default):
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.jsonl`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db`
- `~/.cache/fastdistill/datasets/wikisql/wikisql_1k/eval.db`

## Run distillation (teacher)
If you keep `OPENROUTER_API_KEY` in `.env` at repo root, the examples will load it automatically.

```bash
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
python examples/fastdistill/fastdistill_pipeline.py
```

## Run teacher + student eval (Ollama)
```bash
FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl \
FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db \
OLLAMA_MODEL=qwen3:0.6b \
OLLAMA_STUDENT_MODEL=qwen3:0.6b \
python examples/fastdistill/ollama_distill_e2e.py
```

## Performance knobs
- `FASTDISTILL_LLM_BATCH_SIZE`: LLM task batch size (default 50).
- `FASTDISTILL_DATASET_BATCH_SIZE`: dataset batching for pipeline.
- `OPENROUTER_TIMEOUT` / `OLLAMA_TIMEOUT`: request timeout in seconds.

## Notes
- `train.db` and `eval.db` include the full table sets for their splits.
- The SQL builder normalizes string literals to lowercase to match WikiSQL DBs.
