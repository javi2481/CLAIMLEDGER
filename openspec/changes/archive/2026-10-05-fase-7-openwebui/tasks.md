# Tasks: Phase 7 Open WebUI Host

## Review Workload Forecast

Estimated changed lines: 620–760. Delivery strategy: ask-on-risk. Four PRs. No wave C.

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain on the current branch, no commits unless the user asks. Same delivery as fases 1–7. There is no remote.
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Copy card fields | PR 1 | `pytest tests/openwebui/test_host.py::test_card_text_copies_fields` | N/A — in-memory card | Delete `text.py`, empty `__init__.py`, slice-1 test |
| 2 | Measure then card | PR 2 | `pytest tests/openwebui/test_host.py -k reply` | N/A — stub `read_hashed_json`; no container | Delete `reply.py` and slice-2 tests |
| 3 | Host routes | PR 3 | `pytest tests/openwebui/test_host.py -k "models or completions or bounds"` | N/A — in-process ASGI, port `None` | Delete `app.py` and route tests |
| 4 | Slim screen | PR 4 | `pytest tests/openwebui/test_host.py::test_compose_pins_slim_screen` | N/A — YAML text; do not start Docker | Restore port `8000`; drop `openwebui` |

## Phase 1: card_text (Slice 1)

- [x] 1.1 RED: `test_card_text_copies_fields`. In-memory `ClaimCard`. `claimledger.openwebui.text.card_text(card: ClaimCard) -> str` joins non-empty seal, chips, rows, values, sentence, reason with `\n` only. Do not call `measure`. MUST fail `ModuleNotFoundError` or `ImportError`. No PDF, network, or Docker.
- [x] 1.2 GREEN: Empty `src/claimledger/openwebui/__init__.py` and `card_text` in `text.py`. Copy fields. No Starlette, `measure`, or `render_card`. MUST pass. Do not edit `pyproject.toml`, the 13-path allowlist, `http/`, `card/`, or `measure.py`.

## Phase 2: reply (Slice 2)

- [x] 2.1 RED: Stub `claimledger.retrieval.read.read_hashed_json`. `claimledger.openwebui.reply.reply(artifact_hash: str, question: str) -> str` returns `card_text` after `measure` then `render_card`. Consolidated `21262335`. Parent `21259769`, both rows. Abstain `ME ABSTENGO` adds no verified value. Compare copies both values and no delta. Bad hash raises `IngestError` or `json.JSONDecodeError` and invents no rows. `pytest -k reply` MUST fail. No Docker.
- [x] 2.2 GREEN: `reply.py`: `measure`, then `return card_text(render_card(candidates, result))`. Do not catch errors, parse digits, or import Starlette. MUST pass.

## Phase 3: build_host (Slice 3)

- [x] 3.1 RED: In-process `claimledger.openwebui.app.build_host(artifact_hash: str | None = None)` (`testserver`, port `None`). `GET /v1/models` lists only `MODEL_ID = "claimledger-card"`. `POST /v1/chat/completions` is `_completion` of the card. `_user_question(body)` is the last user `str`. Else or a bad hash: 400 `{"error":"unreadable_artifact"}`, no `measure` or `render_card`. `stream: true`: one SSE card, then `data: [DONE]`. Off `claimledger.http.app` (`POST /claims/query` only). Allowlist stays 13. No module-top Starlette import. MUST fail. No Docker.
- [x] 3.2 GREEN: `app.py` sets `MODEL_ID`, `_user_question`, `_completion`, `build_host`. Import Starlette only inside `build_host`. Nested `get_models`, `post_completions`. Those routes only. `None` reads `CLAIMLEDGER_ARTIFACT_HASH` per request. `dependencies` stays `[]`. Do not pin uvicorn or edit the allowlist, `http/`, or `src/claimledger/__init__.py`. MUST pass.

## Phase 4: Compose (Slice 4)

- [x] 4.1 RED: `test_compose_pins_slim_screen` reads `docker-compose.yml` as text. No Docker. `claimledger` publishes no port, runs uvicorn `claimledger.openwebui.app:build_host` `--factory` on `8000`, and sets `CLAIMLEDGER_ARTIFACT_HASH`. `openwebui` is `ghcr.io/open-webui/open-webui:v0.11.4-slim` at `8080:8080`, base `http://claimledger:8000/v1`, key `claimledger`. OpenAI on. Ollama, titles, follow-ups, tags, autocomplete, Knowledge, tools, MCP, and Pipelines off. `Dockerfile` CMD stays `manual.ui:build_manual_app`. MUST fail now.
- [x] 4.2 GREEN: Edit only `docker-compose.yml`. Leave `Dockerfile`, `manual/ui.py`, and `pyproject.toml`. MUST pass. Do not start Docker.

## Phase 5: Wave C waits (Slice 5)

- [x] 5.1 `test_wave_c_still_waits` locks Closed Bounds / Wave C waits. The package tree has no `crop`, `chart`, `charts`, or `orchestrator`. The only active change is `fase-7-openwebui`. No production code: the absence already held, so the new test passed on the first run.
