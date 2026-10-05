# Proposal: Phase 7 Open WebUI Host

## Intent

Open WebUI must show the existing card: both rows, seal, chips, and `21262335` or `21259769`. `manual/ui.py` cannot; query JSON has no candidates.

## Scope

### In Scope

- Sibling outside `http/`: `measure(artifact_hash, question)` then `render_card`.
- `GET /v1/models` and a card-only completions body: seal, chips, both rows, kernel value, sentence.
- Pin `ghcr.io/open-webui/open-webui:v0.11.4-slim` (v0.11.4, 2026-09-21). Compose opens it, not `manual/ui.py`.
- In-process pytest, stubbed reader. No container, port, network, PDF, or Docker.

### Out of Scope

- LLM, MCP, tools, Pipelines, Knowledge, Ollama, Action buttons, extra claims routes, query candidates.
- Card, `measure` signature, `http/`, gold, `dependencies`, 13-path allowlist.
- Fase 8, 9, 12, 13 stay waiting. No wave C. Keep the card and `manual/ui.py`.

## Capabilities

### New Capabilities

- `openwebui-host`: Slim Open WebUI shows one card. The host calls `measure` then `render_card` and returns only that text.

### Modified Capabilities

- None. `claim-card`, `http-query`, `verify-eval`, and `gold-regression` stay unchanged.

## Approach

Approach 1. A sibling off the 13 paths copies `ClaimCard` fields. No digit parse and no model. Slim image. Titles, follow-ups, Knowledge, tools stay off. Pytest stubs the reader. Empty `__init__.py`. No new dependency. HTTP pin stays `starlette==1.0.0`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| Sibling outside `http/` | New | `measure` then `render_card` |
| Host tests | New | In-process, stubbed reader |
| `docker-compose.yml` | Modified | Pin `v0.11.4-slim` |
| `card/`, `measure.py`, `http/` | Unchanged | Call or leave |
| `manual/ui.py` | Unchanged | Kept, not the close |
| `pyproject.toml`, `test_identity.py` | Unchanged | `[]` deps; 13 paths |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Speaker before the card | Med | Card-only body; slim; features off |
| Host picks the number | Med | Copy card fields |
| Mounted inside `http/` | Low | Sibling only |
| Docker in kernel tests, floating tag, or manual close | Med | Off the 13 paths; pin slim; open Open WebUI |

## Rollback Plan

Remove the host, its tests, and the Open WebUI service. Restore compose for `manual/ui.py`. Leave the card, query route, gold, and allowlist. No migration.

## Dependencies

- `measure` and `render_card`.
- Image `ghcr.io/open-webui/open-webui:v0.11.4-slim`.
- Configured hash for a live card. Do not commit gitignored artifacts.

## Success Criteria

- [ ] Open WebUI shows seal, chips, both rows, and the kernel value.
- [ ] Consolidated is `21262335`. Parent is `21259769`.
- [ ] Only product route: `POST /claims/query`.
- [ ] Host tests in-process, Docker-free. Kernel bans unchanged.
- [ ] `dependencies` stays `[]`. Allowlist stays 13. Manual UI is not the close.
