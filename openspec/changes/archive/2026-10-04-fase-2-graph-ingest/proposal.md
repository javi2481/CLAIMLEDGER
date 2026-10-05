# Proposal: Fase 2 Graph Ingest

## Proposal question round

Settled. No second round.

1. Pain: no EEFF + comunicado + deck fold without a FinancialClaim.
2. Users: the period document book, conflicts visible.
3. Rules: Document, Issuer, Period, Statement; claim in the ledger; zero LLM; no P&L or query rebuild; memoria off 1T26/2T26; `classify.period` stays None; conflict is not `ledger_status`.
4. Outcome: one ingest-time graph, kernel IDs, recorded conflicts and doubts.
5. Gap: `Ledger.upsert` merges claim values, not documents.
6. Impact: `src/claimledger/graph/` + `tests/graph/`. Narrow `sys.modules`. Pin only there.
7. Edges: unknown alias is doubt; transcript may link `2026-06-30` with no claim; ingest must not import `docling-graph`.
8. Decision: approach 1.
9. Non-goals: LlamaIndex, HTTP, UI, VLM, MinerU, Neo4j, orchestrator, `run_pipeline`, extraction backends.
10. Risk: import from ingest or kernel, or claims from the eight non-EEFF files.

## Intent

Document identity the ledger cannot merge. §24: Graph passes. LlamaIndex, HTTP, UI, VLM, MinerU, Neo4j, orchestrator: no.

## Scope

### In Scope

- `src/claimledger/graph/` and `tests/graph/`.
- One `artifacts/graph/` write. Lazy `docling-graph==1.9.1` management only.
- Snapshot `sys.modules` around the seven kernel imports. Keep the 13-path allowlist.

### Out of Scope

- Item 9, plus `press_v1`, `presentation_v1`, period edits, Fase 1 commit, Fase 3.

## Capabilities

### New Capabilities

- `document-graph`: ingest-time Document/Issuer/Period/Statement graph, stable IDs, deterministic merge, recorded conflict and human doubt.

### Modified Capabilities

- `gold-regression`: kernel and ingest stay docling-graph-free; `src/claimledger/graph/` MAY import `docling-graph==1.9.1`. Do not relax gold numbers.

Unchanged, no rewrite: identity, ledger, lookup, query, docling-ingest, evidence-adapter.

## Approach

Approach 1 (§15, §20, §24). IDs: `BYMA`, `normalize_period` (`2026-03-31`, `2026-06-30`), `income_statement`, `artifact_hash`. Period is an edge. Fold same ID; store clashes. Unknown token is doubt. Memoria off quarterly IDs. Transcript may link `2026-06-30` with no claim. Build once. No kernel or ingest import. No `extract_recipe`.

## Affected Areas

- New: `src/claimledger/graph/` (sole `docling_graph` importer), `tests/graph/`, gitignored `artifacts/graph/`.
- Modified: gold-regression spec (permission), `tests/test_identity.py` (import snapshot).
- Unchanged: `src/claimledger/ingest/`.

## Risks

- Med: import outside `graph/`. Keep both forbids.
- Med: non-EEFF claims. No claim nodes. No `extract_recipe`.
- High: `sys.modules` on full pytest. Snapshot the seven kernel imports.
- Med: memoria on a quarter. Year-end token stays doubt.

## Rollback Plan

Delete `src/claimledger/graph/`, `tests/graph/`, and `artifacts/graph/`. Restore the `sys.modules` check and the gold-regression sentence. Leave `Ledger.seed()`. No migration.

## Dependencies

- Declared pin `docling-graph==1.9.1`. No bump.
- Read `artifact_hash`. Do not commit Fase 1.
- Reuse `normalize_period`, `BYMA`, `income_statement`.

## Success Criteria

- [ ] Same-period EEFF, comunicado, and deck share three IDs; no FinancialClaim.
- [ ] Conflicts and doubts recorded. Memoria off 1T26/2T26. One write. Query does not rebuild.
- [ ] Kernel and ingest forbid `docling-graph`. Gold frozen. No `run_pipeline`, LLM, VLM, or Neo4j.
