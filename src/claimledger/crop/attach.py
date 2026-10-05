"""Attach a page crop when extract matches the verified claim."""

from __future__ import annotations

import base64
from pathlib import Path

from claimledger.claim import FinancialClaim
from claimledger.crop.cut import crop_bbox
from claimledger.ingest import store as ingest_store
from claimledger.ingest.classify import DocumentClass
from claimledger.ingest.extract import extract_recipe
from claimledger.ingest.types import StoredDocument
from claimledger.query import QueryResult


def attach(artifact_hash: str, result: QueryResult) -> tuple[str, ...]:
    if result.status != "verified":
        return ()
    pictures: list[str] = []
    for claim in result.claims:
        picture = _picture(artifact_hash, claim)
        if picture is not None:
            pictures.append(picture)
    return tuple(pictures)


def _picture(artifact_hash: str, claim: FinancialClaim) -> str | None:
    json_path = ingest_store.artifacts_dir() / f"{artifact_hash}.json"
    if not json_path.is_file():
        return None
    stored = StoredDocument(
        artifact_hash=artifact_hash,
        json_path=json_path,
        source_pdf=json_path.with_suffix(".pdf"),
    )
    extracted = extract_recipe(
        stored,
        DocumentClass(kind="eeff", issuer=claim.issuer, period=claim.period),
    )
    for item in extracted:
        if item.identity_key != claim.identity_key or item.value != claim.value:
            continue
        if not item.evidence:
            return None
        evidence = item.evidence[0]
        sidecar = ingest_store.page_sidecar(artifact_hash, evidence.page)
        if not sidecar.is_file():
            return None
        png = _crop_sidecar(sidecar, evidence.bbox)
        if png is None:
            return None
        encoded = base64.b64encode(png).decode("ascii")
        return f"![crop](data:image/png;base64,{encoded})"
    return None


def _crop_sidecar(
    path: Path,
    bbox: tuple[float, float, float, float] | None,
) -> bytes | None:
    from io import BytesIO

    from PIL import Image

    with Image.open(BytesIO(path.read_bytes())) as image:
        rgb = image.convert("RGB")
        return crop_bbox(rgb.tobytes(), rgb.width, rgb.height, bbox)
