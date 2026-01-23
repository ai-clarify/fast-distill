# FastDistill student eval flow + baseline (2026-01-23)

## Scope
Align the end-to-end flow with teacher auto-eval → distill → student generation → distilled model eval, and refresh the baseline metrics from a full run.

## Steps
- [x] Update architecture flowchart (EN/中文) to end at distilled model evaluation and reflect student timing.
- [x] Run the full Text2SQL E2E pipeline (`examples/fastdistill/ollama_distill_e2e.py`) to regenerate reports.
- [x] Update `docs/sections/fastdistill/baseline.md` with new timing + quality numbers (teacher + student eval).
- [x] Re-check diffs and prepare commit + push.

## Notes
- Use the latest reports under `~/.cache/fastdistill/artifacts/reports/`.
- Capture `timing_report.json` total p50 for throughput.
