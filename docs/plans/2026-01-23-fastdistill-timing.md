# FastDistill timing instrumentation plan (2026-01-23)

## Scope
Add per-stage timing markers and a timing report for the fastdistill e2e pipeline, and update guidance.

## Steps
- [x] Implement timing steps (mark + report) in `fastdistill.steps.fastdistill`.
- [x] Wire timing markers into the Ollama e2e pipeline and emit a timing report.
- [x] Add unit tests for timing steps.
- [x] Update AGENTS.md guidance for performance/observability.

## Notes
- Timing uses `time.time()` for cross-process comparability.
- Reports are written to `~/.cache/fastdistill/artifacts/reports/timing_report.json` by default.
