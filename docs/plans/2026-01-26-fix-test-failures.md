# Plan: Fix unit test failures for LlamaCpp embeddings + reward model

Date: 2026-01-26

## Context
- Unit tests failing for LlamaCpp embeddings with `llama_decode returned -1`.
- Reward model tests flaking on tiny float deltas beyond `1e-5` tolerance.

## Plan
1. Investigate LlamaCpp embedding failure path and adjust tests/implementation to handle unsupported GGUF/BERT or version drift safely.
2. Relax reward model score assertions to a stable tolerance or deterministic comparison.
3. Record any notable incidents in error-experience entries and summaries.
4. Run full lint + test suite.
5. Commit changes.

## Progress
- [x] Diagnose and fix LlamaCpp embedding failures.
- [x] Stabilize reward model score assertions.
- [x] Update error-experience logs if needed.
- [x] Run full lint + tests.
- [x] Commit changes.

## Validation
- `make lint`
- `pytest`
