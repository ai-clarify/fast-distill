---
description: Layered walkthrough of the FastDistill codebase from entry points to execution internals.
---

# Codebase Walkthrough (from shallow to deep)

This guide is a layered interpretation of the FastDistill codebase. Start at the top, stop when you feel comfortable, and dive deeper only where you still feel uncertain.

## Layer 0 — What runs when you run FastDistill?

**Goal:** identify the entry points and the fastest path to trace a run.

- **CLI entry**: `src/fastdistill/__main__.py` → `src/fastdistill/cli/app.py` → `fastdistill pipeline run` in `src/fastdistill/cli/pipeline/app.py`.
- **Config/script loading**: `src/fastdistill/cli/pipeline/utils.py` reads a pipeline config (`.yaml`) or a Python script and materializes a `Pipeline`.
- **Execution**: `Pipeline.run()` in `src/fastdistill/pipeline/base.py` sets runtime parameters, validates the DAG, and launches execution (locally via `src/fastdistill/pipeline/local.py` or remotely via `src/fastdistill/pipeline/ray.py`).
- **Artifacts & cache**: stored under `~/.cache/fastdistill/pipelines/<pipeline>/<signature>/...` (see `src/fastdistill/constants.py`).

If you want **just one file** to skim for the main flow, start with:
- `src/fastdistill/pipeline/base.py` (overall run lifecycle)

## Layer 1 — Core abstractions (conceptual objects)

**Goal:** understand the nouns that structure the codebase.

| Concept | What it is | Primary files |
| --- | --- | --- |
| Pipeline | Orchestrates Steps as a DAG, handles batching, caching, stages | `src/fastdistill/pipeline/base.py`, `src/fastdistill/pipeline/local.py` |
| DAG | Validates graph structure, inputs/outputs, routing | `src/fastdistill/pipeline/_dag.py` |
| Step | Batch processor with typed inputs/outputs | `src/fastdistill/steps/base.py` |
| GeneratorStep | Root data source (no upstream inputs) | `src/fastdistill/steps/base.py` |
| GlobalStep | Receives all data at once | `src/fastdistill/steps/base.py` |
| Task | Step specialized for LLM generation + formatting | `src/fastdistill/steps/tasks/base.py` |
| Distiset | Output dataset wrapper (HF Hub + artifacts) | `src/fastdistill/distiset.py` |
| Batch | Unit of data flow between steps | `src/fastdistill/pipeline/batch.py` |

### How the pieces fit
1. **Pipeline** builds a **DAG** of **Steps**.
2. **GeneratorStep** emits batches; normal **Step** consumes batches and yields new batches.
3. **GlobalStep** waits for all data (e.g., manifest/report).
4. **Distiset** aggregates leaf outputs, plus artifacts/logs.

## Layer 2 — Execution engine (where the concurrency lives)

**Goal:** understand how batches move and why stages exist.

- **Batch manager** (`src/fastdistill/pipeline/batch_manager.py`) is the scheduler and buffer:
  - Accumulates upstream data until a step has enough rows.
  - Tracks offsets/seq numbers for caching and replay.
  - Handles routed batches (routing functions) and convergence steps.
- **Step wrapper** (`src/fastdistill/pipeline/step_wrapper.py`) executes a Step in a worker process:
  - Calls `step.load()` → `process()` → `step.unload()`.
  - Handles non-fatal errors by emitting empty rows with `None` values.
  - Promotes offline-batch-generation exceptions into a controlled pipeline stop.
- **Stage loading** (in `pipeline/base.py` + `pipeline/_dag.py`):
  - Steps are grouped into **load stages** to isolate `GlobalStep`s and user-defined `load_groups`.
  - Pipeline waits for an entire stage to finish before loading the next stage.

**Minimal runtime flow (local):**
1. `Pipeline.run()` validates DAG and cache status.
2. Spawns a multiprocessing pool (`pipeline/local.py`).
3. Starts output loop: receive batches → write to buffer → schedule successors.
4. When done, `Distiset` is created from cached step outputs.

## Layer 3 — Runtime parameters & serialization

**Goal:** understand how values flow without re-instantiating objects.

- **Runtime parameters** (from `fastdistill.mixins.runtime_parameters`):
  - Any field annotated with `RuntimeParameter[...]` can be supplied via `Pipeline.run(parameters={...})`.
  - `Pipeline.run()` calls `step.set_runtime_parameters()` before cache resolution.
- **Serialization** (from `fastdistill.utils.serialization`):
  - `Pipeline` dumps to `pipeline.yaml` in cache.
  - `DAG.dump()` stores step definitions + routing functions.
