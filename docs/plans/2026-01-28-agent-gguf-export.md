# Plan: Agent GGUF export (2026-01-28)

## Goals
- Export trained agent weights to GGUF for direct use.
- Wire GGUF export into agent distillation flow and CLI/config.
- Document GGUF artifact output and requirements.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, log errors, run full lint/tests).
- Use TDD for new logic.
- Avoid unnecessary defensive code.

## Plan
1. Inspect MLX tooling for GGUF conversion and existing agent artifacts.
2. Add GGUF export utilities and bundle paths.
3. Wire export into agent training flow + CLI/config overrides.
4. Update docs + sample config for GGUF output.
5. Add/extend unit tests for bundle paths/config.
6. Run full lint + unit + integration tests.
7. Commit in small, focused commits.

## Progress
- [x] Inspect MLX tooling for GGUF conversion and existing agent artifacts.
- [x] Add GGUF export utilities and bundle paths.
- [x] Wire export into agent training flow + CLI/config overrides.
- [x] Update docs + sample config for GGUF output.
- [x] Add/extend unit tests for bundle paths/config.
- [x] Run full lint + unit + integration tests.
- [ ] Commit changes.

## Validation
- `source .venv/bin/activate && make lint`
- `source .venv/bin/activate && make unit-tests`
- `source .venv/bin/activate && make integration-tests`
