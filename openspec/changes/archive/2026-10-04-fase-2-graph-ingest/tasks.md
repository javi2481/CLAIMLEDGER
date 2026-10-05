# Tasks: Fase 2 Graph Ingest

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 400–600 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR1 snapshot → PR2 fold → PR3 conflict/store |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Skeleton plus seven-import snapshot; 13-path allowlist unchanged | `fase-2-graph-import-snapshot`, base `fase-0-kernel` | `pytest tests/test_identity.py` | N/A — import snapshot, no PDF | Restore absolute `sys.modules` asserts; delete `src/claimledger/graph/`; revert graph `.gitignore` line |
| 2 | Shared period IDs; memoria off quarters; transcript may link; non-EEFF period stays `None` | `fase-2-graph-period-fold`, base unit 1 | `pytest tests/graph/test_fold.py tests/graph/test_period.py` | N/A — no PDF or network | Delete `schema.py`, `link.py`, `test_fold.py`, `test_period.py` |
| 3 | Node conflict, one write, recorded doubt; no LLM, `run_pipeline`, or P&L | `fase-2-graph-conflict-store`, base unit 2 | `pytest tests/graph/test_conflict.py tests/graph/test_store.py` | N/A — local `artifacts/graph/graph.json`; no PDF or query | Delete `build.py`, those two tests, `artifacts/graph/`; drop `build`/`load` exports |

## Phase 1: Import Snapshot (Unit 1)

- [x] 1.1 RED: In `test_kernel_modules_importable`, pre-seed `sys.modules` with `docling` and `docling_graph`, then import the seven `KERNEL_MODULES`. Leave the absolute asserts. MUST fail on `assert "docling" not in sys.modules`.
- [x] 1.2 GREEN: Keep the pre-seed. Assert only the before/after delta. Leave `_kernel_scan_paths` and the same 13 paths in `tests/test_gold_v1.py` and `tests/test_gold_v2.py`.
- [x] 1.3 RED: Assert `src/claimledger/graph/__init__.py` exists and its AST imports neither `docling` nor `docling_graph`, outside the allowlist. MUST fail: file missing.
- [x] 1.4 GREEN: Add that module with no top-level `docling_graph`. Ignore `artifacts/graph/*.json`. Do not edit `tests/ingest/test_store.py` or `src/claimledger/ingest/`.

## Phase 2: Period Fold (Unit 2)

- [x] 2.1 RED: Add `tests/graph/test_fold.py` and `tests/graph/test_period.py`. Same-period EEFF, comunicado, and deck share `BYMA`, `2026-03-31` or `2026-06-30`, `income_statement`, and id `artifact_hash`. No `FinancialClaim` or `extract_recipe`. Year-end memoria has no quarterly Period. Transcript may link `2026-06-30` with no claim. Non-EEFF `classify.period` stays `None`. MUST fail: no `schema` or `link`.
- [x] 2.2 GREEN: Add `schema.py` (four entities; edges `ISSUED_BY`, `FOR_PERIOD`, `OF_STATEMENT`) and `link.py`. EEFF uses `DocumentClass.period`. Else pass separator-split tokens to `normalize_period`, not the raw filename. Leave `identity.py` and `classify.py` unchanged. No `doubt` yet.

## Phase 3: Conflict and Single Write (Unit 3)

- [x] 3.1 RED: Add `tests/graph/test_conflict.py` and `tests/graph/test_store.py`. A clash stays on `__conflicts__` and MUST NOT set `ledger_status` to `conflicted`. Unknown alias sets Document `doubt` with no LLM. `build` writes `artifacts/graph/graph.json` once; `load` does not rebuild. Forbid `run_pipeline`, LLM/VLM, `ProvenanceBinder`, Neo4j, and P&L. MUST fail: no `build`.
- [x] 3.2 GREEN: Add `build.py`: lazy pin `docling-graph==1.9.1`, `GraphConverter(alias_llm_fn=None)`, `GraphMerger(MergePolicy(conflicts="keep-all", export_format=None))`, local `JSONExporter`, provenance `document_id=artifact_hash`. `ValueError` sets `doubt` and mints no period id. Export `build` and `load` with no top-level `docling_graph`. Leave `claimledger.query` unchanged.

Apply MUST NOT edit `openspec/specs/`. Delta stays in this folder until archive. Do not bump pins or relax gold.
