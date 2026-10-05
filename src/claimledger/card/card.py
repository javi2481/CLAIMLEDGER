"""Display the kernel verdict beside row text. No kernel calls."""

from __future__ import annotations

from dataclasses import dataclass

from claimledger.claim import FinancialClaim
from claimledger.query import QueryResult
from claimledger.retrieval.drawers import Candidate

_PERIOD_CHIP = {"2026-03-31": "1T26", "2026-06-30": "2T26"}
_SCOPE_CHIP = {
    "consolidated": "Consolidado",
    "parent_attributable": "Controlante",
}
_METRIC_CHIP = {"net_income": "Resultado neto"}
_SEAL = {"verified": "VERIFICADO", "abstained": "ME ABSTENGO"}
_SENTENCE = {
    "consolidated": "encontré estas dos filas; verifiqué la consolidada",
    "parent_attributable": "encontré estas dos filas; verifiqué la controlante",
}


@dataclass(frozen=True)
class ClaimCard:
    seal: str
    chips: tuple[str, ...]
    rows: tuple[str, ...]
    values: tuple[str, ...]
    sentence: str
    reason: str | None


def render_card(
    candidates: tuple[Candidate, ...], result: QueryResult
) -> ClaimCard:
    rows = tuple(candidate.text for candidate in candidates)
    if result.status != "verified":
        return ClaimCard(
            seal=_SEAL.get(result.status, ""),
            chips=(),
            rows=rows,
            values=(),
            sentence="",
            reason=result.reason,
        )
    claim = result.claims[0] if len(result.claims) == 1 else None
    return ClaimCard(
        seal=_SEAL["verified"],
        chips=tuple(_chip(item) for item in result.claims),
        rows=rows,
        values=tuple(item.value for item in result.claims),
        sentence=_sentence(claim, rows),
        reason=result.reason,
    )


def _label(mapping: dict[str, str], token: str) -> str:
    try:
        return mapping[token]
    except KeyError as exc:
        raise ValueError(f"unknown chip token {token}") from exc


def _chip(claim: FinancialClaim) -> str:
    period = _label(_PERIOD_CHIP, claim.period)
    scope = _label(_SCOPE_CHIP, claim.scope)
    metric = _label(_METRIC_CHIP, claim.metric)
    return f"{claim.issuer} · {period} · {scope} · {metric}"


def _sentence(claim: FinancialClaim | None, rows: tuple[str, ...]) -> str:
    if claim is not None and len(rows) == 2:
        return _SENTENCE.get(claim.scope, "")
    return ""
