"""Last four quarters, one kernel call each. No model picks a number."""

from __future__ import annotations

from dataclasses import dataclass

from claimledger.identity import PERIOD_2T26, fold
from claimledger.ledger import Ledger
from claimledger.lookup import Intent, understand
from claimledger.query import QueryResult, query


_QUARTER_ENDS = {3: 31, 6: 30, 9: 30, 12: 31}


@dataclass(frozen=True)
class SeriesRun:
    result: QueryResult
    gaps: tuple[str, ...]


def execute(question: str, ledger: Ledger) -> SeriesRun | None:
    if not _asks_last_four(question):
        return None
    base = understand(question)
    if (
        base.route != "identity"
        or base.statement is None
        or base.scope is None
        or base.metric is None
    ):
        return None
    claims = []
    gaps: list[str] = []
    for period in _window(PERIOD_2T26, 4):
        result = query(_step(base, period), ledger)
        if result.status == "verified" and len(result.claims) == 1:
            claims.append(result.claims[0])
        else:
            gaps.append(period)
    if not claims:
        return SeriesRun(
            result=QueryResult(status="abstained", reason="no_matching_claim"),
            gaps=tuple(gaps),
        )
    identity = f"{base.issuer}|*|{base.statement}|{base.scope}|{base.metric}"
    return SeriesRun(
        result=QueryResult(status="verified", claims=tuple(claims), identity=identity),
        gaps=tuple(gaps),
    )


def _asks_last_four(question: str) -> bool:
    folded = fold(question)
    counted = "4" in question or "cuatro" in folded
    return "ultimos" in folded and "trimestre" in folded and counted


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


def _window(end: str, count: int) -> tuple[str, ...]:
    year_text, month_text, _day = end.split("-")
    year, month = int(year_text), int(month_text)
    found: list[str] = []
    for _step_index in range(count):
        found.append(f"{year:04d}-{month:02d}-{_QUARTER_ENDS[month]:02d}")
        year, month = _previous_quarter(year, month)
    return tuple(reversed(found))


def _previous_quarter(year: int, month: int) -> tuple[int, int]:
    if month == 3:
        return year - 1, 12
    return year, month - 3
