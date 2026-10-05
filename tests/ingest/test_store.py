"""Hashed Docling JSON store. Local Path convert only."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from claimledger.ingest.parse import convert_pdf
from claimledger.ingest.store import artifacts_dir, load, load_or_convert
from claimledger.ingest.types import IngestError, StoredDocument

REPO_ROOT = Path(__file__).resolve().parents[2]
INGEST_ROOT = REPO_ROOT / "src" / "claimledger" / "ingest"
FORBIDDEN_SOURCE_TOKENS = (
    "HttpSource",
    "docling-graph",
    "docling_graph",
    "llama_index",
    "http://",
    "https://",
)


def _canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _use_artifacts(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(
        "claimledger.ingest.store.artifacts_dir",
        lambda: root,
    )


def test_load_existing_artifact_by_canonical_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"b": 1, "a": "ñ", "nested": {"z": 2, "y": [3, 1]}}
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    (artifacts / f"{digest}.json").write_bytes(raw)
    _use_artifacts(monkeypatch, artifacts)

    loaded = load(digest)

    assert loaded == payload
    assert _sha256_hex(_canonical_json_bytes(loaded)) == digest


def test_load_second_artifact_is_a_different_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = {"doc": "one", "n": 1}
    second = {"doc": "two", "n": 2}
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    digests = []
    for payload in (first, second):
        raw = _canonical_json_bytes(payload)
        digest = _sha256_hex(raw)
        (artifacts / f"{digest}.json").write_bytes(raw)
        digests.append(digest)
    _use_artifacts(monkeypatch, artifacts)

    assert load(digests[0]) == first
    assert load(digests[1]) == second
    assert digests[0] != digests[1]


def test_missing_hash_converts_local_path_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "local-only.pdf"
    pdf.write_bytes(b"%PDF-1.4 local")
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    seen: list[Path] = []

    def fake_convert(source: Path) -> dict:
        seen.append(source)
        assert isinstance(source, Path)
        assert source.is_file()
        return {"kind": "converted", "name": source.name}

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    stored = load_or_convert(pdf)

    assert seen == [pdf.resolve()]
    assert isinstance(stored, StoredDocument)
    assert stored.source_pdf == pdf.resolve()
    assert stored.json_path == artifacts / f"{stored.artifact_hash}.json"
    on_disk = stored.json_path.read_bytes()
    assert _sha256_hex(on_disk) == stored.artifact_hash
    assert on_disk == _canonical_json_bytes(json.loads(on_disk))
    assert load(stored.artifact_hash) == {"kind": "converted", "name": pdf.name}
    pdf_sha = _sha256_hex(pdf.read_bytes())
    manifest = json.loads((artifacts / "manifest.json").read_text(encoding="utf-8"))
    assert manifest[pdf_sha] == stored.artifact_hash

    stored_again = load_or_convert(pdf)

    assert stored_again.artifact_hash == stored.artifact_hash
    assert seen == [pdf.resolve()]


def test_distinct_pdfs_persist_distinct_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    pdf_a = tmp_path / "a.pdf"
    pdf_b = tmp_path / "b.pdf"
    pdf_a.write_bytes(b"%PDF-1.4 A")
    pdf_b.write_bytes(b"%PDF-1.4 B")

    def fake_convert(source: Path) -> dict:
        return {"kind": "converted", "name": source.name, "size": source.stat().st_size}

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    stored_a = load_or_convert(pdf_a)
    stored_b = load_or_convert(pdf_b)

    assert stored_a.artifact_hash != stored_b.artifact_hash
    assert load(stored_a.artifact_hash)["name"] == "a.pdf"
    assert load(stored_b.artifact_hash)["name"] == "b.pdf"


def test_existing_pdf_hash_loads_without_reconvert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from docling_core.types.doc.document import DoclingDocument

    pdf = tmp_path / "cached.pdf"
    pdf.write_bytes(b"%PDF-1.4 cached")
    payload = DoclingDocument(name="cached").export_to_dict()
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    (artifacts / f"{digest}.json").write_bytes(raw)
    pdf_sha = _sha256_hex(pdf.read_bytes())
    (artifacts / "manifest.json").write_text(
        json.dumps({pdf_sha: digest}),
        encoding="utf-8",
    )
    _use_artifacts(monkeypatch, artifacts)

    def boom(source: Path) -> dict:
        raise AssertionError(f"reconvert of {source}")

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", boom)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", boom)

    stored = load_or_convert(pdf)

    assert stored == StoredDocument(
        artifact_hash=digest,
        json_path=artifacts / f"{digest}.json",
        source_pdf=pdf.resolve(),
    )
    assert load(digest) == payload


def test_saved_json_is_also_stored_as_doclang(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from docling_core.types.doc.document import DoclingDocument

    document = DoclingDocument(name="mini")
    payload = document.export_to_dict()
    expected = document.export_to_doclang()
    pdf = tmp_path / "mini.pdf"
    pdf.write_bytes(b"%PDF-1.4 mini")
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    seen: list[Path] = []

    def fake_convert(source: Path) -> dict:
        seen.append(source)
        return payload

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    stored = load_or_convert(pdf)

    doclang_path = stored.json_path.with_suffix(".dclg")
    assert doclang_path.is_file()
    assert doclang_path.read_text(encoding="utf-8") == expected
    assert load(stored.artifact_hash) == payload
    assert _sha256_hex(stored.json_path.read_bytes()) == stored.artifact_hash
    assert seen == [pdf.resolve()]

    stored_again = load_or_convert(pdf)

    assert stored_again.artifact_hash == stored.artifact_hash
    assert seen == [pdf.resolve()]
    assert doclang_path.read_text(encoding="utf-8") == expected


def test_cached_json_gains_doclang_without_reconvert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from docling_core.types.doc.document import DoclingDocument

    document = DoclingDocument(name="cached")
    payload = document.export_to_dict()
    expected = document.export_to_doclang()
    raw = _canonical_json_bytes(payload)
    digest = _sha256_hex(raw)
    pdf = tmp_path / "cached.pdf"
    pdf.write_bytes(b"%PDF-1.4 cached")
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    json_path = artifacts / f"{digest}.json"
    json_path.write_bytes(raw)
    pdf_sha = _sha256_hex(pdf.read_bytes())
    (artifacts / "manifest.json").write_text(
        json.dumps({pdf_sha: digest}),
        encoding="utf-8",
    )
    _use_artifacts(monkeypatch, artifacts)

    def boom(source: Path) -> dict:
        raise AssertionError(f"reconvert of {source}")

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", boom)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", boom)

    stored = load_or_convert(pdf)

    doclang_path = json_path.with_suffix(".dclg")
    assert stored.json_path == json_path
    assert doclang_path.is_file()
    assert doclang_path.read_text(encoding="utf-8") == expected
    assert load(digest) == payload


def test_load_or_convert_rejects_non_path(tmp_path: Path) -> None:
    with pytest.raises(IngestError):
        load_or_convert("https://example.invalid/file.pdf")  # type: ignore[arg-type]
    with pytest.raises(IngestError):
        load_or_convert(tmp_path / "missing.pdf")


def test_ingest_sources_forbid_url_httpsource_and_docling_graph() -> None:
    sources = sorted(INGEST_ROOT.glob("*.py"))
    assert [path.name for path in sources] == [
        "__init__.py",
        "classify.py",
        "extract.py",
        "parse.py",
        "store.py",
        "types.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in sources)
    for token in FORBIDDEN_SOURCE_TOKENS:
        assert token not in combined

    parse_source = (INGEST_ROOT / "parse.py").read_text(encoding="utf-8")
    tree = ast.parse(parse_source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert any(name == "docling" or name.startswith("docling.") for name in imported | imported_from)
    assert not any("graph" in name for name in imported | imported_from)
    assert "DocumentConverter" in parse_source
    assert "do_ocr=False" in parse_source or "do_ocr = False" in parse_source
    assert "artifacts_path" in parse_source
    assert "2.130.0" in parse_source


def test_default_artifact_root_is_repo_docling_dir() -> None:
    assert artifacts_dir() == REPO_ROOT / "artifacts" / "docling"


def test_convert_pdf_rejects_non_path() -> None:
    with pytest.raises(IngestError):
        convert_pdf("https://example.invalid/file.pdf")  # type: ignore[arg-type]


def test_strip_page_pixels_keeps_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.ingest.store import canonical_json_bytes, strip_page_pixels

    dirty = {
        "name": "synthetic",
        "pages": {
            "1": {
                "image": {"uri": "data:image/png;base64,iVBORw0KGgo=", "width": 4},
                "size": {"width": 10, "height": 10},
            }
        },
        "pictures": [
            {"uri": "data:image/png;base64,QUJDRA==", "label": "mark"},
            "data:image/jpeg;base64,/9j/",
        ],
    }
    other = {
        "pages": {
            "2": {
                "image": {"uri": "data:image/png;base64,OTHER"},
                "size": {"width": 3, "height": 5},
            }
        },
        "scan": {"uri": "data:image/gif;base64,R0lG"},
    }
    clean = {
        "name": "synthetic",
        "pages": {"1": {"size": {"width": 10, "height": 10}}},
        "pictures": [{"label": "mark"}],
    }
    other_clean = {
        "pages": {"2": {"size": {"width": 3, "height": 5}}},
        "scan": {},
    }

    stripped = strip_page_pixels(dirty)
    stripped_other = strip_page_pixels(other)

    assert "image" not in stripped["pages"]["1"]
    assert stripped["pages"]["1"]["size"] == {"width": 10, "height": 10}
    assert "data:image" not in json.dumps(stripped)
    assert "data:image" not in json.dumps(stripped_other)
    assert "image" not in stripped_other["pages"]["2"]
    digest = _sha256_hex(canonical_json_bytes(stripped))
    assert digest == _sha256_hex(canonical_json_bytes(clean))
    assert digest == _sha256_hex(_canonical_json_bytes(clean))
    assert digest != _sha256_hex(canonical_json_bytes(dirty))
    assert _sha256_hex(canonical_json_bytes(stripped_other)) == _sha256_hex(
        canonical_json_bytes(other_clean)
    )
    assert dirty["pages"]["1"]["image"]["uri"].startswith("data:image")

    pdf = tmp_path / "pixels.pdf"
    pdf.write_bytes(b"%PDF-1.4 synthetic")
    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)

    def fake_convert(source: Path) -> dict:
        assert isinstance(source, Path)
        return dirty

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)
    monkeypatch.setattr(
        "claimledger.ingest.store.doclang_from_payload",
        lambda payload: "synthetic-doclang",
    )

    stored = load_or_convert(pdf)

    assert stored.artifact_hash == digest
    on_disk = stored.json_path.read_bytes()
    assert _sha256_hex(on_disk) == digest
    assert on_disk == canonical_json_bytes(clean)
    assert "data:image" not in on_disk.decode("utf-8")
    assert load(stored.artifact_hash) == clean


def test_partial_success_is_not_exported() -> None:
    from types import SimpleNamespace

    from claimledger.ingest.parse import _export_complete

    partial = SimpleNamespace(
        status=SimpleNamespace(name="PARTIAL_SUCCESS", value="partial_success"),
        document=SimpleNamespace(export_to_dict=lambda: {"pages": []}),
    )
    with pytest.raises(IngestError, match="success"):
        _export_complete(partial)

    complete = SimpleNamespace(
        status=SimpleNamespace(name="SUCCESS", value="success"),
        document=SimpleNamespace(export_to_dict=lambda: {"pages": [{"ok": True}]}),
    )
    assert _export_complete(complete) == {"pages": [{"ok": True}]}

    parse_source = (INGEST_ROOT / "parse.py").read_text(encoding="utf-8")
    assert "return _export_complete(result)" in parse_source


def test_sidecar_png_does_not_move_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import claimledger.ingest.parse as parse
    from claimledger.ingest.store import canonical_json_bytes

    png_one = b"\x89PNG\r\n\x1a\npage-one"
    png_two = b"\x89PNG\r\n\x1a\npage-two"
    same = {"kind": "sidecar", "pages": {"1": {"size": {"width": 2, "height": 2}}}}
    empty_payload = {"kind": "no-sidecar"}
    page_pngs: dict[int, bytes] = {}
    monkeypatch.setattr(parse, "last_page_pngs", page_pngs, raising=False)

    artifacts = tmp_path / "docling"
    _use_artifacts(monkeypatch, artifacts)
    monkeypatch.setattr(
        "claimledger.ingest.store.doclang_from_payload",
        lambda payload: "synthetic-doclang",
    )

    def fake_convert(source: Path) -> dict:
        assert isinstance(source, Path)
        assert source.is_file()
        page_pngs.clear()
        if source.name == "with-pages.bin":
            page_pngs[1] = png_one
            page_pngs[2] = png_two
            return same
        return empty_payload

    monkeypatch.setattr("claimledger.ingest.parse.convert_pdf", fake_convert)
    monkeypatch.setattr("claimledger.ingest.store.convert_pdf", fake_convert)

    with_pages = tmp_path / "with-pages.bin"
    with_pages.write_bytes(b"synthetic-pages")
    without_pages = tmp_path / "without-pages.bin"
    without_pages.write_bytes(b"synthetic-empty")

    stored = load_or_convert(with_pages)
    expected = _sha256_hex(canonical_json_bytes(same))
    on_disk = stored.json_path.read_bytes()
    assert stored.artifact_hash == expected
    assert _sha256_hex(on_disk) == expected
    assert on_disk == canonical_json_bytes(same)
    assert png_one not in on_disk
    assert png_two not in on_disk
    assert load(stored.artifact_hash) == same

    stored_empty = load_or_convert(without_pages)
    empty_hash = _sha256_hex(canonical_json_bytes(empty_payload))
    assert stored_empty.artifact_hash == empty_hash
    assert stored_empty.artifact_hash != stored.artifact_hash
    assert list(artifacts.glob(f"{stored_empty.artifact_hash}.p*.png")) == []

    sidecar_one = artifacts / f"{stored.artifact_hash}.p1.png"
    sidecar_two = artifacts / f"{stored.artifact_hash}.p2.png"
    parse_source = (INGEST_ROOT / "parse.py").read_text(encoding="utf-8")
    problems: list[str] = []
    if not sidecar_one.is_file():
        problems.append("missing sidecar file")
    if "generate_page_images = True" not in parse_source:
        problems.append("missing generate_page_images flag")
    assert problems == [], problems

    assert sidecar_one.read_bytes() == png_one
    assert sidecar_two.is_file()
    assert sidecar_two.read_bytes() == png_two
    scale_lines = [
        line.strip()
        for line in parse_source.splitlines()
        if "images_scale" in line and not line.strip().startswith("#")
    ]
    assert scale_lines == [] or scale_lines == ["options.images_scale = 1.0"]
    assert "pil_image" in parse_source
    assert "last_page_pngs" in parse_source
    assert "strip_page_pixels" in parse_source
    assert 'PINNED_DOCLING = "2.130.0"' in parse_source
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "artifacts/docling/*.png" in gitignore


def test_page_images_capture_uses_pil_image() -> None:
    from types import SimpleNamespace

    import claimledger.ingest.parse as parse
    from claimledger.ingest.parse import _export_complete

    captured = b"\x89PNG\r\n\x1a\nfrom-pil"

    class _Image:
        def save(self, buffer: object, format: str) -> None:
            assert format == "PNG"
            buffer.write(captured)  # type: ignore[attr-defined]

    document = SimpleNamespace(
        pages={
            1: SimpleNamespace(image=SimpleNamespace(pil_image=_Image())),
            3: SimpleNamespace(image=None),
        },
        export_to_dict=lambda: {
            "pages": {
                "1": {"image": {"uri": "data:image/png;base64,AAAA"}, "size": 1},
                "3": {"size": 3},
            }
        },
    )
    result = SimpleNamespace(
        status=SimpleNamespace(value="success"),
        document=document,
    )

    payload = _export_complete(result)

    assert payload == {"pages": {"1": {"size": 1}, "3": {"size": 3}}}
    assert "data:image" not in json.dumps(payload)
    assert parse.last_page_pngs == {1: captured}
