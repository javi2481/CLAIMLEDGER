# Proposal: max-docling-parse

## Intent

**Docling Serve** (`docling-serve-cpu:v1.35.0`) = offline document compiler; **CLAIMLEDGER** = financial verification kernel. Remove embedded `DocumentConverter` / models / `export_to_doclang`. Query MUST NOT call serve.

## Scope

### In Scope

- Convert **100%** via `POST /v1/convert/file` to `quay.io/docling-project/docling-serve-cpu:v1.35.0` (slim **2.130.0**; not 1.36.0).
- Drop embedded convert: `DocumentConverter`, `download_models`, in-process pin, `doclang_from_payload` / `export_to_doclang`, `last_page_pngs`.
- ZIP + `image_export_mode=referenced`; `.dclg`/PNGs from ZIP only; missing `.dclg` ⇒ recompile (no local export).
- Dual non-VLM seal: client (rapidocr, `ocr_lang=["es"]`, native enrich ON, VLM OFF) + Compose `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=false`.
- Ban `/v1/convert/source` and URL fetch; local `Path` only.
- `load_or_convert` → `convert_local` → unpack → strip → SHA-256 + sidecars.
- Compose `docling-serve`; runtime no `depends_on`; drop convert-era `site-packages/docling` mount.
- `httpx==0.28.1`; Strict TDD mock ZIP; delta `docling-ingest`.

### Out of Scope

- Pure-JSON `extract_recipe` / drop `docling_core` + `.[docling]` (follow-up).
- `runtime-json-book`, VLM/chart, Redis/async, CUDA.
- Kernel/gold changes; Markdown as SoT; MinerU.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `docling-ingest`: Compiler is docling-serve. DocLang from ZIP only; missing `.dclg` recompiles via serve. Primitive `convert_local`. Pin smoke = `/version` (1.35.0 + slim 2.130.0). PNGs from ZIP. Non-VLM dual seal + remote-off normative. URL convert forbidden.

## Approach

Delta `docling-ingest` → Compose pinned serve → `convert_local` (httpx; thin `convert_pdf` alias MAY remain) → ZIP persist → drop embedded helpers → mock-ZIP tests + smoke. Keep `extract_recipe`+`docling_core` until follow-up.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/ingest/parse.py` | Modified | Serve client; drop embedded compiler |
| `src/claimledger/ingest/store.py` | Modified | ZIP persist; no DocLang regen |
| `docker-compose.yml` | Modified | Add serve; fix mounts |
| `pyproject.toml` | Modified | httpx for convert client |
| `openspec/specs/docling-ingest/spec.md` | Modified | Requirement delta |
| `tests/ingest/` | Modified | Mock ZIP happy path |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Spec blast vs `export_to_doclang` | High | Full MODIFIED delta |
| Hash drift (OCR on) | Med | Recompile EEFF artifacts |
| ZIP member names | Med | Smoke; lock in design |
| httpx vs kernel | Med | Extra + mock-only pytest |

## Rollback Plan

Revert `parse.py`, `store.py`, Compose, spec. Keep prior hashes; do not promote OCR-recompiled artifacts. Kernel unchanged.

## Dependencies

- `docling-serve-cpu:v1.35.0`; `httpx==0.28.1`; plan `docling-serve_ingest_0f758df7`.

## Success Criteria

- [ ] Convert only via serve v1.35.0; no `DocumentConverter` / `download_models` / `export_to_doclang` on happy path
- [ ] ZIP+referenced; `.dclg`/PNGs from ZIP; remote off; no URL convert
- [ ] Query works with serve down; kernel/gold intact; Markdown not SoT
- [ ] Default pytest mock-only; smoke documents `/version` pin
- [ ] `extract_recipe`+`docling_core` deferred explicitly
