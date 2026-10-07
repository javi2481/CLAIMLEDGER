# Proposal: Ground the product ledger in the two quarterly statements

## Intent

Rector §23: the book exists before the question, fed by evidence, and points at the hashed Docling artifact. Product paths still judge `Ledger.seed()`, fourteen literals with empty evidence. The gap: no pinned API turns two hashed quarterly statements into a financial ledger. Docling parses. `extract_recipe` maps the recipe. `Ledger.upsert` records. The missing join is that book.

## Scope

### In Scope

- One function in `src/claimledger/ingest/` builds an in-memory `Ledger` from the two quarterly EEFF in `docs/archivos_muestra`: `load_or_convert`, `classify`, `extract_recipe`, `upsert`. No disk cache of claims.
- `reply`, `measure`, and `POST /claims/query` pass that book to `query`. They MUST NOT call `Ledger.seed()`.
- The screen `artifact_hash` stays the source of table candidates and the page crop. A comunicado does not replace the book. `recipe_no_extract` still comes from `understand`.
- A missing quarterly file raises `IngestError`. No fallback to the seed.
- `load` and a cache hit recompute the SHA-256 of the stored bytes and reject a mismatch. A mismatch MUST NOT trigger a reconvert.
- Kernel gold stays `Ledger.seed()`. `21262335` and `21259769` stay frozen. `query` stays unchanged.

### Out of Scope

- A Neo4j server or driver. A disk cache of claims. A second observed-value branch on a conflict. Phase 10. Relaxing gold. An LLM choosing the number.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `docling-ingest`: `load` and cache hit verify the artifact hash. A new requirement builds the in-memory quarterly book.
- `verify-eval`: `measure` queries the ledger it is given, or the quarterly book when none is given. It MUST NOT call `Ledger.seed()`.
- `http-query`: the route queries the quarterly book. `claims_query` on `Ledger.seed()` still returns `evidence: []`.
- `openwebui-host`: one completion builds the quarterly book once and passes it to `execute`, `ask`, and `measure`.

`gold-regression`, `query`, `ledger`, `book`, and `orchestrate` stay. Callers of `ask` and `execute` may pass the quarterly book; those functions still accept a `Ledger` and do not build one.

## Approach

The book is built per question, in memory, outside the seven kernel modules. `claims_query`, `execute`, and `ask` stay pure. Tests that must not open a PDF pass `Ledger.seed()` or stub the book function. One ingest test builds the real book from the corpus.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `ingest/ground.py` | New | Quarterly book |
| `eval/measure.py` | Modified | Queries the given ledger |
| `openwebui/reply.py` | Modified | One book per completion |
| `http/app.py` | Modified | Route uses the book |
| `ingest/store.py` | Modified | Hash check on load |
| Kernel `ledger.py`, `query.py`, gold tests | Unchanged | Seed remains the oracle |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Extract disagrees with gold | Low | Existing compare test; conflict abstains |
| Host tests start opening PDFs | Med | Stub the book; one corpus test |
| Tampered JSON reconverted | Low | Mismatch raises; convert is not called |
| Torch import on every question | Med | Acceptable; no claim cache on disk |

## Rollback Plan

Delete `ingest/ground.py` and its tests. Restore `Ledger.seed()` in `measure`, `reply`, and `http/app.py`. Restore `load` without the hash check. Revert the four deltas. Kernel seed and gold stay. No migration.

## Dependencies

- Archived phases 0–9 and 11–13. Phase 10 stays deferred.

## Success Criteria

- [x] A product question verifies `21262335` from the quarterly book, with evidence, and `Ledger.seed()` is not called on that path.
- [x] `claims_query` on `Ledger.seed()` still returns `evidence: []`.
- [x] A mismatched artifact hash is rejected and not reconverted.
- [x] Kernel tests still call `query` on `Ledger.seed()` and do not import `docling`.
