"""Fase 0 kernel query tests. Slice 6 neighbor, compare, abstain, no mutate."""

from __future__ import annotations

import dataclasses

from claimledger.claim import FinancialClaim
from claimledger.identity import identity_key
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import QueryResult, query

CLOSED_ABSTAIN_REASONS = frozenset(
    {
        "off_corpus",
        "recipe_no_extract",
        "no_matching_claim",
        "incomplete_comparison",
        "ambiguous_period",
        "unresolved_identity",
    }
)
QUERY_STATUSES = frozenset({"verified", "abstained"})

CANONICAL_CONSOLIDATED = "BYMA|2026-03-31|income_statement|consolidated|net_income"
CANONICAL_PARENT = "BYMA|2026-03-31|income_statement|parent_attributable|net_income"
COMPARE_WILDCARD = "BYMA|*|income_statement|consolidated|net_income"
CONSOLIDATED_2T = "BYMA|2026-06-30|income_statement|consolidated|net_income"

CURRENT_NET_INCOME = "21262335"
NEIGHBOR_PARENT = "21259769"
SECOND_QUARTER_NET = "81956525"
COMPARE_DELTA = "60694190"

ORDINARY_EEFF = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
PARENT_1T = "resultado atribuible a la controlante 1T26"
COMPARE_VS = "Comparar resultado neto consolidado 1T26 vs 2T26"
YPF_CLOSE_BYMA = "¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?"
COMUNICADO_NETO = "¿Cuál es el resultado neto consolidado del comunicado de prensa?"
AMBIGUOUS_PERIOD = "¿Cuál es el resultado neto consolidado?"
UNRESOLVED = "hola"

RECIPE_KEYS: tuple[str, ...] = tuple(
    identity_key("BYMA", period, "income_statement", scope, metric)
    for period, scope, metric in (
        ("2026-03-31", "consolidated", "net_income"),
        ("2026-03-31", "parent_attributable", "net_income"),
        ("2026-03-31", "consolidated", "gross_profit"),
        ("2026-03-31", "consolidated", "operating_income"),
        ("2026-03-31", "consolidated", "income_before_tax"),
        ("2026-03-31", "consolidated", "income_tax"),
        ("2026-03-31", "consolidated", "nci_income"),
        ("2026-06-30", "consolidated", "net_income"),
        ("2026-06-30", "parent_attributable", "net_income"),
        ("2026-06-30", "consolidated", "gross_profit"),
        ("2026-06-30", "consolidated", "operating_income"),
        ("2026-06-30", "consolidated", "income_before_tax"),
        ("2026-06-30", "consolidated", "income_tax"),
        ("2026-06-30", "consolidated", "nci_income"),
    )
)


def _claim(
    *,
    period: str = "2026-03-31",
    scope: str = "consolidated",
    metric: str = "net_income",
    value: str = CURRENT_NET_INCOME,
) -> FinancialClaim:
    key = identity_key("BYMA", period, "income_statement", scope, metric)
    return FinancialClaim(
        identity_key=key,
        issuer="BYMA",
        period=period,
        statement="income_statement",
        scope=scope,
        metric=metric,
        value=value,
        currency="ARS",
        unit=None,
        evidence=(),
        ledger_status="recorded",
    )


def _snapshot(ledger: Ledger) -> dict[str, FinancialClaim]:
    return {key: ledger.get(key) for key in RECIPE_KEYS if ledger.get(key) is not None}


def _assert_query_shape(result: QueryResult) -> None:
    assert isinstance(result, QueryResult)
    assert result.status in QUERY_STATUSES
    assert result.status != "rejected"
    assert result.status != "conflicted"
    if result.reason is not None:
        assert result.reason in CLOSED_ABSTAIN_REASONS
        assert result.reason != "rejected"


def _assert_abstained(result: QueryResult, reason: str) -> None:
    _assert_query_shape(result)
    assert result.status == "abstained"
    assert result.reason == reason
    assert result.claims == ()
    assert not hasattr(result, "value") or getattr(result, "value") is None
    assert not hasattr(result, "delta")


