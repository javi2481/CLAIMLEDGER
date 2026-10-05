"""Open WebUI host copies one existing card into text."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import claimledger.ingest.store as ingest_store
from claimledger.card.card import ClaimCard
from claimledger.ingest.types import IngestError
from claimledger.openwebui.reply import reply
from claimledger.openwebui.text import card_text

_SEAL = "VERIFICADO"
_CHIP = "BYMA · 1T26 · Consolidado · Resultado neto"
_ROW_CONSOLIDATED = "RESULTADO NETO DEL PERÍODO 21.262.335"
_ROW_PARENT = "Resultado neto atribuible a la sociedad controlante 21.259.769"
_VALUE = "21262335"
_SENTENCE = "encontré estas dos filas; verifiqué la consolidada"
_REASON = "filas copiadas"


def test_card_text_copies_fields() -> None:
    card = ClaimCard(
        seal=_SEAL,
        chips=(_CHIP, ""),
        rows=(_ROW_CONSOLIDATED, _ROW_PARENT),
        values=(_VALUE,),
        sentence=_SENTENCE,
        reason=_REASON,
    )

    text = card_text(card)

    assert text == "\n".join(
        (
            _SEAL,
            _CHIP,
            _ROW_CONSOLIDATED,
            _ROW_PARENT,
            _VALUE,
            _SENTENCE,
            _REASON,
        )
    )


def test_card_text_omits_whole_tables() -> None:
    table = "RESULTADO NETO " + ("1.000.000 " * 80)
    card = ClaimCard(
        seal=_SEAL,
        chips=(_CHIP,),
        rows=(
            table,
            "Bolsa de Comercio de Buenos Aires, PARTICIPACIÓN = 30,9%",
            "Claudio Zuchovicki Presidente",
            table,
        ),
        values=(_VALUE,),
        sentence="",
        reason=None,
    )

    text = card_text(card)

    assert text == "\n".join((_SEAL, _CHIP, _VALUE))
    assert "1.000.000" not in text


_NEIGHBOR_CONSOLIDATED = "RESULTADO NETO DEL PERÍODO 21.262.335"
_NEIGHBOR_PARENT = "Resultado neto atribuible a la sociedad controlante 21.259.769"
_CONSOLIDATED_QUESTION = (
    "¿Cuál es el RESULTADO NETO DEL PERÍODO consolidado del 1T26?"
)
_PARENT_QUESTION = "resultado atribuible a la controlante 1T26"
_ABSTAIN_QUESTION = "resultado neto del período en la memoria anual"
_COMPARE_QUESTION = "Comparar resultado neto consolidado 1T26 vs 2T26"
_CONSOLIDATED_VALUE = "21262335"
_PARENT_VALUE = "21259769"
_SECOND_QUARTER_VALUE = "81956525"
_COMPARE_DELTA = str(abs(int(_SECOND_QUARTER_VALUE) - int(_CONSOLIDATED_VALUE)))


def _canonical_json_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _neighbor_payload() -> dict:
    return {
        "parsed_nodes": [
            {
                "text": "Estado de Resultados",
                "label": "section_header",
                "ref": "#/texts/0",
            },
            {
                "text": _NEIGHBOR_CONSOLIDATED,
                "label": "table",
                "ref": "#/tables/1",
            },
            {"text": _NEIGHBOR_PARENT, "label": "table", "ref": "#/tables/1"},
            {
                "text": "política contable de reconocimiento de ingresos",
                "label": "text",
                "ref": "#/texts/4",
            },
        ]
    }


def _parsed_nodes(payload: dict) -> list[SimpleNamespace]:
    return [
        SimpleNamespace(
            text=item["text"],
            metadata={"doc_items": [{"self_ref": item["ref"], "label": item["label"]}]},
        )
        for item in payload["parsed_nodes"]
    ]


def _install_parsed_reader(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.retrieval import read as read_mod

    def fake_read(artifact_hash: str) -> list[SimpleNamespace]:
        return _parsed_nodes(ingest_store.load(artifact_hash))

    monkeypatch.setattr(read_mod, "read_hashed_json", fake_read)


def _prepare_neighbors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    monkeypatch.setattr(ingest_store, "artifacts_dir", lambda: artifacts)
    raw = _canonical_json_bytes(_neighbor_payload())
    digest = _sha256_hex(raw)
    (artifacts / f"{digest}.json").write_bytes(raw)
    _install_parsed_reader(monkeypatch)
    return digest


def test_reply_consolidated_21262335(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _CONSOLIDATED_QUESTION)

    assert text == "\n".join(
        (
            "VERIFICADO",
            "BYMA · 1T26 · Consolidado · Resultado neto",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            _CONSOLIDATED_VALUE,
            "encontré estas dos filas; verifiqué la consolidada",
        )
    )
    assert _CONSOLIDATED_VALUE in text
    assert _PARENT_VALUE not in text


def test_reply_parent_21259769_both_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _PARENT_QUESTION)

    assert text == "\n".join(
        (
            "VERIFICADO",
            "BYMA · 1T26 · Controlante · Resultado neto",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            _PARENT_VALUE,
            "encontré estas dos filas; verifiqué la controlante",
        )
    )
    assert _PARENT_VALUE in text
    assert _NEIGHBOR_CONSOLIDATED in text
    assert _NEIGHBOR_PARENT in text


def test_reply_abstain_adds_no_verified_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _ABSTAIN_QUESTION)

    assert text == "\n".join(
        (
            "ME ABSTENGO",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            "recipe_no_extract",
        )
    )
    assert "ME ABSTENGO" in text
    assert _CONSOLIDATED_VALUE not in text
    assert _PARENT_VALUE not in text
    assert "VERIFICADO" not in text


def test_reply_compare_copies_both_values_without_delta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _COMPARE_QUESTION)

    assert text == "\n".join(
        (
            "VERIFICADO",
            "BYMA · 1T26 · Consolidado · Resultado neto",
            "BYMA · 2T26 · Consolidado · Resultado neto",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            _CONSOLIDATED_VALUE,
            _SECOND_QUARTER_VALUE,
        )
    )
    assert _CONSOLIDATED_VALUE in text
    assert _SECOND_QUARTER_VALUE in text
    assert _COMPARE_DELTA not in text
    assert "delta" not in text.casefold()
    assert f"{_SECOND_QUARTER_VALUE}-{_CONSOLIDATED_VALUE}" not in text


def test_reply_bad_hash_raises_and_invents_no_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _prepare_neighbors(tmp_path, monkeypatch)

    with pytest.raises((IngestError, json.JSONDecodeError)) as caught:
        reply("0" * 64, _CONSOLIDATED_QUESTION)

    detail = str(caught.value)
    assert _NEIGHBOR_CONSOLIDATED not in detail
    assert _NEIGHBOR_PARENT not in detail
    assert _CONSOLIDATED_VALUE not in detail
    assert _PARENT_VALUE not in detail


def _host_request(app: object, method: str, path: str, **kwargs: object):
    from starlette.testclient import TestClient

    with TestClient(app) as client:
        response = client.request(method, path, **kwargs)
        return response


def _assert_in_process(response: object) -> None:
    assert response.request.url.host == "testserver"
    assert response.request.url.port is None


def test_models_lists_only_claimledger_card() -> None:
    from claimledger.openwebui.app import MODEL_ID, build_host

    response = _host_request(build_host("abc"), "GET", "/v1/models")
    _assert_in_process(response)
    body = response.json()
    assert response.status_code == 200
    assert [item["id"] for item in body["data"]] == [MODEL_ID]
    assert MODEL_ID == "claimledger-card"


def test_completions_returns_only_the_card(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.openwebui.app import MODEL_ID, _completion, build_host
    from claimledger.openwebui.reply import reply

    digest = _prepare_neighbors(tmp_path, monkeypatch)
    question = _CONSOLIDATED_QUESTION
    response = _host_request(
        build_host(digest),
        "POST",
        "/v1/chat/completions",
        json={
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": "habla antes"},
                {"role": "user", "content": "primero"},
                {"role": "user", "content": question},
            ],
        },
    )
    _assert_in_process(response)
    assert response.status_code == 200
    assert response.json() == _completion(reply(digest, question))
    assert _CONSOLIDATED_VALUE in response.json()["choices"][0]["message"]["content"]
    assert "habla antes" not in response.text


def test_bad_body_is_400_and_skips_measure(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.openwebui.app import build_host
    import claimledger.openwebui.reply as reply_mod

    def fail_measure(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("measure")

    monkeypatch.setattr(reply_mod, "measure", fail_measure)
    response = _host_request(
        build_host("abc"),
        "POST",
        "/v1/chat/completions",
        json={"model": "gpt", "messages": [{"role": "user", "content": "hola"}]},
    )
    _assert_in_process(response)
    assert response.status_code == 400
    assert response.json() == {"error": "unreadable_artifact"}


def test_bad_hash_is_400_and_skips_render(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.openwebui.app import MODEL_ID, build_host
    import claimledger.openwebui.reply as reply_mod

    _prepare_neighbors(tmp_path, monkeypatch)

    def fail_render(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("render_card")

    monkeypatch.setattr(reply_mod, "render_card", fail_render)
    response = _host_request(
        build_host("0" * 64),
        "POST",
        "/v1/chat/completions",
        json={"model": MODEL_ID, "messages": [{"role": "user", "content": _CONSOLIDATED_QUESTION}]},
    )
    _assert_in_process(response)
    assert response.status_code == 400
    assert response.json() == {"error": "unreadable_artifact"}
    assert _CONSOLIDATED_VALUE not in response.text


def test_stream_is_one_card_then_done(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.openwebui.app import MODEL_ID, build_host
    from claimledger.openwebui.reply import reply

    digest = _prepare_neighbors(tmp_path, monkeypatch)
    card = reply(digest, _CONSOLIDATED_QUESTION)
    response = _host_request(
        build_host(digest),
        "POST",
        "/v1/chat/completions",
        json={
            "model": MODEL_ID,
            "stream": True,
            "messages": [{"role": "user", "content": _CONSOLIDATED_QUESTION}],
        },
    )
    _assert_in_process(response)
    assert response.status_code == 200
    data_lines = [
        line.removeprefix("data: ")
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert len(data_lines) == 2
    chunk = json.loads(data_lines[0])
    assert chunk["choices"][0]["delta"]["content"] == card
    assert data_lines[1] == "[DONE]"


def test_missing_env_hash_is_400(monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.openwebui.app import MODEL_ID, build_host

    monkeypatch.delenv("CLAIMLEDGER_ARTIFACT_HASH", raising=False)
    response = _host_request(
        build_host(None),
        "POST",
        "/v1/chat/completions",
        json={"model": MODEL_ID, "messages": [{"role": "user", "content": "hola"}]},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "unreadable_artifact"}


def test_host_stays_off_claims_route_and_allowlist() -> None:
    import ast

    from claimledger.http.app import build_app
    from claimledger.openwebui.app import build_host

    claims = build_app()
    claim_routes = [route for route in claims.routes if getattr(route, "path", None)]
    assert [route.path for route in claim_routes] == ["/claims/query"]
    assert claim_routes[0].methods == {"POST"}

    host = build_host("abc")
    host_routes = [route for route in host.routes if getattr(route, "path", None)]
    assert {route.path for route in host_routes} == {"/v1/models", "/v1/chat/completions"}

    repo = Path(__file__).resolve().parents[2]
    tree = ast.parse((repo / "tests" / "test_identity.py").read_text(encoding="utf-8"))
    relatives = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "relatives" for target in stmt.targets
            ):
                relatives = tuple(elt.value for elt in stmt.value.elts)
    assert relatives is not None
    assert len(relatives) == 13
    assert not any("openwebui" in path for path in relatives)

    app_tree = ast.parse(
        (repo / "src" / "claimledger" / "openwebui" / "app.py").read_text(encoding="utf-8")
    )
    for node in app_tree.body:
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] != "starlette" for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module is None or node.module.split(".")[0] != "starlette"
    build = next(
        node for node in app_tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_host"
    )
    imported = [
        node
        for node in ast.walk(build)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "starlette"
    ]
    assert imported


def test_compose_pins_slim_screen() -> None:
    repo = Path(__file__).resolve().parents[2]
    compose = (repo / "docker-compose.yml").read_text(encoding="utf-8")
    dockerfile = (repo / "Dockerfile").read_text(encoding="utf-8")
    assert "manual.ui:build_manual_app" in dockerfile
    assert "ghcr.io/open-webui/open-webui:v0.11.4-slim" in compose
    assert "8080:8080" in compose
    assert "claimledger.openwebui.app:build_host" in compose
    assert "--factory" in compose
    assert "CLAIMLEDGER_ARTIFACT_HASH" in compose
    assert "http://claimledger:8000/v1" in compose
    assert "OPENAI_API_KEYS=claimledger" in compose or "OPENAI_API_KEYS: claimledger" in compose
    assert "ENABLE_OPENAI_API=true" in compose or "ENABLE_OPENAI_API: \"true\"" in compose or "ENABLE_OPENAI_API: true" in compose
    for flag in (
        "ENABLE_OLLAMA_API",
        "ENABLE_TITLE_GENERATION",
        "ENABLE_FOLLOW_UP_GENERATION",
        "ENABLE_TAGS_GENERATION",
        "ENABLE_AUTOCOMPLETE_GENERATION",
    ):
        assert flag in compose
        assert "false" in compose
    assert "8000:8000" not in compose
    assert compose.count("ports:") == 1
    folded = compose.casefold()
    assert "pipelines" not in folded
    assert "knowledge" not in folded
    assert "mcp" not in folded
