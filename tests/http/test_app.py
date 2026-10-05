"""In-process POST /claims/query. No bound port. The client is not pinned."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

ORDINARY_EEFF = "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
RECIPE_MEMORIA = "¿Cuál es el resultado neto del período en la memoria anual?"
YPF_CLOSE_BYMA = "¿Cuál fue el precio de cierre de YPF en BYMA el 3 de enero?"
COMPARE_VS = "Comparar resultado neto consolidado 1T26 vs 2T26"
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

KERNEL_ALLOWLIST = (
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

KERNEL_MODULES = (
    "claimledger.identity",
    "claimledger.digits",
    "claimledger.evidence",
    "claimledger.claim",
    "claimledger.ledger",
    "claimledger.lookup",
    "claimledger.query",
)

_BANNED_PINS = ("fastapi", "flask", "uvicorn")


def _assigned_strings(tree: ast.AST, name: str) -> tuple[str, ...]:
    for node in tree.body:  # type: ignore[attr-defined]
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        return tuple(
            elt.value
            for elt in node.value.elts  # type: ignore[attr-defined]
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
        )
    raise AssertionError(f"{name} missing")


def _allowlist_paths(tree: ast.AST) -> tuple[str, ...]:
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            if not any(
                isinstance(target, ast.Name) and target.id == "relatives"
                for target in stmt.targets
            ):
                continue
            return tuple(
                elt.value
                for elt in stmt.value.elts  # type: ignore[attr-defined]
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            )
    raise AssertionError("allowlist missing")


def _import_roots(nodes: list[ast.AST] | tuple[ast.AST, ...]) -> set[str]:
    roots: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _file_import_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return _import_roots(list(ast.walk(tree)))


def _dist_name(requirement: str) -> str:
    name = requirement.split(";", 1)[0].strip()
    for separator in ("===", "==", ">=", "<=", "~=", "!=", ">", "<", "["):
        name = name.split(separator, 1)[0]
    return name.strip().lower().replace("_", "-")


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


def _build_app():
    from claimledger.http.app import build_app

    return build_app()


def _request(app: object, method: str, path: str, **kwargs: object) -> tuple[int, object, str, int | None]:
    """In-process ASGI. TestClient when that import works, otherwise httpx."""
    try:
        from starlette.testclient import TestClient
    except ImportError:
        import httpx

        client_cm = httpx.Client(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        )
    else:
        client_cm = TestClient(app)
    with client_cm as client:
        response = client.request(method, path, **kwargs)
        content_type = response.headers.get("content-type", "")
        body = response.json() if "application/json" in content_type else None
        return (
            response.status_code,
            body,
            response.request.url.host,
            response.request.url.port,
        )


def _assert_in_process(host: str, port: int | None) -> None:
    assert host == "testserver"
    assert port is None


def test_http_extra_pins_starlette_only() -> None:
    import tomllib

    project = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["dependencies"] == []
    extras = project["optional-dependencies"]
    http_extra = extras.get("http")
    assert http_extra == ["starlette==1.0.0"]
    declared = list(project["dependencies"])
    for group in extras.values():
        declared.extend(group)
    names = {_dist_name(item) for item in declared}
    assert names.isdisjoint(_BANNED_PINS)
    assert "starlette" in names


def test_http_stays_off_kernel_allowlist() -> None:
    tree = ast.parse((REPO_ROOT / "tests" / "test_identity.py").read_text(encoding="utf-8"))
    paths = _allowlist_paths(tree)
    modules = _assigned_strings(tree, "KERNEL_MODULES")
    assert paths == KERNEL_ALLOWLIST
    assert len(paths) == 13
    assert modules == KERNEL_MODULES
    assert len(modules) == 7
    for path in paths:
        assert not path.startswith("src/claimledger/http/")
        assert not path.startswith("tests/http/")
        assert "http" not in Path(path).parts
        assert "starlette" not in _file_import_roots(REPO_ROOT / path)
    assert not any(name == "claimledger.http" or name.startswith("claimledger.http.") for name in modules)


def test_post_verified_claim_is_http_200() -> None:
    status, body, host, port = _request(
        _build_app(),
        "POST",
        "/claims/query",
        json={"question": ORDINARY_EEFF},
    )
    _assert_in_process(host, port)
    assert status == 200
    assert body["status"] == "verified"
    assert body["claim"] == {
        "issuer": "BYMA",
        "period": "2026-03-31",
        "statement": "income_statement",
        "scope": "consolidated",
        "metric": "net_income",
        "value": "21262335",
        "currency": "ARS",
    }
    assert body["evidence"] == []
    assert _nested_keys(body).isdisjoint(ABSENT_KEYS)


def test_post_abstained_is_http_200() -> None:
    app = _build_app()
    status, body, host, port = _request(
        app,
        "POST",
        "/claims/query",
        json={"question": YPF_CLOSE_BYMA},
    )
    _assert_in_process(host, port)
    assert status == 200
    assert body == {"status": "abstained", "reason": "off_corpus"}

    status, body, host, port = _request(
        app,
        "POST",
        "/claims/query",
        json={"question": RECIPE_MEMORIA},
    )
    _assert_in_process(host, port)
    assert status == 200
    assert body == {"status": "abstained", "reason": "recipe_no_extract"}
    assert body["reason"] != "no_verified_claim"


def test_post_compare_returns_two_claims_without_delta() -> None:
    status, body, host, port = _request(
        _build_app(),
        "POST",
        "/claims/query",
        json={"question": COMPARE_VS},
    )
    _assert_in_process(host, port)
    assert status == 200
    assert body["status"] == "verified"
    assert "claim" not in body
    assert [item["value"] for item in body["claims"]] == ["21262335", "81956525"]
    assert body["claims"][0]["evidence"] == []
    assert body["claims"][1]["evidence"] == []
    assert "delta" not in body
    dumped = str(body)
    assert COMPARE_DELTA not in dumped
    assert f"-{COMPARE_DELTA}" not in dumped


def test_post_question_calls_understand_then_query(monkeypatch: pytest.MonkeyPatch) -> None:
    import claimledger.http.claims as claims_mod

    order: list[str] = []
    real_understand = claims_mod.understand
    real_query = claims_mod.query

    def _understand(question: str):
        order.append("understand")
        return real_understand(question)

    def _query(intent: object, ledger: object):
        order.append("query")
        return real_query(intent, ledger)

    monkeypatch.setattr(claims_mod, "understand", _understand)
    monkeypatch.setattr(claims_mod, "query", _query)
    status, body, _host, _port = _request(
        _build_app(),
        "POST",
        "/claims/query",
        json={"question": ORDINARY_EEFF},
    )
    assert status == 200
    assert order == ["understand", "query"]
    assert body["claim"]["value"] == "21262335"


@pytest.mark.parametrize(
    "kwargs",
    (
        {"content": b"", "headers": {"content-type": "application/json"}},
        {"content": b"not-json", "headers": {"content-type": "application/json"}},
        {"content": b"null", "headers": {"content-type": "application/json"}},
        {"content": b"[]", "headers": {"content-type": "application/json"}},
        {"content": b'"hola"', "headers": {"content-type": "application/json"}},
        {"content": b"1", "headers": {"content-type": "application/json"}},
        {"json": {}},
        {"json": {"question": None}},
        {"json": {"question": 1}},
        {"json": {"question": ["1T26"]}},
    ),
)
def test_bad_body_is_400_and_skips_kernel(
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict[str, object],
) -> None:
    def _forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("understand and claims_query must not be called")

    monkeypatch.setattr("claimledger.http.claims.claims_query", _forbidden)
    monkeypatch.setattr("claimledger.http.claims.understand", _forbidden)
    monkeypatch.setattr("claimledger.lookup.understand", _forbidden)
    status, body, host, port = _request(_build_app(), "POST", "/claims/query", **kwargs)
    _assert_in_process(host, port)
    assert status == 400
    assert body == {}
    assert "status" not in body


def test_only_post_claims_query() -> None:
    app = _build_app()
    routes = [route for route in app.routes if getattr(route, "path", None)]
    assert [route.path for route in routes] == ["/claims/query"]
    assert routes[0].methods == {"POST"}

    get_status, _body, host, port = _request(app, "GET", "/claims/query")
    _assert_in_process(host, port)
    assert get_status == 405

    other_status, _body, host, port = _request(
        app,
        "POST",
        "/claims",
        json={"question": ORDINARY_EEFF},
    )
    _assert_in_process(host, port)
    assert other_status == 404


def test_starlette_is_imported_only_inside_build_app() -> None:
    from claimledger.http.app import build_app
    import claimledger.http.app as app_mod

    source = Path(app_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level = _import_roots(
        [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    )
    assert "starlette" not in top_level
    assert top_level.isdisjoint({"fastapi", "flask", "uvicorn"})
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "build_app"
    ]
    assert len(functions) == 1
    inside = _import_roots(list(ast.walk(functions[0])))
    assert "starlette" in inside

    saved = {
        name: sys.modules.pop(name)
        for name in list(sys.modules)
        if name == "starlette" or name.startswith("starlette.") or name == "claimledger.http.app"
    }
    try:
        sys.modules.pop("claimledger.http.app", None)
        reloaded = importlib.reload(importlib.import_module("claimledger.http.app"))
        loaded = [
            name
            for name in sys.modules
            if name == "starlette" or name.startswith("starlette.")
        ]
        assert loaded == []
        reloaded.build_app()
        loaded = [
            name
            for name in sys.modules
            if name == "starlette" or name.startswith("starlette.")
        ]
        assert loaded
    finally:
        sys.modules.update(saved)
    assert build_app is app_mod.build_app
