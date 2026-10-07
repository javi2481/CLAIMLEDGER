# Delta for Docling Ingest

## ADDED Requirements

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
