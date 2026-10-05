# Tasks: Fase 1 Docling Evidence Adapter

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 800–1200 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 AST → PR2 store → PR3 classify → PR4 extract → PR5 gold |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | AST allowlist before ingest imports | PR 1, base `fase-0-kernel` | `pytest tests/test_identity.py tests/test_gold_v1.py tests/test_gold_v2.py` | N/A — kernel pytest, no PDF | Revert those three test files |
| 2 | Hashed JSON, local convert only | PR 2, base unit 1 | `pytest tests/ingest/test_store.py` | One local corpus PDF; no URL | Delete store/parse/types/`__init__.py`, `test_store.py`, `.gitkeep`; revert `.gitignore` |
| 3 | Classify 10; eight mint zero identities | PR 3, base unit 2 | `pytest tests/ingest/test_classify.py` | Ten local PDFs, classify only | Delete `classify.py`, `test_classify.py` |
| 4 | Extract two quarterly EEFF | PR 4, base unit 3 | `pytest tests/ingest/test_extract.py` | Two EEFF via hashed JSON | Delete `extract.py`, `test_extract.py` |
| 5 | 14 rows vs frozen `RECIPE_ROWS` | PR 5, base unit 4 | `pytest tests/ingest/test_gold_compare.py` | Optional fresh Ledger; seed untouched | Delete `test_gold_compare.py`; revert extract mapping |

## Phase 1: AST Allowlist (Unit 1)

- [x] 1.1 RED: Assert scan equality in `test_pins_declared_but_unused` and `test_import_scan_stays_clean`: modules `identity`, `digits`, `evidence`, `claim`, `ledger`, `lookup`, `query` plus `tests/test_{identity,ledger,lookup,query,gold_v1,gold_v2}.py`. Today's glob includes `__init__.py` and MUST fail.
- [x] 1.2 GREEN: Allowlist those 13 paths in `tests/test_{identity,gold_v1,gold_v2}.py`. Kernel pytest green; no `ingest/`.

## Phase 2: Parse and Store (Unit 2)

- [x] 2.1 RED: Add `tests/ingest/test_store.py`: load existing `artifacts/docling/<sha256>.json`; missing hash converts a local `Path` only; URL, `HttpSource`, and `docling-graph` fail. Fails: no modules.
- [x] 2.2 GREEN: Add `ingest/{__init__,types,store,parse}.py` (`StoredDocument`, `load`, `load_or_convert`, `do_ocr=False`, local `artifacts_path`, `docling==2.130.0`). Add `artifacts/docling/.gitkeep`; ignore `artifacts/docling/*.json`. No kernel or `pyproject.toml` semantic edits.

## Phase 3: Classify (Unit 3)

- [x] 3.1 RED: Add `tests/ingest/test_classify.py` for all `docs/archivos_muestra` PDFs. Eight non-EEFF are `comunicado|deck|memoria|transcript` with zero P&L identities. Comunicado `21262335` is not identity. MUST fail.
- [x] 3.2 GREEN: Add `classify.py` (`DocumentClass`) and export `classify`.

## Phase 4: Extract (Unit 4)

- [x] 4.1 RED: Add `tests/ingest/test_extract.py`. Only `BYMA_-_EEFF_31-03-2026_VF.pdf` (`2026-03-31`) and `BYMA - EEFF 30-06-2026.pdf` (`2026-06-30`), issuer `BYMA`. Furniture ignored. Evidence has hash, page, locator `label`, bbox in `[0,1]`. Eight empty. MUST fail.
- [x] 4.2 GREEN: Add `extract.py` (`extract_recipe` from grid/provenance). Empty unless `eeff` and `PERIOD_1T26` or `PERIOD_2T26`. No consolidado/controlante choice.

## Phase 5: Gold Compare (Unit 5)

- [x] 5.1 RED: Add `tests/ingest/test_gold_compare.py`: 14 rows match frozen `RECIPE_ROWS` (value, neighbor, tax). Optional fresh-Ledger A/B. `Ledger.seed()` untouched. Comunicado/deck/memoria P&L stays `recipe_no_extract`.
- [x] 5.2 GREEN: Fix extract mapping only until 5.1 passes. Do not relax gold or import `docling-graph`.

Apply MUST NOT edit `openspec/specs/gold-regression/spec.md`; archive merges that delta later.
