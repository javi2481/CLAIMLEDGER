"""Agent tool loop: host executes tool_calls; missing key abstains safely."""

from __future__ import annotations

import json

import pytest

from claimledger.ledger import Ledger

CONSOLIDATED_QUESTION = (
    "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
)
CONSOLIDATED_VALUE = "21262335"


def test_loop_host_executes_verify_tool_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from claimledger.agent import loop as loop_mod

    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    monkeypatch.setattr(loop_mod, "recorded_book", Ledger.seed)

    tool_call = {
        "id": "call_1",
        "type": "function",
        "function": {
            "name": "verify",
            "arguments": json.dumps({"question": CONSOLIDATED_QUESTION}),
        },
    }

    def fake_chat(*, messages, tools=None, **_kwargs):
        if any(m.get("role") == "tool" for m in messages):
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"El valor verificado es {CONSOLIDATED_VALUE}.",
                            "tool_calls": [],
                        }
                    }
                ]
            }
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call],
                    }
                }
            ]
        }

    monkeypatch.setattr(loop_mod, "chat", fake_chat)

    outcome = loop_mod.run(CONSOLIDATED_QUESTION)

    assert outcome.tool_results
    verify_result = outcome.tool_results[0]
    assert verify_result["status"] == "verified"
    assert CONSOLIDATED_VALUE in verify_result["authorized_values"]
    assert outcome.abstained is False


def test_loop_missing_key_abstains_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from claimledger.agent import loop as loop_mod

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    outcome = loop_mod.run("cualquier pregunta")

    assert outcome.abstained is True
    assert outcome.content  # controlled path text
    assert "Traceback" not in outcome.content
    assert "DeepSeekKeyError" not in outcome.content


def test_loop_blank_key_abstains(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.agent import loop as loop_mod

    monkeypatch.setenv("DEEPSEEK_API_KEY", "   ")

    outcome = loop_mod.run("pregunta")

    assert outcome.abstained is True
    assert "Traceback" not in (outcome.content or "")
