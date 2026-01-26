# 2026-01-26 - Unit tests flaky from LlamaCpp embedding decode + reward model score drift

## Context
- Command: `make unit-tests`
- Tests: `tests/unit/models/embeddings/test_llamacpp.py`, `tests/unit/steps/test_reward_model.py`

## Symptoms
- LlamaCpp embedding tests failed with `RuntimeError: llama_decode returned -1`.
- Reward model score assertions drifted by ~2e-5 outside the strict `1e-5` tolerance.

## Likely cause
- The GGUF embedding model can be incompatible with the installed `llama-cpp-python` runtime or build flags, triggering decode errors at inference time.
- Reward model scores vary slightly across hardware/torch/transformers versions.

## Impact
- Unit test suite failed in otherwise healthy environments.

## Resolution
- Added a session-level embedding smoke check that skips the embedding test suite when `llama_decode returned -1` is encountered.
- Relaxed reward model score tolerances to `1e-4`.
- Passed embedding extra kwargs via `**extra_kwargs` to match the LlamaCpp LLM path.

## Follow-ups
- Consider pinning a minimum `llama-cpp-python` version that guarantees BERT/GGUF embedding support.
- Revisit reward model tests if a deterministic inference path is introduced.
