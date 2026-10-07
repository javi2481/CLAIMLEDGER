"""Extras and CI matrix for import-free book vs convert httpx."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _optional_deps(pyproject: str) -> dict[str, list[str]]:
    extras: dict[str, list[str]] = {}
    current: str | None = None
    in_optional = False
    for line in pyproject.splitlines():
        if line.strip() == "[project.optional-dependencies]":
            in_optional = True
            continue
        if in_optional and line.startswith("["):
            break
        if not in_optional:
            continue
        match = re.match(r"^([A-Za-z0-9_-]+)\s*=\s*\[", line)
        if match:
            current = match.group(1)
            extras[current] = []
            continue
        if current is None:
            continue
        pkg = re.match(r'\s*"([^"]+)"', line)
        if pkg:
            extras[current].append(pkg.group(1))
    return extras


def test_ingest_extra_owns_httpx_not_docling() -> None:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    extras = _optional_deps(text)
    assert "ingest" in extras
    assert extras["ingest"] == ["httpx==0.28.1"]
    assert "httpx==0.28.1" not in extras.get("docling", [])
    assert "docling==2.130.0" in extras["docling"]
    assert "docling-graph==1.9.1" in extras["docling"]
    assert "httpx==0.28.1" in extras.get("deepseek", [])


def test_pytest_workflow_extras_matrix() -> None:
    text = (REPO / ".github" / "workflows" / "pytest.yml").read_text(encoding="utf-8")
    assert "--extra dev" in text
    assert "--extra http" in text
    assert "--extra ingest" in text
    assert "--extra docling" in text
    assert "--extra retrieval" in text
    # Product job must not pull Docling; heavy job lists ingest for convert mocks.
    product = text.split("Product tests without Docling")[1].split(
        "Ingest, graph, and retrieval"
    )[0]
    heavy = text.split("Ingest, graph, and retrieval")[1]
    assert "--extra docling" not in product
    assert "--extra ingest" not in product
    assert "--extra ingest" in heavy
    assert "--extra docling" in heavy
    assert "tests/ingest" in heavy
    assert "--all-extras" not in text
