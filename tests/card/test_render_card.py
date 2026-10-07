"""Claim card shows the kernel verdict beside row text."""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from claimledger.card.card import _METRIC_CHIP, ClaimCard, render_card
from claimledger.claim import FinancialClaim
from claimledger.identity import identity_key
from claimledger.query import QueryResult
from claimledger.retrieval.drawers import Candidate

REPO_ROOT = Path(__file__).resolve().parents[2]

CONSOLIDATED_ROW = "RESULTADO NETO DEL PERÍODO 21.262.335"
PARENT_ROW = "Resultado neto atribuible a la sociedad controlante 21.259.769"
CONSOLIDATED_VALUE = "21262335"
PARENT_VALUE = "21259769"
COMPARE_VALUE = "81956525"
CONSOLIDATED_CHIP = "BYMA · 1T26 · Consolidado · Resultado neto"
PARENT_CHIP = "BYMA · 1T26 · Controlante · Resultado neto"
CONSOLIDATED_SENTENCE = "encontré estas dos filas; verifiqué la consolidada"
PARENT_SENTENCE = "encontré estas dos filas; verifiqué la controlante"
_FORBIDDEN_IMPORTS = frozenset({"starlette", "docling", "llama_index", "open_webui"})
_CARD_PATHS = (
    "src/claimledger/card/__init__.py",
    "src/claimledger/card/card.py",
    "tests/card/test_render_card.py",
)


def _claim(period: str, scope: str, value: str) -> FinancialClaim:
    key = identity_key("BYMA", period, "income_statement", scope, "net_income")
    return FinancialClaim(
        identity_key=key,
        issuer="BYMA",
        period=period,
        statement="income_statement",
        scope=scope,
        metric="net_income",
        value=value,
        currency="ARS",
        unit=None,
        evidence=(),
        ledger_status="recorded",
    )


def _consolidated_claim(value: str = CONSOLIDATED_VALUE) -> FinancialClaim:
    return _claim("2026-03-31", "consolidated", value)


def _neighbor_rows() -> tuple[Candidate, Candidate]:
    return (
        Candidate(drawer="tables", text=CONSOLIDATED_ROW, ref="#/texts/0"),
        Candidate(drawer="tables", text=PARENT_ROW, ref="#/texts/1"),
    )


def _visible(card: ClaimCard) -> str:
    reason = card.reason or ""
    return " ".join(
        (
            card.seal,
            card.sentence,
            reason,
            card.difference,
            *card.chips,
            *card.rows,
            *card.values,
        )
    )


