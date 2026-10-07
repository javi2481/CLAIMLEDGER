"""DeepSeek tool loop: host executes tool_calls; missing key → abstention."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

from claimledger.agent.client import DeepSeekKeyError, chat
from claimledger.agent.template import ABSTENTION_TEMPLATE
from claimledger.agent.tools import search, verify
from claimledger.ingest.ground import recorded_book

ToolName = Literal["verify", "search"]

_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "verify",
            "description": "Authorize figures via kernel understand/query on the book.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Find Docling JSON evidence (text/page/ref only).",
            "parameters": {
                "type": "object",
                "properties": {
                    "artifact_hash": {"type": "string"},
                    "question": {"type": "string"},
                },
                "required": ["artifact_hash", "question"],
            },
        },
    },
]


@dataclass(frozen=True)
class LoopOutcome:
    abstained: bool
    content: str
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    authorized_values: list[str] = field(default_factory=list)


def run(
    question: str,
    *,
    artifact_hash: str = "",
    max_rounds: int = 4,
) -> LoopOutcome:
    try:
        return _run_loop(question, artifact_hash=artifact_hash, max_rounds=max_rounds)
    except DeepSeekKeyError:
        return LoopOutcome(abstained=True, content=ABSTENTION_TEMPLATE)
    except Exception:
        return LoopOutcome(abstained=True, content=ABSTENTION_TEMPLATE)


def _run_loop(
    question: str,
    *,
    artifact_hash: str,
    max_rounds: int,
) -> LoopOutcome:
    messages: list[dict[str, Any]] = [{"role": "user", "content": question}]
    tool_results: list[dict[str, Any]] = []
    authorized: list[str] = []

    for _ in range(max_rounds):
        response = chat(messages=messages, tools=_TOOL_SCHEMAS)
        message = response["choices"][0]["message"]
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            content = message.get("content") or ""
            if not authorized:
                return LoopOutcome(
                    abstained=True,
                    content=ABSTENTION_TEMPLATE,
                    tool_results=tool_results,
                    authorized_values=[],
                )
            return LoopOutcome(
                abstained=False,
                content=content,
                tool_results=tool_results,
                authorized_values=list(authorized),
            )

        messages.append(message)
        for call in tool_calls:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"] or "{}")
            result = _execute_tool(name, args, artifact_hash=artifact_hash)
            tool_results.append(result)
            if name == "verify" and result.get("status") == "verified":
                authorized.extend(result.get("authorized_values") or [])
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return LoopOutcome(
        abstained=True,
        content=ABSTENTION_TEMPLATE,
        tool_results=tool_results,
        authorized_values=list(authorized),
    )


def _execute_tool(
    name: str,
    args: dict[str, Any],
    *,
    artifact_hash: str,
) -> dict[str, Any]:
    if name == "verify":
        return verify(str(args.get("question", "")), recorded_book())
    if name == "search":
        digest = str(args.get("artifact_hash") or artifact_hash)
        return search(digest, str(args.get("question", "")))
    return {"error": f"unknown_tool:{name}"}
