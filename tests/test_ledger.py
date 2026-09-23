"""Fase 0 kernel ledger tests. Slice 4 upsert, conflict, and recipe seed."""

from __future__ import annotations

import ast
from pathlib import Path

from claimledger.claim import FinancialClaim
from claimledger.evidence import FinancialEvidence
from claimledger.identity import identity_key
from claimledger.ledger import Ledger

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO_ROOT / "src" / "claimledger" / "ledger.py"

CANONICAL_CONSOLIDATED = "BYMA|2026-03-31|income_statement|consolidated|net_income"
CANONICAL_PARENT = "BYMA|2026-03-31|income_statement|parent_attributable|net_income"
PRIOR_NET_INCOME = "22362983"
CURRENT_NET_INCOME = "21262335"

RECIPE_VALUES: tuple[tuple[str, str, str, str], ...] = (
    ("2026-03-31", "consolidated", "net_income", "21262335"),
    ("2026-03-31", "parent_attributable", "net_income", "21259769"),
    ("2026-03-31", "consolidated", "gross_profit", "60144176"),
    ("2026-03-31", "consolidated", "operating_income", "70223471"),
    ("2026-03-31", "consolidated", "income_before_tax", "36213283"),
    ("2026-03-31", "consolidated", "income_tax", "-14950948"),
    ("2026-03-31", "consolidated", "nci_income", "2566"),
    ("2026-06-30", "consolidated", "net_income", "81956525"),
    ("2026-06-30", "parent_attributable", "net_income", "81946993"),
    ("2026-06-30", "consolidated", "gross_profit", "122610546"),
    ("2026-06-30", "consolidated", "operating_income", "143236114"),
    ("2026-06-30", "consolidated", "income_before_tax", "114688061"),
    ("2026-06-30", "consolidated", "income_tax", "-32731536"),
    ("2026-06-30", "consolidated", "nci_income", "9532"),
)

FORBIDDEN_LEDGER_STATUSES = frozenset({"verified", "candidate", "rejected"})


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
        "value": CURRENT_NET_INCOME,
        "currency": "ARS",
        "unit": None,
        "evidence": (_evidence(),),
        "ledger_status": "recorded",
    }
    fields.update(overrides)
    return FinancialClaim(**fields)  # type: ignore[arg-type]


def test_first_upsert_is_recorded() -> None:
    ledger = Ledger()
    stored = ledger.upsert(_claim())
    fetched = ledger.get(CANONICAL_CONSOLIDATED)
    assert stored.ledger_status == "recorded"
    assert fetched is not None
    assert fetched.value == CURRENT_NET_INCOME
    assert fetched.identity_key == CANONICAL_CONSOLIDATED
    assert fetched.ledger_status == "recorded"


def test_same_identity_and_value_appends_evidence() -> None:
    ledger = Ledger()
    first = _evidence(document_id="src-a", text=CURRENT_NET_INCOME)
    second = _evidence(document_id="src-b", text=CURRENT_NET_INCOME)
    ledger.upsert(_claim(evidence=(first,)))
    stored = ledger.upsert(_claim(evidence=(second,)))
    fetched = ledger.get(CANONICAL_CONSOLIDATED)
    assert stored.ledger_status == "recorded"
    assert fetched is not None
    assert fetched.ledger_status == "recorded"
    assert fetched.value == CURRENT_NET_INCOME
    assert len(fetched.evidence) == 2
    assert fetched.evidence[0].document_id == "src-a"
    assert fetched.evidence[1].document_id == "src-b"


