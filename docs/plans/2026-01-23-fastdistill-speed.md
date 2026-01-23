# FastDistill speed optimization plan (2026-01-23)

## Scope
Reduce pipeline latency and unnecessary work by adding streaming filters/dedup and removing avoidable global-stage barriers in examples.

## Steps
- [x] Add a streaming dedup step to drop duplicates before teacher generation.
- [x] Add a streaming boolean filter to avoid GlobalStep barriers for simple selects.
- [x] Wire the new steps into the e2e example; make load_groups configurable.
- [x] Update docs to reflect the new speed levers.
- [x] Add unit tests for new steps and run fastdistill test suite.

## Notes
- Keep config references YAML-only.
- Prefer streaming steps unless full-dataset context is required.
