"""Fase 0 kernel identity tests. Slice 1: imports and unused pins only."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

KERNEL_MODULES = (
    "claimledger.identity",
    "claimledger.digits",
    "claimledger.evidence",
    "claimledger.claim",
    "claimledger.ledger",
    "claimledger.lookup",
    "claimledger.query",
)

FORBIDDEN_IMPORT_ROOTS = frozenset({"docling", "docling_graph"})
DECLARED_PINS = (
    "docling==2.130.0",
    "docling-graph==1.9.1",
)


def _imported_forbidden_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_IMPORT_ROOTS:
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root in FORBIDDEN_IMPORT_ROOTS:
                found.add(node.module)
    return found


def test_kernel_modules_importable() -> None:
    imported = [importlib.import_module(name) for name in KERNEL_MODULES]
    assert [module.__name__ for module in imported] == list(KERNEL_MODULES)
    assert "docling" not in sys.modules
    assert "docling_graph" not in sys.modules


def test_pins_declared_but_unused() -> None:
    pyproject = REPO_ROOT / "pyproject.toml"
    assert pyproject.is_file()
    text = pyproject.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in text
    assert "pytest" in text
    for pin in DECLARED_PINS:
        assert pin in text

    scanned = list((REPO_ROOT / "tests").glob("*.py"))
    scanned.extend((REPO_ROOT / "src" / "claimledger").glob("*.py"))
    assert {path.name for path in scanned} >= {
        "test_identity.py",
        "identity.py",
        "digits.py",
        "evidence.py",
        "claim.py",
        "ledger.py",
        "lookup.py",
        "query.py",
    }
    forbidden: dict[str, set[str]] = {}
    for path in scanned:
        found = _imported_forbidden_modules(path)
        if found:
            forbidden[str(path.relative_to(REPO_ROOT))] = found
    assert forbidden == {}
