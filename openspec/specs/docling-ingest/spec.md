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
