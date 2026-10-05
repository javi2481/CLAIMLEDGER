"""Fase 0 kernel identity tests. Slices 1–2 identity; slice 3 claim/evidence."""

from __future__ import annotations

import ast
import importlib
import json
import sys
import types
from pathlib import Path

import pytest

from claimledger.claim import ClaimError, FinancialClaim, validate_claim
from claimledger.digits import digits_ars, signed_ars
from claimledger.evidence import EvidenceError, FinancialEvidence, validate_evidence
from claimledger.identity import apply_alias, fold, identity_key, normalize_period

REPO_ROOT = Path(__file__).resolve().parents[1]

CANONICAL_CONSOLIDATED = "BYMA|2026-03-31|income_statement|consolidated|net_income"
CANONICAL_PARENT = "BYMA|2026-03-31|income_statement|parent_attributable|net_income"

PERIOD_1T26_TOKENS = (
    "1t26",
    "1t 26",
    "marzo",
    "2026-03-31",
    "31 de marzo",
    "primer trimestre",
)
PERIOD_2T26_TOKENS = (
    "2t26",
    "2t 26",
    "junio",
    "2026-06-30",
    "30 de junio",
    "segundo trimestre",
)

ALIAS_TABLE = {
    "consolidado|resultado_neto": ("income_statement", "consolidated", "net_income"),
    "controlante|resultado_atribuible_controladora": (
        "income_statement",
        "parent_attributable",
        "net_income",
    ),
    "consolidado|resultado_bruto": ("income_statement", "consolidated", "gross_profit"),
    "consolidado|resultado_operativo": (
        "income_statement",
        "consolidated",
        "operating_income",
    ),
    "consolidado|resultado_antes_impuesto": (
        "income_statement",
        "consolidated",
        "income_before_tax",
    ),
    "consolidado|impuesto_ganancias": ("income_statement", "consolidated", "income_tax"),
    "consolidado|resultado_no_controlante": (
        "income_statement",
        "consolidated",
        "nci_income",
    ),
}

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


def _kernel_scan_paths() -> list[Path]:
    relatives = (
        "src/claimledger/identity.py",
        "src/claimledger/digits.py",
        "src/claimledger/evidence.py",
        "src/claimledger/claim.py",
        "src/claimledger/ledger.py",
        "src/claimledger/lookup.py",
        "src/claimledger/query.py",
        "tests/test_identity.py",
        "tests/test_ledger.py",
        "tests/test_lookup.py",
        "tests/test_query.py",
        "tests/test_gold_v1.py",
        "tests/test_gold_v2.py",
    )
    return [REPO_ROOT / relative for relative in relatives]


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


_IMPORT_SNAPSHOT_NAMES = ("docling", "docling_graph")


def _import_snapshot() -> frozenset[str]:
    return frozenset(name for name in _IMPORT_SNAPSHOT_NAMES if name in sys.modules)


def test_kernel_modules_importable() -> None:
    previous = {name: sys.modules.get(name) for name in _IMPORT_SNAPSHOT_NAMES}
    for name in _IMPORT_SNAPSHOT_NAMES:
        sys.modules[name] = types.ModuleType(name)
    before = _import_snapshot()
    try:
        imported = [importlib.import_module(name) for name in KERNEL_MODULES]
        assert [module.__name__ for module in imported] == list(KERNEL_MODULES)
        assert _import_snapshot() - before == frozenset()
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def test_pins_declared_but_unused() -> None:
    pyproject = REPO_ROOT / "pyproject.toml"
    assert pyproject.is_file()
    text = pyproject.read_text(encoding="utf-8")
    assert 'requires-python = ">=3.11"' in text
    assert "pytest" in text
    for pin in DECLARED_PINS:
        assert pin in text

    scanned = _kernel_scan_paths()
    assert all(path.is_file() for path in scanned)
    assert {path.relative_to(REPO_ROOT).as_posix() for path in scanned} == {
        "src/claimledger/identity.py",
        "src/claimledger/digits.py",
        "src/claimledger/evidence.py",
        "src/claimledger/claim.py",
        "src/claimledger/ledger.py",
        "src/claimledger/lookup.py",
        "src/claimledger/query.py",
        "tests/test_identity.py",
        "tests/test_ledger.py",
        "tests/test_lookup.py",
        "tests/test_query.py",
        "tests/test_gold_v1.py",
        "tests/test_gold_v2.py",
    }
    forbidden: dict[str, set[str]] = {}
    for path in scanned:
        found = _imported_forbidden_modules(path)
        if found:
            forbidden[str(path.relative_to(REPO_ROOT))] = found
    assert forbidden == {}


def test_graph_init_outside_kernel_allowlist() -> None:
    graph_init = REPO_ROOT / "src/claimledger/graph/__init__.py"
    assert graph_init.is_file()
    assert _imported_forbidden_modules(graph_init) == set()
    allowlist = {path.relative_to(REPO_ROOT).as_posix() for path in _kernel_scan_paths()}
    assert graph_init.relative_to(REPO_ROOT).as_posix() not in allowlist
    assert len(allowlist) == 13


