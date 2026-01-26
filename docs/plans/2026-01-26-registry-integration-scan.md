# Plan: Registry integration scan + docs gaps (2026-01-26)

## Goals
- Inventory registry integration points (registry, components gallery, export_components_info, docs).
- Identify gaps for registry usage in CLI/API reference.
- Flag conflicts/risks tied to registry discovery and docs builds.

## Constraints
- Follow `docs/ENGINEERING_PRACTICES.md` (YAML-only configs, log errors if needed).
- Keep index docs index-only.

## Plan
1. Review engineering practices + existing registry-related code paths.
2. Scan components gallery + export_components_info usage and doc references.
3. Note gaps in CLI/API docs for registry usage + propose changes.
4. Flag conflicts/risks and summarize findings.

## Progress
- [x] Review engineering practices.
- [x] Scan registry code, components gallery, export_components_info, docs.
- [x] Identify CLI/API doc gaps and draft recommendations.
- [x] Flag conflicts/risks.

## Validation
- Not applicable (no code changes).
