"""Local Path conversion. OCR off. Models stay on a local artifacts path."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

from claimledger.ingest.types import IngestError

PINNED_DOCLING = "2.130.0"
_REPO_ROOT = Path(__file__).resolve().parents[3]
last_page_pngs: dict[int, bytes] = {}


def model_artifacts_path() -> Path:
    return _REPO_ROOT / "artifacts" / "docling" / "models"


def _ensure_local_models(model_dir: Path) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    from docling.utils.model_downloader import download_models

    download_models(
        output_dir=model_dir,
        with_code_formula=False,
        with_picture_classifier=False,
        with_rapidocr=False,
    )


def _require_pinned_docling() -> None:
    installed = version("docling")
    if installed != PINNED_DOCLING:
        raise IngestError(
            f"docling {installed} does not match pin {PINNED_DOCLING}"
        )


def doclang_from_payload(payload: dict) -> str:
    _require_pinned_docling()
    from docling_core.types.doc.document import DoclingDocument

    return DoclingDocument.model_validate(payload).export_to_doclang()


def _png_bytes(pil_image: object) -> bytes:
    from io import BytesIO
    from PIL import Image

    save = getattr(pil_image, "save", None)
    if not isinstance(pil_image, Image.Image) and not callable(save):
        raise IngestError("page image is missing")
    if not callable(save):
        raise IngestError("page image is missing")
    buffer = BytesIO()
    save(buffer, format="PNG")
    return buffer.getvalue()


def _remember_page_pngs(document: object) -> None:
    global last_page_pngs
    captured: dict[int, bytes] = {}
    pages = getattr(document, "pages", None) or {}
    for key, page in pages.items():
        image = getattr(page, "image", None)
        pil = getattr(image, "pil_image", None) if image is not None else None
        if pil is None:
            continue
        captured[int(key)] = _png_bytes(pil)
    last_page_pngs = captured


def _export_complete(result) -> dict:
    status = result.status
    value = getattr(status, "value", status)
    if value != "success":
        raise IngestError(f"conversion status {value} is not success")
    _remember_page_pngs(result.document)
    from claimledger.ingest.store import strip_page_pixels

    return strip_page_pixels(result.document.export_to_dict())


def convert_pdf(pdf: Path) -> dict:
    if not isinstance(pdf, Path):
        raise IngestError("source must be a local file path")
    if not pdf.is_file():
        raise IngestError("source must be a local file path")
    _require_pinned_docling()
    # Docling imports NumPy before torch. On Windows that order fails c10.dll init.
    import torch  # noqa: F401

    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    model_dir = model_artifacts_path()
    _ensure_local_models(model_dir)
    options = PdfPipelineOptions(do_ocr=False)
    options.generate_page_images = True
    options.artifacts_path = model_dir
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=options),
        }
    )
    result = converter.convert(pdf)
    return _export_complete(result)
