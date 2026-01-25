# 2026-01-25 - LlamaCpp embeddings decode failure (llama_decode returned -1)

## Context
- Command: `make unit-tests`
- Tests: `tests/unit/models/embeddings/test_llamacpp.py`
- Model: `all-MiniLM-L6-v2-Q2_K.gguf` (GGUF)

## Symptoms
- Multiple embedding tests failed with `RuntimeError: llama_decode returned -1` during `LlamaCppEmbeddings.encode`.

## Likely cause
- The Q2_K quantized embedding model appears incompatible with the installed `llama-cpp-python`/llama.cpp runtime or current environment constraints.

## Impact
- Unit test suite fails; CI blocks merges.

## Resolution
- Switched the test fixture model to `all-MiniLM-L6-v2-Q4_0.gguf` and updated references.

## Follow-ups
- Consider pinning a known-compatible `llama-cpp-python` version for embedding tests.
- Document the preferred GGUF quantization for tests.
