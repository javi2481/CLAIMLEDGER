"""Agent evals: YPF verified, recipe_no_extract abstention, metadata exempt."""

from __future__ import annotations

import pytest

from claimledger.agent.gate import gate_prose
from claimledger.agent.normalize import extract_financial_values
from claimledger.agent.template import ABSTENTION_TEMPLATE
from claimledger.ledger import Ledger

YPF_QUESTION = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
YPF_VALUE = "21262335"
RECIPE_QUESTION = "resultado neto del período en la memoria anual"


def test_ypf_verified_no_invented_figure(monkeypatch: pytest.MonkeyPatch) -> None:
    import claimledger.agent.tools as tools

    monkeypatch.setattr(tools, "recorded_book", Ledger.seed)

    verified = tools.verify(YPF_QUESTION)
    assert verified["status"] == "verified"
    assert YPF_VALUE in verified["authorized_values"]

    good = gate_prose(
        f"Para YPF/BYMA el neto consolidado es {YPF_VALUE}.",
        verified["authorized_values"],
    )
    assert good.allowed is True
    assert YPF_VALUE in good.text

    invented = gate_prose(
        "Inventé 55555555 para YPF.",
        verified["authorized_values"],
        regenerate=lambda: "Sigo con 44444444 inventado.",
    )
    assert invented.allowed is False
    assert invented.text == ABSTENTION_TEMPLATE
    assert "55555555" not in invented.text
    assert "44444444" not in invented.text


def test_recipe_no_extract_abstained_template_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.agent.tools as tools
    from claimledger.agent.loop import run

    monkeypatch.setattr(tools, "recorded_book", Ledger.seed)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    verified = tools.verify(RECIPE_QUESTION)
    assert verified["status"] == "abstained"
    assert verified["authorized_values"] == []
    assert verified["claims"] == []

    word_form = "El resultado son veintiún millones de pesos."
    gated = gate_prose(word_form, verified["authorized_values"])
    assert gated.allowed is False
    assert gated.text == ABSTENTION_TEMPLATE
    assert "veintiún" not in gated.text
    assert "millones" not in gated.text

    outcome = run(RECIPE_QUESTION)
    assert outcome.abstained is True
    assert outcome.content == ABSTENTION_TEMPLATE


def test_metadata_in_prose_exempt() -> None:
    prose = (
        "Informe al 31/03/2026, página 14, período 1Q26, "
        "sin cifra financiera adicional."
    )
    assert extract_financial_values(prose) == []

    gated = gate_prose(
        prose + " El neto es 21.262.335.",
        authorized_values=["21262335"],
    )
    assert gated.allowed is True
    assert "31/03/2026" in gated.text
    assert "página 14" in gated.text
    assert "1Q26" in gated.text
