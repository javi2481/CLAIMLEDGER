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
