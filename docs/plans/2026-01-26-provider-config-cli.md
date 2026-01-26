# Plan: Provider adapters + layered config + CLI integration (2026-01-26)

## Goals
- Define a minimal provider adapter interface + request/response envelope for LLM/embeddings/image.
- Add a layered YAML config loader (base → env → run overrides).
- Integrate provider selection by registry name into CLI.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, log errors, run full lint/tests).
- Preserve public APIs; avoid breaking changes.
- Use TDD for new logic; avoid unnecessary defensive code.

## Plan
1. Re-check engineering practices and current architecture touchpoints.
2. Draft provider adapter interface + envelope types (LLM/embeddings/image).
3. Implement layered config loader with validation hooks.
4. Wire config loader into CLI pipeline utilities.
5. Add unit tests for config merging and provider resolution.
6. Update docs with YAML examples (EN + ZH where applicable).
7. Run full lint + tests.
8. Commit in small, focused commits.

## Progress
- [x] Review engineering practices.
- [x] Draft provider adapter interface + envelope types.
- [x] Implement layered config loader.
- [x] Integrate CLI + provider selection.
- [x] Add tests.
- [x] Update docs.
- [x] Run full lint + tests.
- [x] Commit changes.

## Validation
- `make lint`
- `pytest`
