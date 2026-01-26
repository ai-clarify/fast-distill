# Plan: OSS roadmap + component registry foundation (2026-01-26)

## Goals
- Publish an OSS-grade roadmap with parallel workstreams and milestones.
- Land the first foundation slice for plugin-style extensibility (component registry).
- Keep optional dependencies lazy and avoid breaking public APIs.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, log error experiences, run full lint/tests).
- Add English + Chinese docs for new sections when practical.
- Use TDD for new logic and avoid unnecessary defensive code.

## Plan
1. Re-check engineering practices and current architecture touchpoints.
2. Write a detailed roadmap doc (EN + ZH) with parallel tasks and dependencies.
3. Implement component registry with entry-point discovery and lazy import integration.
4. Update component export docs generation to use the registry.
5. Add unit tests for registry discovery + collision handling.
6. Run full lint + tests.
7. Commit in small, focused commits.

## Progress
- [x] Review engineering practices.
- [x] Draft OSS roadmap docs (EN + ZH) and wire into docs.
- [x] Implement component registry foundation + update exports.
- [x] Add unit tests for registry discovery/collisions.
- [x] Run full lint + tests.
- [x] Commit changes.

## Validation
- `make lint`
- `pytest`
