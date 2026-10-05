# Tasks: Fase 6 HTTP Query

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 300–380 |
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
| 1 | Pure `claims_query` on `Ledger.seed()` | Single PR | `pytest tests/http/test_claims_query.py` | N/A — in-memory seed; no socket, Docker, or network | Delete `claims.py`, its tests, and docstring-only `http/__init__.py` if `app.py` is absent |
| 2 | `build_app` and extra `http` | Single PR | `pytest tests/http/test_app.py` | N/A — in-process ASGI; no bound port or uvicorn | Delete `app.py`, `tests/http/test_app.py`, and the `http` extra |

## Phase 1: Pure claims_query (Unit 1)

- [x] 1.1 RED: Create `tests/http/test_claims_query.py` importing `claims_query` from `claimledger.http.claims`. On `Ledger.seed()`: consolidated `21262335` (BYMA, `2026-03-31`, `income_statement`, `consolidated`, `net_income`, `ARS`); parent `21259769`; tax `-14950948`; `evidence` `[]`; absent `answer`, `identity`, `identity_key`, `unit`, `ledger_status`, `artifact_hash`, `label`, `bbox`. `recipe_no_extract` stays that string, not `no_verified_claim`. Also pass `off_corpus`, `unresolved_identity`, `no_matching_claim`, `incomplete_comparison`, `ambiguous_period`. Compare “Comparar resultado neto consolidado 1T26 vs 2T26”: `claims` length 2, `21262335` then `81956525`, no `delta`. A missing or non-string `question` does not call `understand`. Once the module exists, assert it does not import `starlette`. Run: `pytest tests/http/test_claims_query.py`. MUST fail with `ImportError` or `ModuleNotFoundError` before any production code. Do not edit `query.py` or `ledger.py`.

- [x] 1.2 GREEN: Add docstring-only `src/claimledger/http/__init__.py` (no re-export) and `claims_query` only in `src/claimledger/http/claims.py`. No `starlette` import in that module. Call `understand(question)` then `query(intent, ledger)`. Run: `pytest tests/http/test_claims_query.py`. MUST pass. Do not edit `query.py`, `ledger.py`, `lookup.py`, or `src/claimledger/__init__.py`.

## Phase 2: build_app and the pin (Unit 2)

- [x] 2.1 RED: Create `tests/http/test_app.py`. One in-process `POST /claims/query` (`TestClient` if that import works, else `httpx` `ASGITransport`; no bound port; do not pin the client). Import `build_app` inside that test so a missing app fails with `ImportError` or `ModuleNotFoundError`. Read `pyproject.toml`: optional extra `http` must pin `starlette==1.0.0`, `dependencies` stays `[]`, and fastapi, flask, and uvicorn are not pinned. Fail on the missing pin, not a skip. Read `tests/test_identity.py` without editing it: `src/claimledger/http/` and `tests/http/` stay off the 13-path allowlist (`len` 13); the seven kernel modules and six kernel tests do not import `starlette`. Do not edit those 13 paths. Run: `pytest tests/http/test_app.py`. MUST fail because the app or the pin is missing. A fake assertion is the wrong failure. If the allowlist seal already passes, do not weaken it.

- [x] 2.2 GREEN: Add `build_app` in `src/claimledger/http/app.py`. Import `starlette` only inside that function. Only `POST /claims/query`. HTTP 200 for a kernel verified or abstained result. HTTP 400 with `{}` and no `status` for a bad body, and that path does not call `understand` or `claims_query`. Pin `starlette==1.0.0` in extra `http` only. Run: `pytest tests/http/test_app.py`. MUST pass. Do not pin fastapi, flask, or uvicorn. Do not edit `query.py`, `ledger.py`, or `tests/test_identity.py`.
