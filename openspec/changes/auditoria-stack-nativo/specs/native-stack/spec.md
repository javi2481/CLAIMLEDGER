# Native Stack Specification

## Purpose

Custom code exists only for a job the pinned stack cannot do. The stack is Docling `2.130.0`, its DocLang export, docling-graph `1.9.1`, LlamaIndex docling reader and node parser `0.5.0`, Starlette `1.0.0`, and Open WebUI `v0.11.4-slim`.

The check is an on-demand function. It is not a numbered wave phase. Phase 8 remains the page crop.

## Requirements

### Requirement: Native Call Before Custom Code

A change MUST NOT add a script or module for a job one of those pieces already does in the pinned version. The change MUST call that API. Custom code is allowed only when the pinned stack cannot do the job. The change MUST name that gap in the design. MinerU and Markdown as source of truth stay forbidden.

#### Scenario: Stack already does the job

- GIVEN a job the pinned library documents
- WHEN a change needs that job
- THEN the change MUST call the library
- AND it MUST NOT add a parallel script

#### Scenario: Stack cannot do the job

- GIVEN a job no pinned API performs
- WHEN a change needs that job
- THEN the change MAY add the minimum code
- AND the design MUST name the gap

#### Scenario: Identity stays the gap

- GIVEN financial identity, verification, or abstention
- WHEN the audit function runs
- THEN that code MUST stay unless a pinned API is shown to do that exact job
- AND an LLM MUST NOT write `identity_v1` or `identity_v2`

### Requirement: On-Demand Audit Function

The audit MUST be invocable at any time, including while another change is active. One invocation MUST write `openspec/changes/auditoria-stack-nativo/runs/<date>/audit.md` and MUST NOT advance phases 0–13. A later invocation MUST write a new dated folder and MUST leave earlier runs in place. Each row MUST be `keep` with a named gap, or `call-native` or `delete` with a named pinned API. The invocation MUST NOT add a linter, scanner, or script. The comparison MUST use the pinned version's API or docs. Replacing code MUST be a separate step after that file exists, and MUST touch one `call-native` function at a time. Kernel tests MUST NOT import `docling`. Gold numbers MUST NOT change.

#### Scenario: A call returns a verdict file

- GIVEN a requested scope under `src/claimledger/`
- WHEN the audit function is invoked
- THEN `runs/<date>/audit.md` MUST contain one verdict row per custom function in that scope
- AND phase 8 MUST remain the page crop

#### Scenario: A second call does not erase the first

- GIVEN an existing `runs/<date>/audit.md`
- WHEN the function is invoked on a later date
- THEN a new run folder MUST be written
- AND the earlier file MUST stay

#### Scenario: No audit script

- GIVEN an invocation
- WHEN it finishes
- THEN no new package or script exists whose purpose is to run the audit
