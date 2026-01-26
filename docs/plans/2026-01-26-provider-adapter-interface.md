# Plan: Provider adapter interface + envelope analysis (2026-01-26)

## Goals
- Inspect current LLM/Embeddings/ImageGeneration interfaces and call paths.
- Identify extension points and common stats fields in existing outputs.
- Propose a unified provider adapter interface + request/response envelope that preserves current APIs.
- Document minimal, non-breaking changes needed to introduce the adapter layer.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, avoid unnecessary defensive code).
- Preserve current public APIs (`LLM.generate_outputs`, `Embeddings.encode`, `ImageGenerationModel.generate_outputs`).
- Avoid code changes unless strictly necessary for the analysis deliverable.

## Plan
1. Review base model interfaces and output types.
2. Map how tasks consume outputs (statistics + extra fields).
3. Enumerate extension points and common stats fields across providers.
4. Draft a minimal adapter + envelope proposal with backwards-compatible entry points.
5. Capture findings + recommendations in the final response.

## Progress
- [x] Review engineering practices.
- [x] Review base model interfaces + output types.
- [x] Map task consumption expectations.
- [x] Identify extension points + common stats fields.
- [x] Draft adapter + envelope proposal.
- [x] Run full lint + tests.
- [x] Commit changes.
