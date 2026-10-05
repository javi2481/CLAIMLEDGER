# Tasks: Fase 4 Verify Eval

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 220–320 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR, two TDD units |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | `measure` returns `(candidates, result)` via tables `retrieve`, `understand`, then `query(Ledger.seed())` | Single PR | `pytest tests/eval/test_measure.py -k slice1` | N/A — tmp JSON stub; no PDF, network, or Docker | Delete `src/claimledger/eval/` and `tests/eval/` |
| 2 | Abstain, compare, narrative, empty question, shared ref, gold and allowlist seals | Single PR | `pytest tests/eval/test_measure.py -k slice2` | N/A — same stub; gold files are only read | Revert slice-2 tests; do not delete gold |

## Phase 1: Caller join (Unit 1)

- [x] 1.1 RED: Add `tests/eval/test_measure.py`. Stub `read_hashed_json` as in `tests/retrieval/test_drawers.py` (`tmp_path` JSON, `SimpleNamespace` `text` + `metadata.doc_items`). Nodes: `test_slice1_call_order_and_both_neighbors`, `test_slice1_consolidated_21262335`, `test_slice1_parent_21259769`, `test_slice1_no_upsert_and_not_verified`, `test_slice1_retrieve_query_count_stays_zero`. `measure(artifact_hash, question)` returns `(candidates, result)` from `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query` on `Ledger.seed()`. Both neighbor texts present. Consolidated value `21262335` (not `21259769`). Parent value `21259769` (not `21262335`). `ledger_status` is `recorded`. Caller adds no upsert. Candidate is not verified. Spy `query`: calls inside `retrieve` stay 0; the caller calls `query`. Run: `pytest tests/eval/test_measure.py -k slice1`. MUST fail because `measure` is missing (`ImportError` or `AttributeError`). No production code.
- [x] 1.2 GREEN: Add docstring-only `src/claimledger/eval/__init__.py` (no re-export) and `measure` in `src/claimledger/eval/measure.py` with only that order and return. Run: `pytest tests/eval/test_measure.py -k slice1`. MUST pass. Do not edit `query.py`, `lookup.py`, `ledger.py`, `drawers.py`, `read.py`, or `src/claimledger/__init__.py`.

## Phase 2: Abstain, compare, and seals (Unit 2)

- [x] 2.1 RED: Add `test_slice2_recipe_no_extract_abstains`, `test_slice2_compare_two_claims`, `test_slice2_narrative_not_number_source`, `test_slice2_empty_question_keeps_both_rows`, `test_slice2_shared_ref_does_not_select`, `test_slice2_gold_files_not_edited`, `test_slice2_eval_outside_allowlist`. Memoria, comunicado, deck, and contrato `recipe_no_extract` abstain beside a tables candidate that contains `21262335`. Compare “Comparar resultado neto consolidado 1T26 vs 2T26” returns `21262335` and `81956525` with no difference. Narrative text is not a candidate and not the number; one `retrieve(..., "tables", ...)`. Empty question keeps both rows. Shared `#/tables/1` does not select; value follows identity. Read `tests/test_gold_v1.py` and `tests/test_gold_v2.py`: still `Ledger.seed()`, no `retrieve`, including `-14950948`; do not edit them. Read `tests/test_identity.py`: `claimledger.eval` absent from `KERNEL_MODULES` and the 13-path allowlist (`len` stays 13). Do not add `llama_index` to `FORBIDDEN_IMPORT_ROOTS` or widen the 13 paths. Do not edit those files. Run: `pytest tests/eval/test_measure.py -k slice2`. MUST fail with `AssertionError` on a slice-2 case that is not yet true. `ImportError` is the wrong failure. If a node already passes, do not weaken it and do not change production to force a failure.
- [x] 2.2 GREEN: Edit only `src/claimledger/eval/measure.py` if a slice-2 assertion shows a dropped row, narrative as the number, selection by `ref`, or `query` called from `retrieve`. Run: `pytest tests/eval/test_measure.py -k slice2`. MUST pass. Do not edit gold files or `tests/test_identity.py`. Do not edit `openspec/specs/` or relax gold. No ranker or new library.
