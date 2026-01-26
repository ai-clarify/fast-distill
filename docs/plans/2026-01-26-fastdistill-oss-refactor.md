# FastDistill OSS-grade architecture refactor (2026-01-26)

## Scope
Deepen architecture clarity, reduce optional-dependency coupling, and improve developer experience without breaking existing APIs.

## Steps
- [x] Map current architecture (core, pipeline, steps, models, utils) and identify high-impact coupling points.
- [x] Design refactor targets: public API surface, lazy optional dependency boundaries, and docs updates.
- [x] Implement refactor + tests (lazy imports, pipeline decoupling) and validate.
- [x] Run full lint + tests, summarize changes, and commit.

## Validation
- `make lint`
- `pytest`