- **Signature & caching**:
  - Step signatures (mixins) combine with pipeline topology signature to locate caches.
  - If any step changes signature, downstream cache is invalidated (`batch_manager`).

## Layer 4 — Models & providers

**Goal:** map where LLM/embedding/image generation APIs live.

- **LLM base**: `src/fastdistill/models/llms/base.py`
  - `generate()` / `generate_outputs()` + offline batch generation.
- **Providers**: `src/fastdistill/models/llms/` (OpenAI, vLLM, SGLang, Ollama, etc.).
- **Embeddings**: `src/fastdistill/models/embeddings/` (sentence transformers, vLLM, llama.cpp).
- **Image generation**: `src/fastdistill/models/image_generation/`.
- **Legacy imports**: `src/fastdistill/llms.py` (deprecated shim → `fastdistill.models`).

## Layer 5 — FastDistill-specific steps (distillation pipeline building blocks)

These are the **opinionated steps** for deterministic distillation and quality gates.

| Step | Purpose | File |
| --- | --- | --- |
| CanonicalizeFields | Stable canonical string for determinism | `steps/fastdistill/canonicalize.py` |
| ComputeHash | SHA256 hash from selected fields | `steps/fastdistill/hashing.py` |
| DeduplicateByField | Drop/flag duplicates by a field | `steps/fastdistill/dedup.py` |
| RuleFilter / FilterByBool | Cheap rule-based filtering | `steps/fastdistill/filtering.py` |
| SQLiteExecEval | Execute SQL and score pass/gold match | `steps/fastdistill/sql_eval.py` |
| ScoreFromExecEval | Convert exec/gold to teacher score | `steps/fastdistill/scoring.py` |
| KeepByScore | Update keep flag by score threshold | `steps/fastdistill/scoring.py` |
| WriteManifest | Stable stage manifest | `steps/fastdistill/manifest.py` |
| WriteQualityReport | Per-stage quality report | `steps/fastdistill/quality_report.py` |
| MarkTime / WriteTimingReport | Timing markers + report | `steps/fastdistill/timing.py` |
| SqlOutputCleaner | Clean SQL from LLM output | `steps/fastdistill/sql_output.py` |
| evaluate_quality_gate | Validate metrics vs gate | `steps/fastdistill/quality_gate.py` |

These steps are designed to be **small, deterministic, and composable** so you can assemble pipelines that are replayable and auditable.

## Layer 6 — Step/task gallery & utilities

**Goal:** find “what else exists” quickly.

- **Steps**: `src/fastdistill/steps/`
  - `generators/` (load data), `columns/` (column ops), `formatting/`, `filtering/`, `clustering/`, `embeddings/`, `argilla/`.
- **Tasks**: `src/fastdistill/steps/tasks/`
  - LLM tasks (text generation, scoring, structured outputs, evol instruct, etc.).
  - Prompt templates live in `steps/tasks/templates/`.
- **Utils**: `src/fastdistill/utils/`
  - Logging, serialization, docs, templating, HF helpers, etc.
- **Typing**: `src/fastdistill/typing/` defines shared types used across steps/models.

## Layer 7 — Uncertainty killers (where to look when confused)

- **“Where does this column come from?”**
  - Check `Step.inputs` / `Step.outputs` and any `input_mappings` / `output_mappings` in `steps/base.py`.
- **“Why is this step global?”**
  - `GlobalStep` (all inputs at once) and tasks using offline batch generation (`steps/tasks/base.py`).
- **“Why is my batch size mismatched?”**
  - `DAG.validate()` in `pipeline/_dag.py` enforces batch sizing and routing constraints.
- **“Where are artifacts written?”**
  - `Step.save_artifact()` in `steps/base.py` writes into `steps_artifacts` under the cache dir.
- **“Why did cache invalidate?”**
  - Step signature mismatch or `use_cache=False` in `pipeline/base.py` and `batch_manager.py`.
- **“Where is the pipeline log?”**
  - `pipeline.log` in the pipeline cache directory (see `constants.py`).

## Layer 8 — Suggested reading paths

Pick a path based on what you want to do:

1. **Extend the execution engine**: `pipeline/base.py` → `_dag.py` → `batch_manager.py` → `step_wrapper.py`.
2. **Add a new Step**: `steps/base.py` → a sibling in `steps/` → tests in `tests/unit/steps/`.
3. **Add a new LLM provider**: `models/llms/base.py` → new provider in `models/llms/`.
4. **Create a FastDistill pipeline**: `examples/fastdistill/` + fastdistill steps in `steps/fastdistill/`.

---

If you want, I can follow up with a **call graph** for a specific pipeline run or a **step-by-step trace** for a concrete example (`examples/fastdistill/fastdistill_pipeline.py`).
