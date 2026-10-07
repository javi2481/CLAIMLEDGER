"""Period pack: difference is later minus earlier on a verified pair, else None."""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

from claimledger.claim import FinancialClaim
from claimledger.identity import PERIOD_1T26, PERIOD_2T26, identity_key
from claimledger.ledger import RECIPE_ROWS, Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query

_COMPARE_QUESTION = "Comparar resultado neto consolidado 1T26 vs 2T26"
_COMPARE_DIFFERENCE = "60694190"
_SIGNED_DIFFERENCE = "-17780588"
_WILDCARD_NET_INCOME = "BYMA|*|income_statement|consolidated|net_income"
_WILDCARD_INCOME_TAX = "BYMA|*|income_statement|consolidated|income_tax"


def _seed_pair(metric: str = "net_income") -> tuple[FinancialClaim, FinancialClaim]:
    ledger = Ledger.seed()
    earlier = ledger.get(
        identity_key("BYMA", PERIOD_1T26, "income_statement", "consolidated", metric)
    )
    later = ledger.get(
        identity_key("BYMA", PERIOD_2T26, "income_statement", "consolidated", metric)
    )
    assert earlier is not None
    assert later is not None
    return earlier, later


def _verified(
    claims: tuple[FinancialClaim, ...], identity: str = _WILDCARD_NET_INCOME
) -> QueryResult:
    return QueryResult(status="verified", claims=claims, identity=identity)


def _rekeyed(claim: FinancialClaim, **changes: str) -> FinancialClaim:
    merged = {
        "issuer": claim.issuer,
        "period": claim.period,
        "statement": claim.statement,
        "scope": claim.scope,
        "metric": claim.metric,
    }
    for field in merged:
        if field in changes:
            merged[field] = changes[field]
    return dataclasses.replace(
        claim,
        identity_key=identity_key(
            merged["issuer"],
            merged["period"],
            merged["statement"],
            merged["scope"],
            merged["metric"],
        ),
        **changes,
    )


def test_net_income_difference_is_later_minus_earlier() -> None:
    from claimledger.period.difference import difference

    result = query(understand(_COMPARE_QUESTION), Ledger.seed())

    outcome = difference(result)

    assert result.status == "verified"
    assert [claim.value for claim in result.claims] == ["21262335", "81956525"]
    assert _COMPARE_DIFFERENCE not in [claim.value for claim in result.claims]
    assert outcome == _COMPARE_DIFFERENCE
    assert isinstance(outcome, str)
    assert not isinstance(outcome, FinancialClaim)
    assert not hasattr(outcome, "identity_key")


def test_signed_pair_keeps_minus() -> None:
    from claimledger.period.difference import difference

    earlier, later = _seed_pair("income_tax")
    assert earlier.value == "-14950948"
    assert later.value == "-32731536"
    result = _verified((earlier, later), _WILDCARD_INCOME_TAX)

    assert difference(result) == _SIGNED_DIFFERENCE

    positive = difference(_verified(_seed_pair()))
    assert positive == _COMPARE_DIFFERENCE
    assert not positive.startswith("+")

    first, second = _seed_pair()
    level = dataclasses.replace(second, value=first.value)
    assert difference(_verified((first, level))) == "0"


def test_order_follows_period_not_tuple_order() -> None:
    from claimledger.period.difference import difference

    earlier, later = _seed_pair()

    assert difference(_verified((later, earlier))) == _COMPARE_DIFFERENCE
    assert difference(_verified((earlier, later))) == _COMPARE_DIFFERENCE


def test_mismatch_returns_none() -> None:
    from claimledger.period.difference import difference

    earlier, later = _seed_pair()

    mismatched = (
        _rekeyed(later, issuer="YPF"),
        _rekeyed(later, statement="balance_sheet"),
        _rekeyed(later, scope="parent_attributable"),
        _rekeyed(later, metric="gross_profit"),
        dataclasses.replace(later, unit="ARS"),
    )
    assert len(mismatched) == 5
    for variant in mismatched:
        assert difference(_verified((earlier, variant))) is None


def test_non_pair_returns_none() -> None:
    from claimledger.period.difference import difference

    earlier, later = _seed_pair()
    third = Ledger.seed().get(
        identity_key(
            "BYMA", PERIOD_1T26, "income_statement", "consolidated", "gross_profit"
        )
    )
    assert third is not None
    same_period = dataclasses.replace(
        later, period=earlier.period, identity_key=earlier.identity_key
    )
    abstained = QueryResult(
        status="abstained", reason="incomplete_comparison", claims=(earlier, later)
    )
    conflicted = dataclasses.replace(later, ledger_status="conflicted")

    assert difference(_verified((earlier, same_period))) is None
    assert difference(abstained) is None
    assert difference(_verified((earlier,))) is None
    assert difference(_verified((earlier, later, third))) is None
    assert difference(_verified(())) is None
    assert difference(_verified((earlier, conflicted))) is None


def test_rows_and_imports_stay_closed() -> None:
    assert len(RECIPE_ROWS) == 14

    repo = Path(__file__).resolve().parents[2]
    for relative in ("src/claimledger/query.py", "src/claimledger/eval/measure.py"):
        tree = ast.parse(
            (repo / relative).read_text(encoding="utf-8"), filename=relative
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    not alias.name.startswith("claimledger.period")
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith("claimledger.period")

    period_dir = repo / "src" / "claimledger" / "period"
    assert period_dir.is_dir()
    sources = sorted(path.name for path in period_dir.glob("*.py"))
    assert sources == ["__init__.py", "difference.py"]
    for path in period_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not any(
                name == "docling" or name.startswith("docling.") for name in names
            )

    difference_tree = ast.parse(
        (period_dir / "difference.py").read_text(encoding="utf-8"),
        filename="difference.py",
    )
    from_modules: set[str] = set()
    query_names: list[str] = []
    for node in ast.walk(difference_tree):
        assert not isinstance(node, ast.Import)
        if isinstance(node, ast.ImportFrom) and node.module:
            from_modules.add(node.module)
            if node.module == "claimledger.query":
                query_names.extend(alias.name for alias in node.names)
    assert from_modules == {"__future__", "claimledger.query"}
    assert query_names == ["QueryResult"]

    assert [field.name for field in dataclasses.fields(QueryResult)] == [
        "status",
        "reason",
        "claims",
        "identity",
    ]
