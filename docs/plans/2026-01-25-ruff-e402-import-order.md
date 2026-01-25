# Plan: Fix ruff E402 import ordering in tests

Date: 2026-01-25

## Context
- `make lint` fails with E402 because `pytest.importorskip(...)` statements appear before imports.
- Goal: preserve optional dependency skipping while keeping imports at the top of the module.

## Plan
1. Inspect failing test files to understand import ordering and optional dependency usage.
2. Reorder imports so all imports are at the top; replace direct optional imports with `pytest.importorskip` assignments after imports when safe.
3. Re-run `make lint`, `make unit-tests`, and `make integration-tests`.
4. Commit changes in small commits and update this plan.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [ ] Inspected failing test files.
- [ ] Reordered imports / adjusted optional dependency handling.
- [ ] Ran lint + tests.
- [ ] Committed changes.
