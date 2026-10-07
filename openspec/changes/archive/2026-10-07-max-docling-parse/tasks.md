# Tasks: max-docling-parse

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–480 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Serve-only convert + store | single | `python -m pytest tests/ingest/ -q` | Smoke checklist (Phase 6); N/A in default pytest | Revert `parse.py`, `store.py`, Compose, `pyproject`, ingest tests |

Threat matrix: N/A (no RED threat tasks). Keep `extract_recipe` + `.[docling]`. Kernel: no `docling`/httpx/network.

## Phase 1: RED — mock HTTP ZIP (Strict TDD first)

- [x] 1.1 RED `tests/ingest/test_store.py` (or sibling): happy path mocks httpx ZIP (`document.json`+`.dclg`+`page-*.png`); assert POST `/v1/convert/file` with `target_type=zip`, `image_export_mode=referenced`, `ocr_preset=rapidocr`; no network/PDF/Docker.
- [x] 1.2 RED: seal ON/OFF fields (`do_ocr`, `ocr_lang=["es"]`, tables/heading/picture-class ON; picture-description/chart/code/formula/`vlm_pipeline_*` OFF).
- [x] 1.3 RED: happy path never imports/calls `DocumentConverter`, `download_models`, `export_to_doclang`.
- [x] 1.4 RED: non-`Path`/URL/`/v1/convert/source` → `IngestError`; cache hit JSON+`.dclg` skips HTTP; missing `.dclg` recompiles via `convert_local`.
- [x] 1.5 RED: Compose snippet asserts `DOCLING_SERVE_ENABLE_REMOTE_SERVICES="false"` and no `claimledger` `depends_on` serve. Run `pytest tests/ingest/` — fail for missing API (right reason).

## Phase 2: Compose + httpx extra

- [x] 2.1 `docker-compose.yml`: `docling-serve` = `quay.io/docling-project/docling-serve-cpu:v1.35.0`, port `5001`, remote=false, UI off if pin supports, healthcheck `GET /version`; claimledger no `depends_on`; replace site-packages Docling mount with `./artifacts/docling:/app/artifacts/docling:ro`.
- [x] 2.2 `pyproject.toml`: `httpx==0.28.1` in `[docling]` (keep `[deepseek]` pin).

## Phase 3: GREEN — `convert_local` client

- [x] 3.1 `src/claimledger/ingest/types.py`: add `ConvertBundle` (`payload`, `doclang`, `page_pngs`) if not private in parse.
- [x] 3.2 `src/claimledger/ingest/parse.py`: `convert_local(Path)` — lazy httpx multipart to `{DOCLING_SERVE_URL}/v1/convert/file` (default `http://127.0.0.1:5001`); seal + ZIP unpack; `IngestError` on bad Path/down/non-2xx/missing json|dclg; thin `convert_pdf` MAY alias `.payload`.
- [x] 3.3 GREEN: Phase 1 convert/seal/URL tests pass; no embedded converter left on convert path.

## Phase 4: Store wire + delete embedded

- [x] 4.1 `store.py`: miss/missing `.dclg` → `convert_local` → `strip_page_pixels` → hash → write `.json`/ZIP `.dclg`/`{hash}.p{n}.png` + manifest; hit with both loads only; drop `_ensure_doclang` / `doclang_from_payload`.
- [x] 4.2 Delete from `parse.py`/`store.py`: `DocumentConverter`+pipeline options, `download_models`/`model_artifacts_path`, torch convert hack, `_require_pinned_docling`, `last_page_pngs`/`_png_bytes`/memory sidecars.
- [x] 4.3 GREEN: full `tests/ingest/` green; kernel suite still docling-free (`python -m pytest`).

## Phase 5: Active-change docs

- [x] 5.1 `AGENTS.md`: set Active change to `openspec/changes/max-docling-parse/` (brief note only; no rector rewrite).

## Phase 6: Smoke checklist (manual; not default pytest)

- [x] 6.1 Checklist (verify-report later): serve up → `GET /version` require serve `1.35.0` + docling/slim `2.130.0` (not core/parse==2.130.0) → one corpus PDF → `.json`+`.dclg`+`.pN.png`+manifest → query with serve stopped still serves artifacts; lock ZIP member names if they differ.
  - Documented in `design.md` § Smoke `/version`. Manual run deferred to `sdd-verify`.
