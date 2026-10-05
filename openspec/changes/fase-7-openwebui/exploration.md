## Exploration: fase-7-openwebui

Architecture is CLOSED. This change supplies only the host that `openspec/changes/archive/2026-10-04-fase-7-ficha/` left under Waits: a running Open WebUI that draws the existing card. The card package stays the display. The host does not calculate, does not parse digits, and does not let an LLM choose `21262335` or `21259769`. Out of this change, and still waiting: fase 8 photo crop, fase 9 subtraction, fase 12 charts, and fase 13 orchestrator. Also out: Pipelines, Knowledge RAG, MinerU, a second claims route, and stuffing candidates into `POST /claims/query`.

### Current State

`docs/plan-implementacion.md` closes wave B when someone sees `21.262.335 ≠ 21.259.769` on a card inside Open WebUI. The phase 7 row is Open WebUI in front of the API: seal, chips, and row text, with no orchestrator. Pipelines and Knowledge RAG are out. Wave C (phases 8–13) does not start here.

`docs/documento-rector.md` §6 names Open WebUI as the interface. The mouth is an OpenAI-compatible backend or an OpenAPI/MCP tool. Pipelines are out. CLAIMLEDGER verifies; Open WebUI draws. §20 (“Cuando verificamos (Fase 4–7)”) is the sentence, the seal `VERIFICADO` / `ME ABSTENGO`, chips such as `BYMA · 1T26 · Consolidado · Resultado neto`, the row text, and the rule that a chat, if one exists, speaks after the card. §21 drawing (Mermaid, matplotlib, Artifact) is fase 12.

`render_card(candidates, result)` in `src/claimledger/card/card.py` already returns a frozen `ClaimCard`. The seal comes from `QueryResult.status`. Chips come from the closed Spanish map. Both row texts are `Candidate.text` in order. `values` copies `claim.value`. The sentence is emitted only for one verified claim with two rows. The function does not call `measure`, `retrieve`, `understand`, `query`, or `upsert`, and it does not parse digits. `openspec/specs/claim-card/spec.md` forbids that module from importing `starlette`, `docling`, `llama_index`, or `open_webui`.

`measure(artifact_hash, question)` in `src/claimledger/eval/measure.py` returns `(candidates, result)`. That pair is the card input. It retrieves the tables drawer, then calls `understand` and `query(Ledger.seed())`. `tests/eval/test_measure.py` already shows both neighbor texts and the frozen values `21262335` (consolidated) and `21259769` (parent) with a stubbed reader.

`POST /claims/query` (`src/claimledger/http/`) calls `understand` then `query(Ledger.seed())`. It does not call `measure`. Seed evidence is `[]`. The JSON has no candidates, so it cannot print both row texts. `openspec/specs/http-query/spec.md` allows only that route from `src/claimledger/http/`.

`manual/ui.py` is a browser page served by the current image (`Dockerfile` CMD, `docker-compose.yml` port 8000). It posts to `/claims/query` and prints a sentence from that JSON. It is not Open WebUI and it is not the phase-7 close. It is a temporary stand-in.

`dependencies` in `pyproject.toml` stays `[]`. The only HTTP extra pin is `starlette==1.0.0`. The 13-path allowlist in `tests/test_identity.py` (`_kernel_scan_paths`) is seven kernel modules and six kernel tests. Kernel tests must not import `docling`, must not use the network, a PDF, or Docker (`AGENTS.md`, `docs/fase-0.md`).

