# JSON Retrieval Specification

## Purpose

Candidates from hashed Docling JSON.

## Requirements

### Requirement: Hashed JSON Reader

Retrieval MUST read an existing hashed Docling JSON artifact. It MUST NOT convert a PDF or fetch a URL. The reader MUST use JSON. Markdown MUST NOT be the source of truth.

#### Scenario: Stored JSON

- GIVEN a stored hashed JSON artifact
- WHEN retrieval loads it
- THEN it MUST read JSON, with no PDF conversion, URL fetch, or Markdown source of truth

#### Scenario: Missing artifact or Markdown default

- GIVEN no artifact, or a Markdown default
- WHEN retrieval is requested
- THEN PDF conversion, URL fetch, and Markdown as source of truth MUST NOT occur

### Requirement: Two Drawers

A tables request MUST NOT return narrative nodes. A narrative request MUST NOT return table nodes.

#### Scenario: Tables exclude narrative

- GIVEN nodes in both drawers
- WHEN tables are requested
- THEN narrative nodes MUST NOT be returned

#### Scenario: Narrative excludes tables

- GIVEN nodes in both drawers
- WHEN narrative is requested
- THEN table nodes MUST NOT be returned

### Requirement: Candidates Only

The result MUST be candidates only. It MUST NOT set `verified` or `abstained`, write a `FinancialClaim`, or call `query`. Both neighbor rows MAY appear as table candidates. Choosing between them is not this capability.

#### Scenario: Candidates only

- GIVEN found nodes
- WHEN retrieval returns
- THEN it MUST be candidates only, with no `verified`, `abstained`, `FinancialClaim`, or `query` call

#### Scenario: Both neighbor rows

- GIVEN both neighbor rows
- WHEN tables are requested
- THEN both MAY appear and retrieval MUST NOT choose between them
