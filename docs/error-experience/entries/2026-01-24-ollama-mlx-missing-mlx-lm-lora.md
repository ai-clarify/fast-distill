# 2026-01-24 - Ollama + MLX e2e failed: `No module named 'mlx_lm_lora'`

## Context
- Command: `python scripts/run_ollama_mlx_e2e.py`
- Environment: local macOS, Ollama running on `localhost:11434`.

## Symptoms
- Distillation completed, MLX dataset exported.
- Training step failed with `ModuleNotFoundError: No module named 'mlx_lm_lora'`.

## Likely cause
- The MLX training package is not installed or not importable in the current Python environment.

## Impact
- Full local e2e run cannot finish training; no distilled model artifacts produced.

## Resolution
- Install the MLX training package that provides `mlx_lm_lora` and ensure
  `python -m mlx_lm_lora.train --help` works, then rerun.

## Follow-ups
- Script updated to check for `mlx_lm_lora` before starting training and emit a clear error.
