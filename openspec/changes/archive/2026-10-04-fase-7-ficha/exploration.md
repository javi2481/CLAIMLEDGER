## Exploration: fase-7-ficha

Architecture is CLOSED. Phase 7 draws the card: seal, chips, and row text. The screen sentence is “encontré estas dos filas; verifiqué la consolidada”. The card displays the kernel verdict. It does not calculate a number and it does not choose `21262335` over `21259769`. Out of this change: an orchestrator, Pipelines, Knowledge RAG, photo crop (fase 8), subtraction (fase 9), and series charts (fase 12). No `/v1/chat/completions` mouth, because a model would be able to speak before the card. Open WebUI is not installed or run, and no Open WebUI version is pinned.

### Current State

`docs/plan-implementacion.md` closes phase 7 as Open WebUI in front of the API: seal, chips, and row text, with no orchestrator. Pipelines and Knowledge RAG are out. Wave B is done when the neighbor inequality is visible on that card. `docs/documento-rector.md` §6 says Open WebUI draws verified claims and does not calculate. §20 (“Cuando verificamos (Fase 4–7)”) is the screen sentence, the seal `VERIFICADO` / `ME ABSTENGO`, chips such as `BYMA · 1T26 · Consolidado · Resultado neto`, the row text, and the rule that a chat, if one exists, speaks after the card. §21 is later: verified series, Mermaid / matplotlib / Artifact, and click-through to a card. That drawing ladder is fase 12.

`docs/stack-oportunidades.md` offers two mouths. One is a CLAIMLEDGER “model” at `/v1/chat/completions` that emits citations. The other, called more robust there, is a button that calls `POST /claims/query` without tool-calling. The first UI is the card. The same section forbids Knowledge RAG, Pipelines, and a model-written chart. It mentions MCP from Open WebUI 0.6.31 as ecosystem context. This change does not pin or run that version.

`measure` (`src/claimledger/eval/measure.py`) returns `(candidates, QueryResult)`. It calls `retrieve(artifact_hash, "tables", question)`, then `understand(question)`, then `query(intent, Ledger.seed())`. `tests/eval/test_measure.py` stubs the reader and already shows both neighbor texts (`RESULTADO NETO DEL PERÍODO 21.262.335` and `Resultado neto atribuible a la sociedad controlante 21.259.769`) plus the verdict. Consolidated verifies `21262335`. Parent verifies `21259769`. `ledger_status` on those claims stays `recorded`. Both fixture rows share `ref` `#/tables/1`. A candidate is not a `FinancialClaim` and is not `verified`.

`POST /claims/query` (`src/claimledger/http/claims.py`, `src/claimledger/http/app.py`) returns rector JSON from `understand` then `query(Ledger.seed())`. One verified claim is `status`, `claim` (issuer, period, statement, scope, metric, value, currency), and `evidence`. Seed rows are stored with `evidence=()` (`src/claimledger/ledger.py`), so that JSON evidence is `[]`. The body has no `artifact_hash`. The route does not call `measure` or `retrieve`. Nothing in that JSON is a candidate list. `openspec/specs/http-query/spec.md` still allows only this route.

The 13-path allowlist is the tuple in `tests/test_identity.py` (`_kernel_scan_paths`, length 13): seven kernel modules and six kernel tests. `eval/` and `http/` stay outside it. Kernel tests must not import `docling`, `llama_index`, or `starlette`. `pyproject.toml` keeps `dependencies = []`. The only framework pin is the optional extra `http = ["starlette==1.0.0"]`. Gold numbers stay frozen.

There is no card package. There is no Open WebUI client in the repo.

### Affected Areas

