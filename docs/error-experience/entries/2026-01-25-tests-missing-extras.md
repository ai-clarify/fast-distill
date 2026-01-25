# 2026-01-25 - Tests failed due to missing test extras in local venv

## Context
- Commands: `make unit-tests`, `make integration-tests`
- Environment: local macOS virtualenv

## Symptoms
- Unit tests failed during collection: `ModuleNotFoundError: No module named 'PIL'` and async tests missing plugin.
- Integration tests failed at `tests/integration/test_cache.py` with `fixture 'benchmark' not found`.

## Likely cause
- The virtualenv did not have the full test extras installed (Pillow, pytest-asyncio, pytest-benchmark).

## Impact
- Full test suite could not complete in a clean environment, blocking validation.

## Resolution
- Installed missing dependencies in the active venv: `Pillow`, `pytest-asyncio`, `pytest-benchmark`.
- Re-ran unit + integration tests successfully.

## Follow-ups
- When setting up new environments, install the tests extras (`.[tests]`) to include required plugins.
