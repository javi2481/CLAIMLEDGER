"""Pure claims_query on Ledger.seed(). No socket, port, or Starlette."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from claimledger.claim import FinancialClaim
from claimledger.evidence import FinancialEvidence
from claimledger.http.claims import claims_query
from claimledger.identity import identity_key
from claimledger.ledger import Ledger
from claimledger.lookup import Intent
from claimledger.query import query

ORDINARY_EEFF = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
PARENT_1T = "resultado atribuible a la controlante 1T26"
TAX_1T = "impuesto a las ganancias consolidado 1T26"
COMPARE_VS = "Comparar resultado neto consolidado 1T26 vs 2T26"
YPF_CLOSE_BYMA = "¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?"
AMBIGUOUS_PERIOD = "¿Cuál es el resultado neto consolidado?"
UNRESOLVED = "hola"
COMPARE_DELTA = "60694190"

ABSENT_KEYS = (
    "answer",
    "identity",
    "identity_key",
    "unit",
    "ledger_status",
    "artifact_hash",
    "label",
    "bbox",
)

RECIPE_NO_EXTRACT = (
    "¿Cuál es el resultado neto del período en la memoria anual?",
    "¿Cuál es el resultado neto consolidado del comunicado de prensa?",
    "¿Cuál es el resultado neto consolidado del deck?",
    "¿Qué dice la cláusula 5 del contrato?",
)


def _nested_keys(payload: object) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        found.update(str(key) for key in payload)
        for value in payload.values():
            found.update(_nested_keys(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_nested_keys(item))
    return found


def _assert_absent(payload: object) -> None:
    assert _nested_keys(payload).isdisjoint(ABSENT_KEYS)


def _assert_abstained(payload: object, reason: str) -> None:
    assert payload == {"status": "abstained", "reason": reason}
    assert reason != "no_verified_claim"
    assert "claim" not in payload
    assert "claims" not in payload
    assert "value" not in payload


def _rector_claim(
    *,
    period: str,
    scope: str,
    metric: str,
    value: str,
) -> dict[str, str]:
    return {
        "issuer": "BYMA",
        "period": period,
        "statement": "income_statement",
        "scope": scope,
        "metric": metric,
        "value": value,
        "currency": "ARS",
    }


def test_consolidated_net_income_on_seed() -> None:
    result = claims_query({"question": ORDINARY_EEFF}, Ledger.seed())
    assert result["status"] == "verified"
    assert result["claim"] == _rector_claim(
        period="2026-03-31",
        scope="consolidated",
        metric="net_income",
        value="21262335",
    )
    assert result["evidence"] == []
    _assert_absent(result)


def test_parent_is_not_consolidated() -> None:
    result = claims_query({"question": PARENT_1T}, Ledger.seed())
    assert result["status"] == "verified"
    assert result["claim"]["value"] == "21259769"
    assert result["claim"]["value"] != "21262335"
    assert result["evidence"] == []
    _assert_absent(result)


def test_income_tax_keeps_the_sign() -> None:
    result = claims_query({"question": TAX_1T}, Ledger.seed())
    assert result["status"] == "verified"
    assert result["claim"]["value"] == "-14950948"
    assert result["evidence"] == []
    _assert_absent(result)


@pytest.mark.parametrize("question", RECIPE_NO_EXTRACT)
def test_recipe_no_extract_stays_that_string(question: str) -> None:
    result = claims_query({"question": question}, Ledger.seed())
    _assert_abstained(result, "recipe_no_extract")


@pytest.mark.parametrize(
    ("question", "reason"),
    (
        (YPF_CLOSE_BYMA, "off_corpus"),
        (UNRESOLVED, "unresolved_identity"),
        (AMBIGUOUS_PERIOD, "ambiguous_period"),
    ),
)
def test_seed_passes_kernel_abstain_reasons(question: str, reason: str) -> None:
    result = claims_query({"question": question}, Ledger.seed())
    _assert_abstained(result, reason)


def test_seed_passes_no_matching_claim_and_incomplete_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lexicon questions never emit these two reasons against a full seed."""
    intents = {
        "force-no-matching-claim": Intent(
            route="identity",
            issuer="BYMA",
            statement="income_statement",
            scope="consolidated",
            metric="net_income",
            period="2025-12-31",
            compare=False,
            abstain_reason=None,
        ),
        "force-incomplete-comparison": Intent(
            route="identity",
            issuer="BYMA",
            statement="income_statement",
            scope="consolidated",
            metric="not_in_book",
            period=None,
            compare=True,
            abstain_reason=None,
        ),
    }
    monkeypatch.setattr(
        "claimledger.http.claims.understand",
        lambda question: intents[question],
    )
    ledger = Ledger.seed()
    expected = {
        "force-no-matching-claim": "no_matching_claim",
        "force-incomplete-comparison": "incomplete_comparison",
    }
    for question, reason in expected.items():
        kernel = query(intents[question], ledger)
        assert kernel.reason == reason
        result = claims_query({"question": question}, ledger)
        _assert_abstained(result, kernel.reason)


