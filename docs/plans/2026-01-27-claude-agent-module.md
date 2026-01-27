# Plan: Claude agent distillation module (2026-01-27)

## Goals
- Add an agent module powered by `claude-agent-sdk` to turn a user task into a distilled small-model agent bundle.
- Provide a CLI entry point (`fastdistill agent distill`) and YAML config support.
- Persist artifacts (spec, pipeline dump, reports, MLX dataset, optional training config).

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, log errors, run full lint/tests).
- Use TDD for new logic and add unit coverage for agent spec parsing/bundle paths.
- Avoid unnecessary defensive code; respect invariants where guaranteed.

## Plan
1. Inspect existing pipeline/CLI patterns and claude-agent-sdk API.
2. Define agent spec + run config models (YAML-friendly) and artifact layout.
3. Implement Claude agent spec generation + pipeline builder.
4. Add CLI integration + sample YAML config + docs.
5. Add tests for spec normalization, bundle paths, and config loading.
6. Run full lint + unit + integration tests.
7. Commit in small, focused commits.

## Progress
- [x] Review engineering practices.
- [x] Define agent spec + run config models.
- [x] Implement Claude agent spec generation + pipeline builder.
- [x] Add CLI integration + sample YAML config + docs.
- [x] Add tests.
- [x] Run full lint + unit + integration tests.
- [x] Commit changes.

## Validation
- `make lint`
- `make unit-tests`
- `make integration-tests`
