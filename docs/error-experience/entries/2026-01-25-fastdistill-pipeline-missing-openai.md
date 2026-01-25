# 2026-01-25 - FastDistill quick pipeline failed: `openai` dependency missing

## Context
- Command: `python examples/fastdistill/fastdistill_pipeline.py`
- Provider: OpenRouter (via `OpenAILLM`)
- Environment: local macOS.

## Symptoms
- Pipeline failed during step load.
- Error: `OpenAI Python client is not installed. Please install it using 'fastdistill[openai]'`.

## Likely cause
- `openai` extra was not installed in the current Python environment.

## Impact
- Quick distillation pipeline aborted before any dataset artifacts were produced.

## Resolution
- Installed `openai` (`python -m pip install openai`), reran pipeline successfully.

## Follow-ups
- Ensure quickstart docs mention installing provider-specific extras before running OpenRouter/OpenAI flows.
