## Exploration: fase-6-http

Architecture is CLOSED. This change exposes one route, `POST /claims/query`, over the existing kernel. The request body is only `{"question": "..."}`. The route calls `understand(question)` then `query(intent, ledger)`. It does not call `measure`. Out of scope: a large API, the Open WebUI ficha (fase 7), an orchestrator, photo/crop (fase 8), subtraction (fase 9), and series charts (fase 12).

### Current State

`docs/plan-implementacion.md` names phase 6 as `POST /claims/query` and puts a large API outside it. `docs/documento-rector.md` §13 is the HTTP contract. The body is one string field, `question`. Verified fields named there are `status`, `claim` (`issuer`, `period`, `statement`, `scope`, `metric`, `value`, `currency`), and `evidence` (`document_id`, `page`, `text`). The abstained example is `{"status": "abstained", "reason": "no_verified_claim"}`. That example shows the shape of abstention: `status` plus `reason`. It does not require replacing a kernel reason with the string `no_verified_claim`.

`docs/informe-arquitectura.md` shows the same route with an extra `answer` field and a sample evidence row (`page` 4, text `RESULTADO NETO DEL PERÍODO`). The rector does not name `answer`. This change does not add `answer`.

`query` (`src/claimledger/query.py`) returns `QueryResult`: `status` is `verified` or `abstained`, plus `reason`, `claims`, and `identity`. It reads a `Ledger` and does not mutate it. A claim is eligible only when `ledger_status == "recorded"`. `recorded` is not `verified`. Compare (`intent.compare`) returns two recorded claims and does not subtract. One missing period abstains with `incomplete_comparison`. `identity` on a compare result is a wildcard key (`BYMA|*|...`). The rector HTTP body does not name `identity`, so the route does not emit it.

`understand` (`src/claimledger/lookup.py`) is the lexical identity step. Abstain reasons it sets, and that `query` then returns, include `off_corpus`, `recipe_no_extract`, and `unresolved_identity`. `query` itself also returns `unresolved_identity` (including a narrative route), `incomplete_comparison`, `ambiguous_period`, and `no_matching_claim`. `openspec/specs/query/spec.md` closes the set to those six strings. The route passes the kernel reason through. It does not collapse `recipe_no_extract` or any other specific reason into `no_verified_claim` or into a new string.

`Ledger.seed()` (`src/claimledger/ledger.py`) upserts fourteen recipe rows with `evidence=()`. `FinancialClaim.evidence` is a tuple of `FinancialEvidence` (`src/claimledger/claim.py`, `src/claimledger/evidence.py`). Seed claims therefore have no `document_id`, page, or text. An empty evidence list is honest. Rector §12 mentions page 4 as the story of a later verified row that already has evidence. That page is not on the seed book. The route must not invent page 4, a document id, or the informe sample text on a seed claim.

`measure` (`src/claimledger/eval/measure.py`) takes `artifact_hash` and `question`, calls `retrieve`, then `understand`, then `query(intent, Ledger.seed())`. The HTTP body has no hash. Rector §13 does not add one. The route does not call `measure` and does not invent a hash so it can call retrieval.

The 13-path kernel allowlist is the explicit tuple in `tests/test_identity.py`: seven modules (`identity`, `digits`, `evidence`, `claim`, `ledger`, `lookup`, `query`) and six kernel tests. `tests/eval/test_measure.py` repeats that same tuple. HTTP code and HTTP tests stay outside it. Kernel tests must not import the HTTP stack, `docling`, or `llama_index`. `src/claimledger/__init__.py` is empty, so importing a kernel module does not load a sibling package.

`pyproject.toml` has `dependencies = []`. Optional extras pin Docling and LlamaIndex only. No HTTP library is pinned. In this environment these packages import, at these versions: `starlette==1.0.0`, `fastapi==0.135.3`, `flask==3.1.3`, `httpx==0.28.1`, `uvicorn==0.44.0`. Those versions were read from the installed environment. They are not a guessed pin. Nothing else should be invented.

Gold numbers stay frozen: consolidated net income `21262335`, parent attributable `21259769`, income tax `-14950948`. Compare of consolidated net income stays two claims (`21262335` and `81956525`) and no delta.

### Affected Areas

