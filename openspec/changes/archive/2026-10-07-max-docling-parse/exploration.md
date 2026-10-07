## Exploration: max-docling-parse (docling-serve offline ingest)

Architecture is CLOSED. Approved plan: Docling Serve **v1.35.0** = document compiler (offline, non-VLM, no remote); CLAIMLEDGER = verification kernel. Convert path must stop embedding `DocumentConverter` / `export_to_doclang` / in-process model download. Query runtime must not depend on docling-serve.

### Current State

Inspected via CodeGraph + source (not guessed). Call path today:

`load_or_convert` → `convert_pdf` → `_require_pinned_docling` → `DocumentConverter` + `download_models` → in-memory PNGs (`last_page_pngs`) → `strip_page_pixels` → hash JSON → `_ensure_doclang` via `doclang_from_payload` (`export_to_doclang`) → `_write_page_sidecars`.

| Area | Today | Plan target |
|------|--------|-------------|
| Compiler | Embedded `docling==2.130.0` in-process (`parse.convert_pdf`) | `quay.io/docling-project/docling-serve-cpu:v1.35.0` only |
| Transport | In-process dict + module-global PNG map | ZIP `target_type=zip` + `image_export_mode=referenced` from `POST /v1/convert/file` |
| OCR / enrich | `do_ocr=False`; no rapidocr / table / heading / picture classification seal | Client seal: rapidocr + `ocr_lang=["es"]` + native non-VLM ON; VLM flags OFF |
| Pin check | `version("docling") == 2.130.0` in process | Smoke `/version`: serve `1.35.0` + docling/slim `2.130.0` only |
| DocLang | Regenerated locally with `export_to_doclang` (also cache backfill) | Persist `.dclg` bytes from ZIP; **recompile with serve** if missing — no local export fallback |
| HTTP client | `httpx==0.28.1` only under `[deepseek]` | Same pin for convert client (extra placement in design) |
| Compose | `claimledger` + `openwebui`; volume mounts `./artifacts/docling` over `site-packages/docling:ro` | Add `docling-serve`; `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=false`; claimledger runtime **does not** depend on serve; remove convert-era mount misuse |
| `extract_recipe` | Still uses `docling_core` (`iterate_items`, `TableData.grid`) | **Keep** this change; follow-up for pure-JSON extract |
| Kernel | No docling import | Unchanged |

Main spec `openspec/specs/docling-ingest/spec.md` still requires:

- In-process pin `docling==2.130.0` as **parser**
- `.dclg` MUST equal `export_to_doclang()` of the JSON
- Cache miss / backfill of `.dclg` without reconvert via local export
- Scenarios name `convert_pdf` as the convert primitive

Those requirements conflict with the approved serve-only convert path and need a delta.

### Affected Areas

- `src/claimledger/ingest/parse.py` — replace embedded convert with `convert_local` (httpx multipart → ZIP unpack); remove `DocumentConverter`, `download_models`, torch order hack for convert, `doclang_from_payload`, `last_page_pngs` / `_png_bytes` / `_remember_page_pngs`; pin moves to service `/version`
- `src/claimledger/ingest/store.py` — `load_or_convert` wires to ZIP persist; drop `_ensure_doclang` regeneration; PNGs from ZIP referenced names → `{hash}.p{n}.png` (or design-named mapping); missing `.dclg` policy = recompile, not export
- `docker-compose.yml` — new `docling-serve` service (pin, remote=false, healthcheck `/version`, no UI); claimledger no `depends_on` serve; reconsider/remove `artifacts/docling` → `site-packages/docling` mount
- `pyproject.toml` — expose `httpx==0.28.1` for ingest convert client; keep `.[docling]` for extract/graph until follow-up
- `openspec/specs/docling-ingest/spec.md` — MODIFIED/ADDED delta: serve compiler, ban `/v1/convert/source`+URL, ZIP+referenced, non-VLM dual seal, DocLang from compiler only
- `tests/ingest/test_store.py` (and related) — rewrite happy path around mock ZIP HTTP; assert no `DocumentConverter` / `export_to_doclang`; seal form fields; Compose remote=false; URL reject
- `src/claimledger/ingest/ground.py`, `tests/ingest/test_gold_compare.py`, extract tests — still call `load_or_convert`; behavior stays hashed JSON + recipe; convert backend changes
- Out of scope (follow-up): pure-JSON `extract_recipe`, drop `docling` extra, VLM/chart, Redis/async workers, `runtime-json-book`

