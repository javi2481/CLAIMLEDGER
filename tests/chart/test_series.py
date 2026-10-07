"""Verified series → chart spec and Mermaid fence. No invented bar."""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

from claimledger.identity import PERIOD_1T26, PERIOD_2T26, identity_key
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query

_COMPARE = "Comparar resultado neto consolidado 1T26 vs 2T26"
_DIFFERENCE = "60694190"
_TAX_DIFFERENCE = "-17780588"
_GAP = "2026-09-30"
_EARLIER = "BYMA|2026-03-31|income_statement|consolidated|net_income"
_LATER = "BYMA|2026-06-30|income_statement|consolidated|net_income"


def _compare_result() -> QueryResult:
    return query(understand(_COMPARE), Ledger.seed())


def test_series_copies_both_verified_values() -> None:
    from claimledger.chart.series import series_spec

    result = _compare_result()
    spec = series_spec(result)

    assert spec is not None
    assert spec.status == "verified"
    assert spec.title == "Resultado neto consolidado"
    assert [point.label for point in spec.points] == ["1T26", "2T26"]
    assert [point.value for point in spec.points] == ["21262335", "81956525"]
    assert [point.identity for point in spec.points] == [_EARLIER, _LATER]
    assert _DIFFERENCE not in [point.value for point in spec.points]
    assert [claim.value for claim in result.claims] == ["21262335", "81956525"]


def test_missing_period_is_a_hole() -> None:
    from claimledger.chart.series import series_spec

    spec = series_spec(_compare_result(), gaps=(_GAP,))

    assert spec is not None
    assert spec.status == "partial"
    assert [(point.label, point.value) for point in spec.points] == [
        ("1T26", "21262335"),
        ("2T26", "81956525"),
        (_GAP, None),
    ]
    assert spec.points[2].identity is None


def test_non_series_returns_none() -> None:
    from claimledger.chart.series import series_spec

    result = _compare_result()
    earlier, later = result.claims
    assert series_spec(QueryResult(status="abstained", reason="incomplete_comparison")) is None
    assert series_spec(QueryResult(status="verified", claims=(earlier,), identity=earlier.identity_key)) is None
    mismatched = dataclasses.replace(
        later,
        scope="parent_attributable",
        identity_key=identity_key(
            later.issuer,
            later.period,
            later.statement,
            "parent_attributable",
            later.metric,
        ),
    )
    assert series_spec(
        QueryResult(status="verified", claims=(earlier, mismatched), identity=result.identity)
    ) is None
    conflicted = dataclasses.replace(later, ledger_status="conflicted")
    assert series_spec(
        QueryResult(status="verified", claims=(earlier, conflicted), identity=result.identity)
    ) is None


def test_draw_copies_bars_and_names_holes() -> None:
    from claimledger.chart.series import draw, series_spec

    spec = series_spec(_compare_result())
    text = draw(spec)

    assert "bar [21262335, 81956525]" in text
    assert 'y-axis "ARS" 21262335 --> 81956525' in text
    assert _EARLIER in text
    assert _LATER in text
    assert _DIFFERENCE not in text
    assert draw(None) == ""

    hole = draw(series_spec(_compare_result(), gaps=(_GAP,)))
    assert f"Hueco: {_GAP}" in hole
    assert "bar [21262335, 81956525]" in hole
    assert _GAP not in hole.split("bar [", 1)[1].split("]", 1)[0]

    ledger = Ledger.seed()
    tax = tuple(
        ledger.get(identity_key("BYMA", period, "income_statement", "consolidated", "income_tax"))
        for period in (PERIOD_1T26, PERIOD_2T26)
    )
    assert tax[0] is not None and tax[1] is not None
    signed = draw(series_spec(QueryResult(status="verified", claims=tax, identity="tax")))
    assert "bar [-14950948, -32731536]" in signed
    assert _TAX_DIFFERENCE not in signed


def test_chart_stays_off_query_and_docling() -> None:
    repo = Path(__file__).resolve().parents[2]
    chart = repo / "src" / "claimledger" / "chart"
    for path in chart.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not any(name == "docling" or name.startswith("docling.") for name in names)

    for relative in ("src/claimledger/query.py", "src/claimledger/eval/measure.py"):
        tree = ast.parse((repo / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            assert not any(name == "claimledger.chart" or name.startswith("claimledger.chart.") for name in modules)

    fields = {field.name for field in dataclasses.fields(QueryResult)}
    assert fields == {"status", "reason", "claims", "identity"}
