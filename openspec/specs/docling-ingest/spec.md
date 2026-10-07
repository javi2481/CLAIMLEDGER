# Docling-Ingest Specification

## Purpose

Local corpus PDFs → hashed immutable DoclingDocument JSON. Markdown is not SoT.

## Requirements

### Requirement: In-Corpus Local PDFs

Every PDF in `docs/archivos_muestra` MUST be in-corpus. Convert MUST be local. The system MUST NOT fetch a URL.

#### Scenario: Directory files are in corpus

- GIVEN PDFs in `docs/archivos_muestra`
- WHEN ingest enumerates the corpus
- THEN all MUST be in-corpus and MUST NOT be fetched by URL

#### Scenario: URL convert is forbidden

- GIVEN a non-local PDF location
- WHEN convert is requested
- THEN the system MUST NOT fetch a URL

### Requirement: Hashed Immutable JSON Store

Parse MUST persist immutable JSON at `artifacts/docling/<sha256>.json`. Present hash MUST load without reconvert. Missing hash MUST convert locally and persist. Markdown MUST NOT be reconstruct SoT.

#### Scenario: Load or convert by hash

- GIVEN a corpus PDF
- WHEN ingest is asked for that document
- THEN it MUST load `artifacts/docling/<sha256>.json` if present, else convert locally and persist

### Requirement: Docling Pin Without Graph

Ingest MUST pin `docling==2.130.0` and MUST NOT import `docling-graph`. MinerU, VLM, Graph, LlamaIndex, HTTP, and UI MUST NOT be used.

#### Scenario: Pin and graph ban

- GIVEN ingest dependencies
- WHEN ingest runs
- THEN `docling==2.130.0` MUST be the parser and `docling-graph` MUST NOT be imported

### Requirement: Sidecar Page Raster Outside the Hash

At conversion, each page PNG MUST be written as a sidecar beside `artifacts/docling/<artifact_hash>.json` and outside `canonical_json_bytes`. `artifact_hash` MUST be the digest of those JSON bytes only and MUST NOT change because pixels were exported. If export would absorb pixels into the hashed payload, those pixels MUST be stripped before the hash. The parser pin MUST stay `docling==2.130.0`. The PDF MUST NOT be re-rasterized at question time. A missing sidecar MUST leave the hashed JSON unchanged. Tests of this rule MUST use a synthetic payload and MUST NOT import `docling`, open a PDF, use the network, or start Docker.

#### Scenario: Sidecar does not move the hash

- GIVEN JSON that is otherwise identical
- WHEN a page PNG is written beside `artifacts/docling/<artifact_hash>.json`
- THEN `artifact_hash` MUST equal the hash of `canonical_json_bytes` with no pixel bytes

#### Scenario: Absorbed pixels are stripped

- GIVEN an export payload that includes page pixels
- WHEN the artifact is hashed
- THEN those pixels MUST be removed before `canonical_json_bytes`
- AND the digest MUST match the stripped JSON

#### Scenario: Hash proof stays synthetic

- GIVEN a test of this sidecar rule
- WHEN pytest runs
- THEN it MUST use a synthetic payload
- AND it MUST NOT import `docling`, open a PDF, use the network, or start Docker

### Requirement: DocLang Sidecar On Every Parse

Every successful persist of `artifacts/docling/<artifact_hash>.json` MUST also write `artifacts/docling/<artifact_hash>.dclg`. The `.dclg` body MUST be `DoclingDocument.export_to_doclang()` of that same JSON payload. The write MUST happen inside `load_or_convert`, both when `convert_pdf` runs and when a cached JSON has no sidecar yet. A cached JSON that already has the sidecar MUST NOT call `convert_pdf`. `artifact_hash` MUST remain the digest of `canonical_json_bytes` and MUST NOT include the `.dclg` bytes. DocLang MUST NOT be the source read by retrieval or by Claim Query. Markdown MUST NOT be written as a substitute.

#### Scenario: Fresh convert writes JSON and DocLang

