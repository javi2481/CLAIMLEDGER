"""Fase 0 gold v1 regression. Slice 7: frozen numbers, alias-only identity rewrite."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from claimledger.identity import apply_alias
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import query

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = REPO_ROOT / "evals" / "identity_v1.json"
EVALS_DIR = REPO_ROOT / "evals"

FORBIDDEN_IMPORT_ROOTS = frozenset({"docling", "docling_graph"})
NARRATIVE_IDS = tuple(f"na-{i:02d}" for i in range(1, 11))
PRIOR_FIGURE = "22362983"

ID_01_IDENTITY = "BYMA|2026-03-31|income_statement|consolidated|net_income"
ID_01_VALUE = "21262335"
NB_01_REJECTS = ["21259769", "22362983"]
CP_01_IDENTITY = "BYMA|*|income_statement|consolidated|net_income"
CP_01_VALUES = ["21262335", "81956525"]
CP_01_PERIODS = ["2026-03-31", "2026-06-30"]

FROZEN_SINGLE_VALUES = {
    "id-01": "21262335",
    "id-02": "21262335",
    "id-03": "81956525",
    "id-04": "81956525",
    "id-05": "21259769",
    "id-06": "81946993",
    "id-07": "21259769",
    "id-08": "21262335",
    "id-09": "81946993",
    "id-10": "21262335",
    "nb-01": "21262335",
    "nb-02": "21262335",
    "nb-03": "81956525",
    "nb-04": "21262335",
    "nb-05": "21262335",
    "nb-06": "81956525",
    "nb-07": "21262335",
    "nb-08": "21259769",
    "nb-09": "21262335",
    "nb-10": "81956525",
}
FROZEN_COMPARE_VALUES = {
    "cp-01": ["21262335", "81956525"],
    "cp-02": ["21262335", "81956525"],
    "cp-03": ["21262335", "81956525"],
    "cp-04": ["21259769", "81946993"],
    "cp-05": ["21259769", "81946993"],
    "cp-06": ["21262335", "81956525"],
    "cp-07": ["21262335", "81956525"],
    "cp-08": ["21262335", "81956525"],
    "cp-09": ["21262335", "81956525"],
    "cp-10": ["21259769", "81946993"],
}

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


def _load_gold() -> dict:
    payload = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    assert payload["version"] == "identity_v1"
    return payload


def _cases() -> list[dict]:
    cases = _load_gold()["cases"]
    assert len(cases) == 45
    return cases


def _by_id() -> dict[str, dict]:
    return {case["id"]: case for case in _cases()}


def _rewrite_v1_identity(original: str) -> str:
    issuer, period, v1_scope, v1_metric = original.split("|")
    statement, scope, metric = apply_alias(f"{v1_scope}|{v1_metric}")
    return f"{issuer}|{period}|{statement}|{scope}|{metric}"


def _run_query(question: str):
    return query(understand(question), Ledger.seed())


def test_import_scan_stays_clean() -> None:
    scanned = list((REPO_ROOT / "tests").glob("*.py"))
    scanned.extend((REPO_ROOT / "src" / "claimledger").glob("*.py"))
    names = {path.name for path in scanned}
    assert "test_gold_v1.py" in names
    assert names >= {
        "test_gold_v1.py",
        "test_identity.py",
        "identity.py",
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


def test_press_and_deck_gold_stay_out() -> None:
    names = {path.name for path in EVALS_DIR.glob("*.json")}
    assert "press_v1.json" not in names
    assert "presentation_v1.json" not in names
    assert "identity_v1.json" in names


def test_gold_v1_has_exactly_45_cases() -> None:
    cases = _cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == 45
    assert len(set(ids)) == 45
    assert ids[:10] == [f"id-{i:02d}" for i in range(1, 11)]
    assert ids[10:20] == [f"nb-{i:02d}" for i in range(1, 11)]
    assert ids[20:30] == [f"cp-{i:02d}" for i in range(1, 11)]
    assert ids[30:35] == [f"ab-{i:02d}" for i in range(1, 6)]
    assert ids[35:45] == list(NARRATIVE_IDS)


def test_id_01_keeps_neighbor_number_and_aliased_identity() -> None:
    case = _by_id()["id-01"]
    assert case["partition"] == "identity"
    assert case["expected_value"] == ID_01_VALUE
    assert case["expected_identity"] == ID_01_IDENTITY
    assert case["expected_period"] == "2026-03-31"
    assert "consolidado|resultado_neto" not in case["expected_identity"]
    assert apply_alias("consolidado|resultado_neto") == (
        "income_statement",
        "consolidated",
        "net_income",
    )
    assert _rewrite_v1_identity(
        "BYMA|2026-03-31|consolidado|resultado_neto"
    ) == ID_01_IDENTITY

    result = _run_query(case["question"])
    assert result.status == "verified"
    assert len(result.claims) == 1
    assert result.claims[0].value == ID_01_VALUE
    assert result.identity == ID_01_IDENTITY
    assert result.claims[0].identity_key == ID_01_IDENTITY


def test_nb_01_rejects_parent_and_prior() -> None:
    case = _by_id()["nb-01"]
    assert case["partition"] == "neighbor"
    assert case["expected_value"] == ID_01_VALUE
    assert case["reject_values"] == NB_01_REJECTS
    assert PRIOR_FIGURE in case["reject_values"]
    assert case["expected_identity"] == ID_01_IDENTITY

    result = _run_query(case["question"])
    assert result.status == "verified"
    assert len(result.claims) == 1
    assert result.claims[0].value == ID_01_VALUE
    for rejected in NB_01_REJECTS:
        assert result.claims[0].value != rejected
    assert result.identity == ID_01_IDENTITY


def test_cp_01_wildcard_identity_and_two_values() -> None:
    case = _by_id()["cp-01"]
    assert case["partition"] == "comparison"
    assert case["expected_identity"] == CP_01_IDENTITY
    assert case["expected_values"] == CP_01_VALUES
    assert case["expected_periods"] == CP_01_PERIODS
    assert "*" in case["expected_identity"]

    result = _run_query(case["question"])
    assert result.status == "verified"
    assert len(result.claims) == 2
    values = [claim.value for claim in result.claims]
    assert set(values) == set(CP_01_VALUES)
    assert result.identity == CP_01_IDENTITY
    assert not hasattr(result, "delta")
    assert not hasattr(result, "difference")
    subtracted = str(int(CP_01_VALUES[1]) - int(CP_01_VALUES[0]))
    assert subtracted not in values
    periods = {claim.period for claim in result.claims}
    assert periods == set(CP_01_PERIODS)
    for claim in result.claims:
        assert "*" not in claim.identity_key


def test_narrative_cases_are_skipped() -> None:
    cases = _by_id()
    for case_id in NARRATIVE_IDS:
        case = cases[case_id]
        assert case["skip"] is True
        assert case["partition"] == "narrative"
        assert case["route"] == "narrative"
        assert "expected_value" not in case
        assert "expected_values" not in case


def test_prior_figure_is_never_current_net_income_expected_value() -> None:
    for case in _cases():
        assert case.get("expected_value") != PRIOR_FIGURE
        assert PRIOR_FIGURE not in case.get("expected_values", [])
        identity = case.get("expected_identity")
        if identity == ID_01_IDENTITY:
            assert case["expected_value"] == ID_01_VALUE
        if PRIOR_FIGURE in case.get("reject_values", []):
            assert case["partition"] == "neighbor"


def test_null_identity_ports_as_null() -> None:
    case = _by_id()["ab-01"]
    assert case["expected_identity"] is None
    assert case["expected_value"] is None
    assert case["expected_abstain"] is True
    result = _run_query(case["question"])
    assert result.status == "abstained"
    assert result.claims == ()
    assert result.identity is None


def test_alias_only_rewrite_keeps_other_fields() -> None:
    for case in _cases():
        assert case["id"]
        assert case["partition"] in {
            "identity",
            "neighbor",
            "comparison",
            "abstention",
            "narrative",
        }
        assert case["route"] in {"identity", "abstain", "narrative"}
        assert isinstance(case["question"], str) and case["question"]
        assert "expected_abstain" in case
        identity = case.get("expected_identity")
        if identity is None:
            if case["partition"] == "abstention":
                assert case["expected_value"] is None
            continue
        parts = identity.split("|")
        assert len(parts) == 5
        issuer, period, statement, scope, metric = parts
        assert issuer == "BYMA"
        assert period in {"2026-03-31", "2026-06-30", "*"}
        assert statement == "income_statement"
        assert (scope, metric) in {
            ("consolidated", "net_income"),
            ("parent_attributable", "net_income"),
            ("consolidated", "gross_profit"),
            ("consolidated", "operating_income"),
            ("consolidated", "income_before_tax"),
            ("consolidated", "income_tax"),
            ("consolidated", "nci_income"),
        }
        assert "resultado_neto" not in identity
        assert "consolidado|" not in identity


def test_harness_runs_non_skip_cases_and_skips_narrative() -> None:
    skipped: list[str] = []
    ran: list[str] = []
    ledger = Ledger.seed()
    for case in _cases():
        if case.get("skip") is True:
            skipped.append(case["id"])
            continue
        ran.append(case["id"])
        result = query(understand(case["question"]), ledger)
        partition = case["partition"]
        if partition in {"identity", "neighbor"}:
            assert result.status == "verified"
            assert len(result.claims) == 1
            assert result.claims[0].value == case["expected_value"]
            assert result.claims[0].value == FROZEN_SINGLE_VALUES[case["id"]]
            assert result.identity == case["expected_identity"]
            for rejected in case.get("reject_values", []):
                assert result.claims[0].value != rejected
            assert result.claims[0].value != PRIOR_FIGURE
        elif partition == "comparison":
            assert result.status == "verified"
            assert len(result.claims) == 2
            values = {claim.value for claim in result.claims}
            assert values == set(case["expected_values"])
            assert values == set(FROZEN_COMPARE_VALUES[case["id"]])
            assert result.identity == case["expected_identity"]
            assert "*" in result.identity
            assert not hasattr(result, "delta")
            assert not hasattr(result, "difference")
            periods = {claim.period for claim in result.claims}
            assert periods == set(case["expected_periods"])
            first, second = result.claims
            assert first.scope == second.scope
            assert first.metric == second.metric
            assert first.period != second.period
        elif partition == "abstention":
            assert result.status == "abstained"
            assert result.claims == ()
            assert case["expected_identity"] is None
            assert case["expected_value"] is None
            assert case["expected_abstain"] is True
        else:
            raise AssertionError(f"unexpected partition {partition} for {case['id']}")

    assert skipped == list(NARRATIVE_IDS)
    assert len(ran) == 35
    assert all(not case_id.startswith("na-") for case_id in ran)
