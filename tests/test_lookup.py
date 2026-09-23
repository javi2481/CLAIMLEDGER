"""Fase 0 kernel lookup tests. Slice 5 fold-and-order Intent."""

from __future__ import annotations

import dataclasses

import pytest

from claimledger.lookup import Intent, understand

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

YPF_PRICE = "Precio de YPF el 3 enero"
YPF_CLOSE_BYMA = "¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?"
ORDINARY_EEFF = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
COMUNICADO_NETO = "¿Cuál es el resultado neto consolidado del comunicado de prensa?"
MEMORIA_NETO = "resultado neto del período en la memoria anual"
CONTRACT_CLAUSE = "cláusula 5 del contrato"
NARRATIVE_GROWTH = "explica el crecimiento de ingresos"
NARRATIVE_POLICY = "política contable de reconocimiento de ingresos"
NETO_WITH_EXPLICA = "explica el resultado neto consolidado del 1T26"
COMPARE_VS = "Comparar resultado neto consolidado 1T26 vs 2T26"
BOTH_QUARTERS = "resultado neto consolidado 1T26 y 2T26"
SINGLE_1T = "resultado neto consolidado del 1T26"
SINGLE_2T = "resultado neto consolidado del 2T26"
ACCENTED_1T = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del primer trimestre?"
DEFAULT_EEFF = "¿Cuál es el resultado del EEFF del 1T26?"
PARENT_1T = "resultado atribuible a la controlante 1T26"
NOT_ATTRIBUTABLE = "resultado neto consolidado no el atribuible 1T26"
NCI_1T = "resultado no controlante del 1T26"
GROSS_1T = "resultado bruto consolidado 1T26"
OPERATING_1T = "resultado operativo consolidado 1T26"
EBT_1T = "resultado antes de impuesto consolidado 1T26"
TAX_1T = "impuesto a las ganancias consolidado 1T26"
UNRESOLVED = "hola"


def _assert_no_pnl_identity(intent: Intent) -> None:
    assert intent.statement is None
    assert intent.scope is None
    assert intent.metric is None
    assert intent.period is None
    assert intent.compare is False


def _assert_closed_return(intent: Intent) -> None:
    assert isinstance(intent, Intent)
    assert intent.route != "rejected"
    assert intent.abstain_reason != "rejected"
    assert not hasattr(intent, "status") or getattr(intent, "status") != "rejected"
    if intent.abstain_reason is not None:
        assert intent.abstain_reason in CLOSED_ABSTAIN_REASONS


def test_intent_is_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(Intent)
    assert Intent.__dataclass_params__.frozen is True


def test_accents_fold_before_matching() -> None:
    intent = understand(ACCENTED_1T)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.statement == "income_statement"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"
    assert intent.compare is False
    assert intent.abstain_reason is None


def test_ypf_rule_wins_over_default_neto() -> None:
    intent = understand(YPF_PRICE)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "off_corpus"
    _assert_no_pnl_identity(intent)


def test_ypf_close_is_off_corpus_even_when_text_mentions_byma() -> None:
    intent = understand(YPF_CLOSE_BYMA)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "off_corpus"
    _assert_no_pnl_identity(intent)


def test_ordinary_eeff_question_stays_byma() -> None:
    intent = understand(ORDINARY_EEFF)
    assert intent.issuer == "BYMA"
    assert intent.route == "identity"
    assert intent.statement == "income_statement"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"
    assert intent.compare is False
    assert intent.abstain_reason is None


def test_comunicado_plus_neto_abstains() -> None:
    intent = understand(COMUNICADO_NETO)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "recipe_no_extract"
    _assert_no_pnl_identity(intent)


@pytest.mark.parametrize("source", ("presentación", "slides", "deck"))
def test_deck_plus_pnl_abstains(source: str) -> None:
    intent = understand(f"¿Cuál es el resultado neto consolidado de la {source}?")
    assert intent.route == "abstain"
    assert intent.abstain_reason == "recipe_no_extract"
    _assert_no_pnl_identity(intent)


