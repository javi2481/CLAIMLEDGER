"""Recipe P&L claims from a hashed Docling JSON grid. Furniture is ignored."""

from __future__ import annotations

import json
from importlib.metadata import version
from typing import Any

from claimledger.claim import FinancialClaim
from claimledger.digits import signed_ars
from claimledger.evidence import FinancialEvidence
from claimledger.identity import PERIOD_1T26, PERIOD_2T26, fold, identity_key
from claimledger.ingest.classify import DocumentClass
from claimledger.ingest.types import IngestError, StoredDocument

# extract_recipe may use docling_core; convert path does not pin in-process.
PINNED_DOCLING = "2.130.0"
_STATEMENT = "income_statement"
_RECIPE_PERIODS = frozenset({PERIOD_1T26, PERIOD_2T26})
_PERIOD_END = {
    PERIOD_1T26: "31/03/2026",
    PERIOD_2T26: "30/06/2026",
}
_BODY_LABEL_TOKENS = (
    "ingreso",
    "costo",
    "resultado",
    "gasto",
    "impuesto",
)


def extract_recipe(
    stored: StoredDocument, cls: DocumentClass
) -> tuple[FinancialClaim, ...]:
    if not isinstance(stored, StoredDocument) or not isinstance(cls, DocumentClass):
        raise IngestError("extract_recipe expects a StoredDocument and a DocumentClass")
    if cls.kind != "eeff" or cls.period not in _RECIPE_PERIODS:
        return ()
    payload = json.loads(stored.json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise IngestError("artifact JSON must be an object")
    found: dict[tuple[str, str], FinancialClaim] = {}
    for table in _body_tables(payload):
        grid = _table_grid(table)
        if not _is_consolidated_income_table(grid):
            continue
        column = _value_column(grid, cls.period)
        if column is None:
            continue
        for claim in _claims_from_table(table, grid, column, stored, cls, payload):
            key = (claim.scope, claim.metric)
            found.setdefault(key, claim)
    return tuple(found.values())


def _require_pinned_docling() -> None:
    installed = version("docling")
    if installed != PINNED_DOCLING:
        raise IngestError(
            f"docling {installed} does not match pin {PINNED_DOCLING}"
        )


def _load_pinned_docling() -> None:
    # Docling imports NumPy before torch. On Windows that order fails c10.dll init.
    import torch  # noqa: F401

    _require_pinned_docling()


def _body_tables(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Body tables. iterate_items leaves furniture out by default."""
    _load_pinned_docling()
    from docling_core.types.doc.document import DoclingDocument, TableItem

    document = DoclingDocument.model_validate(payload)
    by_ref: dict[str, dict[str, Any]] = {}
    for item in payload.get("tables") or []:
        if isinstance(item, dict) and isinstance(item.get("self_ref"), str):
            by_ref[item["self_ref"]] = item
    tables: list[dict[str, Any]] = []
    for item, _level in document.iterate_items():
        if not isinstance(item, TableItem):
            continue
        stored = by_ref.get(item.self_ref)
        if stored is not None:
            tables.append(stored)
    return tables


def _table_grid(table: dict[str, Any]) -> list[list[dict[str, Any]]]:
    data = table.get("data")
    if not isinstance(data, dict):
        return []
    grid = data.get("grid")
    if isinstance(grid, list) and grid:
        return [row for row in grid if isinstance(row, list)]
    return _grid_from_table_data(data)


def _grid_from_table_data(data: dict[str, Any]) -> list[list[dict[str, Any]]]:
    _load_pinned_docling()
    from docling_core.types.doc.document import TableData

    grid = TableData.model_validate(data).grid
    return [[cell.model_dump() for cell in row] for row in grid]


def _is_consolidated_income_table(grid: list[list[dict[str, Any]]]) -> bool:
    labels = [fold(_row_label(row)) for row in grid]
    has_gross = any(label == "resultado bruto" for label in labels)
    has_parent = any(_is_parent_label(label) for label in labels)
    return has_gross and has_parent


def _is_parent_label(label: str) -> bool:
    return "participacion controlante" in label and "no controlante" not in label


def _claims_from_table(
    table: dict[str, Any],
    grid: list[list[dict[str, Any]]],
    column: int,
    stored: StoredDocument,
    cls: DocumentClass,
    payload: dict[str, Any],
) -> list[FinancialClaim]:
    claims: list[FinancialClaim] = []
    page = _page_no(table)
    page_size = _page_size(payload, page)
    table_bbox = _provenance_bbox(table, page_size)
    document_id = str(table.get("self_ref") or "")
    for row in grid:
        scope_metric = _recipe_slot(fold(_row_label(row)))
        if scope_metric is None or column >= len(row):
            continue
        scope, metric = scope_metric
        cell = row[column]
        text = _cell_text(cell).strip()
        value = _amount(text)
        if value is None:
            continue
        bbox = _cell_bbox(cell, page_size) or table_bbox
        evidence = FinancialEvidence(
            document_id=document_id,
            artifact_hash=stored.artifact_hash,
            page=page,
            text=text,
            label=_row_label(row).strip(),
            bbox=bbox,
        )
        claims.append(
            FinancialClaim(
                identity_key=identity_key(
                    cls.issuer, cls.period, _STATEMENT, scope, metric
                ),
                issuer=cls.issuer,
                period=cls.period,
                statement=_STATEMENT,
                scope=scope,
                metric=metric,
                value=value,
                currency="ARS",
                unit=None,
                evidence=(evidence,),
                ledger_status="recorded",
            )
        )
    return claims


def _recipe_slot(label: str) -> tuple[str, str] | None:
    if "no controlante" in label:
        return ("consolidated", "nci_income")
    if _is_parent_label(label):
        return ("parent_attributable", "net_income")
    if label == "resultado bruto":
        return ("consolidated", "gross_profit")
    if label == "resultado operativo":
        return ("consolidated", "operating_income")
    if label.startswith("resultado antes del impuesto") or label.startswith(
        "resultado antes de impuesto"
    ):
        return ("consolidated", "income_before_tax")
    if label == "impuesto a las ganancias" or label.startswith(
        "impuesto a las ganancias"
    ):
        return ("consolidated", "income_tax")
    if label == "resultado neto del periodo":
        return ("consolidated", "net_income")
    return None


def _value_column(grid: list[list[dict[str, Any]]], period: str) -> int | None:
    width = max((len(row) for row in grid), default=0)
    header_rows: list[list[dict[str, Any]]] = []
    for row in grid:
        if _row_starts_body(row):
            break
        header_rows.append(row)
    matches: list[int] = []
    for column in range(width):
        chunks = [
            _cell_text(row[column])
            for row in header_rows
            if column < len(row) and _cell_text(row[column])
        ]
        if _period_in_header(" ".join(chunks), period):
            matches.append(column)
    for column in matches:
        if _column_has_amount(grid, column):
            return column
    return None


def _row_starts_body(row: list[dict[str, Any]]) -> bool:
    label = fold(_row_label(row))
    return any(token in label for token in _BODY_LABEL_TOKENS)


def _period_in_header(text: str, period: str) -> bool:
    compact = fold(text).replace(" ", "").replace(".", "/").replace("-", "/")
    return _PERIOD_END[period] in compact


def _column_has_amount(grid: list[list[dict[str, Any]]], column: int) -> bool:
    return any(
        column < len(row) and _amount(_cell_text(row[column])) is not None
        for row in grid
    )


def _amount(text: str) -> str | None:
    compact = " ".join(text.split())
    if "." not in compact:
        return None
    return signed_ars(compact)


def _row_label(row: list[dict[str, Any]]) -> str:
    if not row:
        return ""
    first = _cell_text(row[0]).strip()
    if first:
        return first
    for cell in row[1:]:
        text = _cell_text(cell).strip()
        if text:
            return text
    return ""


def _cell_text(cell: object) -> str:
    if isinstance(cell, dict):
        return str(cell.get("text") or "")
    return ""


def _page_no(table: dict[str, Any]) -> int:
    for item in table.get("prov") or []:
        if isinstance(item, dict) and isinstance(item.get("page_no"), int):
            return item["page_no"]
    return 0


def _page_size(payload: dict[str, Any], page_no: int) -> tuple[float, float] | None:
    pages = payload.get("pages")
    if not isinstance(pages, dict):
        return None
    page = pages.get(str(page_no))
    if not isinstance(page, dict):
        page = pages.get(page_no)
    if not isinstance(page, dict):
        return None
    size = page.get("size")
    if not isinstance(size, dict):
        return None
    width = size.get("width")
    height = size.get("height")
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        return None
    if width <= 0 or height <= 0:
        return None
    return float(width), float(height)


def _provenance_bbox(
    table: dict[str, Any], page_size: tuple[float, float] | None
) -> tuple[float, float, float, float] | None:
    if page_size is None:
        return None
    for item in table.get("prov") or []:
        if isinstance(item, dict):
            bbox = _normalize_bbox(item.get("bbox"), page_size)
            if bbox is not None:
                return bbox
    return None


def _cell_bbox(
    cell: dict[str, Any], page_size: tuple[float, float] | None
) -> tuple[float, float, float, float] | None:
    if page_size is None or not isinstance(cell, dict):
        return None
    return _normalize_bbox(cell.get("bbox"), page_size)


def _normalize_bbox(
    bbox: object, page_size: tuple[float, float]
) -> tuple[float, float, float, float] | None:
    if not isinstance(bbox, dict):
        return None
    try:
        left = float(bbox["l"])
        right = float(bbox["r"])
        bottom = float(bbox["b"])
        top = float(bbox["t"])
    except (KeyError, TypeError, ValueError):
        return None
    width, height = page_size
    x0, x1 = sorted((left / width, right / width))
    y0, y1 = sorted((bottom / height, top / height))

    def clamp(value: float) -> float:
        return min(1.0, max(0.0, value))

    return (clamp(x0), clamp(y0), clamp(x1), clamp(y1))