def _kernel_scan_paths() -> tuple[str, ...]:
    """Read `_kernel_scan_paths` from tests/test_identity.py. Do not edit that file."""
    tree = ast.parse((REPO_ROOT / "tests" / "test_identity.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "relatives"
                for target in stmt.targets
            ):
                continue
            elts = stmt.value.elts  # type: ignore[attr-defined]
            return tuple(
                elt.value
                for elt in elts
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            )
    raise AssertionError("_kernel_scan_paths missing")


def _import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_consolidated_card() -> None:
    claim = _consolidated_claim()
    result = QueryResult(
        status="verified", claims=(claim,), identity=claim.identity_key
    )
    candidates = (
        Candidate(drawer="tables", text=CONSOLIDATED_ROW, ref="#/texts/0"),
        Candidate(drawer="tables", text=PARENT_ROW, ref="#/texts/1"),
    )

    card = render_card(candidates, result)

    assert isinstance(card, ClaimCard)
    assert card.seal == "VERIFICADO"
    assert card.chips == (CONSOLIDATED_CHIP,)
    assert card.values == (CONSOLIDATED_VALUE,)
    assert PARENT_VALUE not in card.values
    assert card.rows == (CONSOLIDATED_ROW, PARENT_ROW)
    assert card.sentence == CONSOLIDATED_SENTENCE


def test_consolidated_card_copies_claim_value() -> None:
    claim = _consolidated_claim("100")
    result = QueryResult(status="verified", claims=(claim,), identity=claim.identity_key)
    candidates = (
        Candidate(drawer="tables", text=CONSOLIDATED_ROW, ref="#/texts/0"),
        Candidate(drawer="tables", text=PARENT_ROW, ref="#/texts/1"),
    )

    card = render_card(candidates, result)

    assert card.values == ("100",)
    assert CONSOLIDATED_VALUE not in card.values
    assert PARENT_VALUE not in card.values
    assert card.rows == (CONSOLIDATED_ROW, PARENT_ROW)


def test_parent_card() -> None:
    claim = _claim("2026-03-31", "parent_attributable", PARENT_VALUE)
    result = QueryResult(status="verified", claims=(claim,), identity=claim.identity_key)

    card = render_card(_neighbor_rows(), result)

    assert card.seal == "VERIFICADO"
    assert card.chips == (PARENT_CHIP,)
    assert all("Consolidado" not in chip for chip in card.chips)
    assert card.values == (PARENT_VALUE,)
    assert CONSOLIDATED_VALUE not in card.values
    assert card.rows == (CONSOLIDATED_ROW, PARENT_ROW)
    assert card.sentence == PARENT_SENTENCE
    assert "consolidada" not in card.sentence


def test_recipe_no_extract_abstains() -> None:
    claim = _consolidated_claim()
    result = QueryResult(
        status="abstained",
        reason="recipe_no_extract",
        claims=(claim,),
    )

    card = render_card(_neighbor_rows(), result)

    assert card.seal == "ME ABSTENGO"
    assert card.reason == "recipe_no_extract"
    assert card.sentence == ""
    assert "verifiqué" not in card.sentence
    assert card.values == ()
    assert CONSOLIDATED_VALUE not in card.values


def test_compare_shows_both_values_and_difference() -> None:
    earlier = _consolidated_claim()
    later = _claim("2026-06-30", "consolidated", COMPARE_VALUE)
    result = QueryResult(
        status="verified",
        claims=(earlier, later),
        identity="BYMA|*|income_statement|consolidated|net_income",
    )

    card = render_card(_neighbor_rows(), result, "60694190")

    assert card.values == (CONSOLIDATED_VALUE, COMPARE_VALUE)
    assert card.chips[1] == "BYMA · 2T26 · Consolidado · Resultado neto"
    assert "2026-06-30" not in card.chips[1]
    assert card.difference == "Diferencia entre las dos cifras verificadas: 60694190"
    assert "segundo trimestre" not in card.difference
    assert "trimestre aislado" not in card.difference
    assert "claims" not in card.difference
    assert "delta" not in {field.name for field in dataclasses.fields(ClaimCard)}
    assert not hasattr(card, "delta")
    assert _METRIC_CHIP == {"net_income": "Resultado neto"}


def test_compare_without_string_has_no_line() -> None:
    earlier = _consolidated_claim()
    later = _claim("2026-06-30", "consolidated", COMPARE_VALUE)
    result = QueryResult(
        status="verified",
        claims=(earlier, later),
        identity="BYMA|*|income_statement|consolidated|net_income",
    )

    for card in (
        render_card(_neighbor_rows(), result),
        render_card(_neighbor_rows(), result, None),
    ):
        assert card.difference == ""
        assert card.values == (CONSOLIDATED_VALUE, COMPARE_VALUE)
        assert "60694190" not in _visible(card)


def test_abstain_and_single_ignore_passed_string() -> None:
    claim = _consolidated_claim()
    abstained = QueryResult(
        status="abstained",
        reason="recipe_no_extract",
        claims=(claim,),
    )
    single = QueryResult(
        status="verified", claims=(claim,), identity=claim.identity_key
    )

    for result in (abstained, single):
        card = render_card(_neighbor_rows(), result, "60694190")
        assert card.difference == ""
        assert "60694190" not in _visible(card)


def test_seal_follows_query_status_not_ledger_status() -> None:
    claim = _consolidated_claim()
    assert claim.ledger_status == "recorded"
    result = QueryResult(
        status="abstained",
        reason="recipe_no_extract",
        claims=(claim,),
    )

    card = render_card(_neighbor_rows(), result)

    assert card.seal == "ME ABSTENGO"
    assert card.seal != "VERIFICADO"
    assert card.seal != claim.ledger_status


def test_unknown_verified_period_raises() -> None:
    claim = _claim("1999-01-01", "consolidated", CONSOLIDATED_VALUE)
    result = QueryResult(
        status="verified", claims=(claim,), identity=claim.identity_key
    )

    with pytest.raises(ValueError):
        render_card((), result)


def test_empty_candidates_still_abstain() -> None:
    result = QueryResult(status="abstained", reason="recipe_no_extract")

    card = render_card((), result)

    assert card.seal == "ME ABSTENGO"
    assert card.rows == ()
    assert card.values == ()


def test_render_card_does_not_call_kernel(monkeypatch) -> None:
    calls: list[str] = []

    def _spy(name: str):
        def _record(*_args, **_kwargs):
            calls.append(name)

        return _record

    monkeypatch.setattr("claimledger.eval.measure.measure", _spy("measure"))
    monkeypatch.setattr("claimledger.retrieval.drawers.retrieve", _spy("retrieve"))
    monkeypatch.setattr("claimledger.lookup.understand", _spy("understand"))
    monkeypatch.setattr("claimledger.query.query", _spy("query"))
    monkeypatch.setattr("claimledger.ledger.Ledger.upsert", _spy("upsert"))
    tree = ast.parse(
        (REPO_ROOT / "src/claimledger/card/card.py").read_text(encoding="utf-8")
    )
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    called.update(
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    )
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )

    claim = _consolidated_claim()
    card = render_card(
        _neighbor_rows(),
        QueryResult(status="verified", claims=(claim,), identity=claim.identity_key),
    )

    assert card.seal == "VERIFICADO"
    assert calls == []
    assert called.isdisjoint(
        {"measure", "retrieve", "understand", "query", "upsert", "difference"}
    )
    assert not any(
        module == "claimledger.period" or module.startswith("claimledger.period.")
        for module in imported
    )


def test_card_stays_off_kernel_allowlist() -> None:
    card_py = REPO_ROOT / "src" / "claimledger" / "card" / "card.py"
    assert _import_roots(card_py).isdisjoint(_FORBIDDEN_IMPORTS)
    allowlist = _kernel_scan_paths()
    assert len(allowlist) == 13
    for path in _CARD_PATHS:
        assert path not in allowlist
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "dependencies = []" in pyproject
