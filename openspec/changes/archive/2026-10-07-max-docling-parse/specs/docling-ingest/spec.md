# Delta for Docling-Ingest

## ADDED Requirements

### Requirement: Docling-Serve Convert Only

Convert MUST be 100% via local docling-serve `POST /v1/convert/file` with local `Path`. MUST NOT call `/v1/convert/source`, use `http_sources`, or fetch URLs. Primitive MUST be `convert_local` (`convert_pdf` MAY alias). MUST NOT use `DocumentConverter`, `download_models`, or `export_to_doclang`. Query MUST NOT call serve. Form MUST set `target_type=zip`, `image_export_mode=referenced`, `ocr_preset=rapidocr`. Persist MUST unpack ZIP JSON/DocLang/PNGs only; missing ZIP DocLang MUST `IngestError`.

#### Scenario: Posts ZIP convert/file

- GIVEN local PDF and reachable serve
- WHEN `convert_local` runs
- THEN multipart-POST `{DOCLING_SERVE_URL}/v1/convert/file` with `target_type=zip`, `image_export_mode=referenced`, `ocr_preset=rapidocr`; no `/v1/convert/source` or URL

#### Scenario: Embedded compiler banned

- GIVEN convert happy path
- WHEN convert executes
- THEN no `DocumentConverter`, `download_models`, or `export_to_doclang`; artifacts from ZIP only

#### Scenario: Query independent of serve

- GIVEN hashed JSON stored
- WHEN query / `extract_recipe` runs
- THEN docling-serve MUST NOT be called

### Requirement: Non-VLM Dual Seal

Client MUST seal `do_ocr=true`, `ocr_preset=rapidocr`, `ocr_lang=["es"]` (or pin Spanish tag), accurate tables, picture classification, PDF heading hierarchy when accepted, page/images on; VLM/picture-description/chart/code/formula OFF (no `vlm_pipeline_*`). Compose MUST set `DOCLING_SERVE_ENABLE_REMOTE_SERVICES=false`. Claimledger MUST NOT `depends_on` serve.

#### Scenario: Client seal and remote off

- GIVEN convert form and Compose `docling-serve`
- WHEN inspected
- THEN `ocr_preset=rapidocr`, VLM flags false/absent, `DOCLING_SERVE_ENABLE_REMOTE_SERVICES="false"`

### Requirement: Serve Version Pin Smoke

Pin MUST be `quay.io/docling-project/docling-serve-cpu:v1.35.0` (slim `2.130.0`). Smoke MUST `GET /version` requiring serve `1.35.0` + docling/slim `2.130.0`; MUST NOT require core/parse `==2.130.0`. Convert MUST NOT pin in-process docling as parser.

#### Scenario: /version pin

- GIVEN serve up
- WHEN smoke reads `/version`
- THEN serve `1.35.0` and docling/slim `2.130.0`

### Requirement: Convert Unit Tests Mock HTTP

Convert/store unit tests MUST mock HTTP/ZIP; MUST NOT network, open corpus PDFs, or Docker. Kernel tests MUST NOT import `docling`.

#### Scenario: Default pytest offline

- GIVEN convert/store unit tests
- WHEN default `pytest` runs
- THEN HTTP mocked; no PDF/network/Docker

## MODIFIED Requirements

### Requirement: In-Corpus Local PDFs

Every PDF in `docs/archivos_muestra` MUST be in-corpus. Convert MUST be local via `convert_local` to docling-serve. MUST NOT fetch URL or use `/v1/convert/source`.
(Previously: local convert without serve; URL ban only.)

#### Scenario: Directory files are in corpus

- GIVEN PDFs in `docs/archivos_muestra`
- WHEN ingest enumerates
- THEN all in-corpus; no URL fetch

#### Scenario: URL convert is forbidden

- GIVEN non-local PDF location
- WHEN convert requested
- THEN no URL fetch and no `/v1/convert/source`

### Requirement: Hashed Immutable JSON Store

Persist immutable JSON at `artifacts/docling/<sha256>.json`. Present hash MUST load without reconvert. Missing hash MUST `convert_local` and persist. Markdown MUST NOT be reconstruct SoT. `load` MUST recompute SHA-256 and reject mismatch. Cache hit MUST same-check and MUST NOT `convert_local` on mismatch.
(Previously: named `convert_pdf`.)

#### Scenario: Load or convert by hash

- GIVEN corpus PDF
- WHEN ingest asked for document
- THEN load `artifacts/docling/<sha256>.json` if present, else `convert_local` and persist

#### Scenario: Mismatched bytes are rejected

