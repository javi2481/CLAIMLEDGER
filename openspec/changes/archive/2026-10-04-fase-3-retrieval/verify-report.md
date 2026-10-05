```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:3c58c8631f3118b37d84f381e26ceca6ce8d8395d58e9d054a5a64fe327b7c45
verdict: pass
blockers: 0
critical_findings: 0
requirements: 4/4
scenarios: 11/11
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:3c58c8631f3118b37d84f381e26ceca6ce8d8395d58e9d054a5a64fe327b7c45
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-3-retrieval
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (7702 bytes, Windows CRLF). `build_command` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\fase3-pytest-out.bin`. The preimage is not this markdown file.

Counted from the two change specs (`json-retrieval`, `gold-regression`), matching Engram `sdd/fase-3-retrieval/spec` (#1036): **4 requirements, 11 scenarios**.

This run re-verifies after the ingest and kernel-test `llama_index` ban gained covering tests. Those tests passed in this suite.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 5 |
| Tasks complete | 5 |
| Tasks incomplete | 0 |

All five checkboxes in `tasks.md` are `[x]` (1.1, 1.2, 1.3, 2.1, 2.2). Full suite was allowed to run.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 224 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
collected 224 items

tests\graph\test_conflict.py .....                                       [  2%]
tests\graph\test_fold.py .....                                           [  4%]
tests\graph\test_period.py ............                                  [  9%]
tests\graph\test_store.py ....                                           [ 11%]
tests\ingest\test_classify.py ................                           [ 18%]
tests\ingest\test_extract.py ................                            [ 25%]
tests\ingest\test_gold_compare.py ...............                        [ 32%]
tests\ingest\test_store.py ..........                                    [ 37%]
tests\retrieval\test_drawers.py .......                                  [ 40%]
tests\retrieval\test_read.py ...                                         [ 41%]
tests\test_gold_v1.py ...........                                        [ 46%]
tests\test_gold_v2.py ...........                                        [ 51%]
tests\test_identity.py ...........................................       [ 70%]
tests\test_ledger.py ........                                            [ 74%]
tests\test_lookup.py ..........................................          [ 92%]
tests\test_query.py ................                                     [100%]

====================== 224 passed, 73 warnings in 16.85s ======================
```

**Coverage**: retrieval package statement coverage 93.5% (58/62). Config threshold is 0. pytest-cov combined cover for the package is 88%. No changed production file is under 80% line coverage.

A second command, `python -m pytest tests/ --cov=claimledger.retrieval --cov-branch --cov-report=term-missing`, also exited 0 (224 passed, 73 warnings, 24.64s). That run is not the hashed preimage.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Hashed JSON Reader | Stored JSON | `tests/retrieval/test_read.py > test_stored_json_reader_uses_json_export_on_local_path`, `test_second_artifact_is_read_from_its_own_local_json` | ✅ COMPLIANT |
| Hashed JSON Reader | Missing artifact or Markdown default | `tests/retrieval/test_read.py > test_missing_artifact_raises_without_convert_or_url`; stored-JSON tests assert `export_types == ["json"]` against a double whose default is `"markdown"` | ✅ COMPLIANT |
| Two Drawers | Tables exclude narrative | `tests/retrieval/test_drawers.py > test_tables_call_returns_no_narrative_nodes` | ✅ COMPLIANT |
| Two Drawers | Narrative excludes tables | `tests/retrieval/test_drawers.py > test_narrative_call_returns_no_table_nodes` | ✅ COMPLIANT |
| Candidates Only | Candidates only | `tests/retrieval/test_drawers.py > test_candidate_has_no_claim_status` (also `query` and `upsert` stay 0 on the drawer tests) | ✅ COMPLIANT |
| Candidates Only | Both neighbor rows | `tests/retrieval/test_drawers.py > test_both_neighbor_rows_are_table_candidates`, `test_question_does_not_choose_between_neighbor_rows` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_identity.py > test_ingest_and_kernel_tests_omit_llama_index`, `test_retrieval_init_outside_kernel_allowlist`, `test_pins_declared_but_unused`; `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` (`FORBIDDEN_SOURCE_TOKENS` includes `llama_index`) | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused`, `test_kernel_modules_importable`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph`; `tests/graph/test_store.py > test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out`; `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Kernel absence ignores a later graph load | `tests/test_identity.py > test_kernel_modules_importable` (before/after delta). Same-process suite loaded `docling-graph` from `tests/graph/` and the kernel tests still passed | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Retrieval off the snapshot | `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist`. Retrieval tests import `llama_index` in the same process; the kernel delta stays empty. `FORBIDDEN_IMPORT_ROOTS` stays `docling`, `docling_graph`. Allowlist length stays 13 | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios compliant.

"Import scan stays clean" is compliant in this run. `test_ingest_and_kernel_tests_omit_llama_index` parses `src/claimledger/ingest/*.py` and the six named kernel test files and asserts none contain an `Import` or `ImportFrom` of `llama_index`. A missing kernel test file raises while reading, so the six paths are required. `test_ingest_sources_forbid_url_httpsource_and_docling_graph` asserts the six ingest module names and that `llama_index` is absent from their combined source. Kernel modules still fail the scan if they import `docling` or `docling_graph`. `ingest/`, `graph/`, and `retrieval/` stay outside the 13-path allowlist.

Gold numbers stayed frozen. `src/claimledger/ledger.py` still seeds `21262335` and `21259769`. `press_v1` and `presentation_v1` stay absent. `recipe_no_extract` still covers comunicado and deck P&L. Markdown is not the source of truth: `DoclingReader` is constructed with `export_type="json"`. Candidates are frozen `(drawer, text, ref)` and are not `FinancialClaim`. `query` is not called. One call names one drawer.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Hashed JSON Reader | ✅ Implemented | `read_hashed_json` calls `store.load`, then `DoclingReader(export_type="json")` and `DoclingNodeParser` on `artifacts/docling/<hash>.json`. Missing artifacts raise `IngestError` before the reader is constructed. No `load_or_convert`, `convert_pdf`, or URL fetch in `retrieval/`. |
| Two Drawers | ✅ Implemented | `retrieve` accepts one of `tables` or `narrative`. A table label is `"table"`; every other label stays narrative. Naming both, or an unknown drawer, raises `ValueError` before the reader runs. |
| Candidates Only | ✅ Implemented | `Candidate` is frozen with `drawer`, `text`, `ref`. No `verified`, `abstained`, or ledger write. `question` is accepted and does not drop a row. `query.py` does not import retrieval. |
| Docling-Free Pytest Demo | ✅ Implemented | Kernel import does not load `llama_index`. Ingest sources and the six kernel tests omit `llama_index`, and both bans are asserted by tests that passed. Retrieval may import it, and it does so only inside `_nodes_from_hashed_json`. Pins `docling==2.130.0` and `docling-graph==1.9.1` are unchanged. Numeric gold was not relaxed. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Sibling `retrieval/` plus `tests/retrieval/` | ✅ Yes | Off the 13-path scan. Not placed in `ingest/` or `query.py`. |
| `DoclingReader(export_type="json")` then `DoclingNodeParser` | ✅ Yes | Lazy import inside `_nodes_from_hashed_json`. Markdown is not the source of truth. |
| One drawer per call; mix raises | ✅ Yes | `_one_drawer` rejects any value outside `tables` and `narrative`, including a pair. |
| Candidates only; kernel still judges | ✅ Yes | No `verified` / `abstained`. `query.py` is unchanged and is not called. |
| Lazy import; `FORBIDDEN_IMPORT_ROOTS` unchanged | ✅ Yes | Roots stay `docling`, `docling_graph`. Retrieval `__init__.py` does not import `llama_index`. |
| Pins recorded at apply, compatible with `docling==2.130.0` | ✅ Yes | Extra `retrieval` pins `llama-index-readers-docling==0.5.0` and `llama-index-node-parser-docling==0.5.0`. Existing docling pins were not bumped. |
| `query.py`, `ingest/`, and kernel `__init__.py` unchanged | ✅ Yes | Ingest still has six modules. The coverage fix added tests; it did not add an ingest module or a `llama_index` import there. |
| Canonical `openspec/specs/gold-regression/spec.md` | ✅ Deferred | Tasks say apply must not edit `openspec/specs/` until archive. The Fase 3 delta lives in the change spec. The working-tree canonical file still has no `retrieval/` or `llama_index` sentence. Archive copies that delta. |
| Unit tests, fixture JSON, no PDF, no network | ✅ Yes | Reader tests double `DoclingReader` and `DoclingNodeParser`. Drawer tests stub `read_hashed_json` with parsed nodes. E2E stays out of scope. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram `sdd/fase-3-retrieval/apply-progress` (#1038) has a TDD Cycle Evidence table for tasks 1.1, 1.2, 1.3, 2.1, and 2.2. |
| All tasks have tests | ✅ | 5/5. Files exist: `tests/retrieval/test_read.py`, `tests/test_identity.py`, `tests/retrieval/test_drawers.py`. |
| RED confirmed (tests exist) | ✅ | 5/5 rows record a pre-production failure (`ModuleNotFoundError` or a missing retrieval init). Those test files exist now. The later coverage test `test_ingest_and_kernel_tests_omit_llama_index` also exists. |
| GREEN confirmed (tests pass) | ✅ | This run: 224 passed, exit 0. Reader file: 3 passed. Drawer file: 7 passed. Identity file: 43 passed, including `test_retrieval_init_outside_kernel_allowlist` and `test_ingest_and_kernel_tests_omit_llama_index`. Ingest store file: 10 passed, including the forbid test whose token list now contains `llama_index`. |
| Triangulation adequate | ✅ | Reader: two artifact hashes plus a missing artifact (3 tests, 2 scenarios). Drawers: neighbor pair, a second artifact, and three questions that return the same two table rows (7 tests, 4 scenarios). Import ban: kernel runtime snapshot, 13-path placement, AST scan of ingest plus six kernel tests, and the ingest source-token scan. |
| Safety Net for modified files | ✅ | `test_read.py` and `test_drawers.py` are new. Task 1.2 records 41 passed before editing `tests/test_identity.py`. `drawers.py` and `read.py` are new production files. |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 12 | 3 | pytest (`test_read.py` 3, `test_drawers.py` 7, identity retrieval/import-ban tests 2) |
| Integration | 0 | 0 | not installed |
| E2E | 0 | 0 | not installed |
| **Total** | **12** | **3** | |

Counts are the tests this change added. `tests/ingest/test_store.py` was extended in place: `FORBIDDEN_SOURCE_TOKENS` now includes `llama_index` inside the existing forbid test, which passed. `tests/test_identity.py` now has 43 tests; the other identity cases passed in the same process. Drawer tests stub the reader. Reader tests double LlamaIndex. Capabilities list integration and E2E as not detected. Design testing strategy marks E2E as N/A until Fase 4 wires `query`.

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/retrieval/__init__.py` | 100% (0/0) | 0 branches | — | ✅ Excellent |
| `src/claimledger/retrieval/read.py` | 100% (15/15) | 0 branches | — | ✅ Excellent |
| `src/claimledger/retrieval/drawers.py` | 91.5% (43/47) | 14 branches, 5 partial; tool cover 85% | 43, 46, 53, 71, arc 69→67 | ⚠️ Acceptable |

**Average changed-file statement coverage**: 93.5% (58/62 statements). pytest-cov combined total: 88%. Uncovered statements in changed production files: 4. No changed file is under 80%.

`tests/test_identity.py`, `tests/ingest/test_store.py`, `tests/retrieval/`, and `pyproject.toml` are not in the coverage filter. Uncovered drawer lines are defensive: metadata that is not a dict, `doc_items` that is not a list, a non-dict doc item, and a missing `self_ref`.

### Assertion Quality
**Assertion quality**: ✅ All assertions verify real behavior

0 CRITICAL, 0 WARNING. No `assert True` tautologies. Reader tests call `read_hashed_json` and assert JSON export, the local hashed path, parser input, and zero calls to `load_or_convert`, `convert_pdf`, and `urlopen`. Drawer tests call `retrieve` and assert distinct neighbor texts, drawer names, refs, a frozen `Candidate` field list, and that `query` and `upsert` stay at 0. The empty reader-not-called check sits next to tests that require a non-empty read. `test_ingest_and_kernel_tests_omit_llama_index` asserts an empty offender list after parsing real ingest and kernel-test sources; the companion ingest test asserts the six module names are present and then rejects `llama_index`. `question` variance returns the same two rows.

### Quality Metrics
**Linter**: ➖ Not available (config quality.linter is `not_detected`)
**Type Checker**: ➖ Not available (config quality.type_checker is `not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: None

**SUGGESTION**: No test calls `retrieve` through the real `DoclingReader`. Drawer tests stub `read_hashed_json`. Reader tests double the library. Design marks that E2E seam as Fase 4. Archive still has to copy the gold-regression delta into `openspec/specs/gold-regression/spec.md`; tasks keep that copy out of apply.

### Verdict
PASS

11/11 scenarios have a covering test that passed in `python -m pytest tests/` (exit 0, 224 passed, 0 failed). The previous partial on "Import scan stays clean" is closed: ingest and the six named kernel tests are asserted free of `llama_index`. No critical finding. Gold numbers were not relaxed.