### Approaches

1. **Docling-serve-only convert (approved plan)** — `convert_local(Path)` → `POST {DOCLING_SERVE_URL}/v1/convert/file` with non-VLM seal + ZIP referenced; unpack → strip → hash + persist `.dclg`/PNGs; remove embedded compiler from convert path; keep `extract_recipe` + `docling_core`.
   - Pros: Matches approved thesis (compiler vs kernel); remote services off at infra; OCR/enrichment without VLM; query path stays offline of serve; pin alignment with official CPU image 1.35.0 / slim 2.130.0; Strict TDD with mock ZIP.
   - Cons: Compose + smoke dependency for real corpus recompile; legacy artifacts without compiler `.dclg` need re-ingest; delta rewrites several `docling-ingest` scenarios; httpx must be available outside DeepSeek-only extra.
   - Effort: Medium

2. **Keep embedded DocumentConverter; optional serve sidecar** — Leave `convert_pdf` as primary; add serve as optional enrichment.
   - Pros: Smaller code delta; existing tests mostly stand.
   - Cons: Violates approved plan; dual compilers; still ships torch/models in process; DocLang regeneration stays; Architecture Gate / native-compiler boundary blur.
   - Effort: Low — **reject**

3. **Hybrid: serve for OCR-on, embedded for cache/DocLang backfill** — Call serve on miss; keep `export_to_doclang` for missing sidecars.
   - Pros: Soft migration for existing artifacts.
   - Cons: Explicitly forbidden by plan (“No reintroducir `export_to_doclang` as fallback”); two DocLang authorities.
   - Effort: Medium — **reject**

### Recommendation

Take approach **1** exactly as in `docling-serve_ingest_0f758df7.plan.md`:

1. OpenSpec change `max-docling-parse` — delta `docling-ingest` for 100% serve convert, URL ban, dual non-VLM seal, ZIP+referenced, `.dclg`/PNG from ZIP only.
2. Compose: pinned CPU image `v1.35.0`, `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=false`, healthcheck `/version`; claimledger runtime independent.
3. Client: local `Path` only; form seal with `ocr_preset=rapidocr`, `ocr_lang=["es"]`, non-VLM flags false; never `/v1/convert/source`.
4. Store: unpack → strip pixels → SHA-256 JSON + persist DocLang/PNGs from ZIP; remove embedded convert helpers from `parse.py` / `store.py`.
5. Tests: mock httpx/ZIP first (Strict TDD); smoke documents serve `1.35.0` + slim `2.130.0` only (do not require core/parse == 2.130.0).
6. Keep `extract_recipe` + `.[docling]` until a named follow-up.

### Risks

- **Spec rewrite blast**: DocLang and “docling is the parser” requirements are normative today; incomplete MODIFIED scenarios will fail verify.
- **Artifact invalidation**: Existing hashes may change when OCR/enrichment turns on vs current `do_ocr=False` convert; gold compare / recorded_book may need recompile of EEFF artifacts before product checks.
- **ZIP layout naming**: Plan expects `document.json` / `document.dclg` / `page-*.png`; client must map serve ZIP member names carefully (design after smoke if names differ).
- **httpx packaging**: Currently only `[deepseek]`; convert client needs a deliberate extra without pulling Docling into kernel tests or forcing network in default pytest.
- **Compose mount**: Current `artifacts/docling` → `site-packages/docling` is unrelated to a healthy serve client; removing it must not break the query image’s hashed-JSON read path (artifacts should be mounted as data, not as package overlay).
- **Windows/CI**: Default pytest must stay mock-only (no live serve, no PDF, kernel still docling-free).

### Ready for Proposal

Yes. Orchestrator should run `sdd-propose` for `max-docling-parse` with scope locked to the approved plan (serve-only convert, keep extract_recipe follow-up explicit). No clarification blockers; open design details (exact ZIP member names, which optional-extra owns httpx, PNG filename mapping) belong in `sdd-design` after proposal/spec skeleton.
