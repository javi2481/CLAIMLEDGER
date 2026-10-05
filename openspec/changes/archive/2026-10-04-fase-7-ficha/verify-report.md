```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:d95ce0fb75ad2ca3478a10a19f0d23fe1f464c80ffc8874a96c68c0473017dfa
verdict: pass
blockers: 0
critical_findings: 0
requirements: 8/8
scenarios: 17/17
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:d95ce0fb75ad2ca3478a10a19f0d23fe1f464c80ffc8874a96c68c0473017dfa
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-7-ficha
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (8026 bytes, Windows CRLF, 96 CRLF newlines, 0 bare LF). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\fase7-pytest-reverify.bin`. The preimage is not this markdown file. This re-verify replaces the previous capture (`sha256:907e5eb79cf68c32bbc63dc192ff60665d2ad4ce95814b1dbd4758da19050ece`, 279 passed).

Counted from the two change specs (`claim-card`, `gold-regression`), matching Engram `sdd/fase-7-ficha/spec` (#1066): **8 requirements, 17 scenarios**.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 4 |
| Tasks complete | 4 |
| Tasks incomplete | 0 |

All four checkboxes in `tasks.md` are `[x]` (1.1, 1.2, 2.1, 2.2). Full suite was allowed to run.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 280 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 280 items

tests\card\test_render_card.py .........                                 [  3%]
tests\eval\test_measure.py ............                                  [  7%]
tests\graph\test_conflict.py .....                                       [  9%]
tests\graph\test_fold.py .....                                           [ 11%]
tests\graph\test_period.py ............                                  [ 15%]
tests\graph\test_store.py ....                                           [ 16%]
tests\http\test_app.py ..................                                [ 23%]
tests\http\test_claims_query.py .................                        [ 29%]
tests\ingest\test_classify.py ................                           [ 35%]
tests\ingest\test_extract.py ................                            [ 40%]
tests\ingest\test_gold_compare.py ...............                        [ 46%]
tests\ingest\test_store.py ..........                                    [ 49%]
tests\retrieval\test_drawers.py .......                                  [ 52%]
tests\retrieval\test_read.py ...                                         [ 53%]
tests\test_gold_v1.py ...........                                        [ 57%]
tests\test_gold_v2.py ...........                                        [ 61%]
tests\test_identity.py ...........................................       [ 76%]
tests\test_ledger.py ........                                            [ 79%]
tests\test_lookup.py ..........................................          [ 94%]
tests\test_query.py ................                                     [100%]

====================== 280 passed, 73 warnings in 17.28s ======================
```

`tests/card/test_render_card.py`: 9 passed, including `test_render_card_does_not_call_kernel`. The 73 warnings are Docling and docling-graph deprecations inside graph tests. Card tests added none.

Gold numbers stayed frozen in this run. `src/claimledger/ledger.py` still seeds `21262335`, `21259769`, `-14950948`, and `81956525`. `tests/test_gold_v1.py` and `tests/test_gold_v2.py` still assert those figures, including `test_frozen_numbers_are_intact` and `test_id_01_keeps_neighbor_number_and_aliased_identity`. The six kernel test files do not import `claimledger.card`, `starlette`, `docling`, or `llama_index`. `test_http_stays_off_kernel_allowlist` asserts the 13 allowlist paths do not import `starlette` and passed. `src/claimledger/__init__.py` is empty.

**Coverage**: `claimledger.card` statement coverage 100% (33/33) and branch coverage 100% (4/4). `card/__init__.py` is 0 statements, 100%. Config threshold is 0. Cached `openspec/config.yaml` still says coverage was not detected; pytest-cov 7.1.0 is installed and was used for this extra run only.

A second command, `python -m pytest tests/card/test_render_card.py --cov=claimledger.card --cov-branch --cov-report=term-missing -q --tb=no`, also exited 0 (9 passed, 0.40s). That run is not the hashed preimage.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Pure Display | No kernel calls | `tests/card/test_render_card.py > test_render_card_does_not_call_kernel` | ✅ COMPLIANT |
| Verified Consolidated Card | Consolidated rows and seal | `tests/card/test_render_card.py > test_consolidated_card` | ✅ COMPLIANT |
| Verified Parent Card | Parent scope is not consolidated | `tests/card/test_render_card.py > test_parent_card` | ✅ COMPLIANT |
| Abstain Card | recipe_no_extract keeps the reason | `tests/card/test_render_card.py > test_recipe_no_extract_abstains` | ✅ COMPLIANT |
| Abstain Card | Empty candidates still abstain | `tests/card/test_render_card.py > test_empty_candidates_still_abstain` | ✅ COMPLIANT |
| Compare Card | Two values, no delta | `tests/card/test_render_card.py > test_compare_shows_both_values_without_delta` | ✅ COMPLIANT |
| Seal Follows Query Status | Recorded is not verified | `tests/card/test_render_card.py > test_seal_follows_query_status_not_ledger_status` | ✅ COMPLIANT |
| Package Boundary | Off the allowlist with no new library | `tests/card/test_render_card.py > test_card_stays_off_kernel_allowlist` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_identity.py > test_ingest_and_kernel_tests_omit_llama_index`, `test_retrieval_init_outside_kernel_allowlist`, `test_pins_declared_but_unused`; `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused`, `test_kernel_modules_importable`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph`; `tests/graph/test_store.py > test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out`; `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Kernel absence ignores a later graph load | `tests/test_identity.py > test_kernel_modules_importable`. Same-process suite loaded `docling-graph` from `tests/graph/` and the kernel tests still passed | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Retrieval off the snapshot | `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Eval stays off the scan | `tests/eval/test_measure.py > test_slice2_eval_outside_allowlist`; `tests/test_identity.py > test_retrieval_init_outside_kernel_allowlist` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Gold harness stays on seed | `tests/test_gold_v1.py > test_gold_v1_has_exactly_45_cases`, `test_harness_runs_non_skip_cases_and_skips_narrative`; `tests/test_gold_v2.py > test_gold_v2_has_exactly_26_cases`, `test_harness_runs_all_26_cases`, `test_v2_id_04_keeps_minus_sign_and_aliased_identity`, `test_frozen_numbers_are_intact` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | HTTP stays off the scan | `tests/http/test_app.py > test_http_stays_off_kernel_allowlist` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Card stays off the scan | `tests/card/test_render_card.py > test_card_stays_off_kernel_allowlist`. The six kernel test files contain no import of `claimledger.card`. `card.py` does not import `starlette`, so importing the card does not load a UI stack | ✅ COMPLIANT |

**Compliance summary**: 17/17 scenarios compliant

`test_render_card_does_not_call_kernel` calls `render_card`, asserts seal `VERIFICADO`, spies `measure`, `retrieve`, `understand`, `query`, and `Ledger.upsert` (`calls == []`), and AST-scans `card.py` so those names are absent from `Call` nodes. It passed inside this suite. `test_consolidated_card_copies_claim_value` also passed. It asserts `values == ("100",)` while the row texts still contain `21.262.335` and `21.259.769`, so the value is `claim.value` and the rows are not parsed for digits.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Pure Display | ✅ Implemented | `render_card` lives in `src/claimledger/card/card.py`, takes `(candidates, result)`, copies `Candidate.text` and `claim.value`, and does not call `measure`, `retrieve`, `understand`, `query`, or `upsert`. The covering test passed in this run. |
| Verified Consolidated Card | ✅ Implemented | Seal `VERIFICADO`, chip `BYMA · 1T26 · Consolidado · Resultado neto`, value `21262335`, both neighbor texts in order, sentence `encontré estas dos filas; verifiqué la consolidada`. `21259769` is not the value. |
| Verified Parent Card | ✅ Implemented | Scope `parent_attributable` maps to chip `Controlante`. Seal `VERIFICADO`, value `21259769`, both rows remain, sentence `encontré estas dos filas; verifiqué la controlante`. The chip and sentence do not say consolidado. |
| Abstain Card | ✅ Implemented | `status != "verified"` returns seal `ME ABSTENGO` when status is `abstained`, copies `reason`, `values == ()`, `sentence == ""`. Empty candidates keep that seal. |
| Compare Card | ✅ Implemented | Both claim values are copied in order. `ClaimCard` has no `delta` field. The subtracted number is not part of the card. |
| Seal Follows Query Status | ✅ Implemented | Seal comes from `QueryResult.status`. `ledger_status` is not read. A recorded claim on an abstained result seals `ME ABSTENGO`. |
| Package Boundary | ✅ Implemented | `card.py` imports `claimledger.claim`, `claimledger.query.QueryResult`, and `claimledger.retrieval.drawers.Candidate` only. `dependencies = []`. Card paths are outside the 13-path allowlist. `src/claimledger/__init__.py` is empty. `card/__init__.py` is a docstring with no re-export. |
| Docling-Free Pytest Demo | ✅ Implemented | The 13-path allowlist is unchanged and does not name `card/` or `http/`. Kernel gold remains `Ledger.seed()`. Pins stay metadata. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Frozen `ClaimCard` with seal, chips, rows, values, sentence, reason | ✅ Yes | Matches `QueryResult` / `Candidate` style. |
| Input is `(candidates, QueryResult)` only | ✅ Yes | No HTTP route and no call into `measure`. |
| Seal from `QueryResult.status`, not `ledger_status` | ✅ Yes | `verified` → `VERIFICADO`; `abstained` → `ME ABSTENGO`. |
| `values` copy `claim.value`; rows copy `Candidate.text` | ✅ Yes | No digit parse. |
| `parent_attributable` → `Controlante` | ✅ Yes | Closed map. Chip is not `Consolidado`. |
| Sentence only for one verified claim with two rows | ✅ Yes | Compare and abstain use `sentence == ""`. |
| Abstain copies `reason`, `values == ()` | ✅ Yes | Abstain returns before claim fields are read. |
| Compare shows both values and has no delta | ✅ Yes | |
| No `starlette`, `docling`, `llama_index`, or `open_webui` import | ✅ Yes | |
| `dependencies` stay `[]`; root `__init__.py` stays empty | ✅ Yes | |
| Card paths stay off `_kernel_scan_paths` | ✅ Yes | |
| Unknown verified token raises `ValueError` | ⚠️ No | `_chip` falls back to the stored token (`dict.get(..., token)`). No scenario requires the raise. |
| `2026-06-30` → `2T26` | ⚠️ No | `_PERIOD_CHIP` maps only `2026-03-31` → `1T26`. Compare uses period `2026-06-30` and does not assert the chip. No scenario requires `2T26`. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in Engram `sdd/fase-7-ficha/apply-progress` (#1069) |
| All tasks have tests | ✅ | 4/4 tasks name `tests/card/test_render_card.py`, which exists |
| RED confirmed (tests exist) | ✅ | Test file exists. Historical RED was not re-run. Apply-progress matches the recorded evidence: Unit 1 `pytest tests/card/test_render_card.py::test_consolidated_card` exit 4, `ModuleNotFoundError: No module named 'claimledger.card'`, before production code. Unit 2 `pytest tests/card/test_render_card.py` exit 1, 5 failed with `AssertionError` (parent chip, `ME ABSTENGO`, compare values, seal source, empty candidates), 3 passed, including `test_card_stays_off_kernel_allowlist`, which was not weakened. No `ImportError` on Unit 2. |
| GREEN confirmed (tests pass) | ✅ | This run: 9/9 card tests passed inside `python -m pytest tests/` (280 passed). Apply-progress GREEN was Unit 1 `test_consolidated_card` 1 passed, then Unit 2 8 passed. |
| Triangulation adequate | ✅ | Consolidated has two value cases (`21262335` and `100`). Slice 2 covers parent, abstain with a recorded claim, compare, seal versus `ledger_status`, and empty candidates. “No kernel calls” is one scenario and has one covering test. |
| Safety Net for modified files | ✅ | Unit 1 files were new (`N/A (new)`). Unit 2 reports a pre-edit `pytest tests/card/test_render_card.py` exit 0, 2 passed. That historical run was not repeated. |

**TDD Compliance**: 6/6 checks passed

The coverage seal `test_render_card_does_not_call_kernel` was added after the apply cycle. Its first execution passed (1 passed) because `render_card` already did not call `measure`, `retrieve`, `understand`, `query`, or `upsert`. That pass is recorded. It is not treated as a fake RED or as a protocol failure: the assertion calls production code, spies those five entry points, and AST-scans `card.py`. Units 1 and 2 still have a real RED.

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 9 | 1 | pytest |
| Integration | 0 | 0 | not installed |
| E2E | 0 | 0 | not installed |
| **Total** | **9** | **1** | |

The change’s tests are `tests/card/test_render_card.py`. They build `FinancialClaim`, `QueryResult`, and `Candidate` in memory. No HTTP, browser, PDF, or network. Gold-regression scenarios stay covered by the existing kernel, ingest, graph, retrieval, eval, and HTTP tests that passed in the same run.

---

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/card/card.py` | 100% | 100% | — | ✅ Excellent |
| `src/claimledger/card/__init__.py` | 100% | 100% | — | ✅ Excellent |

**Average changed file coverage**: 100%

`tests/card/test_render_card.py` is the test module, not a production file. Coverage command was the extra pytest-cov run above, not the hashed suite.

---

### Assertion Quality

**Assertion quality**: ✅ All assertions verify real behavior

Card tests call `render_card` and assert seal, chips, rows, values, sentence, or reason. `test_consolidated_card_copies_claim_value` uses a different value (`100`) than the row text. Empty `rows` / `values` on abstain sit next to non-empty consolidated and parent cases. `assert all("Consolidado" not in chip for chip in card.chips)` runs only after `card.chips == (PARENT_CHIP,)`, so the collection is not empty. `test_render_card_does_not_call_kernel` calls `render_card`, asserts seal `VERIFICADO`, and checks that the five kernel spies stayed empty and that `card.py` has no `Call` to those names. No tautology, no assertion that skips production code, no ghost loop.

---

### Quality Metrics
**Linter**: ➖ Not available (cached capabilities: `linter: not_detected`)
**Type Checker**: ➖ Not available (cached capabilities: `type_checker: not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: Design says an unknown chip token on a verified claim raises `ValueError`. Implementation falls back to the stored token. No scenario requires the raise.

**WARNING**: Design maps `2026-06-30` to `2T26`. `_PERIOD_CHIP` maps only `2026-03-31` to `1T26`. No scenario requires `2T26`.

**SUGGESTION**: None.

### Verdict
PASS
17/17 scenarios have a covering test that passed in this run. The suite is green (280 passed, exit 0). Two design notes stay as non-blocking warnings and do not leave a scenario uncovered.

A later chip fix added tests for 2T26 and ValueError; the suite then passed 281, evidence sha256:8daaf6bb5d6256adf1276b174601a9f26ca877ec371e4e6d3313b7c8327779be, and that later pass is not a CRITICAL.
