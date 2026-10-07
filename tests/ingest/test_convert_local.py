"""convert_local → docling-serve ZIP. Mock HTTP only; no network/PDF/Docker."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

from claimledger.ingest.types import ConvertBundle, IngestError

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
PARSE_PATH = REPO_ROOT / "src" / "claimledger" / "ingest" / "parse.py"


def _zip_bytes(
    payload: dict,
    doclang: str = "doclang-from-zip",
    pages: dict[int, bytes] | None = None,
) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("document.json", json.dumps(payload))
        zf.writestr("document.dclg", doclang)
        for page_no, png in (pages or {1: b"\x89PNG\r\n\x1a\npage-1"}).items():
            zf.writestr(f"page-{page_no}.png", png)
    return buf.getvalue()


def _form_values(data: dict[str, Any]) -> dict[str, list[str]]:
    """Normalize httpx multipart form data for assertions."""
    out: dict[str, list[str]] = {}
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            out[key] = [str(v).lower() if isinstance(v, bool) else str(v) for v in value]
        elif isinstance(value, bool):
            out[key] = [str(value).lower()]
        else:
            out[key] = [str(value)]
    return out


class _FakeResponse:
    def __init__(self, content: bytes, status_code: int = 200) -> None:
        self.content = content
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _RecordingClient:
    last_url: str | None = None
    last_data: dict[str, Any] | None = None
    last_files: Any = None
    response_content: bytes = b""
    status_code: int = 200
    raise_connect: bool = False

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def __enter__(self) -> _RecordingClient:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, url: str, files: Any = None, data: Any = None) -> _FakeResponse:
        if self.raise_connect:
            raise ConnectionError("serve down")
        type(self).last_url = url
        type(self).last_data = dict(data or {})
        type(self).last_files = files
        return _FakeResponse(self.response_content, self.status_code)


def _install_httpx(
    monkeypatch: pytest.MonkeyPatch,
    zip_content: bytes,
    *,
    status_code: int = 200,
    raise_connect: bool = False,
) -> type[_RecordingClient]:
    import httpx

    _RecordingClient.response_content = zip_content
    _RecordingClient.status_code = status_code
    _RecordingClient.raise_connect = raise_connect
    _RecordingClient.last_url = None
    _RecordingClient.last_data = None
    _RecordingClient.last_files = None
    monkeypatch.setattr(httpx, "Client", _RecordingClient)
    return _RecordingClient


def test_convert_local_posts_zip_referenced_rapidocr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.parse import convert_local

    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4 sample")
    payload = {"name": "from-zip", "pages": {"1": {"size": {"width": 1, "height": 1}}}}
    png = b"\x89PNG\r\n\x1a\nfrom-serve"
    client = _install_httpx(
        monkeypatch, _zip_bytes(payload, doclang="zip-dclg", pages={1: png})
    )

    bundle = convert_local(pdf)

    assert isinstance(bundle, ConvertBundle)
    assert bundle.payload == payload
    assert bundle.doclang == "zip-dclg"
    assert bundle.page_pngs == {1: png}
    assert client.last_url is not None
    assert client.last_url.endswith("/v1/convert/file")
    assert "/v1/convert/source" not in client.last_url
    form = _form_values(client.last_data or {})
    assert form["target_type"] == ["zip"]
    assert form["image_export_mode"] == ["referenced"]
    assert form["ocr_preset"] == ["rapidocr"]
    assert client.last_files is not None


def test_convert_local_seal_on_and_off_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.parse import convert_local

    pdf = tmp_path / "seal.pdf"
    pdf.write_bytes(b"%PDF-1.4 seal")
    client = _install_httpx(monkeypatch, _zip_bytes({"sealed": True}))

    convert_local(pdf)

    form = _form_values(client.last_data or {})
    assert form["do_ocr"] == ["true"]
    assert form["ocr_lang"] == ["es"]
    assert form["do_table_structure"] == ["true"]
    assert form["table_mode"] == ["accurate"]
    assert form["do_picture_classification"] == ["true"]
    assert form["do_pdf_heading_hierarchy"] == ["true"]
    assert form["include_page_images"] == ["true"]
    assert form["include_images"] == ["true"]
    assert "json" in form["to_formats"]
    assert "doclang" in form["to_formats"]
    assert form["do_picture_description"] == ["false"]
    assert form["do_chart_extraction"] == ["false"]
    assert form["do_code_enrichment"] == ["false"]
    assert form["do_formula_enrichment"] == ["false"]
    for key in form:
        assert not key.startswith("vlm_pipeline_")


def test_convert_local_happy_path_has_no_embedded_compiler() -> None:
    source = PARSE_PATH.read_text(encoding="utf-8")
    assert "DocumentConverter" not in source
    assert "download_models" not in source
    assert "export_to_doclang" not in source
    assert "last_page_pngs" not in source
    assert "doclang_from_payload" not in source


def test_convert_local_rejects_non_path_and_url(tmp_path: Path) -> None:
    from claimledger.ingest.parse import convert_local

    with pytest.raises(IngestError):
        convert_local("https://example.invalid/file.pdf")  # type: ignore[arg-type]
    with pytest.raises(IngestError):
        convert_local(tmp_path / "missing.pdf")


def test_convert_local_errors_when_serve_down_or_non_2xx(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.parse import convert_local

    pdf = tmp_path / "down.pdf"
    pdf.write_bytes(b"%PDF-1.4 down")
    _install_httpx(monkeypatch, b"", raise_connect=True)
    with pytest.raises(IngestError):
        convert_local(pdf)

    _install_httpx(monkeypatch, b"nope", status_code=503)
    with pytest.raises(IngestError):
        convert_local(pdf)


def test_convert_local_errors_when_zip_missing_json_or_dclg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.parse import convert_local

    pdf = tmp_path / "badzip.pdf"
    pdf.write_bytes(b"%PDF-1.4 badzip")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("document.json", "{}")
    _install_httpx(monkeypatch, buf.getvalue())
    with pytest.raises(IngestError):
        convert_local(pdf)


def test_compose_remote_services_false_and_no_runtime_depends_on_serve() -> None:
    text = COMPOSE_PATH.read_text(encoding="utf-8")
    assert 'DOCLING_SERVE_ENABLE_REMOTE_SERVICES: "false"' in text or (
        'DOCLING_SERVE_ENABLE_REMOTE_SERVICES: "false"' in text.replace("'", '"')
    )
    assert "quay.io/docling-project/docling-serve-cpu:v1.35.0" in text
    assert "docling-serve" in text
    assert "/version" in text
    # claimledger must not depend_on docling-serve
    claim_idx = text.index("claimledger:")
    serve_idx = text.index("docling-serve:")
    openwebui_idx = text.index("openwebui:")
    claim_block = text[claim_idx:openwebui_idx] if claim_idx < openwebui_idx else text[claim_idx:]
    assert "depends_on" not in claim_block or "docling-serve" not in claim_block
    assert "site-packages" not in text or "docling:" not in text.split("site-packages")[0][-80:]
    assert "./artifacts/docling:/app/artifacts/docling:ro" in text or (
        "./artifacts/docling:/app/artifacts/docling:ro" in text.replace(" ", "")
    )
    # triangulation: serve block must declare remote=false explicitly
    serve_end = openwebui_idx if serve_idx < openwebui_idx else len(text)
    if claim_idx > serve_idx:
        serve_end = min(serve_end, claim_idx)
    serve_block = text[serve_idx:serve_end]
    assert "DOCLING_SERVE_ENABLE_REMOTE_SERVICES" in serve_block
    assert "false" in serve_block


def test_convert_pdf_aliases_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.parse import convert_pdf

    pdf = tmp_path / "alias.pdf"
    pdf.write_bytes(b"%PDF-1.4 alias")
    payload = {"alias": True}
    _install_httpx(monkeypatch, _zip_bytes(payload))
    assert convert_pdf(pdf) == payload
