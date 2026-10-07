"""DeepSeek client: model and base URL; no live network."""

from __future__ import annotations

import os

import pytest


def test_client_targets_deepseek_flash_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from claimledger.agent import client as client_mod

    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-live")
    calls: list[dict] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "ok",
                            "tool_calls": [],
                        }
                    }
                ]
            }

    def fake_post(url: str, **kwargs: object) -> FakeResponse:
        calls.append({"url": url, **kwargs})
        return FakeResponse()

    monkeypatch.setattr(client_mod.httpx, "post", fake_post)

    result = client_mod.chat(
        messages=[{"role": "user", "content": "hola"}],
        tools=[],
    )

    assert calls, "client must POST once"
    assert calls[0]["url"] == "https://api.deepseek.com/chat/completions"
    body = calls[0]["json"]
    assert body["model"] == "deepseek-flash"
    assert result["choices"][0]["message"]["content"] == "ok"


def test_client_reads_api_key_header(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.agent import client as client_mod

    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-secret-value")
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"role": "assistant", "content": ""}}]}

    def fake_post(url: str, **kwargs: object) -> FakeResponse:
        captured.update(kwargs)
        return FakeResponse()

    monkeypatch.setattr(client_mod.httpx, "post", fake_post)
    client_mod.chat(messages=[{"role": "user", "content": "x"}], tools=[])

    headers = captured["headers"]
    assert headers["Authorization"] == "Bearer sk-secret-value"


def test_client_rejects_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.agent import client as client_mod

    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(client_mod.DeepSeekKeyError):
        client_mod.chat(messages=[{"role": "user", "content": "x"}], tools=[])
