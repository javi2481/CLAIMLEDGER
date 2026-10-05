"""Fourteen extracted EEFF rows against frozen RECIPE_ROWS. Seed stays the kernel book."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from claimledger.claim import FinancialClaim
from claimledger.identity import identity_key
from claimledger.ingest.classify import classify
from claimledger.ingest.extract import extract_recipe
from claimledger.ingest.store import load_or_convert
from claimledger.ingest.types import StoredDocument
from claimledger.ledger import RECIPE_ROWS, Ledger
from claimledger.lookup import understand
from claimledger.query import query

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS = REPO_ROOT / "docs" / "archivos_muestra"

EEFF = {
    "BYMA_-_EEFF_31-03-2026_VF.pdf": "2026-03-31",
    "BYMA - EEFF 30-06-2026.pdf": "2026-06-30",
}
NON_EEFF = (
    "BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf",
    "BYMA-Comunicado_de_Prensa-2T26.pdf",
    "Presentación_de_resultados_BYMA-1T26.pdf",
    "Presentacion_de_resultados_BYMA-2T26.pdf",
    "BYMA_2T26_Transcripcion_Resultados_ES.pdf",
    "Memoria-BYMA-y-EEFF-al-31-12-2023.pdf",
    "BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf",
    "BYMA-MEMORIA_2025.pdf",
)
NEIGHBOR_CONSOLIDATED = "21262335"
NEIGHBOR_PARENT = "21259769"
TAX_BY_PERIOD = {
    "2026-03-31": "-14950948",
    "2026-06-30": "-32731536",
}
REFUSAL_QUESTIONS = (
    "¿Cuál es el resultado neto consolidado del comunicado de prensa?",
    "¿Cuál es el resultado neto consolidado de la presentación?",
    "resultado neto del período en la memoria anual",
)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _cell(text: str) -> dict:
    return {"text": text}


def _poisoned_grid() -> list[list[dict]]:
    rows = (
        ("", "Notas", "31.03.2026", "31.03.2025"),
        ("Resultado bruto", "", "60.144.176", "1.000"),
        ("Resultado operativo", "", "70.223.471", "2.000"),
        ("Resultado antes del impuesto a las ganancias", "", "36.213.283", "3.000"),
        ("Impuesto a las ganancias", "", "(14.950.948)", "4.000"),
        ("RESULTADO NETO DEL PERÍODO", "", "21.262.335", "5.000"),
        (
            "Resultado neto del período atribuible a la participación controlante",
            "",
            "21.259.769",
            "6.000",
        ),
        (
            "Resultado neto del período atribuible a la participación no controlante",
            "",
            "2.566",
            "7.000",
        ),
    )
    return [[_cell(text) for text in row] for row in rows]


def _stored_poison(tmp_path: Path, pdf: Path) -> StoredDocument:
    table = {
        "self_ref": "#/tables/1",
        "content_layer": "body",
        "parent": {"$ref": "#/body"},
        "prov": [{"page_no": 4, "bbox": {"l": 1, "b": 1, "r": 2, "t": 2}}],
        "data": {"grid": _poisoned_grid()},
    }
    payload = {
        "body": {"self_ref": "#/body", "children": [{"$ref": "#/tables/1"}]},
        "tables": [table],
        "pages": {"4": {"size": {"width": 100.0, "height": 100.0}}},
    }
    raw = json.dumps(payload).encode("utf-8")
    digest = _sha256_hex(raw)
    json_path = tmp_path / f"{digest}.json"
    json_path.write_bytes(raw)
    return StoredDocument(
        artifact_hash=digest,
        json_path=json_path,
        source_pdf=pdf.resolve(),
    )


def _row_key(period: str, scope: str, metric: str) -> str:
    return identity_key("BYMA", period, "income_statement", scope, metric)


def _index(
    claims: tuple[FinancialClaim, ...],
) -> dict[tuple[str, str, str], FinancialClaim]:
    found: dict[tuple[str, str, str], FinancialClaim] = {}
    for claim in claims:
        slot = (claim.period, claim.scope, claim.metric)
        assert slot not in found
        found[slot] = claim
    return found


@pytest.fixture(scope="module")
def extracted_rows() -> tuple[FinancialClaim, ...]:
    claims: list[FinancialClaim] = []
    for filename, period in EEFF.items():
        pdf = CORPUS / filename
        assert pdf.is_file()
        stored = load_or_convert(pdf)
        document = classify(pdf, stored)
        assert document.kind == "eeff"
        assert document.issuer == "BYMA"
        assert document.period == period
        batch = extract_recipe(stored, document)
        assert batch
        for claim in batch:
            assert claim.evidence[0].artifact_hash == stored.artifact_hash
        claims.extend(batch)
    return tuple(claims)


def test_fourteen_rows_match_frozen_recipe_rows(
    extracted_rows: tuple[FinancialClaim, ...],
) -> None:
    assert len(RECIPE_ROWS) == 14
    assert len(extracted_rows) == 14
    got = {
        (claim.period, claim.scope, claim.metric, claim.value)
        for claim in extracted_rows
    }
    assert got == set(RECIPE_ROWS)
    keys = [claim.identity_key for claim in extracted_rows]
    assert len(set(keys)) == 14
    for claim in extracted_rows:
        assert claim.identity_key == _row_key(claim.period, claim.scope, claim.metric)
        evidence = claim.evidence[0]
        assert evidence.page >= 1
        assert evidence.label.strip()
        assert evidence.text.strip()


def test_neighbor_trap_keeps_21262335_off_the_parent_row(
    extracted_rows: tuple[FinancialClaim, ...],
) -> None:
    found = _index(extracted_rows)
    consolidated = found[("2026-03-31", "consolidated", "net_income")]
    parent = found[("2026-03-31", "parent_attributable", "net_income")]
    assert consolidated.value == NEIGHBOR_CONSOLIDATED
    assert parent.value == NEIGHBOR_PARENT
    assert consolidated.value != parent.value
    assert consolidated.identity_key != parent.identity_key
    assert NEIGHBOR_PARENT not in consolidated.identity_key
    assert NEIGHBOR_CONSOLIDATED not in parent.identity_key
    assert "controlante" in parent.evidence[0].label.casefold()

    second_consolidated = found[("2026-06-30", "consolidated", "net_income")]
    second_parent = found[("2026-06-30", "parent_attributable", "net_income")]
    assert second_consolidated.value == "81956525"
    assert second_parent.value == "81946993"
    assert second_consolidated.value != second_parent.value


def test_income_tax_keeps_the_frozen_negative_sign(
    extracted_rows: tuple[FinancialClaim, ...],
) -> None:
    found = _index(extracted_rows)
    for period, value in TAX_BY_PERIOD.items():
        claim = found[(period, "consolidated", "income_tax")]
        assert claim.value == value
        assert claim.value.startswith("-")
        assert not claim.value.startswith("--")
        assert claim.identity_key == _row_key(period, "consolidated", "income_tax")


def test_fresh_ledger_matches_seed_values_and_seed_stays_unevidenced(
    extracted_rows: tuple[FinancialClaim, ...],
) -> None:
    seeded = Ledger.seed()
    fresh = Ledger()
    for claim in extracted_rows:
        stored = fresh.upsert(claim)
        assert stored.ledger_status == "recorded"

    questions = (
        (
            "resultado neto consolidado del 1T26",
            NEIGHBOR_CONSOLIDATED,
        ),
        (
            "resultado atribuible a la controlante 1T26",
            NEIGHBOR_PARENT,
        ),
        (
            "impuesto a las ganancias consolidado 1T26",
            TAX_BY_PERIOD["2026-03-31"],
        ),
        (
            "impuesto a las ganancias consolidado 2T26",
            TAX_BY_PERIOD["2026-06-30"],
        ),
    )
    for question, value in questions:
        intent = understand(question)
        assert intent.route == "identity"
        seed_result = query(intent, seeded)
        fresh_result = query(intent, fresh)
        assert seed_result.status == "verified"
        assert fresh_result.status == "verified"
        assert seed_result.claims[0].value == value
        assert fresh_result.claims[0].value == value
        assert seed_result.claims[0].evidence == ()
        assert len(fresh_result.claims[0].evidence) == 1
        assert seed_result.identity == fresh_result.identity

    for period, scope, metric, value in RECIPE_ROWS:
        key = _row_key(period, scope, metric)
        seed_claim = seeded.get(key)
        fresh_claim = fresh.get(key)
        assert seed_claim is not None and fresh_claim is not None
        assert seed_claim.value == value
        assert fresh_claim.value == value
        assert seed_claim.evidence == ()
        assert fresh_claim.evidence != ()

    again = Ledger.seed()
    assert again is not seeded
    assert again is not fresh
    for period, scope, metric, value in RECIPE_ROWS:
        key = _row_key(period, scope, metric)
        claim = again.get(key)
        assert claim is not None
        assert claim.value == value
        assert claim.evidence == ()
        untouched = seeded.get(key)
        assert untouched is not None
        assert untouched.value == value
        assert untouched.evidence == ()


@pytest.mark.parametrize("question", REFUSAL_QUESTIONS)
def test_comunicado_deck_and_memoria_pnl_stay_recipe_no_extract(
    question: str,
    extracted_rows: tuple[FinancialClaim, ...],
) -> None:
    fresh = Ledger()
    for claim in extracted_rows:
        fresh.upsert(claim)
    intent = understand(question)
    assert intent.route == "abstain"
    assert intent.abstain_reason == "recipe_no_extract"
    for book in (Ledger.seed(), fresh):
        result = query(intent, book)
        assert result.status == "abstained"
        assert result.reason == "recipe_no_extract"
        assert result.claims == ()


@pytest.mark.parametrize("filename", NON_EEFF)
def test_eight_sources_mint_no_recipe_identity(filename: str, tmp_path: Path) -> None:
    pdf = CORPUS / filename
    assert pdf.is_file()
    stored = _stored_poison(tmp_path, pdf)
    document = classify(pdf, stored)
    assert document.kind in {"comunicado", "deck", "memoria", "transcript"}

    claims = extract_recipe(stored, document)

    assert claims == ()
