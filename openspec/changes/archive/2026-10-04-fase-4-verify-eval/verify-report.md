```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:efdf4f9255a7d2653ff49480f279f017301fb6a64a7d83cb3297eafaf01de669
verdict: pass
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 19/19
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:efdf4f9255a7d2653ff49480f279f017301fb6a64a7d83cb3297eafaf01de669
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-4-verify-eval
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (7783 bytes, Windows CRLF). `build_command` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\fase4-pytest-out.bin`. The preimage is not this markdown file.

Counted from the two change specs (`verify-eval`, `gold-regression`), matching Engram `sdd/fase-4-verify-eval/spec` (#1046): **9 requirements, 19 scenarios**.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 4 |
| Tasks complete | 4 |
| Tasks incomplete | 0 |

All four checkboxes in `tasks.md` are `[x]` (1.1, 1.2, 2.1, 2.2). Full suite was allowed to run.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 236 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
collected 236 items

tests\eval\test_measure.py ............                                  [  5%]
tests\graph\test_conflict.py .....                                       [  7%]
tests\graph\test_fold.py .....                                           [  9%]
tests\graph\test_period.py ............                                  [ 14%]
tests\graph\test_store.py ....                                           [ 16%]
tests\ingest\test_classify.py ................                           [ 22%]
tests\ingest\test_extract.py ................                            [ 29%]
tests\ingest\test_gold_compare.py ...............                        [ 36%]
tests\ingest\test_store.py ..........                                    [ 40%]
tests\retrieval\test_drawers.py .......                                  [ 43%]
tests\retrieval\test_read.py ...                                         [ 44%]
tests\test_gold_v1.py ...........                                        [ 49%]
tests\test_gold_v2.py ...........                                        [ 53%]
tests\test_identity.py ...........................................       [ 72%]
tests\test_ledger.py ........                                            [ 75%]
tests\test_lookup.py ..........................................          [ 93%]
tests\test_query.py ................                                     [100%]

====================== 236 passed, 73 warnings in 17.64s ======================
```

**Coverage**: eval package statement coverage 100% (10/10). Config threshold is 0. No changed production file is under 80% line coverage.

A second command, `python -m pytest tests/ --cov=claimledger.eval --cov-branch --cov-report=term-missing`, also exited 0 (236 passed, 73 warnings, 24.80s). That run is not the hashed preimage.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Sibling Caller | Outside kernel and retrieve | `tests/eval/test_measure.py > test_slice2_eval_outside_allowlist`; `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist` (kernel import delta loads no `llama_index`) | ✅ COMPLIANT |
| Sibling Caller | No upsert and no verified candidate | `tests/eval/test_measure.py > test_slice1_no_upsert_and_not_verified`, `test_slice1_retrieve_query_count_stays_zero` | ✅ COMPLIANT |
| Call Order | Retrieve, then understand, then query | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors` | ✅ COMPLIANT |
| Call Order | Question does not drop a row | `tests/eval/test_measure.py > test_slice1_consolidated_21262335`, `test_slice1_parent_21259769`, `test_slice2_empty_question_keeps_both_rows` | ✅ COMPLIANT |
| Call Order | Identity is not parsed from candidate text | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors` (`understand` receives only the question; `query` receives that intent) and `test_slice1_consolidated_21262335` | ✅ COMPLIANT |
| Neighbor Measure | Consolidated verifies 21262335 | `tests/eval/test_measure.py > test_slice1_consolidated_21262335` | ✅ COMPLIANT |
| Neighbor Measure | Parent verifies 21259769 | `tests/eval/test_measure.py > test_slice1_parent_21259769` | ✅ COMPLIANT |
| Abstain Beside a Gold Number | No-extract sources abstain beside 21262335 | `tests/eval/test_measure.py > test_slice2_recipe_no_extract_abstains` | ✅ COMPLIANT |
| Compare Without Subtraction | Compare stays two claims | `tests/eval/test_measure.py > test_slice2_compare_two_claims` | ✅ COMPLIANT |
| One Tables Drawer | Narrative is not a number source | `tests/eval/test_measure.py > test_slice2_narrative_not_number_source` | ✅ COMPLIANT |
| Row Text Plus Identity | Shared ref does not select | `tests/eval/test_measure.py > test_slice2_shared_ref_does_not_select` | ✅ COMPLIANT |
| No Rank Metric | Both rows without a rank | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors`, `test_slice1_no_upsert_and_not_verified` (candidate fields are `drawer`, `text`, `ref`; return is the two-value pair) | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_identity.py > test_ingest_and_kernel_tests_omit_llama_index`, `test_retrieval_init_outside_kernel_allowlist`, `test_pins_declared_but_unused`; `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused`, `test_kernel_modules_importable`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph`; `tests/graph/test_store.py > test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out`; `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Kernel absence ignores a later graph load | `tests/test_identity.py > test_kernel_modules_importable`. Same-process suite loaded `docling-graph` from `tests/graph/` and the kernel tests still passed | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Retrieval off the snapshot | `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist`. Retrieval tests import `llama_index` in the same process; the kernel delta stays empty. Allowlist length stays 13 | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Eval stays off the scan | `tests/eval/test_measure.py > test_slice2_eval_outside_allowlist`; `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Gold harness stays on seed | `tests/eval/test_measure.py > test_slice2_gold_files_not_edited`; `tests/test_gold_v1.py > test_gold_v1_has_exactly_45_cases`, `test_harness_runs_non_skip_cases_and_skips_narrative`; `tests/test_gold_v2.py > test_gold_v2_has_exactly_26_cases`, `test_harness_runs_all_26_cases`, `test_v2_id_04_keeps_minus_sign_and_aliased_identity`, `test_frozen_numbers_are_intact` | ✅ COMPLIANT |

**Compliance summary**: 19/19 scenarios compliant

Gold numbers stayed frozen. `src/claimledger/ledger.py` still seeds `21262335`, `21259769`, and `-14950948`. `press_v1` and `presentation_v1` stay absent. Kernel tests do not import `llama_index` or `docling`. `tests/eval/test_measure.py` does not import either library. It stubs `read_hashed_json` and forbids PDF conversion and `urlopen`.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Sibling Caller | ✅ Implemented | `measure` lives in `src/claimledger/eval/measure.py`. `eval/__init__.py` is a docstring only, with no re-export. No upsert and no `verified` field on `Candidate`. `retrieve` is not given a call to `query`. |
| Call Order | ✅ Implemented | Body order is `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query(intent, Ledger.seed())`. The question is passed through. `understand` does not receive candidate text. |
| Neighbor Measure | ✅ Implemented | Consolidated and parent questions keep both row texts. Verified values are `21262335` and `21259769`. `ledger_status` stays `recorded`. |
| Abstain Beside a Gold Number | ✅ Implemented | Memoria, comunicado, deck, and contrato questions return `abstained` / `recipe_no_extract` with empty claims while a tables row still contains `21262335`. |
| Compare Without Subtraction | ✅ Implemented | Compare returns `21262335` and `81956525`. The absolute difference is absent from the claim values. |
| One Tables Drawer | ✅ Implemented | One `retrieve` call uses the literal `"tables"`. Narrative text is not a candidate and is not the verified value. |
| Row Text Plus Identity | ✅ Implemented | Both neighbors share `#/tables/1`. The verified value follows the question identity. |
| No Rank Metric | ✅ Implemented | `measure` returns `(candidates, result)` only. `Candidate` fields stay `drawer`, `text`, `ref`. No Recall@k, MRR, rank score, or new import. |
| Docling-Free Pytest Demo | ✅ Implemented | `claimledger.eval` is outside `KERNEL_MODULES` and the 13-path allowlist. `FORBIDDEN_IMPORT_ROOTS` stays `docling` and `docling_graph`. Gold v1 (45) and v2 (26) still call `query(understand(question), Ledger.seed())`. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| `measure` in `eval/measure.py` returns `(candidates, result)` | ✅ Yes | Signature and body match the design contract. |
| Reject `candidates` on `query` | ✅ Yes | `query.py` still takes `intent` and `ledger` only. It does not import retrieval. |
| Reject choice, `verified`, or upsert inside `retrieve` | ✅ Yes | `drawers.py` was not edited. Spy shows `query` calls inside `retrieve` stay 0. Upserts stay at the 14 seed rows. |
| Reject ranker, Recall@k, MRR, or a new library | ✅ Yes | No rank symbol and no new dependency in `measure.py` or `pyproject.toml`. |
| Reject pointing gold at Docling JSON | ✅ Yes | Gold files still call `Ledger.seed()` and do not call `retrieve`. |
| `eval/__init__.py` docstring only | ✅ Yes | No re-export. `src/claimledger/__init__.py` stays empty of this caller. |
| Stubbed reader; no PDF, network, or Docker | ✅ Yes | Tests write tmp JSON and monkeypatch `read_hashed_json`. IO counters for convert and `urlopen` stay 0. |
| Unit only; integration and E2E out of this change | ✅ Yes | Twelve unit tests in `tests/eval/test_measure.py`. |
| Canonical `openspec/specs/gold-regression/spec.md` | ✅ Deferred | Tasks say apply must not edit `openspec/specs/` until archive. The Fase 4 delta (eval off the 13-path scan; gold must not point at Docling JSON or `llama_index`) lives in the change spec. The working-tree canonical file still stops the exclusion list at `retrieval/`. Archive copies that delta. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram `sdd/fase-4-verify-eval/apply-progress` (#1049) has a TDD Cycle Evidence table for tasks 1.1–1.2 and 2.1–2.2. |
| All tasks have tests | ✅ | 4/4. File exists: `tests/eval/test_measure.py` (12 tests). |
| RED confirmed (tests exist) | ✅ | Unit 1 RED is real: `ModuleNotFoundError: No module named 'claimledger.eval'` (ImportError), 5 failed, before `measure` existed. Unit 2 tests were written first and passed on the first run (7 passed, 5 deselected) because Unit 1 `measure` already satisfied them. Apply-progress records failed nodes: none, and records that production was not edited to force a failure. Task 2.1 requires that outcome when a node is already true. That first-run pass is accepted evidence, not a missing RED. |
| GREEN confirmed (tests pass) | ✅ | This run: 236 passed, exit 0. `tests/eval/test_measure.py`: 12 passed. |
| Triangulation adequate | ✅ | Slice 1: five cases (order, consolidated `21262335`, parent `21259769`, no upsert, query spy). Slice 2: seven cases (four `recipe_no_extract` questions, compare pair, narrative exclusion, empty question, shared ref, gold seal, allowlist seal). Expected values differ across verified, abstained, and two-claim results. |
| Safety Net for modified files | ✅ | Unit 1 files were new (`N/A (new)`). Unit 2 records `pytest tests/eval/test_measure.py -k slice1` → 5 passed before the slice-2 nodes. `measure.py` was not edited in Unit 2. |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 12 | 1 | pytest (`tests/eval/test_measure.py`) |
| Integration | 0 | 0 | not installed |
| E2E | 0 | 0 | not installed |
| **Total** | **12** | **1** | |

Counts are the tests this change added. Capabilities list integration and E2E as not detected. Design marks both as out of this change. Drawer reading is stubbed; gold and identity seals read source or run the in-memory kernel.

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/eval/__init__.py` | 100% (0/0) | 0 branches | — | ✅ Excellent |
| `src/claimledger/eval/measure.py` | 100% (10/10) | 0 branches | — | ✅ Excellent |

**Average changed-file statement coverage**: 100% (10/10 statements). Uncovered statements in changed production files: 0.

`tests/eval/test_measure.py` is not in the coverage filter.

### Assertion Quality
**Assertion quality**: ✅ All assertions verify real behavior

0 CRITICAL, 0 WARNING. No `assert True` tautologies. Slice tests call `measure` and assert call order, both neighbor texts, frozen values `21262335` and `21259769`, `ledger_status == "recorded"`, upsert count 14, `query` inside `retrieve` equal to 0, abstain reason `recipe_no_extract` with empty claims, compare values without their difference, one `"tables"` retrieve, narrative text absent, empty question keeping both rows, and shared `#/tables/1` not selecting the value. The abstain empty-claims check sits next to tests that require non-empty verified claims. Loops over candidates are preceded by `len(candidates) == 2` or by `_assert_both_neighbors`. `RECIPE_QUESTIONS` is a four-item constant, so those assertions run. Gold and allowlist tests parse real source and assert `Ledger.seed()`, no `retrieve` call, `-14950948`, a 13-path allowlist, and `claimledger.eval` absent from `KERNEL_MODULES`.

### Quality Metrics
**Linter**: ➖ Not available (config quality.linter is `not_detected`)
**Type Checker**: ➖ Not available (config quality.type_checker is `not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: None

**SUGGESTION**: Archive still has to copy the gold-regression delta into `openspec/specs/gold-regression/spec.md`. Tasks keep that copy out of apply. The canonical file does not yet say `eval/` stays outside the 13-path scan.

### Verdict
PASS

19/19 scenarios have a covering test that passed in `python -m pytest tests/` (exit 0, 236 passed, 0 failed). Unit 1 had a real ImportError RED (5 failed) before `measure` was written. Unit 2's seven tests passed on first run against that function; that pass is recorded and matches task 2.1. Gold numbers were not relaxed. Kernel tests did not import `llama_index` or `docling`.
