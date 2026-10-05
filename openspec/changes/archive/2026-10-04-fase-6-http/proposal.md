# Proposal: Fase 6 HTTP Query

## Intent

The kernel answers on `Ledger.seed()`. Fase 6 exposes that answer as `POST /claims/query` (`docs/documento-rector.md` §13).

## Proposal question round

Resolved. Approach 1 is fixed.

## Scope

### In Scope

- Sibling `src/claimledger/http/` and `tests/http/`. Strict TDD. No socket, Docker, or network.
- Mapper plus one in-process Starlette route. Body is only `{"question": string}`. Call `understand(question)` then `query(intent, Ledger.seed())`. Do not call `measure`, `retrieve`, or `upsert`.
- One verified claim: `status`; `claim` (issuer, period, statement, scope, metric, value, currency); `evidence` (document_id, page, text). Seed evidence is `[]`.
- Abstain passes `recipe_no_extract`, `off_corpus`, `unresolved_identity`, `no_matching_claim`, `incomplete_comparison`, `ambiguous_period`. Do not rewrite them to `no_verified_claim`.
- Compare on this route: `claims` length 2, values `21262335` and `81956525`, no delta.
- A bad body does not call `understand` and is not a kernel abstain.
- Pin `starlette==1.0.0` only. Kernel tests must not import Starlette. `src/claimledger/__init__.py` stays empty.

### Out of Scope

- Fase 7 ficha, orchestrator, crop, subtraction, series, auth, extra routes, OpenAPI catalog, LLM identity.
- FastAPI, Flask, and uvicorn pins. Invented page-4 evidence. `artifact_hash` on the body.

## Capabilities

### New Capabilities

- `http-query`: `POST /claims/query` over `understand` then `query` on `Ledger.seed()`.

### Modified Capabilities

- `gold-regression`: HTTP code and tests stay off the 13-path allowlist. Kernel modules and tests MUST NOT import `starlette`.

Unchanged: `query`, `lookup`, `ledger`, `identity`, `json-retrieval`, `verify-eval`, `docling-ingest`, `evidence-adapter`, `document-graph`.

## Approach

Approach 1. Architecture Gate: this route is the missing HTTP mouth for a query the kernel already answers. It is not a new product component. HTTP `status` is `QueryResult.status`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/http/` | New | Mapper and route |
| `tests/http/` | New | Off the 13-path scan |
| `pyproject.toml` | Modified | Pin `starlette==1.0.0` |
| `openspec/specs/gold-regression/spec.md` | Modified | Scan excludes HTTP |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Compare dropped to one claim | Med | `claims` length 2, no delta |
| Reasons rewritten | Med | Pass kernel reason through |
| Invented evidence | Med | Seed evidence is `[]` |

## Rollback Plan

Remove the http package, its tests, and the starlette pin. Kernel query and seed stay.

## Dependencies

Fases 0–5. Pin only `starlette==1.0.0`.

## Success Criteria

- [ ] Rector JSON; seed evidence `[]`; no `answer`, identity, bbox, or `ledger_status`.
- [ ] Six abstain reasons pass through. A bad body does not call `understand`.
- [ ] Compare: two claims, `21262335` and `81956525`, no delta. Gold `21259769` and `-14950948` stay.
- [ ] Off the 13-path allowlist. Kernel tests do not import Starlette. No socket.

## Delivery

Decision needed before apply: No.