- GIVEN file bytes ≠ requested name hash
- WHEN `load` called
- THEN raise `IngestError`

#### Scenario: Cache hit does not reconvert a mismatch

- GIVEN manifest JSON bytes ≠ recorded hash
- WHEN `load_or_convert` hits cache
- THEN raise `IngestError`; `convert_local` MUST NOT run

### Requirement: Docling Pin Without Graph

Compiler MUST be serve `v1.35.0` / slim `2.130.0` via `/version`. Convert MUST NOT import `docling-graph`. MinerU, convert-path VLM, Graph, LlamaIndex, UI MUST NOT serve convert. `extract_recipe` MAY use `docling_core` / `.[docling]` (removal OOS). Convert MAY HTTP to local serve; query MUST NOT.
(Previously: in-process `docling==2.130.0`; HTTP banned.)

#### Scenario: Pin and graph ban

- GIVEN ingest convert
- WHEN convert runs
- THEN pin serve `1.35.0` + slim `2.130.0`; no `docling-graph` on convert path

#### Scenario: extract_recipe may keep docling_core

- GIVEN `extract_recipe` on hashed JSON
- WHEN library helpers needed
- THEN MAY use `docling_core` without embedded convert

### Requirement: Sidecar Page Raster Outside the Hash

Page PNGs MUST come from ZIP (`image_export_mode=referenced`) beside `artifacts/docling/<artifact_hash>.json`, outside `canonical_json_bytes`. Hash digests JSON only; strip absorbed pixels before hash. No question-time re-rasterize. Missing sidecar leaves JSON unchanged. Unit tests: synthetic payload; no `docling`/PDF/network/Docker.
(Previously: in-process PNGs; in-process pin required.)

#### Scenario: Sidecar does not move the hash

- GIVEN otherwise identical JSON
- WHEN page PNG written beside artifact
- THEN `artifact_hash` equals `canonical_json_bytes` digest without pixels

#### Scenario: Absorbed pixels are stripped

- GIVEN payload with page pixels
- WHEN hashed
- THEN pixels removed before `canonical_json_bytes`; digest matches stripped JSON

#### Scenario: Hash proof stays synthetic

- GIVEN sidecar-rule test
- WHEN pytest runs
- THEN synthetic payload; no `docling`/PDF/network/Docker

### Requirement: DocLang Sidecar On Every Parse

Persist MUST write `<artifact_hash>.dclg` from ZIP DocLang. MUST NOT use `export_to_doclang()`. Missing `.dclg` MUST recompile via `convert_local`. Cache hit with JSON+`.dclg` MUST NOT convert. Hash excludes `.dclg`. DocLang MUST NOT feed retrieval/Claim Query. Markdown MUST NOT substitute.
(Previously: `.dclg`=`export_to_doclang()`; backfill without reconvert.)

#### Scenario: Fresh convert writes JSON and DocLang

- GIVEN local PDF, no artifact
- WHEN `load_or_convert` converts
- THEN JSON + ZIP `.dclg` exist; not local `export_to_doclang()`; hash = JSON digest

#### Scenario: Missing DocLang forces recompile

- GIVEN hashed JSON, no `.dclg`
- WHEN `load_or_convert` runs
- THEN `convert_local` recompiles; no `export_to_doclang`

#### Scenario: Second call is a no-op

- GIVEN JSON and `.dclg` stored
- WHEN `load_or_convert` again
- THEN `convert_local` MUST NOT run; files stay

### Requirement: Corpus Pass Covers Every Sample PDF

Pass MUST `load_or_convert` once per PDF in `docs/archivos_muestra` (ten BYMA). Each MUST have manifest, hashed JSON, compiler `.dclg`. Local via serve; no URL; no recipe from comunicado/deck/memoria/transcript. Default kernel pytest: no `docling`, no those PDFs, no pass. Closes phase 1; not 8/9.
(Previously: embedded convert; missing `.dclg` without reconvert.)

#### Scenario: Ten local files are stored

- GIVEN ten PDFs in `docs/archivos_muestra`
- WHEN corpus pass finishes
- THEN each PDF sha256 maps in `manifest.json`; JSON and `.dclg` exist

#### Scenario: Existing quarterly JSON is not reconverted when complete

- GIVEN 1T26/2T26 EEFF with matching `.dclg`
- WHEN corpus pass runs
- THEN hashes unchanged; `convert_local` MUST NOT run for those

#### Scenario: Default pytest does not convert the corpus

- GIVEN kernel suite
- WHEN `pytest` without corpus pass
- THEN no `docling` import; no PDF from `docs/archivos_muestra`
