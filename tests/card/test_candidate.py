"""Candidate lives on the card. Evidence rows do not invent neighbors."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from claimledger.claim import FinancialClaim
from claimledger.evidence import FinancialEvidence
from claimledger.identity import identity_key

REPO = Path(__file__).resolve().parents[2]
LABEL = "RESULTADO NETO DEL PERÍODO"
SHARED = "abc123"


def _evidence(text: str, label: str, digest: str = SHARED) -> FinancialEvidence:
    return FinancialEvidence(
        document_id="#/tables/1",
        artifact_hash=digest,
        page=1,
        text=text,
        label=label,
    )


def _claim(evidence: tuple[FinancialEvidence, ...], value: str = "21262335") -> FinancialClaim:
    key = identity_key("BYMA", "2026-03-31", "income_statement", "consolidated", "net_income")
    return FinancialClaim(
        identity_key=key,
        issuer="BYMA",
        period="2026-03-31",
        statement="income_statement",
        scope="consolidated",
        metric="net_income",
        value=value,
        currency="ARS",
        unit=None,
        evidence=evidence,
        ledger_status="recorded",
    )


def test_card_owns_candidate() -> None:
    from claimledger.card.candidate import Candidate
    from claimledger.retrieval.drawers import Candidate as DrawerCandidate

    row = Candidate(drawer="tables", text="21.262.335", ref=SHARED)
    assert DrawerCandidate is Candidate
    assert row.drawer == "tables"
    assert row.text == "21.262.335"
    assert row.ref == SHARED
    with pytest.raises(Exception):
        row.text = "other"  # type: ignore[misc]
    narrative = Candidate(drawer="narrative", text="nota", ref="n1")
    assert narrative.drawer == "narrative"
    assert narrative.text == "nota"


def test_candidates_from_claims_empty_and_blank_label() -> None:
    from claimledger.card.candidate import candidates_from_claims

    assert candidates_from_claims(()) == ()
    blank = candidates_from_claims((_claim((_evidence("", LABEL),)),))
    assert len(blank) == 1
    assert blank[0].drawer == "tables"
    assert blank[0].text == LABEL
    assert blank[0].ref == SHARED


def test_shared_hash_adds_no_neighbor() -> None:
    from claimledger.card.candidate import candidates_from_claims

    claims = (
        _claim(
            (
                _evidence("21.262.335", LABEL),
                _evidence("21.259.769", "controlante"),
            )
        ),
    )
    rows = candidates_from_claims(claims)
    assert [item.drawer for item in rows] == ["tables", "tables"]
    assert [item.text for item in rows] == ["21.262.335", "21.259.769"]
    assert [item.ref for item in rows] == [SHARED, SHARED]
    assert len(rows) == 2


def test_candidate_module_does_not_import_docling() -> None:
    tree = ast.parse((REPO / "src" / "claimledger" / "card" / "candidate.py").read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    assert modules
    assert all(name != "docling" and not name.startswith("docling.") for name in modules)
    assert all("retrieval" not in name for name in modules)
