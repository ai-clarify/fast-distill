# Plan: Fix LlamaCpp embedding test failures

Date: 2026-01-25

## Context
- Unit tests for `LlamaCppEmbeddings` failed with `llama_decode returned -1`.
- Goal: use a more compatible GGUF quantization and ensure tests run without skip paths.

## Plan
1. Switch the test embedding model to a more compatible quantization (Q4_0).
2. Update documentation examples referencing the model name.
3. Re-run lint, unit, and integration tests.
4. Record the incident in error-experience logs.
5. Commit changes and push.

## Progress
- [x] Switched test model to Q4_0 and removed decode skip.
- [x] Updated documentation examples.
- [x] Ran lint + tests.
- [x] Logged error experience.
- [x] Committed changes and pushed.
