"""DeepSeek OpenAI-compatible HTTP client. Optional httpx; no live calls in pytest."""

from __future__ import annotations

import os
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover — optional extra
    httpx = None  # type: ignore[assignment]

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-flash"
_CHAT_PATH = "/chat/completions"


class DeepSeekKeyError(RuntimeError):
    """Missing or empty DEEPSEEK_API_KEY."""


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    *,
    api_key: str | None = None,
) -> dict[str, Any]:
    key = (api_key if api_key is not None else os.environ.get("DEEPSEEK_API_KEY", "")).strip()
    if not key:
        raise DeepSeekKeyError("missing or empty DEEPSEEK_API_KEY")
    if httpx is None:
        raise RuntimeError("httpx is required for DeepSeek client; install claimledger[deepseek]")

    payload: dict[str, Any] = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    response = httpx.post(
        f"{DEEPSEEK_BASE_URL}{_CHAT_PATH}",
        json=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()
