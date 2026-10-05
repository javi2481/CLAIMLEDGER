```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:97c119500a16e0645ed2a9af99b775888c95243b21f5ed3739f83cd57f309cd8
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 7/7
scenarios: 11/11
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:97c119500a16e0645ed2a9af99b775888c95243b21f5ed3739f83cd57f309cd8
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-1-docling-adapter
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (1344 bytes). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 10 |
| Tasks complete | 10 |
| Tasks incomplete | 0 |

All ten checkboxes in `tasks.md` are `[x]` (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.2). Full suite was allowed to run.

Counted from the three change specs, not invented: **7 requirements, 11 scenarios**.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 184 passed / 0 failed / 0 skipped
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
collected 184 items

tests\ingest\test_classify.py ................                           [  8%]
tests\ingest\test_extract.py ................                            [ 17%]
tests\ingest\test_gold_compare.py ...............                        [ 25%]
tests\ingest\test_store.py .........                                     [ 30%]
tests\test_gold_v1.py ...........                                        [ 36%]
tests\test_gold_v2.py ...........                                        [ 42%]
tests\test_identity.py ........................................          [ 64%]
tests\test_ledger.py ........                                            [ 68%]
tests\test_lookup.py ..........................................          [ 91%]
tests\test_query.py ................                                     [100%]

============================= 184 passed in 1.24s =============================
```

Ingest slice inside that run: classify 16, extract 16, gold compare 15, store 9 (56). Kernel files remained in the same process and passed.

**Coverage**: ingest package statement coverage 320/398 (80%); branch-adjusted cover reported by pytest-cov **75%**. Threshold in config is 0. Cached config said coverage was undetected; pytest-cov 7.1.0 is installed and was run as a separate command (`python -m pytest tests/ --cov=src/claimledger/ingest --cov-branch --cov-report=term-missing`). That second run also exited 0 (184 passed). It is not the hashed test command.

Inspector notes (not covering tests): installed `docling` is `2.130.0`; installed `docling-graph` is `1.9.1`. `git diff` is empty for `src/claimledger/ledger.py`, the other kernel modules, `evals/`, `pyproject.toml`, and `openspec/specs/gold-regression/spec.md`. `RECIPE_ROWS` still has 14 frozen rows, including `21262335` / `21259769` and tax `-14950948` / `-32731536`.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| In-Corpus Local PDFs | Directory files are in corpus | `tests/ingest/test_classify.py > test_corpus_lists_the_ten_sample_pdfs`, `test_every_corpus_pdf_is_classified` | ✅ COMPLIANT |
| In-Corpus Local PDFs | URL convert is forbidden | `tests/ingest/test_store.py > test_load_or_convert_rejects_non_path`, `test_convert_pdf_rejects_non_path`, `test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Load or convert by hash | `tests/ingest/test_store.py > test_load_existing_artifact_by_canonical_hash`, `test_missing_hash_converts_local_path_only`, `test_existing_pdf_hash_loads_without_reconvert` | ✅ COMPLIANT |
| Docling Pin Without Graph | Pin and graph ban | `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| Recipe P&L From Two EEFF Only | Two EEFF emit recipe rows | `tests/ingest/test_extract.py > test_quarterly_eeff_emit_recipe_claims`, `test_the_two_eeff_keep_distinct_net_income`, `test_furniture_recipe_row_is_ignored`; `tests/ingest/test_gold_compare.py > test_fourteen_rows_match_frozen_recipe_rows` | ✅ COMPLIANT |
| Eight Classify With Zero P&L Identities | Eight mint zero identities | `tests/ingest/test_classify.py > test_eight_non_eeff_mint_zero_pnl_identities`, `test_comunicado_repeating_21262335_is_not_an_identity`; `tests/ingest/test_extract.py > test_non_eeff_extract_to_empty`, `test_eeff_outside_recipe_periods_stays_empty`; `tests/ingest/test_gold_compare.py > test_eight_sources_mint_no_recipe_identity` | ✅ COMPLIANT |
| Eight Classify With Zero P&L Identities | Lookup refusal stays | `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |
| Evidence Fields From Grid Provenance | EEFF evidence is filled | `tests/ingest/test_extract.py > test_quarterly_eeff_emit_recipe_claims` (`_assert_recipe_claims`: hash, page, label, bbox in [0,1], document_id, text) | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_identity.py > test_pins_declared_but_unused`; `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused`, `test_kernel_modules_importable` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out`; `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios compliant

