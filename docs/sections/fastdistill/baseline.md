# FastDistill Baseline (2026-01-23)

## Run configuration
- Pipeline: `examples/fastdistill/ollama_distill_e2e.py`
- Teacher model: `lfm2.5-thinking:latest` (Ollama, localhost)
- Student model: `lfm2.5-thinking:latest` (defaulted from `OLLAMA_STUDENT_MODEL`)
- Dataset size: 2 samples (Text2SQL mini set)
- Artifacts root: `~/.cache/fastdistill/artifacts`
- Load groups: unset (`FASTDISTILL_LOAD_GROUPS` not set)

## Quality results (teacher/distilled)
From `~/.cache/fastdistill/artifacts/reports/distilled/quality_report.json`:
- total: 2
- kept: 2
- rejected: 0
- p_keep: 1.0
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0
- reject_reason_counts: {"ok": 2}
- exec_error_counts: {}

## Student eval results
From `~/.cache/fastdistill/artifacts/reports/student_eval/quality_report.json`:
- total: 2
- exec_pass_rate: 1.0
- gold_match_rate: 1.0
- judge_score: min 1.0, max 1.0, mean 1.0
- exec_error_counts: {}
- kept/rejected/p_keep: null (not applicable for eval-only stage)

## Timing results (p50)
From `~/.cache/fastdistill/artifacts/reports/timing_report.json`:
- total p50: 24.927s
- raw -> canonical: 0.286s
- canonical -> hashed: 0.307s
- hashed -> teacher: 6.996s
- teacher -> filtered: 0.310s
- filtered -> eval: 0.578s
- eval -> selected: 0.436s
- selected -> distilled: 0.144s
- distilled -> student_gen: 15.420s
- student_gen -> student_eval: 0.450s

## Derived throughput
- pipeline_kept_samples_per_hour (p50-based): 288.85

## Notes
- Token-level throughput is not reported because the Ollama client did not emit token statistics in this run.
- `distilled -> student_gen` includes stage boundaries (report/manifest/keep) before student generation in this reference pipeline.
