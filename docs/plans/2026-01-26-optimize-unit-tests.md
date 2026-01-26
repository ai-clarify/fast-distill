# Plan: Speed up unit test execution

Date: 2026-01-26

## Context
- `make unit-tests` is too slow for local workflows.
- Goal: enable parallel execution when pytest-xdist is available, with safe fallback.

## Plan
1. Add a lightweight test runner script to use pytest-xdist when installed.
2. Wire `make unit-tests` to the new script.
3. Add pytest-xdist to test extras.
4. Run lint + unit + integration tests.
5. Commit changes.

## Progress
- [x] Add xdist-aware test runner script.
- [x] Wire make target + add test extra.
- [ ] Run lint + unit + integration tests.
- [ ] Commit changes.

## Notes
- Lint/unit/integration runs were attempted but blocked by existing repo issues
  (e.g., `Optional` missing in `src/fastdistill/cli/pipeline/utils.py`).
