# FastDistill OSS Roadmap (2026)

## North-star
Build a developer-first data generation + AI feedback framework with:
- **Stable public APIs** (clear compatibility guarantees).
- **Plugin-ready components** (optional providers + steps without hard deps).
- **Reproducible pipelines** (YAML configs, manifests, quality/timing reports).
- **Observable quality** (falsifiable gates, comparable metrics).

## Workstreams (parallel by design)
1. **Core runtime**: pipeline DAG, caching, scheduling, error boundaries.
2. **Component registry**: discovery + lazy loading for LLMs/embeddings/steps/tasks.
3. **Provider adapters**: unified surface for LLM/embedding/image providers.
4. **Config & CLI**: layered YAML config + runtime overrides + validation.
5. **Data plane**: canonicalization, dedup, manifest/report primitives.
6. **Observability**: timing/quality/cost reports + structured logs.
7. **DX & docs**: templates, examples, contribution guide, test matrix.

## Milestones with parallel tasks

### M0 (2026 Q1): Foundation stability
**Deliverables**
- Component registry foundation + entry-point discovery.
- Public API inventory (documented, versioned, and tested).
- Baseline performance + quality reports in docs.

**Parallel tasks**
- Core runtime: tighten error taxonomy, improve cache invalidation docs.
- Registry: add registry + lazy import integration.
- Docs: architecture map + extension points.
- Tests: add unit tests for registry + public API imports.

### M1 (2026 Q1–Q2): Provider + config unification
**Deliverables**
- Provider adapter interfaces (LLM, embeddings, image generation).
- Layered config loader (base → env → run overrides).
- CLI support for provider selection by name.

**Parallel tasks**
- Providers: introduce a common request/response envelope.
- Config: YAML schema + validation + merge rules.
- DX: generate config templates from schemas.

### M2 (2026 Q2): Pipeline reproducibility at scale
**Deliverables**
- Reproducible manifests for all stages.
- Stable run_id + artifact registry layout.
- Deterministic quality gates in core pipelines.

**Parallel tasks**
- Data plane: consistent canonicalization + hashing policy.
- Observability: timing/cost aggregation, per-stage summaries.
- Docs: “reproduce a run” guide with minimal example.

### M3 (2026 Q2–Q3): OSS-grade extension ecosystem
**Deliverables**
- Entry-point plugins for new providers and steps.
- Community contribution templates + compatibility test matrix.
- Release cadence with versioning policy.

**Parallel tasks**
- CI: compatibility checks across extras/providers.
- Docs: “write a plugin” guide with YAML-first examples.
- Examples: reference pipelines per provider.

### M4 (2026 Q3+): Performance + governance
**Deliverables**
- Cost-aware scheduling + dynamic budgets.
- Governance docs: RFC process, deprecations, security policy.

**Parallel tasks**
- Runtime: adaptive batching + load-shedding policies.
- Observability: budget dashboards + alerts.

## Definition of done (per milestone)
- Docs updated (EN + ZH when applicable).
- Unit tests for new logic.
- Full lint + test suite green.
- Clear migration notes for API changes.

## Immediate next slice (current execution)
1. Ship the registry foundation with entry-point discovery.
2. Update component export to use the registry.
3. Add unit tests for registry + collisions.