def test_query_result_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(QueryResult)
    assert QueryResult.__dataclass_params__.frozen is True
    field_names = {field.name for field in dataclasses.fields(QueryResult)}
    assert "delta" not in field_names
    assert "difference" not in field_names


def test_canonical_consolidated_net_income_is_verified() -> None:
    ledger = Ledger.seed()
    result = query(understand(ORDINARY_EEFF), ledger)
    _assert_query_shape(result)
    assert result.status == "verified"
    assert result.reason is None
    assert len(result.claims) == 1
    claim = result.claims[0]
    assert claim.value == CURRENT_NET_INCOME
    assert claim.identity_key == CANONICAL_CONSOLIDATED
    assert claim.issuer == "BYMA"
    assert claim.period == "2026-03-31"
    assert claim.statement == "income_statement"
    assert claim.scope == "consolidated"
    assert claim.metric == "net_income"


def test_consolidated_neighbor_trap_does_not_choose_parent() -> None:
    ledger = Ledger.seed()
    neighbor = ledger.get(CANONICAL_PARENT)
    assert neighbor is not None
    assert neighbor.value == NEIGHBOR_PARENT
    result = query(understand(ORDINARY_EEFF), ledger)
    _assert_query_shape(result)
    assert result.status == "verified"
    assert len(result.claims) == 1
    assert result.claims[0].value == CURRENT_NET_INCOME
    assert result.claims[0].value != NEIGHBOR_PARENT
    assert result.claims[0].identity_key == CANONICAL_CONSOLIDATED
    assert result.claims[0].identity_key != CANONICAL_PARENT


def test_parent_question_chooses_the_neighbor() -> None:
    ledger = Ledger.seed()
    result = query(understand(PARENT_1T), ledger)
    _assert_query_shape(result)
    assert result.status == "verified"
    assert len(result.claims) == 1
    assert result.claims[0].value == NEIGHBOR_PARENT
    assert result.claims[0].value != CURRENT_NET_INCOME
    assert result.claims[0].identity_key == CANONICAL_PARENT
    assert result.claims[0].identity_key != CANONICAL_CONSOLIDATED


def test_compare_returns_two_claims_without_delta() -> None:
    ledger = Ledger.seed()
    result = query(understand(COMPARE_VS), ledger)
    _assert_query_shape(result)
    assert result.status == "verified"
    assert result.reason is None
    assert len(result.claims) == 2
    values = {claim.value for claim in result.claims}
    assert values == {CURRENT_NET_INCOME, SECOND_QUARTER_NET}
    assert COMPARE_DELTA not in values
    assert f"-{COMPARE_DELTA}" not in values
    assert not hasattr(result, "delta")
    assert not hasattr(result, "difference")
    first, second = result.claims
    assert {first.period, second.period} == {"2026-03-31", "2026-06-30"}
    assert first.scope == second.scope == "consolidated"
    assert first.metric == second.metric == "net_income"
    assert first.identity_key != second.identity_key


def test_compare_identity_keeps_wildcard_period() -> None:
    ledger = Ledger.seed()
    result = query(understand(COMPARE_VS), ledger)
    _assert_query_shape(result)
    assert result.status == "verified"
    assert result.identity == COMPARE_WILDCARD
    assert "*" in result.identity
    periods = {claim.period for claim in result.claims}
    keys = {claim.identity_key for claim in result.claims}
    assert periods == {"2026-03-31", "2026-06-30"}
    assert "*" not in "".join(keys)
    assert CANONICAL_CONSOLIDATED in keys
    assert CONSOLIDATED_2T in keys
    for claim in result.claims:
        assert claim.period in {"2026-03-31", "2026-06-30"}
        assert claim.identity_key == identity_key(
            "BYMA", claim.period, "income_statement", "consolidated", "net_income"
        )