@pytest.mark.parametrize("question", (MEMORIA_NETO, CONTRACT_CLAUSE))
def test_memoria_and_contract_abstain(question: str) -> None:
    intent = understand(question)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "recipe_no_extract"
    _assert_no_pnl_identity(intent)


@pytest.mark.parametrize("question", (NARRATIVE_GROWTH, NARRATIVE_POLICY))
def test_growth_narrative_is_narrative(question: str) -> None:
    intent = understand(question)
    assert intent.route == "narrative"
    assert intent.abstain_reason is None
    _assert_no_pnl_identity(intent)


def test_neto_ask_is_not_narrative() -> None:
    intent = understand(NETO_WITH_EXPLICA)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"
    assert intent.compare is False


def test_versus_marks_compare() -> None:
    intent = understand(COMPARE_VS)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.statement == "income_statement"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.compare is True
    assert intent.period is None
    assert intent.abstain_reason is None


def test_both_quarter_tokens_mark_compare() -> None:
    intent = understand(BOTH_QUARTERS)
    assert intent.route == "identity"
    assert intent.compare is True
    assert intent.period is None
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"


def test_single_quarter_binds_period() -> None:
    intent = understand(SINGLE_1T)
    assert intent.route == "identity"
    assert intent.period == "2026-03-31"
    assert intent.compare is False
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"


def test_second_quarter_binds_period() -> None:
    intent = understand(SINGLE_2T)
    assert intent.route == "identity"
    assert intent.period == "2026-06-30"
    assert intent.compare is False


def test_default_metric_is_consolidated_net_income() -> None:
    intent = understand(DEFAULT_EEFF)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.statement == "income_statement"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"


def test_parenthetical_controlante_wins() -> None:
    intent = understand(PARENT_1T)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.statement == "income_statement"
    assert intent.scope == "parent_attributable"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"
    assert intent.compare is False


def test_no_el_atribuible_keeps_consolidated_net_income() -> None:
    intent = understand(NOT_ATTRIBUTABLE)
    assert intent.route == "identity"
    assert intent.scope == "consolidated"
    assert intent.metric == "net_income"
    assert intent.period == "2026-03-31"


@pytest.mark.parametrize(
    ("question", "scope", "metric"),
    (
        (NCI_1T, "consolidated", "nci_income"),
        (PARENT_1T, "parent_attributable", "net_income"),
        (GROSS_1T, "consolidated", "gross_profit"),
        (OPERATING_1T, "consolidated", "operating_income"),
        (EBT_1T, "consolidated", "income_before_tax"),
        (TAX_1T, "consolidated", "income_tax"),
        (SINGLE_1T, "consolidated", "net_income"),
    ),
)
def test_metric_order(question: str, scope: str, metric: str) -> None:
    intent = understand(question)
    assert intent.route == "identity"
    assert intent.issuer == "BYMA"
    assert intent.statement == "income_statement"
    assert intent.scope == scope
    assert intent.metric == metric
    assert intent.period == "2026-03-31"
    assert intent.compare is False
    assert intent.abstain_reason is None


def test_unresolved_identity_when_no_phrase_matches() -> None:
    intent = understand(UNRESOLVED)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "unresolved_identity"
    _assert_no_pnl_identity(intent)


@pytest.mark.parametrize(
    "question",
    (
        YPF_PRICE,
        YPF_CLOSE_BYMA,
        ORDINARY_EEFF,
        COMUNICADO_NETO,
        MEMORIA_NETO,
        CONTRACT_CLAUSE,
        NARRATIVE_GROWTH,
        COMPARE_VS,
        SINGLE_1T,
        PARENT_1T,
        NOT_ATTRIBUTABLE,
        NCI_1T,
        UNRESOLVED,
    ),
)
def test_rejected_is_not_a_lookup_return(question: str) -> None:
    intent = understand(question)
    _assert_closed_return(intent)
    assert dataclasses.is_dataclass(intent)
