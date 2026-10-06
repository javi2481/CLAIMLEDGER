# Delta for Docling Ingest

## ADDED Requirements

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
