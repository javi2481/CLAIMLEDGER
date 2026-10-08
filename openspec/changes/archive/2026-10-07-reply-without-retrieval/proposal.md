# Proposal: Reply Without Retrieval

## Intent

`reply`, `measure`, and the card still take rows from `retrieve` / DoclingReader. Product host must not import `claimledger.retrieval` or DoclingReader.

## Scope

### In Scope

- Move `Candidate` to `claimledger.card.candidate`. `retrieval.drawers` re-exports it (own type only if a cycle). Card does not import retrieval.
- `measure(question, ledger)` is `query(understand(question), ledger)`. Drop `artifact_hash` and `retrieve()`.
- Verified evidence only: `Candidate(drawer="tables", text=Evidence.text or label, ref=evidence.artifact_hash)`, one per item; empty yields `()`. `reply` plan/book/query paths do the same and do not call `retrieve()`.
- Fewer than 2 rows: still render the verified card; omit “encontré estas dos filas…”. A claim-only sentence MAY appear and MUST NOT claim two rows. No invented neighbors.
- Dockerfile: `pip install ".[http,deepseek]"`. `tools.search` MAY call `retrieve`; `ImportError` returns empty hits and does not authorize. Keep `retrieval/` tests. Gold numbers stay frozen.

### Out of Scope

- Deleting `retrieval/` or changing `json-retrieval`. Gold, kernel allowlist, identity, query math, and new libraries stay put. `dependencies` stays `[]`.

## Capabilities

### New Capabilities

None

### Modified Capabilities

- `verify-eval`: no `retrieve`; `understand` then `query`; candidates are verified evidence.
- `claim-card`: fewer than 2 rows still seals; two-row sentence not required.
- `openwebui-host`: reply, measure, and card MUST NOT import retrieval or DoclingReader; drop neighbor-row and stubbed-reader rules.
- `docling-ingest`: remove deferred “reply / Docker `.[retrieval]` out of scope”.
- `agent-host`: search `ImportError` returns empty hits and never authorizes.

## Approach

Approach 1. Build rows from `FinancialEvidence` (`text`, else `label`). Drawers re-export card. Strict TDD.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `card/candidate.py`, `card.py`, `measure.py`, `reply.py` | New/Modified | Evidence rows; no `retrieve` |
| `drawers.py`, `agent/tools.py`, `Dockerfile` | Modified | Re-export; empty hits; `.[http,deepseek]` |
| `tests/openwebui`, `tests/eval`, `tests/card` | Modified | Evidence rows, not a fake reader |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Neighbor lines go; gold values stay | High | Assert value and evidence text |
| Seed evidence empty; search extra missing | Med | Zero rows and empty hits; neither authorizes |
| drawers ↔ card cycle | Low | Re-export; duplicate type only if needed |

## Rollback Plan

Restore `retrieve` in `measure` and `reply`, `Candidate` in drawers, Dockerfile `.[http,retrieval]`, and prior specs. `retrieval/` stays in tree.

## Dependencies

None. Optional `retrieval` extra stays off the product image.

## Success Criteria

- [ ] `reply`, `measure`, and `card` do not import retrieval or DoclingReader and build `tables` candidates only from verified evidence.
- [ ] A verified card with fewer than 2 rows has no two-row sentence and no invented neighbors.
- [ ] Image installs `.[http,deepseek]`. Search `ImportError` returns empty hits. Gold unchanged.
