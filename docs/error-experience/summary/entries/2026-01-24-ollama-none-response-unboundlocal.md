# 2026-01-24 - Ollama no-response UnboundLocalError

## Issue
Ollama generation returned no response; token-stat collection raised `UnboundLocalError`.

## Fix
Guarded token statistics when no completion is returned.
