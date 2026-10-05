"""Classify every corpus PDF. Filename and pack only. No claim extraction."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, fields
from pathlib import Path

import pytest

from claimledger.identity import identity_key
from claimledger.ingest.classify import DocumentClass, classify
from claimledger.ingest.types import StoredDocument

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS = REPO_ROOT / "docs" / "archivos_muestra"
GOLD_NET_INCOME_FIGURE = "21262335"
NON_EEFF_KINDS = frozenset({"comunicado", "deck", "memoria", "transcript"})

EXPECTED: dict[str, DocumentClass] = {
    "BYMA_-_EEFF_31-03-2026_VF.pdf": DocumentClass(
        kind="eeff",
        issuer="BYMA",
        period="2026-03-31",
    ),
    "BYMA - EEFF 30-06-2026.pdf": DocumentClass(
        kind="eeff",
        issuer="BYMA",
        period="2026-06-30",
    ),
    "BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf": DocumentClass(
        kind="comunicado",
        issuer="BYMA",
        period=None,
    ),
    "BYMA-Comunicado_de_Prensa-2T26.pdf": DocumentClass(
        kind="comunicado",
        issuer="BYMA",
        period=None,
    ),
    "Presentación_de_resultados_BYMA-1T26.pdf": DocumentClass(
        kind="deck",
        issuer="BYMA",
        period=None,
    ),
    "Presentacion_de_resultados_BYMA-2T26.pdf": DocumentClass(
        kind="deck",
        issuer="BYMA",
        period=None,
    ),
    "BYMA_2T26_Transcripcion_Resultados_ES.pdf": DocumentClass(
        kind="transcript",
        issuer="BYMA",
        period=None,
    ),
    "Memoria-BYMA-y-EEFF-al-31-12-2023.pdf": DocumentClass(
        kind="memoria",
        issuer="BYMA",
        period=None,
    ),
    "BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf": DocumentClass(
        kind="memoria",
        issuer="BYMA",
        period=None,
    ),
    "BYMA-MEMORIA_2025.pdf": DocumentClass(
        kind="memoria",
        issuer="BYMA",
        period=None,
    ),
}


def _stored(tmp_path: Path, pdf: Path, text: str) -> StoredDocument:
    raw = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    json_path = tmp_path / f"{digest}.json"
    json_path.write_bytes(raw)
    return StoredDocument(
        artifact_hash=digest,
        json_path=json_path,
        source_pdf=pdf.resolve(),
    )


def _pnl_identity_key(document: DocumentClass) -> str | None:
    if document.kind != "eeff" or document.period is None:
        return None
    return identity_key(
        document.issuer,
        document.period,
        "income_statement",
        "consolidated",
        "net_income",
    )


def test_corpus_lists_the_ten_sample_pdfs() -> None:
    names = sorted(path.name for path in CORPUS.glob("*.pdf"))
    assert names == sorted(EXPECTED)
    assert len(names) == 10


@pytest.mark.parametrize("filename", sorted(EXPECTED))
def test_every_corpus_pdf_is_classified(filename: str, tmp_path: Path) -> None:
    pdf = CORPUS / filename
    assert pdf.is_file()
    stored = _stored(tmp_path, pdf, text=GOLD_NET_INCOME_FIGURE)
    result = classify(pdf, stored)

    assert result == EXPECTED[filename]
    assert [field.name for field in fields(result)] == ["kind", "issuer", "period"]


def test_quarterly_eeff_periods_differ(tmp_path: Path) -> None:
    first_name = "BYMA_-_EEFF_31-03-2026_VF.pdf"
    second_name = "BYMA - EEFF 30-06-2026.pdf"
    first_pdf = CORPUS / first_name
    second_pdf = CORPUS / second_name
    first = classify(first_pdf, _stored(tmp_path, first_pdf, text=""))
    second = classify(second_pdf, _stored(tmp_path, second_pdf, text=""))

    assert first == DocumentClass(kind="eeff", issuer="BYMA", period="2026-03-31")
    assert second == DocumentClass(kind="eeff", issuer="BYMA", period="2026-06-30")
    assert first.period != second.period


def test_eight_non_eeff_mint_zero_pnl_identities(tmp_path: Path) -> None:
    non_eeff = [name for name, document in EXPECTED.items() if document.kind != "eeff"]
    assert len(non_eeff) == 8

    for filename in non_eeff:
        pdf = CORPUS / filename
        stored = _stored(tmp_path, pdf, text=GOLD_NET_INCOME_FIGURE)
        result = classify(pdf, stored)

        assert result.kind in NON_EEFF_KINDS
        assert result.period is None
        assert _pnl_identity_key(result) is None
        assert GOLD_NET_INCOME_FIGURE not in json.dumps(asdict(result))


def test_comunicado_repeating_21262335_is_not_an_identity(tmp_path: Path) -> None:
    filename = "BYMA_Comunicado_de_Prensa-Resultados-1T26.pdf"
    pdf = CORPUS / filename
    stored = _stored(
        tmp_path,
        pdf,
        text="Resultado neto del período 21.262.335 (21262335)",
    )
    payload = stored.json_path.read_text(encoding="utf-8")
    assert GOLD_NET_INCOME_FIGURE in payload

    result = classify(pdf, stored)

    assert result == DocumentClass(kind="comunicado", issuer="BYMA", period=None)
    assert _pnl_identity_key(result) is None
    assert GOLD_NET_INCOME_FIGURE not in json.dumps(asdict(result), ensure_ascii=False)


def test_second_comunicado_keeps_the_same_non_identity(tmp_path: Path) -> None:
    filename = "BYMA-Comunicado_de_Prensa-2T26.pdf"
    pdf = CORPUS / filename
    stored = _stored(tmp_path, pdf, text=GOLD_NET_INCOME_FIGURE)
    assert GOLD_NET_INCOME_FIGURE in stored.json_path.read_text(encoding="utf-8")

    result = classify(pdf, stored)

    assert result == DocumentClass(kind="comunicado", issuer="BYMA", period=None)
    assert _pnl_identity_key(result) is None


def test_memoria_filename_containing_eeff_stays_memoria(tmp_path: Path) -> None:
    filename = "BYMA-MEMORIA_2024_y_EEFF_31-12-2024.pdf"
    pdf = CORPUS / filename
    stored = _stored(tmp_path, pdf, text=GOLD_NET_INCOME_FIGURE)

    result = classify(pdf, stored)

    assert "EEFF" in pdf.name
    assert result == DocumentClass(kind="memoria", issuer="BYMA", period=None)
    assert _pnl_identity_key(result) is None
