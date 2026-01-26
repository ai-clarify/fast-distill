# Plan: CLI runtime params + registry commands (2026-01-26)

## Goals
- Add YAML runtime param files to CLI (`--param-file`) with deterministic merge rules.
- Add registry CLI commands to list/show components for developer ergonomics.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, run full lint/tests).
- Preserve public APIs and avoid breaking changes.
- Use TDD for new logic where practical.

## Plan
1. Review CLI + registry integration points and confirm test hooks.
2. Implement `--param-file` YAML support and merge with `--param`.
3. Add `fastdistill registry list/show` commands with YAML output.
4. Add unit tests for runtime param merge and registry CLI.
5. Update CLI docs.
6. Run full lint + tests.
7. Commit in small, focused commits.

## Progress
- [x] Review CLI + registry integration points.
- [x] Implement `--param-file` YAML support.
- [x] Add registry CLI commands.
- [x] Add tests.
- [x] Update docs.
- [x] Run full lint + tests.
- [x] Commit changes.

## Validation
- `make lint`
- `pytest`