def test_one_sided_compare_abstains_incomplete() -> None:
    ledger = Ledger()
    ledger.upsert(_claim())
    assert ledger.get(CANONICAL_CONSOLIDATED) is not None
    assert ledger.get(CONSOLIDATED_2T) is None
    result = query(understand(COMPARE_VS), ledger)
    _assert_abstained(result, "incomplete_comparison")


def test_missing_claim_abstains() -> None:
    ledger = Ledger()
    assert ledger.get(CANONICAL_CONSOLIDATED) is None
    result = query(understand(ORDINARY_EEFF), ledger)
    _assert_abstained(result, "no_matching_claim")


def test_ypf_price_abstains_off_corpus() -> None:
    ledger = Ledger.seed()
    result = query(understand(YPF_CLOSE_BYMA), ledger)
    _assert_abstained(result, "off_corpus")


def test_comunicado_pnl_abstains_recipe_no_extract() -> None:
    ledger = Ledger.seed()
    result = query(understand(COMUNICADO_NETO), ledger)
    _assert_abstained(result, "recipe_no_extract")


def test_ambiguous_period_abstains() -> None:
    ledger = Ledger.seed()
    first = ledger.get(CANONICAL_CONSOLIDATED)
    second = ledger.get(CONSOLIDATED_2T)
    assert first is not None
    assert second is not None
    intent = understand(AMBIGUOUS_PERIOD)
    assert intent.compare is False
    assert intent.period is None
    result = query(intent, ledger)
    _assert_abstained(result, "ambiguous_period")


def test_unresolved_identity_abstains() -> None:
    ledger = Ledger.seed()
    result = query(understand(UNRESOLVED), ledger)
    _assert_abstained(result, "unresolved_identity")


def test_verified_answer_leaves_recorded_intact() -> None:
    ledger = Ledger.seed()
    before = _snapshot(ledger)
    stored = before[CANONICAL_CONSOLIDATED]
    assert stored.ledger_status == "recorded"
    result = query(understand(ORDINARY_EEFF), ledger)
    assert result.status == "verified"
    after = ledger.get(CANONICAL_CONSOLIDATED)
    assert after is not None
    assert after.ledger_status == "recorded"
    assert after.ledger_status != "verified"
    assert after.value == stored.value
    assert after.evidence == stored.evidence
    assert after == stored
    assert not hasattr(after, "verification_status")
    for key, claim in before.items():
        assert ledger.get(key) == claim


def test_abstention_leaves_the_book_unchanged() -> None:
    ledger = Ledger.seed()
    before = _snapshot(ledger)
    result = query(understand(YPF_CLOSE_BYMA), ledger)
    assert result.status == "abstained"
    after = _snapshot(ledger)
    assert after == before
    for key, claim in before.items():
        fetched = ledger.get(key)
        assert fetched == claim
        assert fetched is not None
        assert fetched.ledger_status == claim.ledger_status


def test_query_never_returns_rejected() -> None:
    ledger = Ledger.seed()
    unused_neighbor = ledger.get(CANONICAL_PARENT)
    assert unused_neighbor is not None
    assert unused_neighbor.value == NEIGHBOR_PARENT
    result = query(understand(ORDINARY_EEFF), ledger)
    _assert_query_shape(result)
    assert result.status in QUERY_STATUSES
    assert result.status != "rejected"
    assert result.reason != "rejected"
    assert result.claims[0].value != NEIGHBOR_PARENT


def test_conflicted_claim_is_not_verified_from_ingest_status() -> None:
    ledger = Ledger()
    ledger.upsert(_claim())
    ledger.upsert(_claim(value="22362983"))
    stored = ledger.get(CANONICAL_CONSOLIDATED)
    assert stored is not None
    assert stored.ledger_status == "conflicted"
    result = query(understand(ORDINARY_EEFF), ledger)
    _assert_abstained(result, "no_matching_claim")
    assert result.status != "verified"
    assert stored.ledger_status == "conflicted"
