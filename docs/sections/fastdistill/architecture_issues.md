# FastDistill Architecture: Issue Analysis

Date: 2026-01-26

## Scope
This document reviews the current FastDistill architecture with a focus on maintainability,
reliability, and long-term evolution. The analysis is grounded in the current code structure
(e.g., `src/fastdistill/pipeline/base.py`, `src/fastdistill/steps/base.py`,
`src/fastdistill/mixins/runtime_parameters.py`).

## Executive summary
- The orchestration layer is monolithic and mixes execution, caching, storage, and logging.
- Global mutable state (pipeline context, CUDA device placement) makes concurrency brittle.
- Runtime parameter handling relies on Pydantic internals and is already producing deprecation warnings.
- Serialization/caching lacks explicit schema versioning, making upgrades fragile.
- Lazy-import infrastructure is widespread and complex, which complicates tooling and debugging.

## Key issues

### 1) Orchestration layer is monolithic
**Evidence**: `src/fastdistill/pipeline/base.py` (~1900 LOC) owns execution flow, caching,
filesystem transport, serialization, queue orchestration, and logging.

**Impact**
- High coupling: changing cache or execution semantics touches core orchestration.
- Harder testing: responsibilities are entangled and require expensive integration tests.
- Slower evolution: new execution backends must work around internal invariants.

**Remediation path**
- Extract explicit interfaces: `ExecutionEngine`, `CacheManager`, `StorageBackend`.
- Keep `BasePipeline` focused on DAG composition + lifecycle, delegate execution.
- Introduce small, explicit data contracts between layers.

---

### 2) Global mutable state and environment coupling
**Evidence**: `_GlobalPipelineManager` (pipeline context) and `CudaDevicePlacementMixin`
use process-global state and a host-level temp file for GPU placement.

**Impact**
- Concurrency conflicts when multiple pipelines run in the same process.
- Harder reproducibility in tests/CI, especially for GPU environments.
- Hidden side effects via environment variables (e.g., `CUDA_VISIBLE_DEVICES`).

**Remediation path**
- Replace global pipeline context with explicit context objects passed to steps.
- Make CUDA placement a pure strategy object scoped per pipeline instance.
- Isolate environment mutation behind a single execution boundary.

---

### 3) Runtime parameters depend on Pydantic internals
**Evidence**: `RuntimeParametersMixin` iterates `self.model_fields` (instance attribute),
which emits Pydantic deprecation warnings in the current tests.

**Impact**
- Forward-compatibility risk with new Pydantic releases.
- Repeated warnings across the suite; signals architectural fragility.
- Mixing reflection and mutation increases runtime cost and complexity.

**Remediation path**
- Move to class-level field access (`self.__class__.model_fields`).
- Capture runtime parameter metadata once at class construction time.
- Consider a lightweight schema layer independent of Pydantic internals.

---

### 4) Serialization and caching lack schema versioning
**Evidence**: Custom `_Serializable` dumps include `type_info`, but do not carry explicit
schema versions or migration hooks across releases.

**Impact**
- Cache incompatibility across versions; upgrades can break offline runs.
- Hard to implement safe migrations for persisted pipelines or artifacts.

**Remediation path**
- Add `schema_version` to serialized payloads.
- Introduce migration registry with explicit version upgrade paths.
- Separate cached runtime state from durable pipeline definitions.

---

### 5) Control plane and data plane are tightly coupled
**Evidence**: Steps hold pipeline references, and pipeline orchestration relies on step
side effects (e.g., metadata, reports). Many steps require pipeline-specific context.

**Impact**
- Reduced reusability of steps outside a pipeline execution.
- Policy enforcement (quality/observability) is implicit, not declarative.

**Remediation path**
- Define a minimal execution context interface and pass it explicitly to steps.
- Promote policy configuration into a control-plane layer rather than step internals.
- Make observability outputs a pipeline-level contract (not optional steps).

---

### 6) Lazy-import infrastructure is widespread and complex
**Evidence**: `__getattr__`-based lazy imports exist in top-level packages (`fastdistill`,
`fastdistill.steps`, `fastdistill.models`, etc.), with string-based import maps.

**Impact**
- Harder static analysis and IDE tooling.
- Increased complexity in debugging import-time issues.
- Higher risk of subtle behavior differences between direct import and lazy import.

**Remediation path**
- Keep lazy imports at the top-level API only.
- Use a registry/entry-point system for plugins to replace dynamic maps.
- Centralize lazy import helpers and standardize behavior.

---

### 7) Storage + batch transport is tightly embedded
**Evidence**: Base pipeline owns `_BatchManager` and `_WriteBuffer`, and toggles
filesystem transport via `use_fs_to_pass_data`.

**Impact**
- Performance tuning requires code changes in core orchestration.
- External storage backends (S3, Ray object store) are not first-class.

**Remediation path**
- Introduce a `BatchTransport` interface with memory/fs/object-store implementations.
- Make transport selection a pipeline config, not a core conditional.

---

### 8) Test/CI cost reflects architectural weight
**Evidence**: Integration tests are heavy and long-running; core components are hard to
unit-test without invoking pipeline execution.

**Impact**
- Slow feedback loops and higher CI cost.
- Discourages refactors and architectural iteration.

**Remediation path**
- Carve out testable subcomponents (execution engine, cache, transport).
- Add a small “fast” integration suite and gate slower tests to nightly runs.

## Strengths to preserve
- Clear separation between data generation and training (model plane is external).
- First-class observability artifacts (manifest/quality/timing) already exist.
- Rich step library and multi-provider LLM support.

## Suggested next steps
1. Define a minimal `ExecutionEngine` + `StorageBackend` interface and migrate local
   pipeline first; keep Ray as a separate engine.
2. Formalize serialization schema with versioning and migrations.
3. Replace global pipeline context with explicit execution context objects.
4. Consolidate lazy imports into a single registry + entry-point mechanism.