- `src/claimledger/lookup.py` — read. `understand(question)` stays the identity step. Do not add an LLM route.
- `src/claimledger/query.py` — read. `query(intent, ledger)` stays the judge. Do not add HTTP, retrieval, or a delta.
- `src/claimledger/ledger.py` — read. Tests and the route use `Ledger.seed()`. The handler must not call `upsert`.
- `src/claimledger/claim.py` and `src/claimledger/evidence.py` — read. Map only the rector fields. Seed evidence stays empty.
- `src/claimledger/eval/measure.py` — read. Not on this path. It requires a hash the body does not have.
- `tests/test_identity.py` — read. The 13-path tuple stays as it is. Do not add HTTP modules or HTTP tests to it.
- `tests/test_query.py` — read. Neighbor, compare-without-delta, and abstain reasons already live here. Do not retarget them at HTTP.
- `openspec/specs/query/spec.md` — kernel contract. A delta may say an HTTP caller may sit in front of `query`. It must not weaken compare, the closed reasons, or “HTTP is not required to demonstrate the kernel.”
- `pyproject.toml` — only if the one route imports Starlette. Pin the looked-up version `starlette==1.0.0`. Do not pin a range or a version that was not imported here.
- New sibling package, outside the seven kernel modules and outside the 13 paths (for example `src/claimledger/http/`), with tests outside the six kernel test files (for example `tests/http/`). `src/claimledger/__init__.py` stays empty.

### Approaches

1. **Pure mapper plus one in-process Starlette route** — A function maps the body and a `Ledger` to the JSON dict. It calls `understand(question)` then `query(intent, ledger)`. It does not import retrieval, does not call `measure`, and does not call `upsert`. One Starlette app exposes only `POST /claims/query` and calls that function with `Ledger.seed()`. Pin `starlette==1.0.0`, already importable. Tests of the contract call the function with a dict and `Ledger.seed()`. They do not open a socket, bind `uvicorn`, use Docker, or use the network. An in-process ASGI call may use `httpx==0.28.1` (`ASGITransport`), also already importable; that client is optional because the function test already proves the JSON.
   - Pros: matches plan phase 6 (the route exists) and rector §13 (one small contract). Fase 7 can call the same route later. The pin is a version that imports today. FastAPI’s generated OpenAPI catalog stays out. Kernel files stay free of the HTTP stack.
   - Cons: `dependencies` is empty today, so the design must add the exact Starlette pin. Compare does not fit the rector’s singular `claim` object; the mapper needs a two-claim JSON shape on this same route (see Recommendation). Starlette is a new runtime dependency the kernel never had.
   - Effort: Low

2. **Pure function only, no framework** — Same mapper, tested dict-in / dict-out. No Starlette import and no pin. A later change wraps it in a route.
   - Pros: no new dependency. Tests cannot open a socket. Enough to prove the JSON contract, including pass-through reasons, empty evidence, and two compare claims.
   - Cons: phase 6’s closure in the plan is the route `POST /claims/query`. A function with no app leaves fase 7 without a route to call. The pin problem is not what blocks a route: `starlette==1.0.0` is already importable.
   - Effort: Low

3. **FastAPI app, `measure`, or a wider API** — FastAPI (`fastapi==0.135.3`, also importable) with `/docs` and `/openapi.json`; or the route calls `measure` / retrieval; or extra routes, auth, a series endpoint, or an `answer` field copied from the informe.
   - Pros: FastAPI is a common way to declare one JSON route. `measure` already joins retrieval and query when a hash exists.
   - Cons: an OpenAPI catalog is out of scope. The body has no hash, so `measure` cannot run without inventing one. Extra routes, auth, subtraction, and series charts are later phases or rejected. `answer` is not in the rector. Flask (`flask==3.1.3`) is installed too and is a second framework this route does not need.
   - Effort: Medium — **reject**

### Recommendation

Take approach **1**.

