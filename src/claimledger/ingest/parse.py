"""Local Path conversion via docling-serve ZIP (referenced images)."""

from __future__ import annotations

import json
import os
import re
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

from claimledger.ingest.types import ConvertBundle, IngestError

DEFAULT_SERVE_URL = "http://127.0.0.1:5001"
_PAGE_PNG_RE = re.compile(r"(?:^|/)page-(\d+)\.png$")


def serve_base_url() -> str:
    return os.environ.get("DOCLING_SERVE_URL", DEFAULT_SERVE_URL).rstrip("/")


def convert_form_fields() -> dict[str, Any]:
    """Non-VLM seal for POST /v1/convert/file (multipart form)."""
    return {
        "do_ocr": True,
        "ocr_preset": "rapidocr",
        "ocr_lang": ["es"],
        "do_table_structure": True,
        "table_mode": "accurate",
        "do_picture_classification": True,
        "do_pdf_heading_hierarchy": True,
        "include_page_images": True,
        "include_images": True,
        "image_export_mode": "referenced",
        "target_type": "zip",
        "to_formats": ["json", "doclang"],
        "do_picture_description": False,
        "do_chart_extraction": False,
        "do_code_enrichment": False,
        "do_formula_enrichment": False,
    }


def _unpack_convert_zip(raw: bytes) -> ConvertBundle:
    try:
        archive = zipfile.ZipFile(BytesIO(raw))
    except zipfile.BadZipFile as exc:
        raise IngestError("convert response is not a ZIP") from exc
    names = archive.namelist()
    json_name = next(
        (n for n in names if n.endswith("document.json") or n == "document.json"),
        None,
    )
    dclg_name = next(
        (n for n in names if n.endswith("document.dclg") or n == "document.dclg"),
        None,
    )
    if json_name is None or dclg_name is None:
        raise IngestError("convert ZIP missing document.json or document.dclg")
    try:
        payload = json.loads(archive.read(json_name).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IngestError("convert ZIP document.json is invalid") from exc
    if not isinstance(payload, dict):
        raise IngestError("convert ZIP document.json must be an object")
    doclang = archive.read(dclg_name).decode("utf-8")
    page_pngs: dict[int, bytes] = {}
    for name in names:
        match = _PAGE_PNG_RE.search(name.replace("\\", "/"))
        if match:
            page_pngs[int(match.group(1))] = archive.read(name)
    return ConvertBundle(payload=payload, doclang=doclang, page_pngs=page_pngs)


def convert_local(pdf: Path) -> ConvertBundle:
    if not isinstance(pdf, Path):
        raise IngestError("source must be a local file path")
    if not pdf.is_file():
        raise IngestError("source must be a local file path")
    import httpx

    url = f"{serve_base_url()}/v1/convert/file"
    try:
        with pdf.open("rb") as handle:
            with httpx.Client(timeout=600.0) as client:
                response = client.post(
                    url,
                    files={"files": (pdf.name, handle, "application/pdf")},
                    data=convert_form_fields(),
                )
    except httpx.HTTPError as exc:
        raise IngestError(f"docling-serve unreachable: {exc}") from exc
    except OSError as exc:
        raise IngestError(f"docling-serve unreachable: {exc}") from exc
    if response.status_code >= 400:
        raise IngestError(
            f"docling-serve returned HTTP {response.status_code}"
        )
    return _unpack_convert_zip(response.content)


def convert_pdf(pdf: Path) -> dict:
    """Thin alias: payload only from convert_local."""
    return convert_local(pdf).payload
