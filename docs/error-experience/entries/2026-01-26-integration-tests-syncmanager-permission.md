# 2026-01-26 - Integration tests failed creating `multiprocessing.Manager`

## Context
- Command: `make integration-tests`
- Environment: macOS, local Python 3.11.

## Symptoms
- Many integration tests failed with `PermissionError: [Errno 1] Operation not permitted` when `multiprocessing.Manager()` tried to bind a listener socket.
- Downstream failures surfaced as `EOFError` in pipeline runs and repeated thread exceptions.

## Likely cause
- The environment disallowed the SyncManager server from binding to a local port (sandboxed runtime or OS restriction).

## Impact
- Integration test suite failed early; most pipeline integration coverage did not run.

## Resolution
- Run integration tests in an environment that permits `multiprocessing.Manager` to bind to loopback sockets.
- If running in a restricted sandbox, adjust the execution environment or disable multiprocessing for tests.

## Follow-ups
- Consider adding a test-only switch to run the local pipeline in single-process mode when socket binding is unavailable.
