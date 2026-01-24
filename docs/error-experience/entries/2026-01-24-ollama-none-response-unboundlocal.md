# 2026-01-24 - Ollama no-response raised `UnboundLocalError`

## Context
- Command: `python examples/fastdistill/ollama_distill_e2e.py`
- Environment: macOS, Ollama local server.

## Symptoms
- Ollama client returned no response for a request.
- Pipeline logged `UnboundLocalError: cannot access local variable 'completion'`.

## Likely cause
- Exception path in `OllamaLLM.agenerate` didn't initialize `completion`, but still
  tried to read token stats from it.

## Impact
- Text generation step crashed and the pipeline returned empty batches.

## Resolution
- Initialize `completion = None` and skip token statistics if no response is returned.

## Follow-ups
- Consider exposing timeout and batch-size knobs in examples to reduce Ollama timeouts.