- GIVEN a local PDF with no artifact
- WHEN `load_or_convert` converts it
- THEN `artifacts/docling/<artifact_hash>.json` MUST exist
- AND `artifacts/docling/<artifact_hash>.dclg` MUST exist
- AND the `.dclg` text MUST equal `export_to_doclang()` of that JSON
- AND `artifact_hash` MUST equal the hash of the canonical JSON bytes

#### Scenario: Cached JSON gains DocLang without reconvert

- GIVEN a hashed JSON and a manifest entry, and no `.dclg` beside it
- WHEN `load_or_convert` is called for that same local PDF
- THEN the sidecar MUST be written from the stored JSON
- AND `convert_pdf` MUST NOT run
- AND the artifact hash MUST stay the same

#### Scenario: Second call is a no-op

- GIVEN JSON and `.dclg` already stored for a PDF
- WHEN `load_or_convert` runs again
- THEN `convert_pdf` MUST NOT run
- AND both files MUST stay in place

### Requirement: Corpus Pass Covers Every Sample PDF

An explicit corpus pass MUST call `load_or_convert` once for every PDF in `docs/archivos_muestra` (the ten BYMA files). Each file MUST end with a manifest entry, a hashed JSON, and a `.dclg` sibling. The pass MUST be local. It MUST NOT fetch a URL. It MUST NOT extract recipe claims from comunicado, deck, memoria, or transcript files. Default kernel pytest MUST NOT import `docling`, open those PDFs, or run this pass. This pass closes phase 1. It is not phase 8 and it does not open phase 9.

#### Scenario: Ten local files are stored

- GIVEN the ten PDFs in `docs/archivos_muestra`
- WHEN the corpus pass finishes
- THEN each PDF sha256 MUST map to an artifact hash in `artifacts/docling/manifest.json`
- AND both `<artifact_hash>.json` and `<artifact_hash>.dclg` MUST exist

#### Scenario: Existing quarterly JSON is not reconverted

- GIVEN the 1T26 and 2T26 EEFF artifacts already stored
- WHEN the corpus pass runs
- THEN those artifact hashes MUST be unchanged
- AND only a missing `.dclg` MUST be added

#### Scenario: Default pytest does not convert the corpus

- GIVEN the kernel test suite
- WHEN `pytest` runs without the corpus pass
- THEN it MUST NOT import `docling`
- AND it MUST NOT open a PDF from `docs/archivos_muestra`

### Requirement: Native Table Grid and Body List

`extract_recipe` MUST read each table grid from the grid Docling already stored on that table. When that grid is absent and cells are present, it MUST obtain the grid from `TableData.grid` in the `docling==2.130.0` install. It MUST NOT keep a second span expansion. The list of body tables MUST come from `DoclingDocument.iterate_items` on that same install, with that method's default content layers. Furniture MUST stay out of the recipe. The function MUST still decide which table is the consolidated income statement, which column is the quarter, and which row is a recipe slot. It MUST NOT import `docling` at module level. Kernel tests MUST NOT import `docling`. Gold numbers MUST NOT change.

#### Scenario: Stored grid is used as saved

- GIVEN a table whose `data.grid` is already present
- WHEN `extract_recipe` reads that table
- THEN it MUST use that grid
- AND it MUST NOT rebuild the grid from cell spans

#### Scenario: Missing grid uses the library

- GIVEN a table with `table_cells` and no `grid`
- WHEN `extract_recipe` reads that table
- THEN the grid MUST be `TableData.grid` from the pinned install

#### Scenario: Body list skips furniture

- GIVEN a furniture table and a body table in one document
- WHEN `extract_recipe` lists tables
- THEN only the body table MAY yield a recipe claim
- AND the list MUST come from `iterate_items`

#### Scenario: Recipe choice stays local

- GIVEN the body tables of a quarterly EEFF
- WHEN a recipe claim is built
- THEN the income-statement test, the quarter column, and the row slot MUST remain local code
- AND the consolidated net income for 2026-03-31 MUST remain `21262335`
