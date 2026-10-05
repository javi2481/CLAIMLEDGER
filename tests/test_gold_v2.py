"""Fase 0 gold v2 regression. Slice 8: frozen numbers, alias-only identity rewrite."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from claimledger.identity import apply_alias
from claimledger.ledger import Ledger
from claimledger.lookup import understand
from claimledger.query import query

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = REPO_ROOT / "evals" / "identity_v2.json"
EVALS_DIR = REPO_ROOT / "evals"

FORBIDDEN_IMPORT_ROOTS = frozenset({"docling", "docling_graph"})
PRIOR_FIGURE = "22362983"

V2_ID_04_IDENTITY = "BYMA|2026-03-31|income_statement|consolidated|income_tax"
V2_ID_04_VALUE = "-14950948"
V2_ID_08_VALUE = "-32731536"
V2_CP_PERIODS = ["2026-03-31", "2026-06-30"]

V2_IDENTITY_IDS = tuple(f"v2-id-{i:02d}" for i in range(1, 9))
V2_NEIGHBOR_IDS = tuple(f"v2-nb-{i:02d}" for i in range(1, 9))
V2_COMPARE_IDS = tuple(f"v2-cp-{i:02d}" for i in range(1, 7))
V2_ABSTAIN_IDS = tuple(f"v2-ab-{i:02d}" for i in range(1, 5))

FROZEN_SINGLE_VALUES = {
    "v2-id-01": "60144176",
    "v2-id-02": "70223471",
    "v2-id-03": "36213283",
    "v2-id-04": "-14950948",
    "v2-id-05": "2566",
    "v2-id-06": "122610546",
    "v2-id-07": "143236114",
    "v2-id-08": "-32731536",
    "v2-nb-01": "60144176",
    "v2-nb-02": "70223471",
    "v2-nb-03": "36213283",
    "v2-nb-04": "-14950948",
    "v2-nb-05": "2566",
    "v2-nb-06": "122610546",
    "v2-nb-07": "143236114",
    "v2-nb-08": "21262335",
}
FROZEN_COMPARE_VALUES = {
    "v2-cp-01": ["60144176", "122610546"],
    "v2-cp-02": ["70223471", "143236114"],
    "v2-cp-03": ["36213283", "114688061"],
    "v2-cp-04": ["-14950948", "-32731536"],
    "v2-cp-05": ["2566", "9532"],
    "v2-cp-06": ["60144176", "122610546"],
}
FROZEN_NUMBERS = (
    "-14950948",
    "-32731536",
    "60144176",
    "70223471",
    "36213283",
    "2566",
    "122610546",
    "143236114",
    "114688061",
    "9532",
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


def _load_gold() -> dict:
    payload = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    assert payload["version"] == "identity_v2"
    return payload


def _cases() -> list[dict]:
    cases = _load_gold()["cases"]
    assert len(cases) == 26
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


def test_press_and_deck_gold_stay_out() -> None:
    names = {path.name for path in EVALS_DIR.glob("*.json")}
    assert "press_v1.json" not in names
    assert "presentation_v1.json" not in names
    assert not any(name.startswith("press_") for name in names)
    assert not any(name.startswith("presentation_") for name in names)
    assert "identity_v2.json" in names


def test_gold_v2_has_exactly_26_cases() -> None:
    cases = _cases()
    ids = [case["id"] for case in cases]
    assert len(ids) == 26
    assert len(set(ids)) == 26
    assert ids[:8] == list(V2_IDENTITY_IDS)
    assert ids[8:16] == list(V2_NEIGHBOR_IDS)
    assert ids[16:22] == list(V2_COMPARE_IDS)
    assert ids[22:26] == list(V2_ABSTAIN_IDS)
    assert all(not case.get("skip") for case in cases)


def test_v2_id_04_keeps_minus_sign_and_aliased_identity() -> None:
    case = _by_id()["v2-id-04"]
    assert case["partition"] == "identity"
    assert case["expected_value"] == V2_ID_04_VALUE
    assert case["expected_identity"] == V2_ID_04_IDENTITY
    assert case["expected_period"] == "2026-03-31"
    assert "impuesto_ganancias" not in case["expected_identity"]
    assert apply_alias("consolidado|impuesto_ganancias") == (
        "income_statement",
        "consolidated",
        "income_tax",
    )
    assert _rewrite_v1_identity(
        "BYMA|2026-03-31|consolidado|impuesto_ganancias"
    ) == V2_ID_04_IDENTITY

    result = _run_query(case["question"])
    assert result.status == "verified"
    assert len(result.claims) == 1
    assert result.claims[0].value == V2_ID_04_VALUE
    assert result.identity == V2_ID_04_IDENTITY
    assert result.claims[0].identity_key == V2_ID_04_IDENTITY


def test_v2_id_08_keeps_second_quarter_tax_sign() -> None:
    case = _by_id()["v2-id-08"]
    assert case["expected_value"] == V2_ID_08_VALUE
    assert case["expected_identity"] == (
        "BYMA|2026-06-30|income_statement|consolidated|income_tax"
    )
    result = _run_query(case["question"])
    assert result.status == "verified"
    assert result.claims[0].value == V2_ID_08_VALUE


def test_v2_compare_cases_return_two_claims_without_delta() -> None:
    cases = _by_id()
    for case_id in V2_COMPARE_IDS:
        case = cases[case_id]
        assert case["partition"] == "comparison"
        assert "*" in case["expected_identity"]
        assert case["expected_values"] == FROZEN_COMPARE_VALUES[case_id]
        assert case["expected_periods"] == V2_CP_PERIODS

        result = _run_query(case["question"])
        assert result.status == "verified"
        assert len(result.claims) == 2
        values = [claim.value for claim in result.claims]
        assert set(values) == set(FROZEN_COMPARE_VALUES[case_id])
        assert result.identity == case["expected_identity"]
        assert not hasattr(result, "delta")
        assert not hasattr(result, "difference")
        first, second = FROZEN_COMPARE_VALUES[case_id]
        subtracted = str(int(second) - int(first))
        assert subtracted not in values
        periods = {claim.period for claim in result.claims}
        assert periods == set(V2_CP_PERIODS)
        left, right = result.claims
        assert left.scope == right.scope
        assert left.metric == right.metric
        assert left.period != right.period
        for claim in result.claims:
            assert "*" not in claim.identity_key


def test_null_identity_ports_as_null() -> None:
    case = _by_id()["v2-ab-01"]
    assert case["expected_identity"] is None
    assert case["expected_value"] is None
    assert case["expected_abstain"] is True
    result = _run_query(case["question"])
    assert result.status == "abstained"
    assert result.claims == ()
    assert result.identity is None


def test_frozen_numbers_are_intact() -> None:
    seen: set[str] = set()
    for case in _cases():
        if case.get("expected_value") is not None:
            seen.add(case["expected_value"])
        seen.update(case.get("expected_values", []))
    for number in FROZEN_NUMBERS:
        assert number in seen


def test_prior_figure_is_never_current_net_income_expected_value() -> None:
    for case in _cases():
        assert case.get("expected_value") != PRIOR_FIGURE
        assert PRIOR_FIGURE not in case.get("expected_values", [])


def test_alias_only_rewrite_keeps_other_fields() -> None:
    for case in _cases():
        assert case["id"].startswith("v2-")
        assert case["partition"] in {
            "identity",
            "neighbor",
            "comparison",
            "abstention",
        }
        assert case["route"] in {"identity", "abstain"}
        assert isinstance(case["question"], str) and case["question"]
        assert "expected_abstain" in case
        assert "skip" not in case
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
        assert "resultado_" not in identity
        assert "consolidado|" not in identity
        assert "impuesto_ganancias" not in identity


def test_harness_runs_all_26_cases() -> None:
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

    assert skipped == []
    assert len(ran) == 26
    assert ran == (
        list(V2_IDENTITY_IDS)
        + list(V2_NEIGHBOR_IDS)
        + list(V2_COMPARE_IDS)
        + list(V2_ABSTAIN_IDS)
    )
