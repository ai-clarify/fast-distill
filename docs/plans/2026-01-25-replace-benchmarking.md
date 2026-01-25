# Plan: Replace CodSpeed benchmarks with pytest-benchmark (2026-01-25)

## Goal
Replace the CodSpeed-based benchmark workflow with an in-repo pytest-benchmark flow that does not rely on external tokens.

## Plan
- [x] Swap test dependency from `pytest-codspeed` to `pytest-benchmark`.
- [x] Update the benchmark workflow to run pytest-benchmark and upload artifacts.
- [x] Run lint + unit + integration tests.
- [ ] Commit changes.

## Progress
- Swapped the test dependency and replaced the CodSpeed CI step with pytest-benchmark + artifacts.
- Lint + unit + integration tests completed successfully.
