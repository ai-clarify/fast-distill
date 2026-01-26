# Plan: Auto-venv tests + local Ollama sample run

Date: 2026-01-26

## Context
- Request: optimize tests to auto-use a virtual environment, run a small sample, and inspect local Ollama models for experiments.
- Constraints: follow engineering practices, keep YAML-only config examples, update progress here, run full lint + tests, and commit changes.

## Plan
1. Add a shared test helper to ensure a repo-local venv is created/activated for test scripts.
2. Update unit/integration test runners to use the shared venv helper.
3. Harden test collection for MLX/integration environments where prerequisites are unavailable.
4. Run lint + tests and log any remaining failures.
5. Inspect local Ollama models and run a small sample pipeline.
6. Commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Added venv helper + wired test scripts.
- [x] Hardened MLX/integration test gating.
- [x] Ran full lint + tests.
- [x] Inspected local Ollama models + ran small sample.
- [ ] Committed changes.

## Notes
- Local Ollama models (2026-01-26): `qwen3:0.6b`, `lfm2.5-thinking:latest`, `hf.co/unsloth/GLM-4.7-Flash-GGUF:Q4_K_XL` (`ollama list`).
- Small sample run (2 items): `FASTDISTILL_PROVIDER=ollama OLLAMA_MODEL=lfm2.5-thinking:latest python examples/fastdistill/fastdistill_pipeline.py`.
- Full lint/unit/integration runs completed after venv + gating changes.
