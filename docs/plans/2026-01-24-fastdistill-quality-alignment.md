# FastDistill quality alignment focus (2026-01-24)

## Scope
Make teacher-student score alignment measurable in the Text2SQL pipeline and
expose metrics that show how close student scores are to teacher scores.

## Steps
- [x] Add a score agreement report step (MAE, RMSE, agreement@eps, correlations).
- [x] Wire the agreement report into the Text2SQL e2e pipeline.
- [x] Add docs for quality alignment metrics (EN + ZH) and link from README.
- [x] Add unit tests for the agreement report step.
- [x] Commit + push.