1. New code lives in a sibling package outside the seven kernel modules and outside the 13-path tuple. Kernel tests do not import it. Importing the seven kernel modules must not import Starlette, `docling`, or `llama_index`. `src/claimledger/__init__.py` stays empty.
2. Call order: parse `{"question": "<string>"}`, then `understand(question)`, then `query(intent, ledger)`. The route passes `Ledger.seed()`. The handler does not upsert. Tests pass `Ledger.seed()` into the mapper. Do not call `measure`. Do not add `artifact_hash` to the body.
3. One verified claim uses the rector object and no other fields: `status`, `claim` (`issuer`, `period`, `statement`, `scope`, `metric`, `value`, `currency`), `evidence` (objects with only `document_id`, `page`, `text`). Do not emit `answer`, `identity`, `identity_key`, `unit`, `ledger_status`, `artifact_hash`, `label`, or `bbox`. Seed evidence is `()`. Serialize it as `[]`. Do not invent page 4.
4. Abstention uses the rector shape `{"status": "abstained", "reason": "<kernel reason>"}` and omits claim, evidence, and value. **Pass the kernel reason through unchanged.** `no_verified_claim` in the rector is the shape of that object, not a string to substitute. `recipe_no_extract`, `off_corpus`, `unresolved_identity`, `no_matching_claim`, `incomplete_comparison`, and `ambiguous_period` stay those strings. Do not collapse them.
5. Compare on this same route returns both claims and no delta. A singular `claim` would drop one period, so a two-claim result uses `claims` (length 2), not a new route. Each item reuses the rector claim object plus that claim’s own `evidence` list (empty on seed). Periods stay `2026-03-31` and `2026-06-30`. Values for consolidated net income stay `21262335` and `81956525`. No `delta`, no subtracted amount, no `answer`. This is not a series endpoint and does not serve “últimos 4 trimestres” (fase 12).
6. Canonical checks on `Ledger.seed()`: consolidated 1T26 net income `21262335`; parent 1T26 `21259769`; income tax `-14950948`. Response `status` comes from `QueryResult.status`, never from `ledger_status`. `recorded` stays recorded on the book.
7. A body that is not a JSON object with a string `question` is a request failure. Do not call `understand`. Do not report that failure as `no_verified_claim` or as any kernel reason.
8. Pin only `starlette==1.0.0` if the route module imports it. Do not pin FastAPI, Flask, or uvicorn for this change. Do not invent a version. Tests do not bind a port.

**In this change:** the mapper, one route, and pytest that proves the rector JSON on `Ledger.seed()` without a socket.

**Waits:** fase 7 ficha and any Open WebUI client; orchestrator; photo/crop; subtraction; series charts; auth; extra routes; OpenAPI catalogs; LLM identity; Markdown as truth.

### Risks

- **Singular `claim` vs compare.** Rector §13 shows one claim object. The kernel returns two claims for compare. Emitting one object drops a verified period. The `claims` list above is the smallest shape that keeps both on this route. A series endpoint would move that case into fase 12.
- **Reason rewrite.** Mapping every abstention to `no_verified_claim` would hide `recipe_no_extract` and the other five kernel reasons. Pass-through is required.
- **Invented evidence.** Copying the informe’s page 4 onto `Ledger.seed()` would publish evidence the book does not have. Empty `evidence` is the honest seed response.
- **`measure` on a hash-less body.** Calling `measure` or `retrieve` from the route needs an artifact hash the rector body does not include. That would invent a field or a hidden hash.
- **`recorded` shown as verified.** The HTTP `status` must be `QueryResult.status`. Copying `ledger_status` into `status` would call a stored row verified without the judge.
- **Kernel scan.** Adding the HTTP module or `tests/http/` to the 13-path tuple, or importing Starlette from a kernel module, breaks the allowlist. `src/claimledger/__init__.py` must stay empty.
- **Unpinned framework.** `dependencies = []`. A route that imports Starlette must pin `starlette==1.0.0` and no other version. FastAPI would also publish an OpenAPI catalog, which this change rejects.
- **Gold drift.** Asserting any number other than the frozen strings, or subtracting the two compare values, relaxes the kernel. Compare stays two claims.
- **400-line review budget.** One mapper, one route, and focused tests should stay well under 400 lines. `sdd-tasks` should still forecast it. Not a reason to put the route inside `query.py`.

### Ready for Proposal

Yes. The orchestrator should tell the user that phase 6 is one route, `POST /claims/query`, implemented as a pure mapper plus one in-process Starlette app pinned at `starlette==1.0.0`. The body is only `question`. The route calls `understand` then `query` on `Ledger.seed()`, passes kernel abstain reasons through, emits an empty evidence list for seed claims, and returns both compare claims without a delta. It does not add `answer`, does not call `measure`, and does not start fase 7.
