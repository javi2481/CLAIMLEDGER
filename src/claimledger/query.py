"""Read-only Intent + Ledger → QueryResult. Never mutates the book."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from claimledger.claim import FinancialClaim
from claimledger.identity import PERIOD_1T26, PERIOD_2T26, identity_key
from claimledger.ledger import Ledger
from claimledger.lookup import Intent

QueryStatus = Literal["verified", "abstained"]

_BOOK_PERIODS = (PERIOD_1T26, PERIOD_2T26)


@dataclass(frozen=True)
class QueryResult:
    status: QueryStatus
    reason: str | None = None
    claims: tuple[FinancialClaim, ...] = ()
    identity: str | None = None


def _abstain(reason: str) -> QueryResult:
    return QueryResult(status="abstained", reason=reason)


def _verified(
    claims: tuple[FinancialClaim, ...], identity: str
) -> QueryResult:
    return QueryResult(status="verified", claims=claims, identity=identity)


def _recorded(ledger: Ledger, key: str) -> FinancialClaim | None:
    claim = ledger.get(key)
    if claim is None or claim.ledger_status != "recorded":
        return None
    return claim


def _key_for(intent: Intent, period: str) -> str:
    return identity_key(
        intent.issuer, period, intent.statement, intent.scope, intent.metric
    )


def _matching_recorded(intent: Intent, ledger: Ledger) -> tuple[FinancialClaim, ...]:
    found: list[FinancialClaim] = []
    for period in _BOOK_PERIODS:
        claim = _recorded(ledger, _key_for(intent, period))
        if claim is not None:
            found.append(claim)
    return tuple(found)


def query(intent: Intent, ledger: Ledger) -> QueryResult:
    if intent.route == "abstain":
        return _abstain(intent.abstain_reason or "unresolved_identity")
    if intent.route != "identity":
        return _abstain("unresolved_identity")
    if intent.statement is None or intent.scope is None or intent.metric is None:
        return _abstain("unresolved_identity")

    if intent.compare:
        claims = _matching_recorded(intent, ledger)
        if len(claims) != 2:
            return _abstain("incomplete_comparison")
        wildcard = f"{intent.issuer}|*|{intent.statement}|{intent.scope}|{intent.metric}"
        return _verified(claims, wildcard)

    if intent.period is None:
        claims = _matching_recorded(intent, ledger)
        if len(claims) >= 2:
            return _abstain("ambiguous_period")
        return _abstain("no_matching_claim")

    claim = _recorded(ledger, _key_for(intent, intent.period))
    if claim is None:
        return _abstain("no_matching_claim")
    return _verified((claim,), claim.identity_key)
