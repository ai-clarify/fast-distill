# FastDistill Baseline (2026-01-23)

## Run configuration
- Pipeline: `examples/fastdistill/ollama_distill_e2e.py`
- Model: `lfm2.5-thinking:latest` (Ollama, localhost)
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`
- Load groups: unset (`FASTDISTILL_LOAD_GROUPS` not set)

## Quality results
From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 2
- kept: 2
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- reject_reason_counts: {"ok": 2}
- exec_error_counts: {}

## Timing results (p50)
From `~/.cache/fastdistill/artifacts/reports/timing_report.json`:
- total p50: 9.338s
- raw -> canonical: 0.219s
- canonical -> hashed: 0.201s
- hashed -> teacher: 8.097s
- teacher -> filtered: 0.171s
- filtered -> eval: 0.200s
- eval -> selected: 0.348s
- selected -> distilled: 0.101s

## Derived throughput
- pipeline_kept_samples_per_hour (p50-based): 771.03

## Notes
- Token-level throughput is not reported because the Ollama client did not emit token statistics in this run.
