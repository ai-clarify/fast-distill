# 2026-01-26 - OpenRouter JSON decode error during 1k teacher run

## Context
- Command: `FASTDISTILL_PROVIDER=openrouter OPENROUTER_MODEL=deepseek/deepseek-v3.2 OPENROUTER_TIMEOUT=240 OPENROUTER_TEMPERATURE=0.2 OPENROUTER_MAX_TOKENS=128 FASTDISTILL_LLM_BATCH_SIZE=20 FASTDISTILL_DATA_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.jsonl FASTDISTILL_DB_PATH=~/.cache/fastdistill/datasets/wikisql/wikisql_1k/train.db FASTDISTILL_ARTIFACTS_DIR=~/.cache/fastdistill/artifacts/openrouter_wikisql_1k_teacher_2026-01-26 python examples/fastdistill/fastdistill_pipeline.py`
- Environment: macOS, OpenRouter remote teacher.

## Symptoms
- `text_generation_0` emitted `JSONDecodeError` while parsing response body.
- Pipeline warned and sent an empty batch filled with `None` for batch 3.

## Likely cause
- Partial/invalid JSON response from OpenRouter under higher batch size.

## Impact
- Output batch contained missing generations, lowering exec pass rate for the run.
- Run was terminated to avoid mixing partial artifacts.

## Resolution
- Re-run with smaller `FASTDISTILL_LLM_BATCH_SIZE` (e.g., 10 or 5) to reduce response size/concurrency.

## Follow-ups
- Consider adding retry logic or response validation to OpenAI client wrapper for transient JSON decode failures.
