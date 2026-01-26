# 2026-01-26 - Unit tests aborted importing `mlx_lm`

## Context
- Command: `make unit-tests`
- Environment: macOS, local Python 3.11.

## Symptoms
- Test collection aborted with `Fatal Python error: Aborted`.
- Traceback shows import of `mlx_lm/convert.py` crashing during `pytest.importorskip("mlx_lm")` in `tests/unit/models/llms/test_mlx.py`.

## Likely cause
- The installed `mlx_lm` extension aborted during import (incompatible build/runtime or missing MLX dependencies).

## Impact
- Unit test suite stopped before running the remaining tests.

## Resolution
- Ensure `mlx_lm` is installed with a compatible MLX runtime for the current macOS/Apple Silicon build.
- If MLX coverage is not required for this run, remove `mlx_lm` from the environment so `pytest.importorskip("mlx_lm")` cleanly skips the tests.

## Follow-ups
- Consider guarding MLX tests behind a dedicated env flag to avoid aborting the full suite.
