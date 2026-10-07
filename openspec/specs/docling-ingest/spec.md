# Docling-Ingest Specification

## Purpose

Local corpus PDFs → hashed immutable DoclingDocument JSON. Markdown is not SoT. Convert is 100% via local docling-serve; CLAIMLEDGER hashes, stores, and verifies.

## Requirements

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

### Requirement: In-Corpus Local PDFs

Every PDF in `docs/archivos_muestra` MUST be in-corpus. Convert MUST be local via `convert_local` to docling-serve. MUST NOT fetch URL or use `/v1/convert/source`.

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

Compiler MUST be serve `v1.35.0` / slim `2.130.0` via `/version`. Convert MUST NOT import `docling-graph`. MinerU, convert-path VLM, Graph, LlamaIndex, UI MUST NOT serve convert. `extract_recipe` MUST NOT use `docling_core` / in-process pinned `docling` for body list or grid. Convert MAY HTTP to local serve; query MUST NOT.

#### Scenario: Pin and graph ban

- GIVEN ingest convert
- WHEN convert runs
- THEN pin serve `1.35.0` + slim `2.130.0`; no `docling-graph` on convert path

#### Scenario: extract_recipe must not use docling_core

- GIVEN `extract_recipe` on hashed JSON
- WHEN body tables or grids are read
- THEN it MUST NOT import or call `docling_core` / pinned in-process `docling`

### Requirement: Sidecar Page Raster Outside the Hash

Page PNGs MUST come from ZIP (`image_export_mode=referenced`) beside `artifacts/docling/<artifact_hash>.json`, outside `canonical_json_bytes`. Hash digests JSON only; strip absorbed pixels before hash. No question-time re-rasterize. Missing sidecar leaves JSON unchanged. Unit tests: synthetic payload; no `docling`/PDF/network/Docker.

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

### Requirement: Native Table Grid and Body List

`extract_recipe` MUST read each table grid only from that table's stored non-empty `data.grid` in hashed JSON. Missing or empty `data.grid` MUST raise `IngestError`. It MUST NOT use `TableData`, cell/span expansion, or any in-process Docling pin. Body tables MUST come from a local walk of hashed JSON starting at `body`, resolving `$ref` into payload collections (including nested `groups`) to table refs. The walk MUST NOT enter `furniture`. Furniture MUST stay out of the recipe. Income-statement table, quarter column, and row slot choice MUST remain local. It MUST NOT import `docling` / `docling_core` / `torch` at module level or on the extract path. Kernel tests MUST NOT import `docling`. Gold numbers MUST NOT change.

#### Scenario: Stored grid is used as saved

- GIVEN a table with non-empty `data.grid`
- WHEN `extract_recipe` reads that table
- THEN it MUST use that grid
- AND it MUST NOT rebuild from cell spans

#### Scenario: Missing grid is an error

- GIVEN a table with `table_cells` and no usable `data.grid`
- WHEN `extract_recipe` reads that table
- THEN it MUST raise `IngestError`
- AND it MUST NOT call `TableData` or any Docling pin

#### Scenario: Body list skips furniture

- GIVEN a furniture table and a body table in one document
- WHEN `extract_recipe` lists tables
- THEN only the body table MAY yield a recipe claim
- AND the list MUST come from a local JSON walk of `body` (not `iterate_items`, not `furniture`)

#### Scenario: Nested body refs are resolved

- GIVEN body children that `$ref` nested `groups` which `$ref` tables
- WHEN `extract_recipe` lists body tables
- THEN those tables MUST be included
- AND furniture refs MUST remain excluded

#### Scenario: Recipe choice stays local

- GIVEN the body tables of a quarterly EEFF
- WHEN a recipe claim is built
- THEN income-statement test, quarter column, and row slot MUST remain local code
- AND consolidated net income for 2026-03-31 MUST remain `21262335`

### Requirement: Import-Free Recipe Extract Path

`extract_recipe`, `ground`, and the product book/query path for hashed recipe claims MUST NOT import `docling`, `docling_core`, or `torch`, and MUST NOT load an in-process Docling pin (`PINNED_DOCLING` or equivalent) for body listing or grid materialization. Open WebUI `reply` / `DoclingReader` / Docker `.[retrieval]` remain out of scope (documented follow-up). Convert via local docling-serve and graph pin rules are unchanged.

#### Scenario: Extract sources ban Docling imports

- GIVEN `extract_recipe` and its direct extract helpers
- WHEN sources are inspected
- THEN they MUST NOT reference `docling`, `docling_core`, `torch`, or `PINNED_DOCLING`

#### Scenario: Book path stays Docling-free at import time

- GIVEN hashed JSON and a cache-hit load
- WHEN `recorded_book` / `ground` / `query` run for recipe claims
- THEN those modules MUST NOT require `docling` / `docling_core` / `torch` installed

#### Scenario: Reply retrieval remains deferred

- GIVEN this change
- WHEN scope is applied
- THEN `reply.py`, `retrieval/*`, and Dockerfile `.[retrieval]` MUST NOT be required to drop `DoclingReader`

### Requirement: Quarterly Book

The product book MUST be built by `recorded_book` in `src/claimledger/ingest/`, outside the seven kernel modules. It MUST `load_or_convert`, `classify`, and `extract_recipe` the two quarterly EEFF in `docs/archivos_muestra`, then `upsert` those claims into a new in-memory `Ledger`. It MUST NOT write a claim cache to disk. It MUST NOT call `Ledger.seed()`. A missing quarterly file MUST raise `IngestError`. Kernel tests MUST keep calling `query` on `Ledger.seed()` and MUST NOT import `docling`.

#### Scenario: Fourteen rows with evidence

- GIVEN the two quarterly EEFF files
- WHEN `recorded_book` runs
- THEN the book MUST hold the fourteen recipe values, including `21262335` and `21259769`
- AND each claim MUST have evidence
- AND `query` on that book for consolidated 1T26 net income MUST verify `21262335`

#### Scenario: Missing file

- GIVEN one quarterly EEFF file is absent
- WHEN `recorded_book` runs
- THEN it MUST raise `IngestError`
- AND it MUST NOT return `Ledger.seed()`
