```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:e68dd431d1f8cf1f257704b96b50929e61b198ccf3c573bba31a5f187ec85fff
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 4/4
scenarios: 8/8
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:e68dd431d1f8cf1f257704b96b50929e61b198ccf3c573bba31a5f187ec85fff
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-2-graph-ingest
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (7540 bytes, CRLF). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture. The preimage is not this markdown file.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 8 |
| Tasks complete | 8 |
| Tasks incomplete | 0 |

All eight checkboxes in `tasks.md` are `[x]` (1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2). Full suite was allowed to run.

Counted from the two change specs (`document-graph`, `gold-regression`), matching Engram `sdd/fase-2-graph-ingest/spec` (#1028): **4 requirements, 8 scenarios**.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 212 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 212 items

tests\graph\test_conflict.py .....                                       [  2%]
tests\graph\test_fold.py .....                                           [  4%]
tests\graph\test_period.py ............                                  [ 10%]
tests\graph\test_store.py ....                                           [ 12%]
tests\ingest\test_classify.py ................                           [ 19%]
tests\ingest\test_extract.py ................                            [ 27%]
tests\ingest\test_gold_compare.py ...............                        [ 34%]
tests\ingest\test_store.py ..........                                    [ 39%]
tests\test_gold_v1.py ...........                                        [ 44%]
tests\test_gold_v2.py ...........                                        [ 49%]
tests\test_identity.py .........................................         [ 68%]
tests\test_ledger.py ........                                            [ 72%]
tests\test_lookup.py ..........................................          [ 92%]
tests\test_query.py ................                                     [100%]

============================== warnings summary ===============================
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1037: DeprecationWarning: deprecated
    self.picture_description_local is not None

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1052: DeprecationWarning: deprecated
    self.vlm_pipeline_model,

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1053: DeprecationWarning: deprecated
    self.vlm_pipeline_model_local,

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1054: DeprecationWarning: deprecated
    self.vlm_pipeline_model_api,

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1075: DeprecationWarning: deprecated
    self.vlm_pipeline_model is not None

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1076: DeprecationWarning: deprecated
    or self.vlm_pipeline_model_local is not None

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1077: DeprecationWarning: deprecated
    or self.vlm_pipeline_model_api is not None

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1106: DeprecationWarning: deprecated
    self.picture_description_local is not None

tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
tests/graph/test_conflict.py::test_kind_clash_stays_on_conflicts_and_not_ledger_status[rows0-eeff-comunicado]
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling\datamodel\service\options.py:1107: DeprecationWarning: deprecated
    or self.picture_description_api is not None

tests/graph/test_conflict.py: 19 warnings
tests/graph/test_store.py: 8 warnings
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling_graph\core\utils\alias_reconciler.py:95: PydanticDeprecatedSince211: Accessing the 'model_fields' attribute on the instance is deprecated. Instead, you should access this attribute from the model class. Deprecated in Pydantic V2.11 to be removed in V3.0.
    if id(instance) in seen or not hasattr(instance, "model_fields"):

tests/graph/test_conflict.py: 13 warnings
tests/graph/test_store.py: 6 warnings
  C:\Users\Equipo\AppData\Local\Programs\Python\Python311\Lib\site-packages\docling_graph\core\utils\alias_reconciler.py:102: PydanticDeprecatedSince211: Accessing the 'model_fields' attribute on the instance is deprecated. Instead, you should access this attribute from the model class. Deprecated in Pydantic V2.11 to be removed in V3.0.
    if hasattr(value, "model_fields"):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
====================== 212 passed, 73 warnings in 16.22s ======================
```

`pyproject.toml` sets `addopts = "--import-mode=importlib"`. Pins in that diff are unchanged: `docling==2.130.0`, `docling-graph==1.9.1`. Graph tests ran before kernel tests in this process (`tests/graph/` then `tests/test_identity.py`). The kernel snapshot still passed. Behavioral `build` calls exercise the pin check inside `build.py`; a mismatched install would have failed those tests.