Kernel scan allowlist observed in the passing tests: seven modules (`identity`, `digits`, `evidence`, `claim`, `ledger`, `lookup`, `query`) and six tests (`test_identity`, `test_ledger`, `test_lookup`, `test_query`, `test_gold_v1`, `test_gold_v2`). `src/claimledger/ingest/` is outside that set. Ingest sources contain a `docling` import and the pin string `2.130.0`, and the forbid-token test found no `docling-graph`, `docling_graph`, `HttpSource`, `http://`, or `https://`. This suite did not execute `convert_pdf` (coverage missed `parse.py` lines 41–61), so the runtime version gate did not run; the pin scenario is still covered by the passing source/AST test, and the installed distribution is `2.130.0`.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| In-Corpus Local PDFs | ✅ Implemented | Ten local PDFs classified from `docs/archivos_muestra`. Non-path and missing-file convert raise `IngestError`. |
| Hashed Immutable JSON Store | ✅ Implemented | `load` / `load_or_convert`, canonical JSON hash, `manifest.json` (`pdf_sha` → artifact hash). Cache hit does not reconvert. |
| Docling Pin Without Graph | ✅ Implemented | `PINNED_DOCLING = "2.130.0"` in `parse.py`. No `docling-graph` import in ingest. Package `docling-graph==1.9.1` is installed and unused by ingest. |
| Recipe P&L From Two EEFF Only | ✅ Implemented | Both quarterly EEFF emit both scopes (`consolidated` and `parent_attributable`). Furniture figure `9999999` is excluded. Issuer `BYMA`. Periods `2026-03-31` and `2026-06-30`. |
| Eight Classify With Zero P&L Identities | ✅ Implemented | Eight files are `comunicado`, `deck`, `memoria`, or `transcript` with empty claims. Comunicado text `21262335` does not become an identity. Year-end period stays empty. |
| Evidence Fields From Grid Provenance | ✅ Implemented | Evidence carries artifact hash, page, label, `document_id`, text, and a unit-square bbox. Markdown export is not the extract path. |
| Docling-Free Pytest Demo | ✅ Implemented | Kernel modules and the six named tests do not import `docling`. `Ledger.seed()` still builds the 14 frozen rows with empty evidence. `press_v1` / `presentation_v1` stay absent. Canonical `openspec/specs/gold-regression/spec.md` was not edited; the delta remains in this change until archive. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| `src/claimledger/ingest/` plus `tests/ingest/` | ✅ Yes | Package exists and is not re-exported by the empty kernel `__init__.py`. |
| Hashed JSON plus `manifest.json` | ✅ Yes | Store writes and reads the manifest. Markdown is not SoT. |
| Classify eight, extract two quarterly EEFF | ✅ Yes | Both scopes emitted. No consolidado-versus-controlante choice. |
| `Ledger.seed()` stays the kernel book | ✅ Yes | Fresh-ledger test compares values and asserts seed evidence stays empty. |
| Pin `docling==2.130.0`; never import `docling-graph` | ✅ Yes | Pin in parser source. Graph import absent. `pyproject.toml` not edited. |
| Explicit AST allowlist of 7+6 files | ✅ Yes | Equality asserted in identity and both gold scan tests. |
| `DocumentClass` on `types.py` | ⚠️ Partial | Design file table puts `DocumentClass` on `types.py`. Implementation keeps `StoredDocument` on `types.py` and `DocumentClass` on `classify.py`, which matches task 3.2. |
| Table-structure A/B as a test with one winner | ⚠️ No | One `PdfPipelineOptions(do_ocr=False)` path. No test compares table-structure engines. Fresh-ledger A/B is present and is a different decision. |
| Canonical gold-regression spec edited in this change | Deferred | Design lists that edit. Tasks forbid it until archive. File is unchanged. |
| `do_ocr=False` and local `artifacts_path` | ✅ Yes | Present in `parse.py`. The passing store test asserts those strings. The convert body was not executed in this run. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | `sdd/fase-1-docling-adapter/apply-progress` contains a TDD Cycle Evidence table for tasks 1.1–5.2. |
| All tasks have tests | ✅ | 10/10. Files exist: `tests/test_identity.py`, `tests/test_gold_v1.py`, `tests/test_gold_v2.py`, `tests/ingest/test_store.py`, `tests/ingest/test_classify.py`, `tests/ingest/test_extract.py`, `tests/ingest/test_gold_compare.py`. |
| RED confirmed (tests exist) | ⚠️ | 10/10 test files exist. Tasks 1.1, 2.1, 3.1, and 4.1 record a real pre-implementation failure. Task 5.1 records first-run exit 0 (15 passed) before any `extract.py` edit, because rows already matched frozen `RECIPE_ROWS`. |
| GREEN confirmed (tests pass) | ✅ | This run: 184 passed, exit 0, including every file named in the evidence table. |
| Triangulation adequate | ✅ | Store 9, classify 16, extract 16, gold compare 15. Distinct values cover both periods, both scopes, the neighbor pair, negative tax, and the eight non-EEFF files. |
| Safety Net for modified files | ✅ | New ingest tests and ingest modules are new files. The three modified kernel test files record a 62-passed safety net; this run left them green inside the full suite. |

