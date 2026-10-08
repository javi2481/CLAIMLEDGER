# Delta for Docling-Ingest

## MODIFIED Requirements

### Requirement: Import-Free Recipe Extract Path

`extract_recipe`, `ground`, and the product book/query path for hashed recipe claims MUST NOT import `docling`, `docling_core`, or `torch`, and MUST NOT load an in-process Docling pin (`PINNED_DOCLING` or equivalent) for body listing or grid materialization. Product `reply`, `measure`, and card MUST NOT import `DoclingReader`. The product image MUST NOT install `.[retrieval]`. Convert via local docling-serve and graph pin rules are unchanged. Gold numbers MUST stay frozen. Kernel tests MUST NOT import `docling`.

(Previously: Open WebUI `reply` / `DoclingReader` / Docker `.[retrieval]` were out of scope.)

#### Scenario: Extract sources ban Docling imports

- GIVEN `extract_recipe` and its direct extract helpers
- WHEN sources are inspected
- THEN they MUST NOT reference `docling`, `docling_core`, `torch`, or `PINNED_DOCLING`

#### Scenario: Book path stays Docling-free at import time

- GIVEN hashed JSON and a cache-hit load
- WHEN `recorded_book` / `ground` / `query` run for recipe claims
- THEN those modules MUST NOT require `docling` / `docling_core` / `torch` installed

#### Scenario: Reply retrieval is no longer deferred

- GIVEN `reply`, `measure`, `card`, and the product Dockerfile
- WHEN imports and install extras are read
- THEN those modules MUST NOT import `DoclingReader`
- AND the image MUST NOT install `.[retrieval]`
