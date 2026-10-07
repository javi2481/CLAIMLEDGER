## Exploration: llm-tools-host

Architecture is CLOSED. Product idea (locked): Search finds. Verify authorizes. DeepSeek decides tools and drafts. Host controls what can leave. CLAIMLEDGER keeps authority over the datum.

Prerequisite: `ground-ledger` is archived at `openspec/changes/archive/2026-10-07-ground-ledger/`. Product paths already use `recorded_book()`; kernel gold stays `Ledger.seed()`. Design locked in plan `llm_tools_host_732e4561.plan.md`.

### Current State

**Host today is card-only.** `src/claimledger/openwebui/reply.py` builds one completion: `recorded_book()` → `execute` / `ask` / `measure` → `render_card` → optional crop images → optional Mermaid fence. `src/claimledger/openwebui/app.py` exposes `GET /v1/models` and `POST /v1/chat/completions` and returns that string. Open WebUI `v0.11.4-slim` draws only. No LLM, no tool loop, no prose after the card.

**Verify path already exists as deterministic kernel callers.** `measure` retrieves tables candidates then `understand` + `query(ledger)`. `execute` / `ask` / `difference` fan out or subtract without inventing values. `QueryResult` is `verified | abstained` with `claims: tuple[FinancialClaim, ...]`. Claim `value` is already a canonical digit string (`^-?\d+$`). There is no `authorized_values` projection yet — that is a new agent-facing shape derived from verified claim values.

**Search path already exists as retrieval.** `retrieval/read.py` loads hashed Docling JSON via pinned `DoclingReader(export_type="json")` + `DoclingNodeParser`. `drawers.retrieve` returns `Candidate(drawer, text, ref)` — evidence/context only. Candidates never authorize a number (`openspec/specs/json-retrieval`, `verify-eval`).

**No `src/claimledger/agent/` package.** Sibling packages already off the 13-path allowlist: `openwebui/`, `chart/`, `orchestrate/`, `book/`, `eval/`, `http/`, `crop/`, `card/`, `retrieval/`, `ingest/`, `graph/`. Pattern to copy: new package outside kernel; tests outside the six kernel files; `src/claimledger/__init__.py` stays empty.

**Digits helper is kernel-scoped.** `digits.digits_ars` normalizes thousand-dot ARS forms and rejects commas / trailing `m`. The host claim-value guard needs a broader normalizer (dots, commas, spaces, `$`) and must treat dates/pages/period labels as non-financial. That logic belongs in the agent package — do not widen `digits.py` or touch `query.py` / `ledger.py` / gold / `identity_key`.

**Secrets stub exists; compose does not inject it.** `.env.example` already has `DEEPSEEK_API_KEY=`. `docker-compose.yml` only sets `CLAIMLEDGER_ARTIFACT_HASH` on `claimledger`. No DeepSeek client, no `httpx` / OpenAI SDK pin in `pyproject.toml` extras.

**Spec tension to resolve in propose/spec (not invent architecture).** `openspec/specs/openwebui-host/spec.md` currently requires: card-only completion; host MUST NOT parse digits or let an LLM choose gold figures; Open WebUI tools / Pipelines / Knowledge / MCP stay off. This change keeps Open WebUI as a dumb drawer and keeps Pipelines out, but adds an internal CLAIMLEDGER tool loop and gated prose (or a controlled abstention template) after the card. Delta specs must restate: Open WebUI features stay off; the host (not the model) enforces authorization; verified claims are the unit of truth; `authorized_values` are the gate projection.

### Affected Areas

- `src/claimledger/agent/` (new) — tools `verify` / `search`, DeepSeek client + tool loop, host gate, numeric normalize guard, abstention template. Off the 13-path allowlist.
- `src/claimledger/openwebui/reply.py` — compose: card first, then gated DeepSeek prose **or** controlled abstention template (no LLM financial prose on abstained).
- `src/claimledger/openwebui/app.py` — unchanged protocol surface; still completions → `reply`.
- `docker-compose.yml` / `.env.example` — inject `DEEPSEEK_API_KEY` from `.env` into `claimledger` only; never commit secrets.
- `pyproject.toml` — optional extra for HTTP client to DeepSeek (e.g. pinned `httpx`) if needed; `dependencies` stays `[]`.
- `tests/agent/`, `tests/openwebui/` — mock DeepSeek; stub search; verified normalize evals; abstained template evals (LLM word-number prose must not reach the user).
- `openspec/specs/openwebui-host/spec.md` — MODIFIED: card-first + gate; Features Off still bans Open WebUI tools/Pipelines.
- Read-only reuse: `ingest/ground.recorded_book`, `lookup.understand`, `query.query`, `orchestrate.execute`, `book.ask`, `period.difference`, `retrieval.drawers` / `read`, `card.render_card`, `crop.attach`, `chart.draw`.
- **OUT (do not touch):** `query.py`, `ledger.py`, gold files, `identity_key` / kernel allowlist contents, Neo4j server, DocLang tool, VLM, Pipelines, relaxing `21262335` / `21259769`.

### Approaches