No Open WebUI image is pinned in the repo. Docs mention MCP from 0.6.31 as a floor, not a pin. A real release exists and is safe to pin: GitHub release [v0.11.4](https://github.com/open-webui/open-webui/releases/tag/v0.11.4) (published 2026-09-21, not a prerelease). The GHCR manifests for `ghcr.io/open-webui/open-webui:v0.11.4` and `ghcr.io/open-webui/open-webui:v0.11.4-slim` both return HTTP 200. The upstream compose file on that tag defaults `WEBUI_DOCKER_TAG` to `main`. Do not use `main` or `latest`. The v0.11.4 notes say the slim image leaves local models out. That is the image to run.

Open WebUI’s own docs treat an OpenAI-compatible connection as the protocol mouth (`/v1/models`, chat completions): [OpenAI-compatible](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/). Tools are abilities an LLM calls. Functions customize the UI. Pipelines are the separate advanced server. [Tools & Functions](https://docs.openwebui.com/features/extensibility/plugin/) still says pipelines are for advanced offload. The plan keeps Pipelines out.

### Affected Areas

- `src/claimledger/card/card.py` — read. Host calls `render_card`. Do not change the card, its maps, or its import ban.
- `src/claimledger/eval/measure.py` — read. Host calls `measure` to obtain the pair. Do not make `measure` render, and do not change its signature.
- `src/claimledger/http/` and `openspec/specs/http-query/spec.md` — read. The only product route stays `POST /claims/query`. Do not mount the host here and do not add candidates to that JSON.
- `manual/ui.py`, `Dockerfile`, `docker-compose.yml` — the stand-in on port 8000. Leave the module. The phase-7 run must not present this page as the close.
- `tests/test_identity.py` — read. The 13-path tuple stays unchanged. Host code and host tests stay off it.
- `pyproject.toml` — `dependencies` stays `[]`. No Open WebUI pip package. No new extra. `uvicorn` stays unpinned in the project, as the HTTP spec already requires.
- New sibling package outside `http/` and outside the 13 paths, with tests outside the six kernel files. `src/claimledger/__init__.py` stays empty.

### Approaches

1. **Deterministic OpenAI-compatible host that prints the existing card** — A sibling module calls `measure(artifact_hash, question)` then `render_card(candidates, result)` and formats that `ClaimCard` as the only assistant text: seal, chips, both row texts, kernel `values`, and the sentence when the card already set one. A small Starlette app, not inside `src/claimledger/http/`, exposes `GET /v1/models` and `POST /v1/chat/completions` and returns that text. There is no model weight and no generation step. Open WebUI `v0.11.4-slim` is a connection client pointed at that app. No Ollama, no Pipelines, no Knowledge, no MCP tool call. Pytest builds the pair the way `tests/eval/test_measure.py` already does (stubbed reader, in-process ASGI, no bound port, no PDF, no network, no container) and asserts the consolidated card shows `21262335` with both neighbor rows, and the parent card shows `21259769`.
   - Pros: Matches rector §6’s OpenAI-compatible mouth and the plan’s “Open WebUI → API” picture without an LLM that can speak first. The card still owns seal, chips, and rows. Both neighbor texts come from `measure`, which `POST /claims/query` cannot supply. Pytest proves the adapter without a live container. Kernel tests stay Docker-free because they do not import this package.
   - Cons: The operator must point the host at a real `artifact_hash` under `artifacts/docling/` (gitignored) before the live screen shows those rows. Open WebUI task calls (titles, follow-ups) must stay off so they are not a second speaker. The completions URL is the protocol Open WebUI already speaks; it is not an LLM mouth.
   - Effort: Medium

2. **Action button that calls `POST /claims/query`** — The stack’s “more robust” button, with no tool-calling.
   - Pros: No model chooses a tool. The product route already exists.
   - Cons: That JSON has no candidates and seed `evidence` is `[]`, so both row texts are missing. Stuffing candidates into the body breaks `http-query`. An Action also attaches to a message, so something would speak before the card.
   - Effort: Low — **reject**

3. **Second product route, for example `POST /claims/card`** — The claims app calls `measure` and returns the card.
   - Pros: One HTTP call would carry rows and the verdict.
   - Cons: `openspec/specs/http-query/spec.md` says `src/claimledger/http/` exposes only `POST /claims/query`. A second route on that package is a new product mouth. The hash does not belong on the phase-6 body. The host can call `measure` in its own package without widening that spec.
   - Effort: Medium — **reject**

4. **MCP or OpenAPI tool, or a `/v1/chat/completions` LLM** — A model calls a tool or writes the reply, and the UI paints a card from that.
   - Pros: Cited in the rector as an alternate mouth, and in the stack as the citation model. MCP exists from 0.6.31.
   - Cons: The model can speak before the card and can restate the number. Rector §20 puts any chat after the card. The archived card change rejected this LLM mouth for that reason. 0.6.31 is a floor, not a pin. Pipelines and Knowledge RAG stay out either way.
   - Effort: High — **reject**

5. **Treat `manual/ui.py` as the close** — Keep the current image on port 8000.
   - Pros: It already runs.
   - Cons: It is not Open WebUI. It reads phase-6 JSON, so it cannot show both neighbor rows. The plan’s close is the card inside Open WebUI.
   - Effort: Low — **reject**

### Recommendation

Take approach **1**. Pin `ghcr.io/open-webui/open-webui:v0.11.4-slim` ([release v0.11.4](https://github.com/open-webui/open-webui/releases/tag/v0.11.4); GHCR manifest HTTP 200). Do not pin `latest` or `main`.

The host is a sibling of `http/`, not a second claims route. It calls `measure` then the existing `render_card`, and the completions response is only that card. Open WebUI draws the markdown. No LLM chooses the number. `POST /claims/query` stays the only route in `src/claimledger/http/`, with no candidates added. `manual/ui.py` stays in the tree and stops being the face of the demo once this host is the compose entry the user opens.

Pytest can prove the adapter without a live container: stub the reader, call the formatter and the in-process ASGI app, assert seal, chips, both row texts, `21262335` for consolidated and `21259769` for parent. Kernel tests still forbid Docker; they do not import the host, and `_kernel_scan_paths` stays the same 13 paths. `dependencies` stays `[]`.

**In this change:** the host adapter, its in-process tests, and a compose run of Open WebUI `v0.11.4-slim` pointed at that adapter.

**Waits:** fase 8 crop, fase 9 subtraction, fase 12 charts (Mermaid / matplotlib / Artifact), fase 13 orchestrator. Also still out: Pipelines, Knowledge RAG, an LLM completions mouth, MCP tool-calling as the speaker, and any edit to the archived `fase-7-ficha` change.

### Risks

- **Phase-6 JSON used as the card feed.** `POST /claims/query` has no candidates and seed evidence is `[]`. The host must call `measure`, then `render_card`.
- **An LLM speaks before the card.** Title generation, follow-ups, Knowledge, tools, MCP, or a bundled Ollama model can emit a number first. The slim image has no local model. Do not attach one. Leave those Open WebUI features off.
- **The host re-decides the neighbor.** Formatting must copy `ClaimCard` fields. It must not parse `21.262.335` out of row text or compare the two kernel values.
- **Second claims route.** Mounting `/v1/chat/completions` inside `src/claimledger/http/` would break the only-route rule. Keep that package untouched.
- **Kernel scan and Docker.** Adding the host to `_kernel_scan_paths`, or starting a container from a kernel test, breaks the allowlist and the kernel rule. Host tests stay in-process and off the 13 paths.
- **Live rows need a hash.** `artifacts/docling/` is gitignored. Pytest stubs the reader. The running host needs a configured `artifact_hash` or the live card has no row text.
- **Floating image tags.** Upstream compose defaults to `main`. `latest` also exists on GHCR. Pin `v0.11.4-slim` only.
- **Stand-in confusion.** Leaving port 8000’s manual page as the thing the user opens would not close phase 7.
- **400-line review budget.** Adapter, tests, and compose notes should stay under 400 authored lines. `sdd-tasks` still forecasts it.

### Ready for Proposal

Yes. Nothing found here stops `sdd-propose`. The orchestrator should tell the user that phase 7’s host is Open WebUI `v0.11.4-slim` drawing the existing card through a deterministic OpenAI-compatible adapter that calls `measure` then `render_card`, with no LLM choosing the number. Pytest proves that adapter without a container. Kernel tests still forbid Docker. Fase 8, 9, 12, and 13 stay waiting. Do not start `sdd-propose` inside this phase. Do not commit. Do not start wave C.
