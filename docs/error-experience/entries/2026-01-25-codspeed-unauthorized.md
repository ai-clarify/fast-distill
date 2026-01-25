# 2026-01-25 - CodSpeed benchmarks failed with 401 unauthorized

## Context
- Workflow: `.github/workflows/codspeed.yml` (Benchmarks)
- Runner: `CodSpeedHQ/action@v3`

## Symptoms
- CI error: `Failed to retrieve upload data: 401 Unauthorized`.
- Message: `Repository not found or you do not have access to it.`

## Likely cause
- `CODSPEED_TOKEN` secret missing or the repo is not authorized in CodSpeed (fork PRs do not receive secrets).

## Impact
- Benchmarks job failed even though tests ran locally.

## Resolution
- Replaced CodSpeed with pytest-benchmark + artifact upload to remove the external token dependency.

## Follow-ups
- If CodSpeed is desired again, ensure repository authorization and `CODSPEED_TOKEN` in repo secrets.
