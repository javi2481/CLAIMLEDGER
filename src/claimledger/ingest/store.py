"""Canonical JSON hash store. Load by hash; convert a local file on miss."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from claimledger.ingest.parse import convert_local
from claimledger.ingest.types import ConvertBundle, IngestError, StoredDocument

_REPO_ROOT = Path(__file__).resolve().parents[3]


def artifacts_dir() -> Path:
    return _REPO_ROOT / "artifacts" / "docling"


def page_sidecar(artifact_hash: str, page_no: int) -> Path:
    return artifacts_dir() / f"{artifact_hash}.p{page_no}.png"


def canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _without_data_image_uris(node: object) -> object:
    if isinstance(node, dict):
        cleaned: dict = {}
        for key, value in node.items():
            if isinstance(value, str) and value.startswith("data:image"):
                continue
            cleaned[key] = _without_data_image_uris(value)
        return cleaned
    if isinstance(node, list):
        cleaned_list: list = []
        for value in node:
            if isinstance(value, str) and value.startswith("data:image"):
                continue
            cleaned_list.append(_without_data_image_uris(value))
        return cleaned_list
    return node


def strip_page_pixels(payload: dict) -> dict:
    cleaned = copy.deepcopy(payload)
    pages = cleaned.get("pages")
    if isinstance(pages, dict):
        for page in pages.values():
            if isinstance(page, dict):
                page.pop("image", None)
    stripped = _without_data_image_uris(cleaned)
    if not isinstance(stripped, dict):
        raise IngestError("artifact JSON must be an object")
    return stripped


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _manifest_path(root: Path) -> Path:
    return root / "manifest.json"


def _read_manifest(root: Path) -> dict[str, str]:
    path = _manifest_path(root)
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise IngestError("manifest must map pdf sha256 to artifact hash")
    mapping: dict[str, str] = {}
    for pdf_sha, artifact_hash in payload.items():
        if not isinstance(pdf_sha, str) or not isinstance(artifact_hash, str):
            raise IngestError("manifest must map pdf sha256 to artifact hash")
        mapping[pdf_sha] = artifact_hash
    return mapping


def _write_manifest(root: Path, manifest: dict[str, str]) -> None:
    _manifest_path(root).write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _doclang_path(json_path: Path) -> Path:
    return json_path.with_suffix(".dclg")


def _write_page_sidecars(artifact_hash: str, page_pngs: dict[int, bytes]) -> None:
    for page_no, png in page_pngs.items():
        page_sidecar(artifact_hash, int(page_no)).write_bytes(png)


def _persist_bundle(
    root: Path,
    resolved: Path,
    pdf_sha: str,
    manifest: dict[str, str],
    bundle: ConvertBundle,
) -> StoredDocument:
    payload = strip_page_pixels(bundle.payload)
    raw = canonical_json_bytes(payload)
    artifact_hash = _sha256_hex(raw)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{artifact_hash}.json"
    json_path.write_bytes(raw)
    _doclang_path(json_path).write_text(bundle.doclang, encoding="utf-8")
    _write_page_sidecars(artifact_hash, bundle.page_pngs)
    manifest[pdf_sha] = artifact_hash
    _write_manifest(root, manifest)
    return StoredDocument(
        artifact_hash=artifact_hash,
        json_path=json_path,
        source_pdf=resolved,
    )


def load(artifact_hash: str) -> dict:
    path = artifacts_dir() / f"{artifact_hash}.json"
    if not path.is_file():
        raise IngestError(f"missing artifact {artifact_hash}")
    raw = path.read_bytes()
    if _sha256_hex(raw) != artifact_hash:
        raise IngestError(f"artifact hash does not match {artifact_hash}")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise IngestError("artifact JSON must be an object")
    return payload


def load_or_convert(pdf: Path) -> StoredDocument:
    if not isinstance(pdf, Path):
        raise IngestError("source must be a local file path")
    if not pdf.is_file():
        raise IngestError("source must be a local file path")
    resolved = pdf.resolve()
    pdf_sha = _sha256_hex(resolved.read_bytes())
    root = artifacts_dir()
    manifest = _read_manifest(root)
    artifact_hash = manifest.get(pdf_sha)
    if artifact_hash:
        json_path = root / f"{artifact_hash}.json"
        if json_path.is_file() and _doclang_path(json_path).is_file():
            load(artifact_hash)
            return StoredDocument(
                artifact_hash=artifact_hash,
                json_path=json_path,
                source_pdf=resolved,
            )
        if json_path.is_file() and not _doclang_path(json_path).is_file():
            # Integrity check before recompile; mismatch must not convert.
            load(artifact_hash)
    bundle = convert_local(resolved)
    return _persist_bundle(root, resolved, pdf_sha, manifest, bundle)