1. **Sibling `agent/` host with verify + search tools, DeepSeek tool loop, claim-value gate** — Package outside kernel. Tool `verify` wraps `understand` + `query` on `recorded_book()` (and host-owned compare/series paths via existing `execute` / `ask` / `difference`) and returns structured `{status, claims, authorized_values}`. Tool `search` wraps LlamaIndex over hashed Docling JSON; returns text/page/ref only — never `verified` / `authorized_values`. Host runs DeepSeek `deepseek-flash` at `https://api.deepseek.com` (OpenAI-compatible); model emits `tool_call`; host executes. Gate: verified → accumulate claims → DeepSeek prose → normalize numeric forms → allow only authorized values (dates/pages/periods exempt). Abstained → **no LLM financial prose**; deterministic abstention template only. Open WebUI draws the assembled completion.
   - Pros: Matches locked product split; reuses kernel and retrieval without skipping them; prompt is help, not enforcement; abstained path closes word-number leakage without NLP; TDD slices A–D map cleanly; rollback is delete `agent/` + restore card-only `reply`.
   - Cons: New optional network dependency (mocked in tests); openwebui-host delta must carefully preserve card-first and Features Off; guard MVP does not catch “21.26 millones” on verified path (accepted by plan).
   - Effort: Medium–High

2. **Open WebUI Pipelines / native tools as the loop** — Model tools and gates live in Open WebUI or a Pipelines server.
   - Pros: Less custom host code.
   - Cons: Moves authority out of CLAIMLEDGER; contradicts rector and Features Off; Pipelines explicitly OUT.
   - Effort: Medium — **reject**

3. **Prompt-only gate (no host normalize / no abstained template)** — Trust system prompt and model schema strict mode.
   - Pros: Smallest code change.
   - Cons: Prompt is not enforcement; word-number prose can leak on abstain; violates hard rules.
   - Effort: Low — **reject**

4. **Fold agent into `openwebui/` without a sibling package** — Client, tools, and gate live next to `reply.py`.
   - Pros: Fewer packages.
   - Cons: Blurs “Open WebUI draws only” vs orchestration; harder to keep kernel-adjacent tests and allowlist seals clean; weaker Architecture Gate story than `chart/` / `orchestrate/` siblings.
   - Effort: Medium — **reject** (prefer sibling `agent/`)

### Recommendation

Take approach **1**.

Defaults already locked (do not reopen):

| Decision | Choice |
|----------|--------|
| Package | `src/claimledger/agent/` outside kernel |
| Tools (MVP) | `verify` + `search`; DocLang later sidecar |
| Model | `deepseek-flash` @ `https://api.deepseek.com` |
| Secrets | `DEEPSEEK_API_KEY` from `.env` only |
| Loop location | Inside CLAIMLEDGER host (not Open WebUI tools, not Pipelines) |
| Unit of truth | Verified claims; `authorized_values` = canonical projection |
| Guard | Normalize numeric forms; dates/pages/periods not financial claims |
| Abstained | Controlled template only — no LLM financial prose |
| Verified | DeepSeek prose + guard (normalize) then response |
| Evidence ≠ authorization | Search never authorizes assertion |
| OUT | Neo4j, DocLang tool, VLM, Pipelines, gold relax, `query.py` / `ledger.py` / gold / `identity_key` |

Apply slices (TDD, red first):

| Slice | Scope |
|-------|--------|
| A | Tools `verify` / `search`; `claims` + `authorized_values` contract; no network |
| B | DeepSeek client + tool loop (mock); missing key → controlled error / abstention |
| C | Host gate verified (normalize) + abstained (template); ficha; compose + `.env` |
| D | Evals YPF / `recipe_no_extract` / metadata in prose |

Native-stack note: LlamaIndex already does retrieval; Docling already parses. Gap named by this change: no pinned stack component runs an authorization gate over LLM prose or an abstention template that forbids financial prose when verify abstains. That gap is the `agent/` host.

### Risks

- **Spec drift on openwebui-host.** Card-only and “MUST NOT parse digits / MUST NOT let an LLM choose” wording must become host-enforced authorization without allowing Open WebUI tools or Pipelines back in.
- **Abstained leakage.** Any path that still asks DeepSeek for free prose when `authorized_values == []` breaks the hard rule. Assembly must short-circuit to the template.
- **Naive digit regex.** Stripping all digits would treat `31/03/2026`, `página 14`, `1Q26` as claims. Guard must normalize financial forms and exempt metadata.
- **Verified MVP hole.** Natural-language magnitudes (“veintiún millones”) on the verified path are out of MVP; do not pretend the guard covers them — harden only via abstained short-circuit and later contract.
- **Kernel / allowlist.** Putting agent code on the 13-path scan, importing DeepSeek from kernel modules, or editing `query.py` / gold breaks Fase 0. Agent and its tests stay outside.
- **Network in tests.** Live DeepSeek calls are forbidden in pytest; mock the client. Kernel suite stays network-free.
- **Compose secret handling.** Inject from `.env`; never commit real keys; document `.env.example` only.
- **Search misread as authority.** UI or prose that treats retrieval hits as verified numbers violates “evidence ≠ authorization.”
- **400-line review budget.** Slices A–D likely need chained PRs; `sdd-tasks` must forecast.

### Ready for Proposal

Yes. Prerequisite archive is done; active change folder can open. Next phase: `sdd-propose` for `llm-tools-host` with scope, hard rules, rollback (delete `agent/`, restore card-only `reply`, remove DeepSeek env from compose), and explicit OUT list. Do not implement code in explore. Do not commit.