def _llama_index_modules() -> set[str]:
    return {
        name
        for name in sys.modules
        if name == "llama_index" or name.startswith("llama_index.")
    }


def test_retrieval_init_outside_kernel_allowlist() -> None:
    retrieval_init = REPO_ROOT / "src/claimledger/retrieval/__init__.py"
    assert retrieval_init.is_file()
    assert _imported_forbidden_modules(retrieval_init) == set()
    tree = ast.parse(retrieval_init.read_text(encoding="utf-8"), filename=str(retrieval_init))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert "llama_index" not in imported_roots
    assert FORBIDDEN_IMPORT_ROOTS == frozenset({"docling", "docling_graph"})
    allowlist = {path.relative_to(REPO_ROOT).as_posix() for path in _kernel_scan_paths()}
    assert retrieval_init.relative_to(REPO_ROOT).as_posix() not in allowlist
    assert "src/claimledger/retrieval/__init__.py" not in allowlist
    assert len(allowlist) == 13
    before = _llama_index_modules()
    imported = [importlib.import_module(name) for name in KERNEL_MODULES]
    assert [module.__name__ for module in imported] == list(KERNEL_MODULES)
    assert _llama_index_modules() - before == set()


def _imports_llama_index(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] == "llama_index" for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] == "llama_index":
                return True
    return False


def test_ingest_and_kernel_tests_omit_llama_index() -> None:
    ingest = sorted((REPO_ROOT / "src/claimledger/ingest").glob("*.py"))
    kernel_tests = [
        REPO_ROOT / "tests" / name
        for name in (
            "test_identity.py",
            "test_ledger.py",
            "test_lookup.py",
            "test_query.py",
            "test_gold_v1.py",
            "test_gold_v2.py",
        )
    ]
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in (*ingest, *kernel_tests)
        if _imports_llama_index(path)
    ]
    assert offenders == []


def test_identity_key_neighbor_consolidated_excludes_value() -> None:
    key = identity_key(
        "BYMA", "2026-03-31", "income_statement", "consolidated", "net_income"
    )
    assert key == CANONICAL_CONSOLIDATED
    assert "21262335" not in key


def test_identity_key_neighbor_parent_is_distinct() -> None:
    consolidated = identity_key(
        "BYMA", "2026-03-31", "income_statement", "consolidated", "net_income"
    )
    parent = identity_key(
        "BYMA", "2026-03-31", "income_statement", "parent_attributable", "net_income"
    )
    assert parent == CANONICAL_PARENT
    assert consolidated != parent
    assert "21259769" not in parent
    assert "21262335" not in consolidated


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1T26", "1t26"),
        ("1T 26", "1t 26"),
        ("PRIMER TRIMESTRE", "primer trimestre"),
        ("período", "periodo"),
        ("MARZO", "marzo"),
        ("2T26", "2t26"),
    ],
)
def test_fold_lowercases_and_strips_accents(raw: str, expected: str) -> None:
    assert fold(raw) == expected


@pytest.mark.parametrize("token", PERIOD_1T26_TOKENS)
def test_normalize_period_1t26_tokens(token: str) -> None:
    assert normalize_period(token) == "2026-03-31"
    assert normalize_period(token.upper()) == "2026-03-31"


@pytest.mark.parametrize("token", PERIOD_2T26_TOKENS)
def test_normalize_period_2t26_tokens(token: str) -> None:
    assert normalize_period(token) == "2026-06-30"
    assert normalize_period(token.upper()) == "2026-06-30"


def test_digits_ars_collapses_thousand_dots() -> None:
    assert digits_ars("21.262.335") == "21262335"
    assert digits_ars("81.956.525") == "81956525"


def test_digits_ars_empty_or_none_is_none() -> None:
    assert digits_ars("") is None
    assert digits_ars(None) is None
    assert digits_ars("   ") is None


def test_digits_ars_compact_millions_is_not_neighbor() -> None:
    # Slice 3 rejects compact form at claim level. Slice 2: not neighbor digits.
    assert digits_ars("21,26 M") != "21262335"
    assert digits_ars("8,19 M") != "81956525"


def test_signed_ars_parentheses_are_negative() -> None:
    assert signed_ars("(14.950.948)") == "-14950948"
    assert signed_ars("(32.731.536)") == "-32731536"


def test_signed_ars_empty_or_none_is_none() -> None:
    assert signed_ars("") is None
    assert signed_ars(None) is None


def test_aliases_table_is_one_to_one() -> None:
    path = REPO_ROOT / "evals" / "aliases.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(rows, list)
    assert len(rows) == 7
    mapped = {row["v1"]: (row["statement"], row["scope"], row["metric"]) for row in rows}
    assert mapped == ALIAS_TABLE
    assert len(mapped) == 7


def test_apply_alias_consolidado_neto_is_canonical_neighbor() -> None:
    statement, scope, metric = apply_alias("consolidado|resultado_neto")
    key = identity_key("BYMA", "2026-03-31", statement, scope, metric)
    assert key == CANONICAL_CONSOLIDATED


