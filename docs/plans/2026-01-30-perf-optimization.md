# Performance Optimization: Pipeline Orchestration

**Created:** 2026-01-30
**Status:** Complete
**Commits:** 12

## Phase 1: Hot Path Algorithm Fixes (6 items)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1.1 | `add_batch` bisect.insort | Done | `9d829d9` |
| 1.2 | orjson data hash | Done | `8c1256e` |
| 1.3 | Filter vs pop in `_get_data_normal` | Done | `87e2ff9` |
| 1.4 | `built_batches` deque | Done | `a296a0a` |
| 1.5 | Shallow batch copy | Done | `cb1d801` |
| 1.6 | orjson `flatten_dict` | Done | `90f53df` |

## Phase 2: I/O and Serialization (3 items)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 2.1 | WriteBuffer schema-aware close | Done | `81c3908` |
| 2.2 | Proactive flatten detection | Done | `91bd357` |
| 2.3 | Remove `validate_assignment=True` | Done | `8ba0f45` |

## Phase 3: Low Priority (3 items)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 3.1 | threading.Condition for stage polling | Done | `16454eb` |
| 3.2 | Cache `_group_batches_by_created_from` | Done | `67d930d` |
| 3.3 | orjson in distiset | Done | `c9cb827` |

## Notes

- 1.2: Full lazy hash deferred because tests directly access `data_hash` field. Applied orjson.dumps for the serialization speedup instead.
- All 655 unit tests pass. Lint clean.
