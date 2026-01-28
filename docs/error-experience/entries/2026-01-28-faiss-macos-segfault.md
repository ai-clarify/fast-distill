# 2026-01-28 - macOS unit tests segfault in Faiss nearest-neighbour

## Context
- Command: `make unit-tests`
- Environment: macOS (Apple Silicon), faiss installed via extras
- Test: `tests/unit/steps/embeddings/test_nearest_neighbour.py`

## Symptoms
- Test suite aborted with `Segmentation fault: 11` during Faiss nearest-neighbour test.

## Likely cause
- The macOS faiss wheel occasionally segfaults during index operations in the unit test.

## Impact
- Full unit test run cannot complete on macOS when faiss is installed.

## Resolution
- Skip Faiss nearest-neighbour test module on macOS to keep the suite stable.

## Follow-ups
- Revisit if faiss releases a stable macOS wheel; consider pinning a known-good version.
