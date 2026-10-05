# Proposal: Fase 3 Retrieval

## Intent

Hashed Docling JSON and the graph exist, but nothing returns search candidates. A later question needs both neighbor rows before the kernel judges.

## Proposal question round

Settled. Nothing remains open. Pain: no candidates. Rules: two drawers; forced `export_type=json`; Markdown is not source of truth; candidates are not claims; kernel judges; no orchestrator, HTTP, UI, VLM, MinerU, or Neo4j. Gap: `query` reads only the ledger. Impact: sibling package; 13-path scan; no LlamaIndex in ingest or kernel. Edges: override the markdown default; mixing drawers fails; `verified` is out. Decision: approach 1. Non-goals: Fase 4 wiring, orchestration, ficha, relaxing gold. Pin: none; choose later from a documented compatible release.

## Scope

### In Scope

- `src/claimledger/retrieval/` and `tests/retrieval/` (strict TDD).
- `store.load` of `artifacts/docling/<hash>.json`; `DoclingReader(export_type="json")` then `DoclingNodeParser`.
- Tables drawer for numbers; narrative drawer to explain later. Candidates only; both neighbor rows may appear.

### Out of Scope

- Wiring `query`, orchestration, HTTP, UI, ficha, VLM, MinerU, Neo4j, ledger writes, graph rebuild, and any LlamaIndex version.

## Capabilities

### New Capabilities

- `json-retrieval`: hashed Docling JSON, forced JSON reader, two drawers, candidates only.

### Modified Capabilities

- `gold-regression`: kernel and ingest stay free of `llama_index`; retrieval may import it. Do not relax gold numbers. Copy-full is for the spec phase.

Unchanged: identity, ledger, lookup, query, docling-ingest, evidence-adapter, document-graph.

## Approach

Approach 1. Gate (rector §6, §15 Fase 3, §20, §24; Oleada B): LlamaIndex only as retrieval over JSON structure. Lazy-import inside `retrieval/`. `dependencies` is `[]`; extra `docling` lists only `docling==2.130.0` and `docling-graph==1.9.1`. Pin LlamaIndex later from a documented release compatible with that Docling pin.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/retrieval/` | New | Reader, two drawers, candidates |
| `tests/retrieval/` | New | Outside the 13-path scan |
| `openspec/specs/gold-regression/spec.md` | Modified | Retrieval off the scan |
| `pyproject.toml` | Unchanged | Pin deferred |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Markdown default | High | Test `export_type="json"` |
| Mixed drawers or `verified` | High | Fail the mix; candidates only |
| Invented pin or scanned import | Med | No version; stay off 13 paths |

## Rollback Plan

Delete `src/claimledger/retrieval/` and `tests/retrieval/`. Revert the gold-regression delta. Leave kernel, ingest, graph, `query`, and hashed JSON. Drop any later LlamaIndex pin in that same revert.

## Dependencies

Fase 1 hashed JSON. Existing pins `docling==2.130.0` and `docling-graph==1.9.1`. No LlamaIndex dependency.

## Success Criteria

- [ ] Asked drawer returns candidates, including both neighbor rows when present.
- [ ] JSON export is forced; mixed drawers fail; result is not `verified`.
- [ ] Gold numbers and the 13 paths stay.
