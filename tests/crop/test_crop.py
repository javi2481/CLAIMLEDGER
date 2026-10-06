"""Synthetic page-bbox crop."""

from __future__ import annotations

import base64
import json
import math
import struct
import sys
import zlib
from pathlib import Path

from claimledger.claim import FinancialClaim
from claimledger.crop.cut import crop_bbox
from claimledger.identity import PERIOD_1T26, PERIOD_2T26, identity_key
from claimledger.ingest.classify import DocumentClass
from claimledger.ingest.extract import extract_recipe
from claimledger.ingest.types import StoredDocument
from claimledger.ledger import RECIPE_ROWS
from claimledger.query import QueryResult


def _rgb(width: int, height: int, marker: int) -> bytes:
    raw = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            i = (y * width + x) * 3
            raw[i] = y
            raw[i + 1] = x
            raw[i + 2] = marker
    return bytes(raw)


def _window(
    width: int, height: int, bbox: tuple[float, float, float, float]
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = bbox
    return (
        math.floor((1 - y1) * height),
        math.ceil((1 - y0) * height),
        math.floor(x0 * width),
        math.ceil(x1 * width),
    )


def _slice(
    pixels: bytes, width: int, row0: int, row1: int, col0: int, col1: int
) -> bytes:
    span = (col1 - col0) * 3
    out = bytearray()
    for row in range(row0, row1):
        start = (row * width + col0) * 3
        out.extend(pixels[start : start + span])
    return bytes(out)


def _decode_png_rgb(png: bytes) -> tuple[int, int, bytes]:
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    pos = 8
    width = height = 0
    idat = bytearray()
    while pos + 12 <= len(png):
        length = struct.unpack(">I", png[pos : pos + 4])[0]
        tag = png[pos + 4 : pos + 8]
        data = png[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height, depth, color = struct.unpack(">IIBB", data[:10])
            assert (depth, color) == (8, 2)
        elif tag == b"IDAT":
            idat.extend(data)
        elif tag == b"IEND":
            break
    inflated = zlib.decompress(bytes(idat))
    stride = width * 3
    pixels = bytearray()
    cursor = 0
    for _ in range(height):
        assert inflated[cursor] == 0
        cursor += 1
        pixels.extend(inflated[cursor : cursor + stride])
        cursor += stride
    assert cursor == len(inflated)
    return width, height, bytes(pixels)


def test_crop_bbox_y_window_no_padding() -> None:
    width, height = 10, 10
    pixels = _rgb(width, height, 17)
    bbox = (0.2, 0.5, 0.4, 0.6)
    row0, row1, col0, col1 = _window(width, height, bbox)
    assert (row0, row1, col0, col1) == (4, 5, 2, 4)

    png = crop_bbox(pixels, width, height, bbox)
    assert png is not None
    cropped_w, cropped_h, cropped = _decode_png_rgb(png)
    assert (cropped_w, cropped_h) == (col1 - col0, row1 - row0)
    assert cropped == _slice(pixels, width, row0, row1, col0, col1)

    assert crop_bbox(pixels, width, height, None) is None
    assert crop_bbox(pixels, width, height, (0.2, 0.5, 0.2, 0.6)) is None
    assert crop_bbox(pixels, width, height, (0.2, 0.5, 0.4, 0.5)) is None

    source = (
        Path(__file__).resolve().parents[2] / "src" / "claimledger" / "crop" / "cut.py"
    ).read_text(encoding="utf-8")
    assert "PIL" not in source
    assert "pillow" not in source.lower()


def test_crop_bbox_other_window_matches_source_pixels() -> None:
    width, height = 5, 4
    pixels = _rgb(width, height, 3)
    bbox = (0.1, 0.25, 0.5, 0.75)
    row0, row1, col0, col1 = _window(width, height, bbox)
    assert (row0, row1, col0, col1) == (1, 3, 0, 3)

    png = crop_bbox(pixels, width, height, bbox)
    assert png is not None
    cropped_w, cropped_h, cropped = _decode_png_rgb(png)
    assert (cropped_w, cropped_h) == (3, 2)
    assert cropped == _slice(pixels, width, row0, row1, col0, col1)


_PAGE = 10
_NET_BOX = (2.0, 5.0, 4.0, 6.0)
_PARENT_BOX = (6.0, 1.0, 8.0, 3.0)
_TABLE_BOX = (0.0, 0.0, 10.0, 10.0)


def _encode_png_rgb(pixels: bytes, width: int, height: int) -> bytes:
    stride = width * 3
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        raw.extend(pixels[row * stride : (row + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


def _pdf_box(left: float, bottom: float, right: float, top: float) -> dict:
    return {
        "l": left,
        "b": bottom,
        "r": right,
        "t": top,
        "coord_origin": "BOTTOMLEFT",
    }


def _cell(text: str, box: tuple[float, float, float, float] | None = None) -> dict:
    cell: dict = {"text": text}
    if box is not None:
        cell["bbox"] = _pdf_box(*box)
    return cell


def _income_table(
    self_ref: str,
    header: str,
    net_text: str,
    parent_text: str,
    page_no: int,
) -> dict:
    grid = [
        [_cell(""), _cell(header)],
        [_cell("Resultado bruto"), _cell("60.144.176")],
        [
            _cell("RESULTADO NETO DEL PERÍODO"),
            _cell(net_text, _NET_BOX),
        ],
        [
            _cell(
                "Resultado neto del período atribuible a la participación controlante"
            ),
            _cell(parent_text, _PARENT_BOX),
        ],
    ]
    return {
        "self_ref": self_ref,
        "content_layer": "body",
        "parent": {"$ref": "#/body"},
        "prov": [
            {
                "page_no": page_no,
                "charspan": [0, 0],
                "bbox": _pdf_box(*_TABLE_BOX),
            }
        ],
        "data": {"grid": grid},
    }


def _payload(tables: list[dict], page_nos: tuple[int, ...]) -> dict:
    return {
        "name": "sample",
        "pages": {
            str(page_no): {
                "page_no": page_no,
                "size": {"width": float(_PAGE), "height": float(_PAGE)},
            }
            for page_no in page_nos
        },
        "body": {
            "self_ref": "#/body",
            "children": [{"$ref": table["self_ref"]} for table in tables],
        },
        "tables": tables,
    }


def _claim(period: str, scope: str, metric: str, value: str) -> FinancialClaim:
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


def _write_artifact(root: Path, artifact_hash: str, payload: dict) -> StoredDocument:
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{artifact_hash}.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")
    return StoredDocument(
        artifact_hash=artifact_hash,
        json_path=json_path,
        source_pdf=root / "source.pdf",
    )


def _write_sidecar(root: Path, artifact_hash: str, page_no: int, marker: int) -> bytes:
    pixels = _rgb(_PAGE, _PAGE, marker)
    (root / f"{artifact_hash}.p{page_no}.png").write_bytes(
        _encode_png_rgb(pixels, _PAGE, _PAGE)
    )
    return pixels


def _markdown(png: bytes) -> str:
    encoded = base64.b64encode(png).decode("ascii")
    return f"![crop](data:image/png;base64,{encoded})"


def _matched_evidence(stored: StoredDocument, claim: FinancialClaim):
    found = [
        item
        for item in extract_recipe(
            stored,
            DocumentClass(kind="eeff", issuer=claim.issuer, period=claim.period),
        )
        if item.identity_key == claim.identity_key and item.value == claim.value
    ]
    assert len(found) == 1
    assert len(found[0].evidence) == 1
    return found[0].evidence[0]


def _docling_modules() -> set[str]:
    return {
        name
        for name in sys.modules
        if name == "docling" or name.startswith("docling.")
    }


def _imports_docling(path: Path) -> bool:
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        if any(name == "docling" or name.startswith("docling.") for name in names):
            return True
    return False


def _crop_sources() -> list[Path]:
    root = Path(__file__).resolve().parents[2]
    crop = root / "src" / "claimledger" / "crop"
    return [Path(__file__), *sorted(crop.glob("*.py"))]


def _forbid_pdf_open(monkeypatch) -> list[str]:
    opened: list[str] = []
    original = Path.open

    def guarded(self: Path, *args, **kwargs):
        opened.append(self.suffix.lower())
        if self.suffix.lower() == ".pdf":
            raise AssertionError(f"source_pdf re-raster: {self}")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    return opened


def test_attach_matches_identity_key_and_value(tmp_path: Path, monkeypatch) -> None:
    from claimledger.crop.attach import attach
    import claimledger.ingest.store as ingest_store

    assert ("2026-03-31", "consolidated", "net_income", "21262335") in RECIPE_ROWS
    assert ("2026-03-31", "parent_attributable", "net_income", "21259769") in RECIPE_ROWS
    assert [path.name for path in _crop_sources() if _imports_docling(path)] == []
    before_docling = _docling_modules()

    monkeypatch.setattr(ingest_store, "artifacts_dir", lambda: tmp_path)
    consolidated = _claim(PERIOD_1T26, "consolidated", "net_income", "21262335")
    parent = _claim(PERIOD_1T26, "parent_attributable", "net_income", "21259769")

    match_hash = "a" * 64
    match_stored = _write_artifact(
        tmp_path,
        match_hash,
        _payload(
            [
                _income_table(
                    "#/tables/0",
                    "31.03.2026",
                    "21.262.335",
                    "21.259.769",
                    page_no=1,
                )
            ],
            (1,),
        ),
    )
    match_pixels = _write_sidecar(tmp_path, match_hash, 1, 17)
    match_evidence = _matched_evidence(match_stored, consolidated)
    assert match_evidence.page == 1
    assert match_evidence.bbox == (0.2, 0.5, 0.4, 0.6)
    parent_evidence = _matched_evidence(match_stored, parent)
    assert parent_evidence.bbox == (0.6, 0.1, 0.8, 0.3)
    match_png = crop_bbox(match_pixels, _PAGE, _PAGE, match_evidence.bbox)
    parent_png = crop_bbox(match_pixels, _PAGE, _PAGE, parent_evidence.bbox)
    assert match_png is not None and parent_png is not None and match_png != parent_png

    opened = _forbid_pdf_open(monkeypatch)
    images = attach(
        match_hash,
        QueryResult(status="verified", claims=(consolidated,), identity=consolidated.identity_key),
    )
    assert images == (_markdown(match_png),)
    assert _markdown(parent_png) not in images
    assert ".pdf" not in opened
    assert ".png" in opened

    other_hash = "b" * 64
    _write_artifact(
        tmp_path,
        other_hash,
        _payload(
            [
                _income_table(
                    "#/tables/0",
                    "31.03.2026",
                    "11.111.111",
                    "21.259.769",
                    page_no=1,
                )
            ],
            (1,),
        ),
    )
    _write_sidecar(tmp_path, other_hash, 1, 17)
    assert consolidated.value == "21262335"
    assert attach(
        other_hash,
        QueryResult(status="verified", claims=(consolidated,), identity=consolidated.identity_key),
    ) == ()

    assert attach(
        match_hash,
        QueryResult(status="abstained", reason="recipe_no_extract", claims=(consolidated,)),
    ) == ()

    missing_hash = "c" * 64
    _write_artifact(
        tmp_path,
        missing_hash,
        _payload(
            [
                _income_table(
                    "#/tables/0",
                    "31.03.2026",
                    "21.262.335",
                    "21.259.769",
                    page_no=1,
                )
            ],
            (1,),
        ),
    )
    assert not (tmp_path / f"{missing_hash}.p1.png").is_file()
    assert attach(
        missing_hash,
        QueryResult(status="verified", claims=(consolidated,), identity=consolidated.identity_key),
    ) == ()
    assert ".pdf" not in opened

    later = _claim(PERIOD_2T26, "consolidated", "net_income", "81956525")
    earlier = consolidated
    compare_hash = "d" * 64
    compare_stored = _write_artifact(
        tmp_path,
        compare_hash,
        _payload(
            [
                _income_table(
                    "#/tables/0",
                    "30.06.2026",
                    "81.956.525",
                    "81.946.993",
                    page_no=2,
                ),
                _income_table(
                    "#/tables/1",
                    "31.03.2026",
                    "21.262.335",
                    "21.259.769",
                    page_no=1,
                ),
            ],
            (1, 2),
        ),
    )
    later_pixels = _write_sidecar(tmp_path, compare_hash, 2, 29)
    earlier_pixels = _write_sidecar(tmp_path, compare_hash, 1, 17)
    later_png = crop_bbox(
        later_pixels,
        _PAGE,
        _PAGE,
        _matched_evidence(compare_stored, later).bbox,
    )
    earlier_png = crop_bbox(
        earlier_pixels,
        _PAGE,
        _PAGE,
        _matched_evidence(compare_stored, earlier).bbox,
    )
    assert later_png is not None and earlier_png is not None
    compare = attach(
        compare_hash,
        QueryResult(
            status="verified",
            claims=(later, earlier),
            identity="BYMA|*|income_statement|consolidated|net_income",
        ),
    )
    assert compare == (_markdown(later_png), _markdown(earlier_png))
    delta = str(int(later.value) - int(earlier.value))
    assert delta == "60694190"
    assert delta not in "\n".join(compare)
    assert ".pdf" not in opened
    assert _docling_modules() == before_docling
