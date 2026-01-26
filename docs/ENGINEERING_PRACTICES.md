# Engineering Practices

This repository prioritizes correctness, maintainability, and repeatability. Use
the checklist below when making changes.

## Core rules
- Create a plan in `docs/plans/` for multi-step work and keep it updated.
- Log important incidents in `docs/error-experience/entries/` and summarize them
  in `docs/error-experience/summary/entries/` (index files stay index-only).
- Prefer YAML for configuration; avoid JSON config examples.
- Favor simple, direct access over defensive guards when invariants are known.
- Run relevant tests (unit + affected integration paths) before delivery.
- For fast iteration, prefer `make test-changed`, but still run the full suite before final delivery.

## FastDistill-specific expectations
- Keep the pipeline reproducible by writing manifests and quality reports.
- Record baseline runs in `docs/sections/fastdistill/baseline.md`.
- Track performance in `docs/sections/fastdistill/performance.md`.

## Documentation hygiene
- Update the README for key changes and new entry points.
- Add both English and Chinese docs for new FastDistill sections when practical.
