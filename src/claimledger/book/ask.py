"""Periods from the Cypher script. Each number comes from query."""

from __future__ import annotations

import re
from dataclasses import dataclass

from claimledger.identity import fold
from claimledger.ledger import Ledger
from claimledger.lookup import (
    ISSUER_BYMA,
    METRIC_NET_INCOME,
    SCOPE_CONSOLIDATED,
    STATEMENT_INCOME,
    Intent,
    understand,
)
from claimledger.query import QueryResult, query

_PERIOD_VALUE = re.compile(r'n\.period = "(\d{4}-\d{2}-\d{2})"')


@dataclass(frozen=True)
class BookRun:
    result: QueryResult
    gaps: tuple[str, ...]


def read_script() -> str:
    from claimledger.graph.build import graph_json_path

    path = graph_json_path().with_suffix(".cypher")
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def periods_in_script(script: str) -> tuple[str, ...]:
    found: list[str] = []
    for match in _PERIOD_VALUE.finditer(script):
        period = match.group(1)
        if period not in found:
            found.append(period)
    return tuple(sorted(found))


def ask(question: str, ledger: Ledger, script: str) -> BookRun | None:
    if not _asks_book(question):
        return None
    base = _identity(question)
    if base is None:
        return None
    periods = periods_in_script(script)
    if not periods:
        return None
    claims = []
    gaps: list[str] = []
    for period in periods:
        result = query(_step(base, period), ledger)
        if result.status == "verified" and len(result.claims) == 1:
            claims.append(result.claims[0])
        else:
            gaps.append(period)
    if not claims:
        return BookRun(
            result=QueryResult(status="abstained", reason="no_matching_claim"),
            gaps=tuple(gaps),
        )
    identity = f"{base.issuer}|*|{base.statement}|{base.scope}|{base.metric}"
    return BookRun(
        result=QueryResult(status="verified", claims=tuple(claims), identity=identity),
        gaps=tuple(gaps),
    )


def _asks_book(question: str) -> bool:
    folded = fold(question)
    if "todos" not in folded or "resultado" not in folded or "neto" not in folded:
        return False
    if "ypf" in folded or _asks_last_four(question):
        return False
    return True


def _asks_last_four(question: str) -> bool:
    folded = fold(question)
    counted = "4" in question or "cuatro" in folded
    return "ultimos" in folded and "trimestre" in folded and counted


def _identity(question: str) -> Intent | None:
    found = understand(question)
    if (
        found.route == "identity"
        and found.statement is not None
        and found.scope is not None
        and found.metric is not None
    ):
        return found
    if found.route == "abstain" and found.abstain_reason == "unresolved_identity":
        return Intent(
            route="identity",
            issuer=ISSUER_BYMA,
            statement=STATEMENT_INCOME,
            scope=SCOPE_CONSOLIDATED,
            metric=METRIC_NET_INCOME,
            period=None,
            compare=False,
        )
    return None


def _step(base: Intent, period: str) -> Intent:
    return Intent(
        route="identity",
        issuer=base.issuer,
        statement=base.statement,
        scope=base.scope,
        metric=base.metric,
        period=period,
        compare=False,
        abstain_reason=None,
    )
