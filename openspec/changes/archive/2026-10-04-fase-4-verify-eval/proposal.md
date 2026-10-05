# Proposal: Fase 4 Verify Eval

## Intent

`query` and `retrieve` cannot show the neighbor trap together. A sibling caller places tables candidates in front of Claim Query and measures the frozen verdict.

## Proposal question round

Resolved. No open product questions. `docs/documento-rector.md` and the exploration fix placement, call order, and the measure: approach 1; identity from `understand`; no dropped row; gold on `Ledger.seed()`; narrative is not a number source; pins stay.

## Scope

### In Scope

- `src/claimledger/eval/` and `tests/eval/`, outside the seven kernel modules and outside `retrieve`. Strict TDD.
- `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query(intent, Ledger.seed())`.
- Both neighbor texts are candidates. Consolidated verifies `21262335`. Parent verifies `21259769`. The other number is not the answer. `ledger_status` stays `recorded`.
- `recipe_no_extract` abstains even if a candidate holds a gold number. Compare stays two claims, no subtraction.

### Out of Scope

- Fase 6 `POST /claims/query`, Open WebUI ficha, orchestrator, VLM, MinerU, Neo4j, fase 9 subtraction.
- Relaxing gold, LLM-written identity, Markdown as source of truth, an agent that skips the kernel.
- `candidates` on `query.py`, choice inside `retrieve`, Recall@k/MRR, any new library.

## Capabilities

### New Capabilities

- `verify-eval`: tables candidates, then `understand`, then `query` on `Ledger.seed()`.

### Modified Capabilities

- `gold-regression`: caller off the 13-path scan. Gold v1 45 and v2 26 stay on the seed harness and MUST NOT point at Docling JSON.

Unchanged: `query`, `lookup`, `ledger`, `json-retrieval`, `identity`, `docling-ingest`, `evidence-adapter`, `document-graph`.

## Approach

Approach 1. Architecture Gate: this caller solves the missing measured join that current `query` and `retrieve` cannot do alone. It is not a new product component. No upsert, no verified candidate, no `llama_index` in kernel modules. `retrieve` must not call `query`. Measure row text plus identity, not ref.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/eval/` | New | Caller |
| `tests/eval/` | New | Off the 13-path scan |
| `openspec/specs/gold-regression/spec.md` | Modified | Seed gold |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Upsert or verified candidate | High | Seed stays `recorded` |
| Gold on Docling JSON | High | Gold tests stay on seed |

## Rollback Plan

Remove the new caller and its tests. Kernel `query` and `Ledger.seed()` stay. Do not delete gold.

## Dependencies

Fases 0–3. Pins stay as declared. No new library.

## Success Criteria

- [ ] Both neighbor texts; consolidated `21262335`; parent `21259769`; the other number is not the answer; `ledger_status` stays `recorded`.
- [ ] `recipe_no_extract` abstains beside a gold number. Compare is two claims, no subtraction.
- [ ] Gold v1 45 and v2 26 stay on seed, including `-14950948`.

## Delivery

Decision needed before apply: No.
