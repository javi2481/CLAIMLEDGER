# Tasks: Fase 3 Retrieval

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 280–450 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR1 JSON reader → PR2 drawers |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Reader over an existing hashed JSON path; force `export_type=json`; missing artifact fails closed | `fase-3-retrieval-json-reader`, base `fase-0-kernel` | `pytest tests/retrieval/test_read.py tests/test_identity.py` | N/A — fixture JSON; no PDF, URL, or network | Delete `src/claimledger/retrieval/` and `tests/retrieval/test_read.py`; revert the `tests/test_identity.py` snapshot asserts; drop the LlamaIndex pin from `pyproject.toml` |
| 2 | Two drawers and candidates only | `fase-3-retrieval-drawers`, base unit 1 | `pytest tests/retrieval/test_drawers.py` | N/A — fixture JSON; `query` is not called | Delete `src/claimledger/retrieval/drawers.py` and `tests/retrieval/test_drawers.py` |

## Phase 1: Hashed JSON Reader (Unit 1)

- [x] 1.1 RED: Add `tests/retrieval/test_read.py`. Load `artifacts/docling/<sha256>.json` through `store.load`. Assert `DoclingReader(export_type="json")` then `DoclingNodeParser` on that local path. A missing artifact raises `IngestError` and does not call `load_or_convert`, `convert_pdf`, or a URL fetch. MUST fail: no `read` module.
- [x] 1.2 RED: In `tests/test_identity.py`, assert `src/claimledger/retrieval/__init__.py` is outside `_kernel_scan_paths()` and `len(allowlist) == 13`. Importing the seven `KERNEL_MODULES` MUST NOT put `llama_index` in `sys.modules`. Leave `FORBIDDEN_IMPORT_ROOTS` as `docling`, `docling_graph`. MUST fail: retrieval init missing.
- [x] 1.3 GREEN: Add `src/claimledger/retrieval/__init__.py` with no `llama_index` import, and `read.py` that lazy-imports `DoclingReader` and `DoclingNodeParser` inside the function and forces `export_type="json"`. At apply time, identify a documented release compatible with `docling==2.130.0`, then record that pin in `pyproject.toml`. Leave `src/claimledger/ingest/` and `query.py` unchanged.

## Phase 2: Drawers and Candidates (Unit 2)

- [x] 2.1 RED: Add `tests/retrieval/test_drawers.py`. A `tables` call returns no narrative nodes. A `narrative` call returns no table nodes. Both neighbor rows MAY be table candidates. `Candidate` has no `verified` or `abstained` and is not a `FinancialClaim`. `claimledger.query` is not called. Naming both drawers, or an unknown drawer, raises. MUST fail: no `drawers`.
- [x] 2.2 GREEN: Add `src/claimledger/retrieval/drawers.py` with `DrawerName`, frozen `Candidate` (`drawer`, `text`, `ref`), and `retrieve(artifact_hash, drawer, question) -> tuple[Candidate, ...]`. One drawer per call. Do not write the ledger. Leave `query.py` unchanged.

Apply MUST NOT edit `openspec/specs/`. The gold-regression delta stays in this change until archive. Do not relax gold numbers.
