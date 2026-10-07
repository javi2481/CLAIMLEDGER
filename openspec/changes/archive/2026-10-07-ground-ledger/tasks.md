# Tasks: Ground the product ledger

## Review Workload Forecast

Estimated changed lines for apply: ~400 (code ~120, tests ~280). SDD artifacts sit beside that. Risk against the 400-line review budget: Medium. Two slices. Slice A is the book and the three callers. Slice B is the hash check.

Delivery strategy: sequential slices on the current branch. Slice B starts after slice A is green.

Decision needed before apply: No
Chained PRs recommended: No
**Apply MUST NOT commit and MUST NOT open a PR unless the user asks.** Phase 10 stays unopened. No Neo4j driver.

### Closed bounds (apply MUST NOT touch)

`query.py`, `ledger.py` `RECIPE_ROWS`, gold files, `evals/`, the 13-path allowlist, `book/ask.py`, `orchestrate/plan.py`, `http/claims.py`. Kernel tests keep `Ledger.seed()`. No disk claim cache. No conflict-model reshape.

## Slice A: Quarterly book

- [x] 1.1 RED: `tests/eval/test_measure.py` passes an explicit ledger into `measure` and asserts `query` receives that object and `measure.py` does not call `Ledger.seed()`. Pytest MUST fail with `TypeError` until `measure` accepts the ledger.
- [x] 1.2 GREEN: `measure` queries the passed ledger. Existing eval calls pass `Ledger.seed()` so they stay off PDF. A call with no ledger uses `recorded_book`.
- [x] 1.3 RED: `tests/ingest/test_ground.py` imports `recorded_book`. On the corpus it returns the fourteen `RECIPE_ROWS` values, each with evidence, and `query` verifies `21262335`. A missing file raises `IngestError`. Pytest MUST fail with `ImportError` before `ground.py` exists.
- [x] 1.4 GREEN: `recorded_book` in `ingest/ground.py`. No claim file written beside the JSON.
- [x] 1.5 `reply` calls `recorded_book` once and passes that ledger to `execute`, `ask`, and `measure`. It does not call `Ledger.seed()`. Host tests stub the book.
- [x] 1.6 `build_app` passes `recorded_book()` to `claims_query`. `claims_query` on `Ledger.seed()` still returns `evidence: []`. A stub book with evidence is forwarded by the route.

## Slice B: Hash check

- [x] 2.1 RED: `load` of a file whose bytes do not hash to the requested name raises `IngestError`. A cache hit on a mismatched file raises and does not call `convert_pdf`.
- [x] 2.2 GREEN: `load` and the cache hit in `load_or_convert` compare SHA-256 of the file bytes to the hash.