def test_other_value_marks_conflicted_and_keeps_both_evidences() -> None:
    ledger = Ledger()
    original = _evidence(document_id="current-eeff", text=CURRENT_NET_INCOME)
    prior = _evidence(document_id="prior-note", text=PRIOR_NET_INCOME)
    ledger.upsert(_claim(evidence=(original,)))
    stored = ledger.upsert(_claim(value=PRIOR_NET_INCOME, evidence=(prior,)))
    fetched = ledger.get(CANONICAL_CONSOLIDATED)
    assert stored.ledger_status == "conflicted"
    assert fetched is not None
    assert fetched.ledger_status == "conflicted"
    assert fetched.value == CURRENT_NET_INCOME
    assert fetched.value != PRIOR_NET_INCOME
    assert len(fetched.evidence) == 2
    texts = {item.text for item in fetched.evidence}
    assert texts == {CURRENT_NET_INCOME, PRIOR_NET_INCOME}
    assert fetched.evidence[0].document_id == "current-eeff"
    assert fetched.evidence[1].document_id == "prior-note"


def test_seeded_ledger_has_fourteen_recipe_rows() -> None:
    ledger = Ledger.seed()
    assert len(RECIPE_VALUES) == 14
    found: dict[str, str] = {}
    for period, scope, metric, value in RECIPE_VALUES:
        key = identity_key("BYMA", period, "income_statement", scope, metric)
        claim = ledger.get(key)
        assert claim is not None
        assert claim.value == value
        assert claim.issuer == "BYMA"
        assert claim.statement == "income_statement"
        assert claim.ledger_status == "recorded"
        found[key] = claim.value
    assert len(found) == 14
    parent = ledger.get(CANONICAL_PARENT)
    assert parent is not None
    assert parent.value == "21259769"
    assert parent.identity_key != CANONICAL_CONSOLIDATED


def test_prior_figure_is_not_current_net_income() -> None:
    ledger = Ledger.seed()
    current = ledger.get(CANONICAL_CONSOLIDATED)
    assert current is not None
    assert current.value == CURRENT_NET_INCOME
    assert current.value != PRIOR_NET_INCOME
    for period, scope, metric, value in RECIPE_VALUES:
        key = identity_key("BYMA", period, "income_statement", scope, metric)
        claim = ledger.get(key)
        assert claim is not None
        if metric == "net_income":
            assert claim.value != PRIOR_NET_INCOME


def test_ingest_never_stamps_verified() -> None:
    ledger = Ledger()
    stored = ledger.upsert(_claim())
    fetched = ledger.get(CANONICAL_CONSOLIDATED)
    assert stored.ledger_status == "recorded"
    assert stored.ledger_status != "verified"
    assert fetched is not None
    assert fetched.ledger_status == "recorded"
    assert fetched.ledger_status not in FORBIDDEN_LEDGER_STATUSES
    assert not hasattr(fetched, "verification_status")
    seeded = Ledger.seed()
    for period, scope, metric, _value in RECIPE_VALUES:
        key = identity_key("BYMA", period, "income_statement", scope, metric)
        claim = seeded.get(key)
        assert claim is not None
        assert claim.ledger_status == "recorded"
        assert claim.ledger_status not in FORBIDDEN_LEDGER_STATUSES


def test_ledger_instances_are_isolated() -> None:
    first = Ledger()
    second = Ledger()
    first.upsert(_claim())
    assert first.get(CANONICAL_CONSOLIDATED) is not None
    assert second.get(CANONICAL_CONSOLIDATED) is None
    seeded = Ledger.seed()
    empty = Ledger()
    seeded_claim = seeded.get(CANONICAL_CONSOLIDATED)
    assert seeded_claim is not None
    assert seeded_claim.value == CURRENT_NET_INCOME
    assert empty.get(CANONICAL_CONSOLIDATED) is None


def test_ledger_is_not_store_and_writes_no_disk_cache() -> None:
    source = LEDGER_PATH.read_text(encoding="utf-8")
    assert "store.py" not in source
    tree = ast.parse(source, filename=str(LEDGER_PATH))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                raise AssertionError("ledger must not open disk files")
            if isinstance(func, ast.Attribute) and func.attr in {
                "write_text",
                "write_bytes",
                "dump",
            }:
                raise AssertionError("ledger must not write a disk cache")
    assert "pathlib" not in imported
    assert "store" not in imported
