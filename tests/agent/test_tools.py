"""Agent tools: verify authorizes; search finds only."""

from __future__ import annotations

from pathlib import Path

import pytest

from claimledger.ledger import Ledger

CONSOLIDATED_QUESTION = (
    "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
)
ABSTAIN_QUESTION = "resultado neto del período en la memoria anual"
CONSOLIDATED_VALUE = "21262335"


def test_verify_verified_projects_authorized_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools

    monkeypatch.setattr(tools, "recorded_book", Ledger.seed)

    result = tools.verify(CONSOLIDATED_QUESTION)

    assert result["status"] == "verified"
    assert CONSOLIDATED_VALUE in result["authorized_values"]


def test_verify_abstained_empties_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools

    monkeypatch.setattr(tools, "recorded_book", Ledger.seed)

    result = tools.verify(ABSTAIN_QUESTION)

    assert result["status"] == "abstained"
    assert result["claims"] == []
    assert result["authorized_values"] == []


def test_search_returns_text_page_ref_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools
    from claimledger.retrieval.drawers import Candidate

    hits = (
        Candidate(
            drawer="tables",
            text="RESULTADO NETO DEL PERÍODO 21.262.335",
            ref="#/tables/1",
        ),
    )
    monkeypatch.setattr(
        tools,
        "retrieve",
        lambda artifact_hash, drawer, question: hits,
    )

    result = tools.search("deadbeef", "resultado neto")

    assert "verified" not in result
    assert "authorized_values" not in result
    assert "status" not in result
    assert len(result["hits"]) == 1
    hit = result["hits"][0]
    assert hit["text"] == "RESULTADO NETO DEL PERÍODO 21.262.335"
    assert hit["ref"] == "#/tables/1"
    assert "page" in hit
    assert set(hit) <= {"text", "page", "ref"}


def test_search_never_authorizes_digits_in_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools
    from claimledger.retrieval.drawers import Candidate

    monkeypatch.setattr(
        tools,
        "retrieve",
        lambda *_a, **_k: (
            Candidate(drawer="tables", text="21.262.335", ref="#/tables/1"),
        ),
    )

    result = tools.search("hash", "q")

    assert "authorized_values" not in result
    assert "verified" not in result
    assert result["hits"][0]["text"] == "21.262.335"


def test_identity_key_comes_from_kernel_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools

    monkeypatch.setattr(tools, "recorded_book", Ledger.seed)

    result = tools.verify(CONSOLIDATED_QUESTION)

    assert result["status"] == "verified"
    assert len(result["claims"]) >= 1
    claim = result["claims"][0]
    assert "identity_key" in claim
    assert claim["value"] == CONSOLIDATED_VALUE
    assert "|" in claim["identity_key"]


def test_agent_package_off_kernel_allowlist() -> None:
    import ast

    repo = Path(__file__).resolve().parents[2]
    tree = ast.parse((repo / "tests" / "test_identity.py").read_text(encoding="utf-8"))
    relatives: tuple[str, ...] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "relatives" for t in stmt.targets
            ):
                relatives = tuple(elt.value for elt in stmt.value.elts)
    assert relatives is not None
    assert len(relatives) == 13
    assert not any("agent" in path for path in relatives)
    agent_init = repo / "src" / "claimledger" / "agent" / "__init__.py"
    assert agent_init.is_file()
    assert agent_init.relative_to(repo).as_posix() not in relatives
