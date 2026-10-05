# Tasks: Fase 7 Claim Card

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 180–260 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR, two TDD units |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Consolidated seal, chips, rows, value, sentence | Single PR | `pytest tests/card/test_render_card.py::test_consolidated_card` | N/A — in-memory objects; no PDF, network, or Docker | Delete `tests/card/test_render_card.py`, `src/claimledger/card/card.py`, and `src/claimledger/card/__init__.py` |
| 2 | Parent, abstain, compare, seal source, allowlist | Single PR | `pytest tests/card/test_render_card.py` | N/A — same in-memory module; no live reader | Revert `card.py` and the slice-2 cases in `tests/card/test_render_card.py` |

## Phase 1: Consolidated card (Unit 1)

- [x] 1.1 RED: Create `tests/card/test_render_card.py`. Import `render_card` and `ClaimCard` from `claimledger.card.card` (no re-export). Build `FinancialClaim` (`evidence=()`, `ledger_status="recorded"`), `QueryResult`, and `Candidate` in memory. Verified consolidated claim: seal `VERIFICADO`, chips `BYMA · 1T26 · Consolidado · Resultado neto`, value `21262335`, rows `RESULTADO NETO DEL PERÍODO 21.262.335` then `Resultado neto atribuible a la sociedad controlante 21.259.769`, sentence `encontré estas dos filas; verifiqué la consolidada`. `21259769` is not the value. No production code. Run: `pytest tests/card/test_render_card.py::test_consolidated_card`. MUST fail with `ImportError` or `ModuleNotFoundError`. No PDF, network, or Docker. Do not edit `query.py`, `measure.py`, http, or gold files.

- [x] 1.2 GREEN: Add docstring-only `src/claimledger/card/__init__.py` (no re-export) and minimum `render_card` plus frozen `ClaimCard` in `src/claimledger/card/card.py`. Copy `claim.value` and `Candidate.text` in order. Do not call `measure`, `retrieve`, `understand`, `query`, or `upsert`. Do not pre-satisfy slice-2 behavior. Run: `pytest tests/card/test_render_card.py::test_consolidated_card`. MUST pass. Refactor only while green. Do not edit `query.py`, `measure.py`, http, gold, `tests/test_identity.py`, or `src/claimledger/__init__.py`.

## Phase 2: Parent, abstain, compare, boundary (Unit 2)

- [x] 2.1 RED: Extend `tests/card/test_render_card.py` only. Parent chip `Controlante` (not `Consolidado`), value `21259769`, both rows remain, sentence `encontré estas dos filas; verifiqué la controlante`. `recipe_no_extract`: seal `ME ABSTENGO`, reason unchanged, sentence does not say verified, `21262335` is not a value. Compare shows `21262335` and `81956525` with no delta. Seal is not `ledger_status`. Empty candidates with abstain stay `ME ABSTENGO`. `card.py` does not import `starlette`, `docling`, `llama_index`, or `open_webui`. Read `_kernel_scan_paths` from `tests/test_identity.py` without editing it; card paths stay off the 13-path allowlist. If a node already passes, do not weaken it or change production to force a failure. Run: `pytest tests/card/test_render_card.py`. MUST fail with `AssertionError` on a case that is not yet true, not `ImportError`.

- [x] 2.2 GREEN: Edit only `src/claimledger/card/card.py` if a slice-2 assertion is false. Map `parent_attributable` to `Controlante`. Abstain copies `reason`, uses `values == ()`, and `sentence == ""`. Compare copies both claim values and has no delta. If a slice-2 assertion is already true, do not add code to manufacture a failure. Run: `pytest tests/card/test_render_card.py`. MUST pass. Do not edit `query.py`, `measure.py`, http, gold, `tests/test_identity.py`, or `pyproject.toml`. `dependencies` stays `[]`. `src/claimledger/__init__.py` stays empty.