**TDD Compliance**: 5/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 41 | 3 | pytest (`test_store.py` 9, `test_classify.py` 16, `test_extract.py` 16) |
| Integration | 15 | 1 | pytest (`test_gold_compare.py`; local hashed JSON and in-memory `Ledger`) |
| E2E | 0 | 0 | not installed (design: no HTTP/UI) |
| **Total** | **56** | **4** | |

The other 128 passes are the existing kernel suite in the same `python -m pytest tests/` process. No Playwright or HTTP client is used. Capabilities list integration as not detected; these integration tests are pytest plus local files, which matches the design testing table.

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/ingest/__init__.py` | 100% (5/5) | 0 branches | — | ✅ Excellent |
| `src/claimledger/ingest/types.py` | 100% (9/9) | 0 branches | — | ✅ Excellent |
| `src/claimledger/ingest/classify.py` | 87% (34/39) | 5/14 partial | 47, 54, 59, 61, 64 | ⚠️ Acceptable |
| `src/claimledger/ingest/store.py` | 93% (57/61) | 5/20 partial | 42, 46, 61, 64, 80→86 | ⚠️ Acceptable |
| `src/claimledger/ingest/extract.py` | 81% (203/251) | 37/138 partial; tool cover 75% | 34, 39, 47, 62, 65, 91-93, 95, 99, 101, 105, 120, 124, 129-146, 182, 253, 282, 290, 296, 303, 309, 312, 314, 317, 321, 323, 331, 337, 344, 352, 358-359, plus partial branches | ⚠️ Acceptable on statements; combined cover below 80% |
| `src/claimledger/ingest/parse.py` | 36% (12/33) | 1/6 partial | 15, 19-22, 31-33, 41-61 | ⚠️ Low |

**Average changed-file statement coverage**: 80% (320/398 statements). Branch-adjusted total reported by pytest-cov: 75%. Uncovered statements in changed production files: 78.

Kernel production modules were not part of this change and were not the coverage filter.

### Assertion Quality
| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/ingest/test_extract.py` | 298 | `assert all(GOLD_NET_INCOME_FIGURE not in claim.identity_key for claim in claims)` | Vacuous after `assert claims == ()` on the previous line. The emptiness assertion does call `extract_recipe` and can fail. | WARNING |
| `tests/ingest/test_extract.py` | 367–372 | substring checks on `extract.py` source | Does not call `extract_recipe`. Grid behavior is covered by the recipe-claim tests. | WARNING |

**Assertion quality**: 0 CRITICAL, 2 WARNING

No `assert True` tautologies. Loops over the eight non-EEFF files assert `len == 8` or iterate a non-empty parametrize list before the body assertions.

### Quality Metrics
**Linter**: ➖ Not available (config quality.linter is `not_detected`)
**Type Checker**: ➖ Not available (config quality.type_checker is `not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**:
- Task 5.1 RED did not fail. Apply recorded `python -m pytest tests/ingest/test_gold_compare.py` exit 0, 15 passed, before any `extract.py` edit. The test file exists and passes now. Gold numbers were not relaxed.
- `parse.py` statement coverage is 36%. `convert_pdf` and `_require_pinned_docling` did not run in this suite (cache/mocks). Installed `docling` is still `2.130.0`.
- `extract.py` branch-adjusted cover is 75% (statements 81%).
- `DocumentClass` is defined in `classify.py`. The design file table also names `types.py`.
- No table-structure engine A/B test. One PDF pipeline is compared with frozen gold.
- `test_extract.py` line 298 is a vacuous `all()` over an empty claim tuple.
- `test_extract_source_reads_grid_not_markdown` asserts source text and does not call production extract.

**SUGGESTION**: None. E2E remains out of scope for this change.

### Verdict
PASS WITH WARNINGS

11/11 scenarios have a covering test that passed in `python -m pytest tests/` (exit 0, 184 passed). No critical finding. Kernel tests stayed free of a `docling` import. Ingest may import `docling==2.130.0` and does not import `docling-graph`. Frozen `RECIPE_ROWS` and `Ledger.seed()` were not edited.
