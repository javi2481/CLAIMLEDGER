# Proposal: LLM tools host

## Intent

Completions are card-only. Need tool-orchestrated prose without the model authorizing figures. Gap: no pinned component gates LLM prose or abstains via template. Search finds. Verify authorizes. DeepSeek drafts/orchestrates. Host gates. CLAIMLEDGER owns the datum.

## Scope

### In Scope

- `src/claimledger/agent/`: tools `verify` + `search`; DeepSeek tool loop; host gate; normalize guard; abstention template.
- `verify` → `{status, claims, authorized_values}` via `understand`/`query` on `recorded_book()` (plus existing `execute`/`ask`/`difference`).
- `search` → LlamaIndex Docling JSON text/page/ref only (never `verified`/`authorized_values`).
- Model `deepseek-flash` @ `https://api.deepseek.com`; **host executes** tool calls.
- Verified → prose + normalize guard (dates/pages/periods exempt). Abstained → template only (no LLM financial prose).
- Wire `openwebui/reply.py` (card first + gated prose or template). Inject `DEEPSEEK_API_KEY`; optional `httpx` extra; `dependencies` stays `[]`.
- Tests: mock DeepSeek; stub search; gate evals.

### Out of Scope

Neo4j; VLM; Pipelines/Open WebUI tools; DocLang tool; edits to `query.py`/`ledger.py`/gold/`identity_key`; relaxing gold; verified-path word-number NLP; prompt-only gate.

## Capabilities

### New Capabilities

- `agent-host`: verify/search tools, DeepSeek loop, host gate (verified claims + `authorized_values`), normalize guard, abstention template, evidence ≠ authorization.

### Modified Capabilities

- `openwebui-host`: card-first may append host-gated prose or abstention template; Features Off unchanged; host enforces authorization.

## Approach

Approach 1. Truth = verified claims; `authorized_values` = canonical projection. Prompt helps; host enforces. TDD A–D. Kernel network-free.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/claimledger/agent/` | New | Tools, loop, gate, guard, template |
| `openwebui/reply.py` | Modified | Card + gated prose or template |
| compose / `.env.example` | Modified | `DEEPSEEK_API_KEY` |
| `pyproject.toml` | Modified | Optional HTTP extra |
| `tests/agent/`, `tests/openwebui/` | New/Modified | Mocked evals |
| Kernel / gold / Neo4j / Pipelines | Unchanged | OUT |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Spec drift card-only→gate | Med | Delta: Features Off + host enforcement |
| Abstained prose leak | High | Short-circuit; no LLM financial call |
| Metadata as claims | Med | Exempt dates/pages/periods |
| Verified word-number hole | Med | Accepted MVP |
| Live API in pytest | Med | Mock; kernel offline |
| 400-line budget | High | Chained PRs A–D |

## Rollback Plan

Delete `agent/` + tests. Restore card-only `reply`. Drop DeepSeek env/extra. Revert deltas. Book and kernel remain.

## Dependencies

`ground-ledger` archived. Local `DEEPSEEK_API_KEY` (never committed).

## Success Criteria

- [ ] Host executes tools; model never writes `identity_key` or authorizes figures.
- [ ] Verified: only normalized `authorized_values` leave; metadata exempt.
- [ ] Abstained: template only; no LLM financial prose.
- [ ] Search never authorizes; Features Off; gold + 13-path intact; kernel network-free.
