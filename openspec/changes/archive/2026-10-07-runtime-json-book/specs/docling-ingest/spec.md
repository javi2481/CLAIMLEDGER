# Delta for Docling-Ingest

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Docling Pin Without Graph

Compiler MUST be serve `v1.35.0` / slim `2.130.0` via `/version`. Convert MUST NOT import `docling-graph`. MinerU, convert-path VLM, Graph, LlamaIndex, UI MUST NOT serve convert. `extract_recipe` MUST NOT use `docling_core` / in-process pinned `docling` for body list or grid. Convert MAY HTTP to local serve; query MUST NOT.

(Previously: `extract_recipe` MAY use `docling_core` / `.[docling]`; removal OOS.)

#### Scenario: Pin and graph ban

- GIVEN ingest convert
- WHEN convert runs
- THEN pin serve `1.35.0` + slim `2.130.0`; no `docling-graph` on convert path

#### Scenario: extract_recipe must not use docling_core

- GIVEN `extract_recipe` on hashed JSON
- WHEN body tables or grids are read
- THEN it MUST NOT import or call `docling_core` / pinned in-process `docling`

### Requirement: Native Table Grid and Body List

`extract_recipe` MUST read each table grid only from that table's stored non-empty `data.grid` in hashed JSON. Missing or empty `data.grid` MUST raise `IngestError`. It MUST NOT use `TableData`, cell/span expansion, or any in-process Docling pin. Body tables MUST come from a local walk of hashed JSON starting at `body`, resolving `$ref` into payload collections (including nested `groups`) to table refs. The walk MUST NOT enter `furniture`. Furniture MUST stay out of the recipe. Income-statement table, quarter column, and row slot choice MUST remain local. It MUST NOT import `docling` / `docling_core` / `torch` at module level or on the extract path. Kernel tests MUST NOT import `docling`. Gold numbers MUST NOT change.

(Previously: body via `iterate_items`; missing grid via pinned `TableData.grid`; in-process `docling==2.130.0` on extract.)

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
