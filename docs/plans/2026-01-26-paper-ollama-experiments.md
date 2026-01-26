# Plan: Paper-driven experiments with local Ollama teacher

Date: 2026-01-26

## Context
- Request: start experiments based on distillation papers using a strong local Ollama model as the teacher.
- Constraints: follow engineering practices, keep config examples YAML-only, update progress here, run full lint + tests, and commit changes.

## Plan
1. Review engineering practices and existing pipelines/docs for Ollama usage.
2. Draft a paper-to-experiment playbook that fits the current pipeline capabilities.
3. Add a local Ollama teacher pipeline YAML variant for reproducible runs.
4. Update docs (EN + ZH) and README entry points.
5. Run full lint + tests.
6. Commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Reviewed existing pipelines/docs for Ollama usage.
- [x] Added paper experiment playbook docs (EN/ZH).
- [x] Added Ollama teacher pipeline YAML.
- [x] Updated README/docs entry points.
- [x] Ran full lint + tests (unit/integration failures logged).
- [ ] Committed changes.
