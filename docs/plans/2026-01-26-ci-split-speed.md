# Plan: Split CI tests for faster feedback

Date: 2026-01-26

## Context
- Current CI runs lint, unit, and integration tests sequentially in a single job.
- Goal: run them in parallel to reduce wall-clock time.

## Plan
1. Update GitHub Actions workflow to split lint, unit, and integration tests into separate jobs.
2. Ensure each job shares the same dependency installation and caching strategy.
3. Run full lint + unit + integration tests locally after changes.
4. Commit changes.

## Progress
- [x] Update workflow jobs.
- [x] Validate lint + unit + integration locally.
- [ ] Commit changes.
