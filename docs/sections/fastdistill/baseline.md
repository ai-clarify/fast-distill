# FastDistill Baseline (2026-01-23)

## Run configuration
- Pipeline: `examples/fastdistill/ollama_distill_e2e.py`
- Model: `lfm2.5-thinking:latest` (Ollama, localhost)
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`

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
- total p50: 43.945s
- raw -> canonical: 5.286s
- canonical -> hashed: 5.258s
- hashed -> teacher: 12.316s
- teacher -> filtered: 5.286s
- filtered -> eval: 5.258s
- eval -> selected: 7.919s
- selected -> distilled: 2.623s

## Derived throughput
- pipeline_kept_samples_per_hour (p50-based): 163.84

## Notes
- Token-level throughput is not reported because the Ollama client did not emit token statistics in this run.