def test_compare_returns_two_claims_without_delta() -> None:
    result = claims_query({"question": COMPARE_VS}, Ledger.seed())
    assert result["status"] == "verified"
    assert "claim" not in result
    assert len(result["claims"]) == 2
    assert [item["value"] for item in result["claims"]] == ["21262335", "81956525"]
    assert result["claims"][0] == {
        **_rector_claim(
            period="2026-03-31",
            scope="consolidated",
            metric="net_income",
            value="21262335",
        ),
        "evidence": [],
    }
    assert result["claims"][1]["value"] == "81956525"
    assert result["claims"][1]["evidence"] == []
    assert "delta" not in result
    assert "delta" not in _nested_keys(result)
    dumped = str(result)
    assert COMPARE_DELTA not in dumped
    assert f"-{COMPARE_DELTA}" not in dumped
    _assert_absent(result)


def test_nonempty_evidence_emits_document_page_and_text_only() -> None:
    key = identity_key(
        "BYMA", "2026-03-31", "income_statement", "consolidated", "net_income"
    )
    evidence = FinancialEvidence(
        document_id="byma-eeff-1t26",
        artifact_hash="abc",
        page=4,
        text="RESULTADO NETO DEL PERÍODO",
        label="net_income",
        bbox=(0.1, 0.2, 0.3, 0.4),
    )
    ledger = Ledger()
    ledger.upsert(
        FinancialClaim(
            identity_key=key,
            issuer="BYMA",
            period="2026-03-31",
            statement="income_statement",
            scope="consolidated",
            metric="net_income",
            value="21262335",
            currency="ARS",
            unit=None,
            evidence=(evidence,),
            ledger_status="recorded",
        )
    )
    result = claims_query({"question": ORDINARY_EEFF}, ledger)
    assert result["evidence"] == [
        {
            "document_id": "byma-eeff-1t26",
            "page": 4,
            "text": "RESULTADO NETO DEL PERÍODO",
        }
    ]
    _assert_absent(result)


def test_missing_or_non_string_question_does_not_call_understand(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _forbidden(_question: str) -> Intent:
        raise AssertionError("understand must not be called")

    monkeypatch.setattr("claimledger.http.claims.understand", _forbidden)
    ledger = Ledger.seed()
    for body in ({}, {"question": None}, {"question": 1}, {"question": ["1T26"]}):
        result = claims_query(body, ledger)
        assert not isinstance(result, dict) or "status" not in result


def test_string_question_calls_understand_then_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import claimledger.http.claims as claims_mod

    order: list[str] = []
    real_understand = claims_mod.understand
    real_query = claims_mod.query

    def _understand(question: str):
        order.append("understand")
        return real_understand(question)

    def _query(intent: Intent, ledger: Ledger):
        order.append("query")
        assert ledger is seen["ledger"]
        return real_query(intent, ledger)

    seen: dict[str, Ledger] = {}
    monkeypatch.setattr(claims_mod, "understand", _understand)
    monkeypatch.setattr(claims_mod, "query", _query)
    ledger = Ledger.seed()
    seen["ledger"] = ledger
    claims_query({"question": ORDINARY_EEFF}, ledger)
    assert order == ["understand", "query"]


def test_claims_module_does_not_import_starlette() -> None:
    import claimledger.http.claims as claims_mod

    tree = ast.parse(Path(claims_mod.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(name == "starlette" or name.startswith("starlette.") for name in imported)


def test_http_init_is_docstring_only() -> None:
    import claimledger.http as http_pkg

    init = Path(http_pkg.__file__)
    tree = ast.parse(init.read_text(encoding="utf-8"))
    assert ast.get_docstring(tree)
    assert all(isinstance(node, ast.Expr) for node in tree.body)
    assert not hasattr(http_pkg, "claims_query")
    assert not hasattr(http_pkg, "build_app")
