# Tasks: LLM tools host

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~550–750 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR A → B → C → D |
| Delivery strategy | sequential A→B→C→D on current branch (resolved) |
| Chain strategy | single working tree — no PRs / no commit / no push |

Decision needed before apply: No (resolved by user)
Chained PRs recommended: Yes (forecast); delivery = sequential slices, no PRs
Chain strategy: single-working-tree (no stacked PRs)
400-line budget risk: High

**Apply MUST NOT commit unless the user asks.** Phase 10 / Neo4j / VLM / Pipelines / DocLang out. `dependencies` stays `[]`.

### Suggested Work Units

| Unit | Goal | PR | Focused test | Runtime harness | Rollback |
|------|------|----|--------------|-----------------|----------|
| A | verify/search | PR1←feature | `pytest tests/agent/test_tools.py -q` | N/A no net | drop tools+tests |
| B | client+loop mock | PR2←PR1 | `pytest tests/agent/test_{client,loop}.py -q` | N/A mocked | drop client/loop+tests |
| C | gate+reply+env | PR3←PR2 | `pytest tests/agent/test_{gate,normalize}.py tests/openwebui/test_host.py -q` | N/A in-process | card-only reply; drop env/extra |
| D | evals | PR4←PR3 | `pytest tests/agent/test_evals.py -q` | N/A stubs | drop evals |

### Closed bounds

MUST NOT touch: `query.py`, `ledger.py`, gold, `identity_key`, 13-path allowlist. Kernel network/docling-free. Stub book; mock DeepSeek.

## Slice A: Tools verify/search (no network)

- [x] 1.1 RED: `tests/agent/test_tools.py` — verified stub `21262335` → `status=verified`, `authorized_values` has `"21262335"`.
- [x] 1.2 GREEN: `agent/__init__.py` + `tools.py` `verify` via `understand`/`query` on stubbed book.
- [x] 1.3 RED→GREEN: abstained → empty `claims` + `authorized_values`.
- [x] 1.4 RED: `search` → text/page/ref only; never `verified`/`authorized_values`.
- [x] 1.5 GREEN: stubbed LlamaIndex/Docling JSON search.
- [x] 1.6 RED→GREEN: `identity_key` not from model; `agent/` off allowlist. Slice A green.

## Slice B: deepseek-flash client + loop (mock)

- [x] 2.1 RED: `tests/agent/test_client.py` — `deepseek-flash` @ `https://api.deepseek.com`; no live net.
- [x] 2.2 GREEN: `client.py` + optional `httpx` extra (`dependencies` `[]`).
- [x] 2.3 RED: `tests/agent/test_loop.py` — mocked `verify` `tool_call`; host executes.
- [x] 2.4 GREEN: `loop.py` host-runs tools.
- [x] 2.5 RED→GREEN: missing/invalid `DEEPSEEK_API_KEY` → abstention; no stack trace. Slice B green.

## Slice C: Gate + template + reply + compose

- [x] 3.1 RED: `tests/agent/test_normalize.py` — dots/commas/spaces/`$` → `21262335`; dates/pages/periods exempt.
- [x] 3.2 GREEN: `normalize.py`.
- [x] 3.3 RED: `tests/agent/test_gate.py` — authorized OK; unauthorized after one regen → template.
- [x] 3.4 GREEN: `gate.py`.
- [x] 3.5 RED→GREEN: empty auth + word-form → `template.py` Spanish `ME ABSTENGO` constant (lock in RED).
- [x] 3.6 RED: `tests/openwebui/test_host.py` — card first then prose OR template; Features Off; no LLM gold auth.
- [x] 3.7 GREEN: wire `reply.py`; compose inject `DEEPSEEK_API_KEY`; `.env.example`. Slice C green.

## Slice D: Evals YPF / recipe_no_extract / metadata

- [x] 4.1 RED→GREEN: `tests/agent/test_evals.py` YPF verified — no invented figure.
- [x] 4.2 RED→GREEN: `recipe_no_extract`/abstained → template only.
- [x] 4.3 RED→GREEN: metadata (`31/03/2026`, `página 14`, `1Q26`) exempt. Full `pytest` green. No commit.
