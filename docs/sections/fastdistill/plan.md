# FastDistill retrofit plan (conclusion first)

**Conclusion:** we can retrofit this repo by adding a small set of new steps + a pipeline template, while keeping the core scheduler untouched. The first execution slice is to land a stable data contract (canonicalize + sample_id), add manifest/quality reports, and ship a reference pipeline that targets a Provider Gateway (OpenAI-compatible) via existing LLM integrations.

## Goals and hard constraints (config-gated)

- **Speed metrics (log-verifiable)**
  - `teacher_tokens_per_sec`
  - `pipeline_kept_samples_per_hour`
  - `train_tokens_per_sec`
- **Quality metrics (falsifiable)**
  - `test_exec_accuracy`
  - `online_win_rate`
- **Hard gates** (values live in config, any change requires new `run_id` and new eval record)
  - `test_exec_accuracy` must be >= baseline model.
  - `online_win_rate` must be >= teacher lower bound or >= previous version confidence lower bound.

## Architecture (four planes, data-contract coupling only)

- **Control plane**: run_id, sharding, retries, backpressure, rate limiting, orchestration.
- **Data plane**: canonical schema, parquet artifacts, manifest + indexing, dedup cache.
- **Inference plane**: teacher generation + judge scoring, unified Provider Gateway.
- **Training plane**: SFT + distillation, decoupled from inference providers.

## Directory layout and module boundaries (this repo)

```
configs/
  fastdistill/
    run_config.sample.yaml
    quality_gates.sample.yaml
    provider_gateway.sample.yaml

examples/
  fastdistill/
    fastdistill_pipeline.py

src/fastdistill/steps/
  fastdistill/
    __init__.py
    canonicalize.py
    hashing.py
    manifest.py
    quality_report.py

docs/sections/fastdistill/
  plan.md
  provider_gateway_contract.yaml
  run_config.sample.yaml
```

Notes:
- Only new steps + pipelines are added. No changes to core scheduling or pipeline execution.
- Provider Gateway stays external; fastdistill calls it via OpenAI-compatible LLM clients.

## Provider Gateway (OpenAI-compatible surface)

- **External interface**: `/chat/completions` and optional `/embeddings`.
- **Internal**: adapter to cloud APIs or self-hosted vLLM/sglang with capability probing, request shaping, and rate/backpressure.
- **Contract**: a stable request envelope with `provider_id`, `model`, `decode`, `constraints`, `trace` for AB and replay.

## Data contract (replayable)

- **Stable ID**: `sample_id = sha256(task_id + schema_hash + canonical_input + decode_profile)`
- **Artifacts (parquet)**: `raw`, `canonical`, `teacher_candidates`, `filtered`, `distilled`
- **Manifest**: `{count, field_hash, min/max sample_id}` per shard per stage.
- **Dedup cache**: key by `prompt_hash + model + decode_profile`.

## Quality gates (deterministic)

- **Rules**: empty outputs, length bounds, banned tokens, format checks.
- **Parse**: SQL (or task-specific) parseability.
- **Exec**: runtime errors reject; result schema mismatch reject.
- **Semantic**: gold match if available; else judge (only for exec_pass).

## Execution roadmap

- **V0 (2 weeks)**: Provider Gateway integration, data contract + manifest, TeacherGen/Parse/Exec/Select pipeline, training runner outputs with hard gates.
- **V1 (1 month)**: request coalescing, token budget backpressure, dedup cache, judge isolation, hard_sample queue.
- **V2 (2 months)**: uncertainty-driven re-sampling, budgeted judge/teacher.
- **V3 (3 months)**: multi-task + tool-use + RAG through unified messages; online data re-entry.
- **V4 (optional)**: logits distill only if offline+online gates pass.

## Start of execution (this PR)

- Add fastdistill steps for canonicalization, stable hashing, manifest and quality reporting.
- Add a reference pipeline pointing to Provider Gateway via OpenAI-compatible LLM clients.
- Add config templates for run parameters and quality gates.
- Add timing markers + timing report to make per-stage latency visible.
- Add SQLite exec evaluation step for Text2SQL auto-scoring.
