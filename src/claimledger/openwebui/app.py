"""Open WebUI host. Starlette is imported only inside build_host."""

from __future__ import annotations

import json
import os

from claimledger.ingest.types import IngestError

MODEL_ID = "claimledger-card"


def _user_question(body: object) -> str | None:
    if not isinstance(body, dict) or body.get("model") != MODEL_ID:
        return None
    messages = body.get("messages")
    if not isinstance(messages, list):
        return None
    question: str | None = None
    for item in messages:
        if (
            isinstance(item, dict)
            and item.get("role") == "user"
            and isinstance(item.get("content"), str)
        ):
            question = item["content"]
    return question


def _completion(text: str) -> dict[str, object]:
    return {
        "id": "chatcmpl-claimledger",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
    }


def build_host(artifact_hash: str | None = None):
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse, StreamingResponse
    from starlette.routing import Route

    from claimledger.openwebui.reply import reply

    async def get_models(_request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "object": "list",
                "data": [{"id": MODEL_ID, "object": "model", "owned_by": "claimledger"}],
            }
        )

    def _hash() -> str | None:
        if artifact_hash is not None:
            return artifact_hash
        value = os.environ.get("CLAIMLEDGER_ARTIFACT_HASH")
        if isinstance(value, str) and value != "":
            return value
        return None

    async def post_completions(request: Request):
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse({"error": "unreadable_artifact"}, status_code=400)
        question = _user_question(body)
        digest = _hash()
        if question is None or digest is None:
            return JSONResponse({"error": "unreadable_artifact"}, status_code=400)
        try:
            text = reply(digest, question)
        except (IngestError, json.JSONDecodeError):
            return JSONResponse({"error": "unreadable_artifact"}, status_code=400)
        if isinstance(body, dict) and body.get("stream") is True:
            payload = json.dumps(
                {
                    "id": "chatcmpl-claimledger",
                    "object": "chat.completion.chunk",
                    "choices": [{"index": 0, "delta": {"content": text}}],
                },
                ensure_ascii=False,
            )

            async def chunks():
                yield f"data: {payload}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(chunks(), media_type="text/event-stream")
        return JSONResponse(_completion(text))

    return Starlette(
        routes=[
            Route("/v1/models", get_models, methods=["GET"]),
            Route("/v1/chat/completions", post_completions, methods=["POST"]),
        ]
    )
