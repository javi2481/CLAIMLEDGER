"""Lexical fold-and-order question → Intent. No press/deck identity routes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from claimledger.identity import PERIOD_1T26, PERIOD_2T26, fold

Route = Literal["identity", "narrative", "abstain"]

ISSUER_BYMA = "BYMA"
STATEMENT_INCOME = "income_statement"

SCOPE_CONSOLIDATED = "consolidated"
SCOPE_PARENT = "parent_attributable"

METRIC_NET_INCOME = "net_income"
METRIC_NCI = "nci_income"
METRIC_GROSS = "gross_profit"
METRIC_OPERATING = "operating_income"
METRIC_EBT = "income_before_tax"
METRIC_TAX = "income_tax"

NET_INCOME_PHRASES = (
    "resultado neto",
    "ganancia neta",
    "utilidad neta",
    "neto del",
)

_TOKENS_1T26 = (
    "1t26",
    "1t 26",
    "marzo",
    "2026-03-31",
    "31 de marzo",
    "primer trimestre",
)
_TOKENS_2T26 = (
    "2t26",
    "2t 26",
    "junio",
    "2026-06-30",
    "30 de junio",
    "segundo trimestre",
)

_PNL_SOURCE_TOKENS = ("neto", "consolidado", "controlante", "bruto", "impuesto")
_NARRATIVE_HITS = (
    "crecimiento de ingresos",
    "explica",
    "politica contable",
    "highlights",
    "hechos relevantes",
    "webcast",
    "conference call",
)
_COMPARE_HITS = (
    "compar",
    " vs ",
    "versus",
    "mayor",
    "diferencia",
    "ambos periodos",
)
_NEGATED_PARENT = (
    "no el atribuible",
    "no atribuible",
    "no la controlante",
    "no el controlante",
)
_IDENTITY_ASK = (
    "del periodo",
    "trimestre",
    "consolidado",
    "eeff",
    "1t26",
    "2t26",
    "sintesis",
)


@dataclass(frozen=True)
class Intent:
    route: Route
    issuer: str
    statement: str | None
    scope: str | None
    metric: str | None
    period: str | None
    compare: bool
    abstain_reason: str | None = None


def _asks_net_income(question: str) -> bool:
    return any(phrase in question for phrase in NET_INCOME_PHRASES)


def _abstain(reason: str) -> Intent:
    return Intent(
        route="abstain",
        issuer=ISSUER_BYMA,
        statement=None,
        scope=None,
        metric=None,
        period=None,
        compare=False,
        abstain_reason=reason,
    )


def _narrative() -> Intent:
    return Intent(
        route="narrative",
        issuer=ISSUER_BYMA,
        statement=None,
        scope=None,
        metric=None,
        period=None,
        compare=False,
        abstain_reason=None,
    )


def _identity(
    scope: str, metric: str, period: str | None, compare: bool
) -> Intent:
    return Intent(
        route="identity",
        issuer=ISSUER_BYMA,
        statement=STATEMENT_INCOME,
        scope=scope,
        metric=metric,
        period=period,
        compare=compare,
        abstain_reason=None,
    )


def _has_pnl_source_metric(question: str) -> bool:
    return _asks_net_income(question) or any(
        token in question for token in _PNL_SOURCE_TOKENS
    )


def _compare_and_period(folded: str) -> tuple[bool, str | None]:
    compare = any(token in folded for token in _COMPARE_HITS)
    has_1t = any(token in folded for token in _TOKENS_1T26)
    has_2t = any(token in folded for token in _TOKENS_2T26)
    if has_1t and has_2t:
        return True, None
    if has_1t:
        return compare, PERIOD_1T26
    if has_2t:
        return compare, PERIOD_2T26
    return compare, None


def understand(question: str) -> Intent:
    folded = fold(question)
    if "ypf" in folded and any(
        token in folded for token in ("precio", "cierre", "3 de enero", "3 enero")
    ):
        return _abstain("off_corpus")
    if "memoria" in folded and any(
        token in folded for token in ("resultado", "neto", "eeff")
    ):
        return _abstain("recipe_no_extract")
    if "comunicado" in folded and _has_pnl_source_metric(folded):
        return _abstain("recipe_no_extract")
    deck = any(token in folded for token in ("presentacion", "slides", "deck"))
    if deck and _has_pnl_source_metric(folded):
        return _abstain("recipe_no_extract")
    if any(token in folded for token in ("contrato", "clausula")):
        return _abstain("recipe_no_extract")
    if any(token in folded for token in _NARRATIVE_HITS) and not _asks_net_income(
        folded
    ):
        return _narrative()

    compare, period = _compare_and_period(folded)
    if "no controlante" in folded:
        return _identity(SCOPE_CONSOLIDATED, METRIC_NCI, period, compare)
    negated_parent = any(phrase in folded for phrase in _NEGATED_PARENT)
    if (
        "controlante" in folded or "atribuible" in folded or "propietarios" in folded
    ) and not negated_parent:
        return _identity(SCOPE_PARENT, METRIC_NET_INCOME, period, compare)
    if "resultado bruto" in folded or "bruto del" in folded:
        return _identity(SCOPE_CONSOLIDATED, METRIC_GROSS, period, compare)
    if "resultado operativo" in folded:
        return _identity(SCOPE_CONSOLIDATED, METRIC_OPERATING, period, compare)
    if "antes del impuesto" in folded or "antes de impuesto" in folded:
        return _identity(SCOPE_CONSOLIDATED, METRIC_EBT, period, compare)
    if "impuesto a las ganancias" in folded or "impuesto a las" in folded:
        return _identity(SCOPE_CONSOLIDATED, METRIC_TAX, period, compare)

    identity_ask = _asks_net_income(folded) or any(
        token in folded for token in _IDENTITY_ASK
    )
    if identity_ask or compare:
        return _identity(SCOPE_CONSOLIDATED, METRIC_NET_INCOME, period, compare)
    return _abstain("unresolved_identity")
