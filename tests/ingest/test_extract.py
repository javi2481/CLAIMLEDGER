"""Extract recipe P&L claims from the two quarterly EEFF. Grid and provenance only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from claimledger.claim import FinancialClaim
from claimledger.digits import signed_ars
from claimledger.identity import PERIOD_1T26, PERIOD_2T26, identity_key
from claimledger.ingest.classify import DocumentClass, classify
from claimledger.ingest.extract import extract_recipe
from claimledger.ingest.store import load_or_convert
from claimledger.ingest.types import StoredDocument
from claimledger.ledger import RECIPE_ROWS

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS = REPO_ROOT / "docs" / "archivos_muestra"
INGEST_ROOT = REPO_ROOT / "src" / "claimledger" / "ingest"
GOLD_NET_INCOME_FIGURE = "21262335"
FURNITURE_FIGURE = "9999999"

EEFF = {
    "BYMA_-_EEFF_31-03-2026_VF.pdf": PERIOD_1T26,
    "BYMA - EEFF 30-06-2026.pdf": PERIOD_2T26,
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

_PAGE_WIDTH = 600.0
_PAGE_HEIGHT = 800.0


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _cell(text: str, *, bbox: dict | None = None) -> dict:
    return {
        "text": text,
        "bbox": bbox
        or {
            "l": 72.0,
            "b": 400.0,
            "r": 240.0,
            "t": 420.0,
            "coord_origin": "BOTTOMLEFT",
        },
    }


def _table(
    self_ref: str,
    grid: list[list[dict]],
    *,
    layer: str,
    parent: str,
    page_no: int = 4,
) -> dict:
    return {
        "self_ref": self_ref,
        "content_layer": layer,
        "parent": {"$ref": parent},
        "prov": [
            {
                "page_no": page_no,
                "charspan": [0, 0],
                "bbox": {
                    "l": 50.0,
                    "b": 80.0,
                    "r": 550.0,
                    "t": 720.0,
                    "coord_origin": "BOTTOMLEFT",
                },
            }
        ],
        "data": {"grid": grid},
    }


def _recipe_grid(period_header: str) -> list[list[dict]]:
    rows = (
        ("", "Notas", period_header, "31.03.2025"),
        ("Ingresos por servicios", "", "1.000.000", "900.000"),
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
        ("Total del patrimonio", "", "9.999.999", "8.000"),
    )
    return [[_cell(text) for text in row] for row in rows]


def _document(
    *,
    body_tables: list[dict],
    furniture_tables: list[dict],
) -> dict:
    tables = furniture_tables + body_tables
    return {
        "schema_name": "DoclingDocument",
        "name": "sample",
        "pages": {
            "4": {
                "page_no": 4,
                "size": {"width": _PAGE_WIDTH, "height": _PAGE_HEIGHT},
            }
        },
        "furniture": {
            "self_ref": "#/furniture",
            "content_layer": "furniture",
            "children": [{"$ref": table["self_ref"]} for table in furniture_tables],
        },
        "body": {
            "self_ref": "#/body",
            "content_layer": "body",
            "children": [{"$ref": table["self_ref"]} for table in body_tables],
        },
        "tables": tables,
    }


def _stored(tmp_path: Path, pdf: Path, payload: dict) -> StoredDocument:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    digest = _sha256_hex(raw)
    json_path = tmp_path / f"{digest}.json"
    json_path.write_bytes(raw)
    return StoredDocument(
        artifact_hash=digest,
        json_path=json_path,
        source_pdf=pdf.resolve(),
    )


def _bbox_in_unit_square(bbox: tuple[float, float, float, float] | None) -> None:
    assert bbox is not None
    x0, y0, x1, y1 = bbox
    assert 0.0 <= x0 <= x1 <= 1.0
    assert 0.0 <= y0 <= y1 <= 1.0


def _assert_recipe_claims(
    claims: tuple[FinancialClaim, ...],
    stored: StoredDocument,
    period: str,
) -> None:
    expected = {
        (scope, metric, value)
        for row_period, scope, metric, value in RECIPE_ROWS
        if row_period == period
    }
    assert len(expected) == 7
    got = {(claim.scope, claim.metric, claim.value) for claim in claims}
    assert got == expected
    assert len(claims) == len(expected)

    scopes = {claim.scope for claim in claims}
    assert scopes == {"consolidated", "parent_attributable"}

    for claim in claims:
        assert claim.issuer == "BYMA"
        assert claim.period == period
        assert claim.statement == "income_statement"
        assert claim.currency == "ARS"
        assert claim.unit is None
        assert claim.ledger_status == "recorded"
        assert claim.identity_key == identity_key(
            "BYMA", period, "income_statement", claim.scope, claim.metric
        )
        assert len(claim.evidence) == 1
        evidence = claim.evidence[0]
        assert evidence.artifact_hash == stored.artifact_hash
        assert evidence.document_id.startswith("#/tables/")
        assert evidence.page == 4
        assert evidence.label.strip()
        assert evidence.text.strip()
        assert signed_ars(evidence.text) == claim.value
        _bbox_in_unit_square(evidence.bbox)
        if claim.scope == "consolidated" and claim.metric == "net_income":
            assert "RESULTADO NETO DEL PERÍODO" in evidence.label
        if claim.scope == "parent_attributable":
            assert "controlante" in evidence.label.casefold()
            assert "no controlante" not in evidence.label.casefold()


@pytest.mark.parametrize("filename", sorted(EEFF))
def test_quarterly_eeff_emit_recipe_claims(filename: str) -> None:
    pdf = CORPUS / filename
    assert pdf.is_file()
    stored = load_or_convert(pdf)
    document = classify(pdf, stored)

    claims = extract_recipe(stored, document)

    assert document == DocumentClass(
        kind="eeff", issuer="BYMA", period=EEFF[filename]
    )
    _assert_recipe_claims(claims, stored, EEFF[filename])


def test_the_two_eeff_keep_distinct_net_income() -> None:
    first_pdf = CORPUS / "BYMA_-_EEFF_31-03-2026_VF.pdf"
    second_pdf = CORPUS / "BYMA - EEFF 30-06-2026.pdf"
    first_stored = load_or_convert(first_pdf)
    second_stored = load_or_convert(second_pdf)
    first = extract_recipe(first_stored, classify(first_pdf, first_stored))
    second = extract_recipe(second_stored, classify(second_pdf, second_stored))

    def _net(claims: tuple[FinancialClaim, ...], scope: str) -> str:
        matches = [
            claim.value
            for claim in claims
            if claim.metric == "net_income" and claim.scope == scope
        ]
        assert len(matches) == 1
        return matches[0]

    assert _net(first, "consolidated") == "21262335"
    assert _net(first, "parent_attributable") == "21259769"
    assert _net(second, "consolidated") == "81956525"
    assert _net(second, "parent_attributable") == "81946993"
    assert {claim.period for claim in first} == {PERIOD_1T26}
    assert {claim.period for claim in second} == {PERIOD_2T26}


@pytest.mark.parametrize("filename", NON_EEFF)
def test_non_eeff_extract_to_empty(filename: str, tmp_path: Path) -> None:
    pdf = CORPUS / filename
    assert pdf.is_file()
    stored = _stored(
        tmp_path,
        pdf,
        _document(
            body_tables=[
                _table(
                    "#/tables/1",
                    _recipe_grid("31.03.2026"),
                    layer="body",
                    parent="#/body",
                )
            ],
            furniture_tables=[],
        ),
    )
    document = classify(pdf, stored)

    claims = extract_recipe(stored, document)

    assert document.kind in {"comunicado", "deck", "memoria", "transcript"}
    assert claims == ()


def test_comunicado_repeating_21262335_does_not_become_identity(
    tmp_path: Path,
) -> None:
    filename = "BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf"
    pdf = CORPUS / filename
    payload = _document(
        body_tables=[
            _table(
                "#/tables/1",
                _recipe_grid("31.03.2026"),
                layer="body",
                parent="#/body",
            )
        ],
        furniture_tables=[],
    )
    stored = _stored(tmp_path, pdf, payload)
    raw = stored.json_path.read_text(encoding="utf-8")
    assert GOLD_NET_INCOME_FIGURE in raw.replace(".", "")

    claims = extract_recipe(stored, classify(pdf, stored))

    assert claims == ()
    assert all(GOLD_NET_INCOME_FIGURE not in claim.identity_key for claim in claims)


def test_furniture_recipe_row_is_ignored(tmp_path: Path) -> None:
    pdf = CORPUS / "BYMA_-_EEFF_31-03-2026_VF.pdf"
    poisoned = _recipe_grid("31.03.2026")
    for row in poisoned:
        if row[0]["text"] == "RESULTADO NETO DEL PERÍODO":
            row[2] = _cell("9.999.999")
    furniture = _table(
        "#/tables/0",
        poisoned,
        layer="furniture",
        parent="#/furniture",
    )
    body = _table(
        "#/tables/1",
        _recipe_grid("31.03.2026"),
        layer="body",
        parent="#/body",
    )
    stored = _stored(
        tmp_path,
        pdf,
        _document(body_tables=[body], furniture_tables=[furniture]),
    )
    document = DocumentClass(kind="eeff", issuer="BYMA", period=PERIOD_1T26)

    claims = extract_recipe(stored, document)

    _assert_recipe_claims(claims, stored, PERIOD_1T26)
    assert FURNITURE_FIGURE not in {claim.value for claim in claims}
    assert all(claim.evidence[0].document_id == "#/tables/1" for claim in claims)


def test_eeff_outside_recipe_periods_stays_empty(tmp_path: Path) -> None:
    pdf = CORPUS / "Memoria-BYMA-y-EEFF-al-31-12-2023.pdf"
    stored = _stored(
        tmp_path,
        pdf,
        _document(
            body_tables=[
                _table(
                    "#/tables/1",
                    _recipe_grid("31.12.2023"),
                    layer="body",
                    parent="#/body",
                )
            ],
            furniture_tables=[],
        ),
    )
    year_end = DocumentClass(kind="eeff", issuer="BYMA", period="2023-12-31")
    missing_period = DocumentClass(kind="eeff", issuer="BYMA", period=None)
    comunicado_period = DocumentClass(
        kind="comunicado", issuer="BYMA", period=PERIOD_1T26
    )

    assert extract_recipe(stored, year_end) == ()
    assert extract_recipe(stored, missing_period) == ()
    assert extract_recipe(stored, comunicado_period) == ()


def test_body_tables_come_from_iterate_items(tmp_path: Path) -> None:
    pdf = CORPUS / "BYMA_-_EEFF_31-03-2026_VF.pdf"
    poisoned = _recipe_grid("31.03.2026")
    for row in poisoned:
        if row[0]["text"] == "RESULTADO NETO DEL PERÍODO":
            row[2] = _cell("9.999.999")
    stored = _stored(
        tmp_path,
        pdf,
        _document(
            body_tables=[
                _table(
                    "#/tables/1",
                    _recipe_grid("31.03.2026"),
                    layer="body",
                    parent="#/body",
                )
            ],
            furniture_tables=[
                _table(
                    "#/tables/0",
                    poisoned,
                    layer="furniture",
                    parent="#/furniture",
                )
            ],
        ),
    )
    document = DocumentClass(kind="eeff", issuer="BYMA", period=PERIOD_1T26)

    claims = extract_recipe(stored, document)

    assert FURNITURE_FIGURE not in {claim.value for claim in claims}
    source = (INGEST_ROOT / "extract.py").read_text(encoding="utf-8")
    assert "iterate_items" in source
    assert "def _index_items" not in source
    assert "def _ordered_items" not in source


def test_extract_recipe_is_exported_from_ingest_package() -> None:
    import claimledger.ingest as ingest

    assert ingest.extract_recipe is extract_recipe


def test_extract_source_reads_grid_not_markdown() -> None:
    source = (INGEST_ROOT / "extract.py").read_text(encoding="utf-8")
    assert "export_to_markdown" not in source
    assert "TableData" not in source or "grid" in source
    assert ".grid" in source or '["grid"]' in source or "['grid']" in source
    assert "furniture" in source


def _table_from_cells(self_ref: str, grid: list[list[dict]]) -> dict:
    table = _table(self_ref, grid, layer="body", parent="#/body")
    cells = []
    for row_index, row in enumerate(grid):
        for col_index, cell in enumerate(row):
            cells.append(
                {
                    "text": cell["text"],
                    "bbox": cell["bbox"],
                    "start_row_offset_idx": row_index,
                    "end_row_offset_idx": row_index + 1,
                    "start_col_offset_idx": col_index,
                    "end_col_offset_idx": col_index + 1,
                }
            )
    table["data"] = {
        "num_rows": len(grid),
        "num_cols": len(grid[0]) if grid else 0,
        "table_cells": cells,
    }
    return table


def test_cells_without_grid_match_stored_grid(tmp_path: Path) -> None:
    pdf = CORPUS / "BYMA_-_EEFF_31-03-2026_VF.pdf"
    grid = _recipe_grid("31.03.2026")
    with_grid = _stored(
        tmp_path,
        pdf,
        _document(
            body_tables=[_table("#/tables/0", grid, layer="body", parent="#/body")],
            furniture_tables=[],
        ),
    )
    from_cells = _stored(
        tmp_path,
        pdf,
        _document(
            body_tables=[_table_from_cells("#/tables/0", grid)],
            furniture_tables=[],
        ),
    )
    document = DocumentClass(kind="eeff", issuer="BYMA", period=PERIOD_1T26)

    def _slots(stored: StoredDocument) -> set[tuple[str, str, str]]:
        return {
            (claim.scope, claim.metric, claim.value)
            for claim in extract_recipe(stored, document)
        }

    assert _slots(from_cells) == _slots(with_grid)
    assert _slots(from_cells)

    source = (INGEST_ROOT / "extract.py").read_text(encoding="utf-8")
    assert "TableData" in source
    assert "start_row_offset_idx" not in source
