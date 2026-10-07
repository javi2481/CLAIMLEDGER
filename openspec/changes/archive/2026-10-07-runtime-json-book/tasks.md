# Tasks: Runtime JSON Book

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 280–400 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | single PR; apply A→B→C in order |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| A | Pure JSON extract | single | `python -m pytest tests/ingest/test_extract.py tests/ingest/test_gold_compare.py -q` | N/A (unit fixtures) | Revert `extract.py` + extract tests |
| B | Import-scan book path | single | `python -m pytest tests/ingest/test_extract.py tests/ingest/test_ground.py -q` | Optional cache-hit book smoke | Revert import-scan tests only |
| C | `ingest` extra + CI | single | workflow extras dry-read; `python -m pytest tests/ingest/test_convert_local.py -q` | N/A (CI config) | Revert `pyproject.toml` + `pytest.yml` |

Threat matrix: N/A (no RED threat tasks). Gold `21262335` / `21259769` frozen. `reply` / `retrieval/*` / Dockerfile unchanged.

## Phase A: Extract pure JSON (Strict TDD)

- [x] A.1 RED `tests/ingest/test_extract.py`: nested `groups` fixture (body→groups→tables) + furniture table; only body tables yield recipe; assert walk not `iterate_items` (flip `test_body_tables_come_from_iterate_items`).
- [x] A.2 RED: cells-only / empty `data.grid` → `IngestError` (rewrite `test_cells_without_grid_*`; no `TableData`).
- [x] A.3 RED: source ban — `extract.py` text MUST NOT contain `docling`, `docling_core`, `torch`, `PINNED_DOCLING`. Run pytest — fail for right reason.
- [x] A.4 GREEN `src/claimledger/ingest/extract.py`: DFS/BFS from `payload["body"]`, resolve `$ref` (incl. nested `groups`), never `furniture`; `_table_grid` = non-empty `data.grid` else `IngestError`; delete pin/torch/`_grid_from_table_data` helpers.
- [x] A.5 Merge delta → `openspec/specs/docling-ingest/spec.md` (*Native Table Grid and Body List* + import-free + pin MODIFY).
- [x] A.6 GREEN: `python -m pytest tests/ingest/test_extract.py tests/ingest/test_gold_compare.py` — gold unchanged.

## Phase B: Import scans (book / ground / query)

- [x] B.1 RED/GREEN import-scan: `extract.py`, `ground.py`, and book→query graph modules ban `docling` / `docling_core` / `torch` / `PINNED_DOCLING` (spec *Import-Free Recipe Extract Path*).
- [x] B.2 Confirm no API change to `recorded_book` / `query`; cache-hit load stays serve-free.
- [x] B.3 Note gap only (no code): `reply.py` → drawers → `DoclingReader`; Dockerfile keeps `.[retrieval]` (design/archive).

## Phase C: pyproject + CI

- [x] C.1 `pyproject.toml`: add `ingest = ["httpx==0.28.1"]`; strip `httpx` from `[docling]` (keep docling/graph pins; `deepseek` may keep httpx).
- [x] C.2 `.github/workflows/pytest.yml`: Kernel `dev`; Product `dev`+`http` (no Docling); heavy = `dev`+`ingest`+`docling`+`retrieval`+`http` (+`deepseek` if openwebui); keep full `tests/ingest` on heavy job.
- [x] C.3 GREEN: convert_local mocks resolve via `ingest` extra; no accidental product-job convert without httpx.

## Phase D: Active change + verify prep

- [x] D.1 `AGENTS.md`: set Active change to `openspec/changes/runtime-json-book/`.
- [x] D.2 Smoke/verify checklist (manual; not default pytest): optional cache-hit `recorded_book`+`query` on hashed artifacts without Docling wheel; full `python -m pytest` green; confirm reply/retrieval gap named for archive.
