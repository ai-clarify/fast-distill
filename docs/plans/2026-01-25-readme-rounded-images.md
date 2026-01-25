# Plan: README image rounded corners

Date: 2026-01-25

## Context
- README images use inline CSS for rounded corners, but GitHub strips styles.
- Goal: bake rounded corners into the actual PNG assets used in the README.

## Plan
1. Inspect README + assets to confirm target images and current sizes.
2. Apply rounded-corner alpha masks to the relevant PNGs (icon + architecture).
3. Validate updated assets (size, alpha) and update plan progress.
4. Run full lint + unit + integration tests.
5. Commit changes with a concise message.

## Progress
- [x] Reviewed engineering practices in `docs/ENGINEERING_PRACTICES.md`.
- [x] Located README image references and assets.
- [x] Applied rounded-corner masks to README assets.
- [x] Validated asset outputs.
- [x] Ran lint + tests.
- [ ] Committed changes.
