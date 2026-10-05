# Proposal: Fase 7 Claim Card

## Intent

Query JSON and `measure` cannot show the verdict beside both rows. The card does. It does not choose `21262335` over `21259769`.

## Proposal question round

Resolved. Approach 1 is fixed.

## Scope

### In Scope

- `src/claimledger/card/` and `tests/card/`, outside the seven kernel modules and the 13-path tuple. Strict TDD. `src/claimledger/__init__.py` stays empty.
- `render_card(candidates, result)` takes the pair `measure` already returns. It does not call `measure`, `retrieve`, `understand`, `query`, or `upsert`.
- Seal `VERIFICADO` when `status` is `verified`; `ME ABSTENGO` when `abstained`. Not from `ledger_status`. `recorded` stays recorded.
- Chips from verified claim fields via a closed Spanish map. Canonical: `BYMA · 1T26 · Consolidado · Resultado neto`. Parent is not labeled `Consolidado`.
- Rows are `Candidate.text` in given order. Shown value is `claim.value`. No digit parse. No choice between `21262335` and `21259769`.
- Two-row copy only when one verified consolidated claim has both rows. Abstention keeps `ME ABSTENGO` plus the kernel reason and must not say a row was verified. Compare stays two claims and does not subtract.
- No new library. `dependencies` stays `[]`. No Docker, network, PDF, Open WebUI, `starlette`, `docling`, or `llama_index`.

### Out of Scope

- Open WebUI, `/v1/chat/completions`, Pipelines, Knowledge, a second HTTP route, crop, charts, subtraction, orchestrator.
- Changes to `measure`, `POST /claims/query`, gold, or `tests/test_identity.py`.

## Capabilities

### New Capabilities

- `claim-card`: display dict from `(candidates, QueryResult)`.

### Modified Capabilities

None.

## Approach

Approach 1. Architecture Gate: the card is the missing display of a verdict and two rows. It is not a new product component and it is not a UI framework.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/card/` | New | `render_card` |
| `tests/card/` | New | Off the 13-path scan |
| `src/claimledger/eval/measure.py` | Read | Pair unchanged |
| `src/claimledger/http/` | Read | Sole route stays |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Phase-6 JSON as input | Med | Use `measure`'s pair |
| Neighbor re-chosen | Med | Print text; show `claim.value` |
| Abstention claims a verified row | Med | Keep seal and kernel reason |

## Rollback Plan

Delete the card package and its tests. Kernel, `measure`, and `POST /claims/query` stay.

## Dependencies

None. `dependencies` stays `[]`.

## Success Criteria

- [ ] Consolidated: `VERIFICADO`, chips `BYMA · 1T26 · Consolidado · Resultado neto`, both rows, value `21262335`.
- [ ] Parent is not `Consolidado`; value `21259769`. Abstention keeps `ME ABSTENGO` and the kernel reason.
- [ ] Compare stays two claims and does not subtract. Off the 13-path allowlist. No new dependency.

## Delivery

Decision needed before apply: No.
