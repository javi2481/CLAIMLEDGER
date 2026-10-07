# Delta for Docling Ingest

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Hashed Immutable JSON Store

Parse MUST persist immutable JSON at `artifacts/docling/<sha256>.json`. Present hash MUST load without reconvert. Missing hash MUST convert locally and persist. Markdown MUST NOT be reconstruct SoT. `load` MUST recompute the SHA-256 of the stored file bytes and MUST reject the file when that digest is not the requested hash. A cache hit in `load_or_convert` MUST use the same check and MUST NOT call `convert_pdf` when the bytes do not match.

#### Scenario: Load or convert by hash

- GIVEN a corpus PDF
- WHEN ingest is asked for that document
- THEN it MUST load `artifacts/docling/<sha256>.json` if present, else convert locally and persist

#### Scenario: Mismatched bytes are rejected

- GIVEN a file whose bytes do not hash to the requested name
- WHEN `load` is called with that name
- THEN it MUST raise `IngestError`

#### Scenario: Cache hit does not reconvert a mismatch

- GIVEN a manifest entry whose JSON bytes do not match the recorded hash
- WHEN `load_or_convert` hits that cache
- THEN it MUST raise `IngestError`
- AND `convert_pdf` MUST NOT run
