"""Host authorization gate: authorized OK; unauthorized → regen once → template."""

from __future__ import annotations

from claimledger.agent.template import ABSTENTION_TEMPLATE


def test_authorized_normalized_prose_passes() -> None:
    from claimledger.agent.gate import gate_prose

    prose = "El resultado neto consolidado fue 21.262.335."
    result = gate_prose(prose, authorized_values=["21262335"])

    assert result.allowed is True
    assert result.text == prose
    assert result.text != ABSTENTION_TEMPLATE


def test_unauthorized_after_one_regen_falls_to_template() -> None:
    from claimledger.agent.gate import gate_prose

    drafts = iter(
        [
            "Inventé 99999999 pesos.",
            "Sigo inventando 88888888.",
        ]
    )

    def regenerate() -> str:
        return next(drafts)

    result = gate_prose(
        "Inventé 99999999 pesos.",
        authorized_values=["21262335"],
        regenerate=regenerate,
    )

    assert result.allowed is False
    assert result.text == ABSTENTION_TEMPLATE
    assert "99999999" not in result.text
    assert "88888888" not in result.text


def test_regen_authorized_on_second_draft_passes() -> None:
    from claimledger.agent.gate import gate_prose

    drafts = iter(["Inventé 99999999.", "El valor es 21.262.335."])

    result = gate_prose(
        next(drafts),
        authorized_values=["21262335"],
        regenerate=lambda: next(drafts),
    )

    assert result.allowed is True
    assert "21.262.335" in result.text
    assert result.text != ABSTENTION_TEMPLATE


def test_empty_auth_blocks_word_form_to_template() -> None:
    from claimledger.agent.gate import gate_prose

    draft = "El resultado asciende a veintiún millones de pesos."
    result = gate_prose(draft, authorized_values=[])

    assert result.allowed is False
    assert result.text == ABSTENTION_TEMPLATE
    assert "veintiún" not in result.text
    assert "ME ABSTENGO" in ABSTENTION_TEMPLATE
    assert ABSTENTION_TEMPLATE == (
        "ME ABSTENGO: no hay cifras verificadas autorizadas para esta respuesta."
    )
