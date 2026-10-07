"""Normalize financial forms; exempt dates, pages, periods."""

from __future__ import annotations


def test_forms_normalize_to_canonical() -> None:
    from claimledger.agent.normalize import extract_financial_values, normalize_amount

    authorized = "21262335"
    forms = (
        "21.262.335",
        "21,262,335",
        "21 262 335",
        "$21.262.335",
    )
    for form in forms:
        assert normalize_amount(form) == authorized

    prose = "El resultado fue $21.262.335 (o 21,262,335)."
    found = extract_financial_values(prose)
    assert authorized in found


def test_metadata_exempt_from_financial_claims() -> None:
    from claimledger.agent.normalize import extract_financial_values

    prose = (
        "Al 31/03/2026, en la página 14 del informe 1Q26, "
        "sin cifra financiera autorizada aquí."
    )
    found = extract_financial_values(prose)
    assert "31032026" not in found
    assert "14" not in found
    assert "126" not in found
    assert found == []


def test_mixed_prose_keeps_financial_drops_metadata() -> None:
    from claimledger.agent.normalize import extract_financial_values

    prose = "Al 31/03/2026 (página 14, 1Q26) el neto fue 21.262.335."
    found = extract_financial_values(prose)
    assert found == ["21262335"]
