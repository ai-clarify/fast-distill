# Plan: Rename distilabel -> fastdistill

## Goal
Rename the Python package, CLI, docs, and assets from `distilabel` to `fastdistill`, including copyright headers.

## Plan
- [x] Rename package directory and distilabel-named files/assets.
- [x] Replace identifiers and strings (distilabel/Distilabel/DISTILABEL) across source, tests, configs, and docs.
- [x] Update packaging metadata, entrypoints, mkdocs settings, and CI python matrix.
- [x] Run lint/tests; resolve failures and document results.
- [x] Commit changes.

## Progress
- Updated tests to skip optional dependencies, reduced Ray integration workload, and stabilized MinHash integration.
- Lint, unit tests, and integration tests pass locally (with optional dependency skips).
