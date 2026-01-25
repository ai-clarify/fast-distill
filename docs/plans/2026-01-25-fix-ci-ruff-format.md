# Plan: Fix CI ruff format failures

Date: 2026-01-25

## Context
- CI lint fails because ruff format wants to reformat a few files.
- Goal: apply ruff formatting, ensure lint + tests pass, and push.

## Plan
1. Run ruff format on the reported files.
2. Re-run `make lint`, `make unit-tests`, and `make integration-tests`.
3. Commit changes (formatting + plan updates) and push.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Applied ruff format to the failing files.
- [x] Ran lint + tests.
- [ ] Committed changes and pushed.
