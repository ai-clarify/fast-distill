# Plan: Config loader inspection + layered YAML proposal

Date: 2026-01-26

## Context
- Request: inspect CLI/config loading, identify existing behaviors/risks, and propose a layered YAML loader (base -> env -> run overrides) with CLI integration.
- Constraints: follow engineering practices, update progress here, run full lint + tests, and commit changes.

## Plan
1. Review config/CLI loading paths and serialization utilities.
2. Collect existing YAML config examples and current behavior notes.
3. Identify risks/edge cases in the current loader pipeline.
4. Propose a layered YAML config loader design (merge semantics + CLI integration).
5. Update this plan with progress/results and commit changes.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Reviewed config/CLI loading paths and serialization utilities.
- [x] Collected existing YAML config examples and current behavior notes.
- [x] Identified risks/edge cases in the current loader pipeline.
- [x] Proposed layered YAML loader + CLI integration.
- [ ] Ran full lint + tests.
- [ ] Committed changes.

## Findings
- CLI loads serialized `pipeline.yaml` or a remote script; local YAML uses `yaml.FullLoader`, remote YAML uses `yaml.safe_load`.
- `_Serializable.load_with_type_info` drops unknown keys for `BaseModel`s, so config typos can be silently ignored.
- `DAG.from_dict` uses wrapper `name` for connections but does not validate it matches `step.name`.
- Remote config/script downloads have no timeout; script import uses module cache and leaves files in CWD.
- CLI runtime parameters are string-only (type coercion depends on Pydantic assignment).

## Proposal (layered YAML config)
- Introduce `fastdistill.config.loader` with `load_yaml_layer`, `merge_layers` (deep-merge dicts, replace lists), and `apply_step_overrides` keyed by step name.
- Add CLI options `--config-env`, `--config-run`, and `--param-file` (YAML). Merge order: base < env < run < param-file < `--param`.
- Normalize YAML loading to `safe_load` and add strict validation (optional flag) to surface unknown keys and `pipeline`/`step` name mismatches.
