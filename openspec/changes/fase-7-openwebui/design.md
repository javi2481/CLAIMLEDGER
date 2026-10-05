# Design: Phase 7 Open WebUI Host

## Technical Approach

`specs/openwebui-host/spec.md`. `src/claimledger/openwebui/` is outside `src/claimledger/http/`. `reply` calls `measure(artifact_hash, question)` then `render_card`. `card_text` copies that `ClaimCard` into the only assistant string. `build_host` serves `GET /v1/models` and `POST /v1/chat/completions`. Compose runs `ghcr.io/open-webui/open-webui:v0.11.4-slim` against that host.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Location | `src/claimledger/openwebui/` | Routes on `http/app.py`; `POST /claims/card` | Only product route is `POST /claims/query` |
| Call order | `reply` → `measure` → `render_card` → `card_text` | Phase-6 JSON | No candidates |
| Numbers | Copy `values` in order | Parse digits; pick either gold value | The card already chose |
| Body | One choice; `content` is `card_text` | Title, follow-up, tool, MCP, Knowledge | One completion is one card |
| Bad hash | 400 `{"error":"unreadable_artifact"}`; skip `render_card` | Empty verified card | No invented rows or values |
| Models | `MODEL_ID = "claimledger-card"` | LLM id; card payload | Models is not a card |
| Screen | Only `openwebui` publishes a port | `manual/ui.py`; `latest`; `main` | Slim image is the screen |
| Deps | No `pyproject.toml` edit | Pin `uvicorn` or Open WebUI | HTTP extra stays `starlette==1.0.0` |
| Tests | In-process ASGI, stubbed reader | Docker, port, network, PDF | Closed bounds |
| Wave C | Fases 8, 9, 12, 13 wait | Crop, subtraction, charts, orchestrator | Spec |

## Data Flow

```
openwebui v0.11.4-slim
  POST /v1/chat/completions   last user string = question
        |
build_host   hash = argument or CLAIMLEDGER_ARTIFACT_HASH
        |
reply → measure → render_card → card_text
        |
choices[0].message.content    one card, including abstain and compare
```

`GET /v1/models` returns `{"object":"list","data":[{"id":"claimledger-card","object":"model","owned_by":"claimledger"}]}` and stops.

`card_text` joins non-empty fields with `\n`: `seal`, each chip, each row, each value, `sentence` if set, `reason` if set. No other line. Consolidated `values` is `21262335`; the parent row may still show. Parent `values` is `21259769`. Compare copies both value strings and appends no difference. `IngestError` or `json.JSONDecodeError` from `measure` is 400 and skips `render_card`. `stream: true` is one SSE object with the full card in `delta.content`, then `data: [DONE]`. One `reply` call either way.

## File Changes

| File | Action | Description |
|---|---|---|
| `src/claimledger/openwebui/__init__.py` | Create | Empty marker |
| `src/claimledger/openwebui/text.py` | Create | `card_text(card: ClaimCard) -> str` |
| `src/claimledger/openwebui/reply.py` | Create | `reply(artifact_hash: str, question: str) -> str` |
| `src/claimledger/openwebui/app.py` | Create | `MODEL_ID`, `_user_question`, `_completion`, `build_host` |
| `tests/openwebui/test_host.py` | Create | In-process tests |
| `docker-compose.yml` | Modify | Slim UI pointed at the host |
| `http/`, `card/`, `measure.py`, `manual/ui.py`, `Dockerfile`, `pyproject.toml`, `src/claimledger/__init__.py`, `tests/test_identity.py` | Unchanged | Bounds |

## Interfaces / Contracts

Import Starlette only inside `build_host`. `text.py` and `reply.py` do not.

```python
MODEL_ID = "claimledger-card"  # claimledger.openwebui.app

def card_text(card: ClaimCard) -> str: ...

def reply(artifact_hash: str, question: str) -> str:
    candidates, result = measure(artifact_hash, question)
    return card_text(render_card(candidates, result))

def build_host(artifact_hash: str | None = None):
    # None reads CLAIMLEDGER_ARTIFACT_HASH per request.
    # Nested get_models, post_completions.
    # GET /v1/models and POST /v1/chat/completions only.
```

`_user_question(body)` is the last `messages` item with `role=="user"` and `content` a `str`. Any other body, or `model` other than `MODEL_ID`, is 400 `{"error":"unreadable_artifact"}` and does not call `measure`. Authorization is ignored.

`_completion(text)` is `{"id":"chatcmpl-claimledger","object":"chat.completion","choices":[{"index":0,"message":{"role":"assistant","content":text},"finish_reason":"stop"}]}`.

Compose `claimledger`: `build: .`, command `["uvicorn", "claimledger.openwebui.app:build_host", "--factory", "--host", "0.0.0.0", "--port", "8000"]`, `CLAIMLEDGER_ARTIFACT_HASH: ${CLAIMLEDGER_ARTIFACT_HASH:-}`, no `ports`. Service `openwebui`: image `ghcr.io/open-webui/open-webui:v0.11.4-slim`, `ports: ["8080:8080"]`, `OPENAI_API_BASE_URL=http://claimledger:8000/v1`, `OPENAI_API_KEYS=claimledger`, `ENABLE_OPENAI_API=true`, `ENABLE_OLLAMA_API=false`, `ENABLE_TITLE_GENERATION=false`, `ENABLE_FOLLOW_UP_GENERATION=false`, `ENABLE_TAGS_GENERATION=false`, `ENABLE_AUTOCOMPLETE_GENERATION=false`. No Knowledge volume, tool server, MCP, Pipelines, or Ollama. Dockerfile `CMD` stays `manual.ui:build_manual_app`. `uvicorn` stays an image install, not a `pyproject.toml` pin.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Field copy; abstain adds no verified value; compare has both values and no delta | Call `card_text` |
| Integration | Card content; models has `MODEL_ID` only; bad hash is 400; query route unchanged; slim tag; 13 paths | In-process ASGI (`testserver`, port `None`). Stub `read_hashed_json` |
| E2E | Out of scope | No container, port, network, or PDF |

## Threat Matrix

| Boundary | Applicability | Design response | Planned RED tests |
|---|---|---|---|
| Documentation-like paths | N/A: no executable-doc classification | — | — |
| Git repository selection | N/A: no git cwd selection | — | — |
| Commit state | N/A: no commit | — | — |
| Push state | N/A: no push | — | — |
| PR commands | N/A: no PR automation | — | — |

## Migration / Rollout

No migration. Rollback deletes the new package, `tests/openwebui/`, and service `openwebui`, and restores `claimledger` port `8000` without the command override. Card, query route, gold, and the allowlist stay.

## Open Questions

None. Live use needs `CLAIMLEDGER_ARTIFACT_HASH`. Do not commit gitignored artifacts.