**Coverage**: separate command, not the hashed test. `python -m pytest tests/ --cov=src/claimledger/graph --cov-branch --cov-report=term-missing` exited 0 (212 passed). Config threshold is 0. Cached capabilities said coverage was undetected; pytest-cov 7.1.0 is installed.

Inspector notes: `git diff` does not include `src/claimledger/query.py`, `src/claimledger/identity.py`, `src/claimledger/ledger.py`, `src/claimledger/ingest/`, or `evals/`. The gold-test diff only replaces the import scan with the explicit 13-path set. Frozen number tables in those files are untouched, including `21262335` and `81956525`.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Entities, Write Once, Import | Closed pack | `tests/graph/test_fold.py > test_schema_is_four_entities_with_spec_edges`, `test_fold_mints_no_financial_claim_and_does_not_call_extract_recipe`; `tests/graph/test_store.py > test_build_writes_graph_json_once_and_load_does_not_rebuild`, `test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl`; `tests/test_identity.py > test_kernel_modules_importable`, `test_pins_declared_but_unused`, `test_graph_init_outside_kernel_allowlist`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| IDs, Fold, Conflict | Quarterly ids | `tests/graph/test_fold.py > test_same_period_pack_shares_issuer_period_statement_and_hash`, `test_both_quarters_fold_one_issuer_and_one_statement` | ✅ COMPLIANT |
| IDs, Fold, Conflict | Clash | `tests/graph/test_conflict.py > test_kind_clash_stays_on_conflicts_and_not_ledger_status` | ✅ COMPLIANT |
| Classify, Doubt, Memoria, Transcript | Edges | `tests/graph/test_period.py > test_non_eeff_classify_period_stays_none_while_graph_links_token`, `test_year_end_memorias_have_no_quarterly_period`, `test_transcript_may_link_period_and_mints_no_claim`; `tests/graph/test_conflict.py > test_unknown_alias_sets_doubt_and_mints_no_period`, `test_year_end_memoria_doubt_stays_off_the_eeff_quarter`, `test_resolved_transcript_links_period_without_doubt` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_identity.py > test_pins_declared_but_unused`, `test_graph_init_outside_kernel_allowlist`; `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused`, `test_kernel_modules_importable`; `tests/graph/test_store.py > test_graph_package_forbids_pipeline_llm_vlm_binder_neo4j_and_pl`; `tests/ingest/test_store.py > test_ingest_sources_forbid_url_httpsource_and_docling_graph` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out`; `tests/ingest/test_gold_compare.py > test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Kernel absence ignores a later graph load | `tests/test_identity.py > test_kernel_modules_importable` (before/after delta, not process-wide absence). Same-process suite loaded `docling-graph` from `tests/graph/` and then passed the kernel files | ✅ COMPLIANT |

**Compliance summary**: 8/8 scenarios compliant

Kernel and ingest production modules do not import `docling_graph`. The only production importer is `src/claimledger/graph/build.py`, and those imports are inside functions. `graph/__init__.py` exports `build` and `load` with no top-level `docling_graph` import. `claimledger.query` does not reference the graph package.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Entities, Write Once, Import | ✅ Implemented | Document, Issuer, Period, Statement. `build` writes `artifacts/graph/graph.json`. `load` reads the file and does not convert. No `FinancialClaim`, `extract_recipe`, `run_pipeline`, or Neo4j in the graph package. |
| IDs, Fold, Conflict | ✅ Implemented | Shared `BYMA`, `2026-03-31` / `2026-06-30`, `income_statement`, document id `artifact_hash`. Kind clash stays on `__conflicts__`. Encoded payload has no `ledger_status`. |
| Classify, Doubt, Memoria, Transcript | ✅ Implemented | Non-EEFF `DocumentClass.period` stays `None`. Unknown alias sets `doubt` from `ValueError` and mints no Period. Year-end memoria stays off both quarters. Transcript may link `2026-06-30` with no Statement and no claim. |
| Docling-Free Pytest Demo | ✅ Implemented | Thirteen-path allowlist excludes `graph/` and `ingest/`. Gold numbers in the test diff are unchanged. `press_v1` and `presentation_v1` stay absent. `recipe_no_extract` still covers comunicado and deck P&L. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Sibling `src/claimledger/graph/` plus `tests/graph/` | ✅ Yes | Four modules. Ingest package was not used as the home of the graph. |
| One `artifacts/graph/graph.json`; query does not rebuild | ✅ Yes | `load` returns a replaced on-disk marker. `query.py` is unchanged and does not import the graph. |
| Four entities; no `extract_recipe` | ✅ Yes | Schema and fold tests. |
| `classify.period` stays `None` off EEFF | ✅ Yes | EEFF uses `DocumentClass.period`. Other kinds use separator-split tokens. |
| Lazy pin `docling-graph==1.9.1` | ✅ Yes | `version("docling-graph")` compared to `1.9.1` inside the builder. |
| `GraphConverter(alias_llm_fn=None)`, `NodeIDRegistry`, `MergePolicy(conflicts="keep-all", export_format=None)`, local `JSONExporter` | ✅ Yes | Present in `build.py`. Conflict tests observe `__conflicts__`. |
| Provenance `document_id=artifact_hash` plus local path | ✅ Yes | Stamped after merge so the merger does not replace the local path. Contract matches the design. |
| No `run_pipeline`, LLM/VLM, `ProvenanceBinder`, Neo4j | ✅ Yes | AST forbid test over the four graph modules. |
| Kernel and ingest never import `docling_graph` | ✅ Yes | Passing scan tests. |
| Thirteen-path allowlist unchanged in intent | ✅ Yes | Identity, gold v1, and gold v2 assert the same 13 paths. `graph/` is outside. |
| `doubt` recorded on `ValueError` with no period id | ⚠️ Partial | Design file table assigns doubt to `link.py`. `link.py` skips unknown tokens. `build.py` sets `Document.doubt`. Spec scenario "Edges" is covered because the graph is built through `build`. |
| `pyproject.toml` addopts | ⚠️ Extra | `addopts = "--import-mode=importlib"` is not in the design file list. Pin strings were not bumped. Needed so `tests/graph/test_store.py` and `tests/ingest/test_store.py` collect together. |
| Canonical `openspec/specs/gold-regression/spec.md` | ⚠️ Edited early | Tasks say apply must not edit `openspec/specs/` until archive. The working tree file has the Fase 1 sentence (ingest may import `docling`, scan excludes ingest) and does not yet include the Fase 2 graph permission or the scenario "Kernel absence ignores a later graph load". Those live in the change delta. Numeric gold in that spec still requires `21262335`. |
| `.gitignore` ignores `artifacts/graph/*.json` | ✅ Yes | Also contains `artifacts/docling/*.json` and `artifacts/docling/models/`. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram `sdd/fase-2-graph-ingest/apply-progress` (#1030) has a TDD Cycle Evidence table for tasks 1.1–3.2. |
| All tasks have tests | ✅ | 8/8. Files exist: `tests/test_identity.py`, `tests/graph/test_fold.py`, `tests/graph/test_period.py`, `tests/graph/test_conflict.py`, `tests/graph/test_store.py`. |
| RED confirmed (tests exist) | ✅ | 8/8 rows record a pre-production failure (missing assert, missing file, or `ModuleNotFoundError`). Those test files exist now. |
| GREEN confirmed (tests pass) | ✅ | This run: 212 passed, exit 0, including every file named in the evidence table. Graph package: conflict 5, fold 5, period 12, store 4 (26). |
| Triangulation adequate | ✅ | Unit 2: both quarters, memorias, transcripts, six non-EEFF links, glued token. Unit 3: two kind clashes, unknown alias, year-end memoria doubt, resolved transcript with `doubt is None`. Tasks 1.2 and 1.4 are single structural snapshots; the spec has one expected delta and one absent forbidden import. |
| Safety Net for modified files | ✅ | New graph modules and new graph tests are new files. Task 3.2 records 58 passed before editing `schema.py` and `__init__.py`. This full suite left identity, gold, and ingest green in the same process. |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 61 | 4 | pytest (`test_identity.py` 41, `test_fold.py` 5, `test_period.py` 12, plus 3 AST/path tests in `test_store.py`) |
| Integration | 6 | 2 | pytest and installed `docling-graph` (`test_conflict.py` 5, `test_build_writes_graph_json_once_and_load_does_not_rebuild`) |
| E2E | 0 | 0 | not installed |
| **Total** | **67** | **5** | |

Counts are the changed test files only. The other passes are the existing kernel and ingest suite in the same process. No browser or HTTP runner. Capabilities list integration as not detected; these six tests call the real converter and merger with no PDF and no network, which matches the design testing table.

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/graph/__init__.py` | 100% (2/2) | 0 branches | — | ✅ Excellent |
| `src/claimledger/graph/build.py` | 93.6% (73/78) | 22 branches, 4 partial; tool cover 91% | 39, 49, 55, 64, 101 | ⚠️ Acceptable |
| `src/claimledger/graph/link.py` | 98.5% (64/65) | 18 branches, 1 partial; tool cover 98% | 64 | ✅ Excellent |
| `src/claimledger/graph/schema.py` | 96.8% (30/31) | 2 branches, 1 partial; tool cover 94% | 33 | ✅ Excellent |

**Average changed-file statement coverage**: 96.0% (169/176 statements). Branch-adjusted total reported by pytest-cov: 94%. Uncovered statements in changed production files: 7. No changed file is under 80%.

`tests/test_identity.py`, `.gitignore`, and `pyproject.toml` are not in the coverage filter.

### Assertion Quality
| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/graph/test_store.py` | 153–162 | `"alias_llm_fn=None" in build_text`, `conflicts="keep-all"`, `"1.9.1" in build_text`, and the other source substrings | This test does not call `build`. Pin, converter, and merge behavior are covered by the passing `build` / conflict tests. | WARNING |

**Assertion quality**: 0 CRITICAL, 1 WARNING

No `assert True` tautologies. Empty-period asserts for memoria have companion tests that expect `2026-03-31` and `2026-06-30`. The forbid loop runs over the four graph modules after asserting that list. Clash tests assert both the kept `kind` and the `__conflicts__` value.

### Quality Metrics
**Linter**: ➖ Not available (config quality.linter is `not_detected`)
**Type Checker**: ➖ Not available (config quality.type_checker is `not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**:
- `Document.doubt` is set in `build.py`. The design file table says `link.py` records the period edge or doubt. `fold_documents` still leaves `doubt` unset. Built-graph tests cover the spec.
- `pyproject.toml` gained `addopts = "--import-mode=importlib"`. Not listed in the design file table. Pin versions were not changed.
- `openspec/specs/gold-regression/spec.md` is modified in the working tree. Tasks forbid that until archive. The checked-in wording there is the Fase 1 scan. The Fase 2 graph permission and the fourth scenario are only in `openspec/changes/fase-2-graph-ingest/specs/gold-regression/spec.md`.
- `tests/graph/test_store.py` lines 153–162 assert source text and do not call `build`.

**SUGGESTION**: No test calls `claimledger.query.query` after `build` and then re-reads `graph.json`. `query.py` does not import the graph, and `load` is tested not to rebuild. E2E stays out of scope.

### Verdict
PASS WITH WARNINGS

8/8 scenarios have a covering test that passed in `python -m pytest tests/` (exit 0, 212 passed, 0 failed). No critical finding. Gold numbers in the gold-test diff were not relaxed. Kernel and ingest do not import `docling-graph`. The graph package may import `docling-graph==1.9.1`, and it does so only inside `build.py`.