def test_apply_alias_controlante_is_parent_neighbor() -> None:
    statement, scope, metric = apply_alias(
        "controlante|resultado_atribuible_controladora"
    )
    key = identity_key("BYMA", "2026-03-31", statement, scope, metric)
    assert key == CANONICAL_PARENT


def _evidence(**overrides: object) -> FinancialEvidence:
    fields = {
        "document_id": "byma-eeff-1t26",
        "artifact_hash": "",
        "page": 4,
        "text": "RESULTADO NETO DEL PERÍODO",
        "label": "net_income",
        "bbox": None,
    }
    fields.update(overrides)
    return FinancialEvidence(**fields)  # type: ignore[arg-type]


def _claim(**overrides: object) -> FinancialClaim:
    fields = {
        "identity_key": CANONICAL_CONSOLIDATED,
        "issuer": "BYMA",
        "period": "2026-03-31",
        "statement": "income_statement",
        "scope": "consolidated",
        "metric": "net_income",
        "value": "21262335",
        "currency": "ARS",
        "unit": None,
        "evidence": (),
        "ledger_status": "recorded",
    }
    fields.update(overrides)
    return FinancialClaim(**fields)  # type: ignore[arg-type]


def test_claim_consistent_key_constructs() -> None:
    claim = _claim()
    assert claim.identity_key == CANONICAL_CONSOLIDATED
    assert claim.issuer == "BYMA"
    assert claim.period == "2026-03-31"
    assert claim.statement == "income_statement"
    assert claim.scope == "consolidated"
    assert claim.metric == "net_income"
    assert claim.value == "21262335"
    assert claim.currency == "ARS"
    assert claim.unit is None
    assert claim.ledger_status == "recorded"
    validate_claim(claim)


def test_claim_parent_neighbor_is_distinct_identity() -> None:
    claim = _claim(
        identity_key=CANONICAL_PARENT,
        scope="parent_attributable",
        value="21259769",
    )
    assert claim.identity_key == CANONICAL_PARENT
    assert claim.identity_key != CANONICAL_CONSOLIDATED
    assert claim.value == "21259769"
    assert "21262335" not in claim.identity_key


def test_claim_inconsistent_key_is_rejected() -> None:
    with pytest.raises(ClaimError, match="identity_key"):
        _claim(identity_key=CANONICAL_PARENT)
    with pytest.raises(ClaimError, match="identity_key"):
        _claim(identity_key="OTHER|2026-03-31|income_statement|consolidated|net_income")


def test_claim_has_no_verification_status() -> None:
    claim = _claim()
    assert not hasattr(claim, "verification_status")
    assert "verification_status" not in claim.__dataclass_fields__
    conflicted = _claim(ledger_status="conflicted")
    assert conflicted.ledger_status == "conflicted"
    assert not hasattr(conflicted, "verification_status")
    with pytest.raises(ClaimError, match="ledger_status"):
        _claim(ledger_status="verified")


def test_claim_rejects_compact_millions_value() -> None:
    with pytest.raises(ClaimError, match="value"):
        _claim(value="21,26 M")
    with pytest.raises(ClaimError, match="value"):
        _claim(value="8,19 M")
    signed = _claim(
        identity_key="BYMA|2026-03-31|income_statement|consolidated|income_tax",
        metric="income_tax",
        value="-14950948",
    )
    assert signed.value == "-14950948"


def test_claim_unit_ars_or_null() -> None:
    with_unit = _claim(unit="ARS")
    assert with_unit.unit == "ARS"
    with pytest.raises(ClaimError, match="unit"):
        _claim(unit="USD")
    with pytest.raises(ClaimError, match="currency"):
        _claim(currency="USD")


def test_evidence_empty_hash_and_bbox_allowed() -> None:
    evidence = _evidence()
    assert evidence.artifact_hash == ""
    assert evidence.bbox is None
    assert evidence.page == 4
    validate_evidence(evidence)


def test_evidence_good_bbox_constructs() -> None:
    evidence = _evidence(bbox=(0.1, 0.2, 0.3, 0.4))
    assert evidence.bbox == (0.1, 0.2, 0.3, 0.4)
    point = _evidence(bbox=(0.5, 0.5, 0.5, 0.5))
    assert point.bbox == (0.5, 0.5, 0.5, 0.5)


def test_evidence_invalid_bbox_is_rejected() -> None:
    with pytest.raises(EvidenceError, match="bbox"):
        _evidence(bbox=(1.5, 0.0, 1.6, 0.1))
    with pytest.raises(EvidenceError, match="bbox"):
        _evidence(bbox=(0.8, 0.1, 0.2, 0.3))
    with pytest.raises(EvidenceError, match="bbox"):
        _evidence(bbox=(0.1, 0.8, 0.2, 0.3))


def test_claim_keeps_evidence_tuple() -> None:
    evidence = _evidence(bbox=(0.0, 0.0, 1.0, 1.0))
    claim = _claim(evidence=(evidence,))
    assert len(claim.evidence) == 1
    assert claim.evidence[0].document_id == "byma-eeff-1t26"
    assert claim.evidence[0].text == "RESULTADO NETO DEL PERÍODO"