- `src/claimledger/eval/measure.py` — read. Already returns the pair the card needs. Do not change its signature and do not make it render.
- `src/claimledger/query.py` — read. `QueryResult.status` is the seal source. Do not import a card here. Do not re-decide the neighbor.
- `src/claimledger/retrieval/drawers.py` — read. `Candidate.text` is the row text. `question` still does not drop a row. Shared `ref` still does not select.
- `src/claimledger/http/claims.py` and `src/claimledger/http/app.py` — read. Phase-6 JSON has no candidates and seed evidence is `[]`. Do not call `measure` from this route and do not add a second route.
- `src/claimledger/ledger.py` — read. `Ledger.seed()` evidence stays empty. `recorded` stays recorded.
- `tests/eval/test_measure.py` — read. Neighbor texts, frozen values, and the stubbed reader already exist. Do not retarget gold through the card.
- `tests/test_identity.py` — read. The 13-path tuple stays as it is. Do not add the card package or its tests.
- `openspec/specs/http-query/spec.md` — the only route stays `POST /claims/query`. A delta must not weaken that by stuffing candidates into this body.
- `openspec/specs/verify-eval/spec.md` — `measure` stays the join. The card consumes its return value and does not become a second judge.
- New sibling package outside the 13 paths, for example `src/claimledger/card/`, with tests outside the six kernel test files, for example `tests/card/`. `src/claimledger/__init__.py` stays empty.

### Approaches

1. **Pure card from `measure`’s pair** — A function takes `(candidates, QueryResult)` and returns a display dict. Seal is `VERIFICADO` when `result.status == "verified"` and `ME ABSTENGO` when `result.status == "abstained"`. Chips are a closed Spanish label map over the verified claim’s own fields (issuer, period, scope, metric), so the canonical consolidated case reads `BYMA · 1T26 · Consolidado · Resultado neto`. Row text is `Candidate.text` in retrieval order. The two-row sentence is emitted only for a single verified claim, and it names that claim’s scope. The function does not call `measure`, `retrieve`, `understand`, `query`, or `upsert`. It does not parse digits out of row text. Tests build the pair the way `tests/eval/test_measure.py` already does (stubbed reader, no PDF, no network) or pass the objects directly. No new library. No Docker. No Open WebUI process.
   - Pros: the two-row sentence has both inputs it needs. The card cannot re-choose the neighbor because it never compares the two numbers. Phase-6 JSON and gold stay untouched. Kernel tests stay free of a UI framework, `docling`, `llama_index`, and `starlette`. A later button can render this dict after the kernel has spoken.
   - Cons: `POST /claims/query` alone cannot feed this card. A running Open WebUI is not part of the pytest proof. The plan’s “Open WebUI draws the card” stays a host that this change does not install.
   - Effort: Low

2. **Card client of `POST /claims/query` only** — The button calls the existing route and the card renders that JSON.
   - Pros: matches the stack’s more robust mouth. No model speaks first. The route already exists and does not calculate.
   - Cons: the JSON has no candidates. Seed `evidence` is `[]`, so there is no row text to print. The screen sentence would be invented or omitted. Extending that JSON means calling `measure` from a route whose body has no artifact hash, which the archived HTTP contract forbids.
   - Effort: Low — **reject** as the card’s input

3. **`/v1/chat/completions` model, then the card** — A CLAIMLEDGER “model” emits citations and the UI paints a card from the completion.
   - Pros: matches the other mouth in `docs/stack-oportunidades.md`. Citations could carry page and text once a live Open WebUI exists.
   - Cons: the model can speak before the card. Rector §20 says the chat speaks after the card. This change forbids an LLM, forbids installing Open WebUI, and forbids inventing a version. Pipelines and Knowledge RAG stay out either way.
   - Effort: High — **reject**

4. **New route that calls `measure` and returns the card** — For example `POST /claims/card` with `question` plus `artifact_hash`.
   - Pros: a button would have one HTTP call that includes both rows and the verdict.
   - Cons: `openspec/specs/http-query/spec.md` allows only `POST /claims/query`. A second route is a new mouth, not the pure card. It still needs a hash the phase-6 body does not have, and it pulls retrieval onto the HTTP package. Open WebUI would still not be running.
   - Effort: Medium — **reject** for this change

### Recommendation

Take approach **1**. The card’s input is the pair `measure` already returns: `tuple[Candidate, ...]` and `QueryResult`. It is not the phase-6 JSON.

That input is required because the screen sentence needs both table candidates and the verdict. `measure` returns both. `claims_query` returns the verdict only, with `evidence: []` on `Ledger.seed()`, and its route must not call `measure`. A chat-completions model is the wrong mouth because it can speak before the card.

1. New code lives in a sibling package outside the seven kernel modules and outside the 13-path tuple. Kernel tests do not import it. The card module does not import `starlette`, `docling`, `llama_index`, or Open WebUI. `src/claimledger/__init__.py` stays empty. `dependencies` stays `[]`. No new extra.
2. `render_card(candidates, result)` does not call `measure`, `retrieve`, `understand`, `query`, or `upsert`. It does not read `ledger_status` as the seal. `recorded` stays recorded on the claim. The seal is `VERIFICADO` or `ME ABSTENGO` from `QueryResult.status` only.
3. Chips come from the verified claim’s fields through a closed display map. Canonical consolidated chips: `BYMA · 1T26 · Consolidado · Resultado neto`. A parent verdict is not labeled `Consolidado`. The map does not parse the question and does not parse candidate text.
4. Row text is the candidate texts, unchanged, in the order `measure` returned them. Both neighbor rows stay visible. The card does not pick a row by `ref`, by digits, or by comparing `21262335` with `21259769`. The verified value shown is `claim.value` from the kernel (`21262335` or `21259769` for the neighbor trap). Gold stays frozen.
5. The sentence “encontré estas dos filas; verifiqué la consolidada” is display copy for one verified consolidated claim when both row texts are present. A verified parent claim names the parent scope instead. An abstention keeps `ME ABSTENGO`, keeps the kernel reason, shows the rows if they were passed in, and does not say a row was verified. Compare stays two claims and does not subtract.
6. Tests sit in `tests/card/` and may reuse the stubbed reader pattern from `tests/eval/test_measure.py`. No PDF, no network, no Docker, no live Open WebUI. Do not edit `tests/test_identity.py`.

**In this change:** the pure card and pytest that prove seal, chips, both row texts, and the kernel verdict.

**Waits:** a running Open WebUI, any Open WebUI version pin, `/v1/chat/completions`, Pipelines, Knowledge, a second HTTP route, photo crop, subtraction, Mermaid and other charts, and the orchestrator.

### Risks

- **Phase-6 JSON mistaken for the card input.** Rendering `POST /claims/query` alone drops both neighbor texts because candidates are absent and seed evidence is `[]`. The card must take `measure`’s pair.
- **The card re-decides the neighbor.** Parsing `21.262.335` out of row text, or breaking the shared `#/tables/1` ref, would choose a claim the kernel already chose. Display `QueryResult` and print `Candidate.text` only.
- **`recorded` shown as verified.** Seed claims are `recorded` and the verdict is `verified`. The seal must read `QueryResult.status`. Copying `ledger_status` would abstain a verified claim or verify a stored row the judge did not return.
- **Abstention overridden by a nearby number.** A `recipe_no_extract` result can still arrive with both rows, including a row that contains `21262335`. The seal stays `ME ABSTENGO`. The sentence must not say the consolidated row was verified.
- **Chat before the card.** A `/v1/chat/completions` model can emit prose first. Rector §20 puts any chat after the card. This change does not add that mouth.
- **Kernel scan.** Adding `src/claimledger/card/` or `tests/card/` to the 13-path tuple, or importing a UI framework, `docling`, `llama_index`, or `starlette` from a kernel module, breaks the allowlist. Importing `Candidate` from `drawers.py` does not import `llama_index` at module level; importing `measure` and calling it does reach the reader. The card function should accept the pair and leave the call to the test or to a later host.
- **Second route.** Adding `POST /claims/card` would break the http-query rule that the only route is `POST /claims/query`, and it still needs an artifact hash.
- **Open WebUI host left unrun.** The plan’s visible closure is a ficha inside Open WebUI. This change proves the card dict in pytest and does not install the host, because kernel tests forbid Docker and network and no version may be invented. `sdd-propose` should keep that boundary.
- **Gold drift.** Asserting any number other than the frozen strings, or subtracting compare claims, relaxes the kernel. The card displays the values it was given.
- **400-line review budget.** One pure function and focused tests should stay well under 400 lines. `sdd-tasks` should still forecast it. Not a reason to put the card inside `query.py` or `claims.py`.

### Ready for Proposal

Yes. The orchestrator should tell the user that phase 7 is a pure card whose input is the `(candidates, QueryResult)` pair `measure` already returns, not the phase-6 JSON and not a chat-completions model. The card prints the kernel seal, Spanish chips, and both row texts, and it does not choose between `21262335` and `21259769`. Open WebUI is not installed in this change. Do not start `sdd-propose` inside this phase. Do not commit.
