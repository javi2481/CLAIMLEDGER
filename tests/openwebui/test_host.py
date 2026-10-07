"""Open WebUI host copies one existing card into text."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import claimledger.ingest.store as ingest_store
from claimledger.agent.template import ABSTENTION_TEMPLATE
from claimledger.card.card import ClaimCard
from claimledger.ingest.types import IngestError
from claimledger.openwebui.reply import reply
from claimledger.openwebui.text import card_text


def _with_agent_trailing(core: str) -> str:
    return f"{core}\n{ABSTENTION_TEMPLATE}"

_SEAL = "VERIFICADO"
_CHIP = "BYMA · 1T26 · Consolidado · Resultado neto"
_ROW_CONSOLIDATED = "RESULTADO NETO DEL PERÍODO 21.262.335"
_ROW_PARENT = "Resultado neto atribuible a la sociedad controlante 21.259.769"
_VALUE = "21262335"
_SENTENCE = "encontré estas dos filas; verifiqué la consolidada"
_REASON = "filas copiadas"


@pytest.fixture(autouse=True)
def _stub_quarterly_book(monkeypatch: pytest.MonkeyPatch) -> None:
    import claimledger.openwebui.reply as reply_mod
    from claimledger.ledger import Ledger

    monkeypatch.setattr(reply_mod, "recorded_book", Ledger.seed)


def test_reply_uses_the_quarterly_book() -> None:
    import ast

    repo = Path(__file__).resolve().parents[2]
    source = (repo / "src" / "claimledger" / "openwebui" / "reply.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "recorded_book"
    ]
    assert len(calls) == 1
    assert "Ledger.seed" not in source


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
_SERIES_QUESTION = "Compará el resultado neto consolidado de los últimos 4 trimestres"
_BOOK_QUESTION = "todos los resultados netos de BYMA"
_BOOK_SCRIPT = """
MERGE (n:Period {id: "2026-03-31"})
SET n.period = "2026-03-31";
MERGE (n:Period {id: "2026-06-30"})
SET n.period = "2026-06-30";
"""
_CONSOLIDATED_VALUE = "21262335"
_PARENT_VALUE = "21259769"
_SECOND_QUARTER_VALUE = "81956525"
_DIFFERENCE_LINE = "Diferencia entre las dos cifras verificadas: 60694190"


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
        "name": "sample",
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

    assert text == _with_agent_trailing(
        "\n".join(
            (
                "VERIFICADO",
                "BYMA · 1T26 · Consolidado · Resultado neto",
                _NEIGHBOR_CONSOLIDATED,
                _NEIGHBOR_PARENT,
                _CONSOLIDATED_VALUE,
                "encontré estas dos filas; verifiqué la consolidada",
            )
        )
    )
    assert text.startswith("VERIFICADO\n")
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert _CONSOLIDATED_VALUE in text
    assert _PARENT_VALUE not in text


def test_reply_parent_21259769_both_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _PARENT_QUESTION)

    assert text == _with_agent_trailing(
        "\n".join(
            (
                "VERIFICADO",
                "BYMA · 1T26 · Controlante · Resultado neto",
                _NEIGHBOR_CONSOLIDATED,
                _NEIGHBOR_PARENT,
                _PARENT_VALUE,
                "encontré estas dos filas; verifiqué la controlante",
            )
        )
    )
    assert _PARENT_VALUE in text
    assert _NEIGHBOR_CONSOLIDATED in text
    assert _NEIGHBOR_PARENT in text
    assert text.endswith(ABSTENTION_TEMPLATE)


def test_reply_abstain_adds_no_verified_value(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _ABSTAIN_QUESTION)

    assert text == _with_agent_trailing(
        "\n".join(
            (
                "ME ABSTENGO",
                _NEIGHBOR_CONSOLIDATED,
                _NEIGHBOR_PARENT,
                "recipe_no_extract",
            )
        )
    )
    assert text.startswith("ME ABSTENGO\n")
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert "ME ABSTENGO" in text
    assert _CONSOLIDATED_VALUE not in text.split(ABSTENTION_TEMPLATE)[0]
    assert _PARENT_VALUE not in text
    assert "VERIFICADO" not in text


def test_reply_compare_copies_both_values_shows_code_difference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _COMPARE_QUESTION)

    assert text == _with_agent_trailing(_compare_card() + "\n" + _series_chart())
    assert "60694190" not in text.split("```mermaid", 1)[1].split(ABSTENTION_TEMPLATE)[0]
    assert _CONSOLIDATED_VALUE in text
    assert _SECOND_QUARTER_VALUE in text
    assert "60694190" in text
    assert "+60694190" not in text
    assert "delta" not in text.casefold()
    assert f"{_SECOND_QUARTER_VALUE}-{_CONSOLIDATED_VALUE}" not in text


def test_reply_last_four_quarters_leaves_holes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _SERIES_QUESTION)

    assert text.startswith("VERIFICADO\n")
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert "bar [21262335, 81956525]" in text
    assert "Hueco: 2025-09-30" in text
    assert "Hueco: 2025-12-31" in text
    assert "60694190" not in text
    assert _CONSOLIDATED_VALUE in text
    assert _SECOND_QUARTER_VALUE in text


def test_reply_all_net_results_draws_the_book(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "claimledger.openwebui.reply.read_script",
        lambda: _BOOK_SCRIPT,
        raising=False,
    )

    text = reply(digest, _BOOK_QUESTION)

    assert text.startswith("VERIFICADO\n")
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert "bar [21262335, 81956525]" in text
    assert "60694190" not in text


def test_reply_all_net_results_without_script_abstains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "claimledger.openwebui.reply.read_script",
        lambda: "",
        raising=False,
    )

    text = reply(digest, _BOOK_QUESTION)

    assert "ME ABSTENGO" in text
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert "81956525" not in text
    assert "```mermaid" not in text


_PAGE = 10
_NET_BOX = (2.0, 5.0, 4.0, 6.0)
_PARENT_BOX = (6.0, 1.0, 8.0, 3.0)
_CROP_BBOX = (0.2, 0.5, 0.4, 0.6)


def _pdf_box(left: float, bottom: float, right: float, top: float) -> dict:
    return {
        "l": left,
        "b": bottom,
        "r": right,
        "t": top,
        "coord_origin": "BOTTOMLEFT",
    }


def _cell(text: str, box: tuple[float, float, float, float] | None = None) -> dict:
    cell: dict = {"text": text}
    if box is not None:
        cell["bbox"] = _pdf_box(*box)
    return cell


def _income_table(
    self_ref: str,
    header: str,
    net_text: str,
    parent_text: str,
    page_no: int,
) -> dict:
    grid = [
        [_cell(""), _cell(header)],
        [_cell("Resultado bruto"), _cell("60.144.176")],
        [_cell("RESULTADO NETO DEL PERÍODO"), _cell(net_text, _NET_BOX)],
        [
            _cell(
                "Resultado neto del período atribuible a la participación controlante"
            ),
            _cell(parent_text, _PARENT_BOX),
        ],
    ]
    return {
        "self_ref": self_ref,
        "content_layer": "body",
        "parent": {"$ref": "#/body"},
        "prov": [
            {
                "page_no": page_no,
                "charspan": [0, 0],
                "bbox": _pdf_box(0.0, 0.0, 10.0, 10.0),
            }
        ],
        "data": {"grid": grid},
    }


def _picture_payload() -> dict:
    tables = [
        _income_table("#/tables/0", "31.03.2026", "21.262.335", "21.259.769", 1),
        _income_table("#/tables/1", "30.06.2026", "81.956.525", "81.946.993", 2),
    ]
    payload = _neighbor_payload()
    payload["pages"] = {
        "1": {"page_no": 1, "size": {"width": float(_PAGE), "height": float(_PAGE)}},
        "2": {"page_no": 2, "size": {"width": float(_PAGE), "height": float(_PAGE)}},
    }
    payload["body"] = {
        "self_ref": "#/body",
        "children": [{"$ref": table["self_ref"]} for table in tables],
    }
    payload["tables"] = tables
    return payload


def _rgb(marker: int) -> bytes:
    pixels = bytearray(_PAGE * _PAGE * 3)
    for offset in range(0, len(pixels), 3):
        pixels[offset] = marker
        pixels[offset + 2] = 255 - marker
    return bytes(pixels)


def _png_bytes(pixels: bytes) -> bytes:
    from io import BytesIO

    from PIL import Image

    image = Image.frombytes("RGB", (_PAGE, _PAGE), pixels)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _crop_markdown(png_file: bytes) -> str:
    from io import BytesIO

    from PIL import Image

    from claimledger.crop.cut import crop_bbox

    with Image.open(BytesIO(png_file)) as image:
        rgb = image.convert("RGB")
        cropped = crop_bbox(rgb.tobytes(), rgb.width, rgb.height, _CROP_BBOX)
    assert cropped is not None
    encoded = base64.b64encode(cropped).decode("ascii")
    return f"![crop](data:image/png;base64,{encoded})"


def _prepare_picture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str, str]:
    artifacts = tmp_path / "docling"
    artifacts.mkdir()
    monkeypatch.setattr(ingest_store, "artifacts_dir", lambda: artifacts)
    raw = _canonical_json_bytes(_picture_payload())
    digest = _sha256_hex(raw)
    (artifacts / f"{digest}.json").write_bytes(raw)
    page_one = _png_bytes(_rgb(17))
    page_two = _png_bytes(_rgb(29))
    (artifacts / f"{digest}.p1.png").write_bytes(page_one)
    (artifacts / f"{digest}.p2.png").write_bytes(page_two)
    _install_parsed_reader(monkeypatch)
    return digest, _crop_markdown(page_one), _crop_markdown(page_two)


def _consolidated_card() -> str:
    return "\n".join(
        (
            "VERIFICADO",
            "BYMA · 1T26 · Consolidado · Resultado neto",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            _CONSOLIDATED_VALUE,
            "encontré estas dos filas; verifiqué la consolidada",
        )
    )


def _abstain_card() -> str:
    return "\n".join(
        (
            "ME ABSTENGO",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            "recipe_no_extract",
        )
    )


def _compare_card() -> str:
    return "\n".join(
        (
            "VERIFICADO",
            "BYMA · 1T26 · Consolidado · Resultado neto",
            "BYMA · 2T26 · Consolidado · Resultado neto",
            _NEIGHBOR_CONSOLIDATED,
            _NEIGHBOR_PARENT,
            _CONSOLIDATED_VALUE,
            _SECOND_QUARTER_VALUE,
            _DIFFERENCE_LINE,
        )
    )


def _series_chart() -> str:
    return "\n".join(
        (
            "```mermaid",
            "xychart-beta",
            '    title "Resultado neto consolidado"',
            '    x-axis ["1T26", "2T26"]',
            '    y-axis "ARS" 21262335 --> 81956525',
            "    bar [21262335, 81956525]",
            "```",
            "BYMA|2026-03-31|income_statement|consolidated|net_income",
            "BYMA|2026-06-30|income_statement|consolidated|net_income",
        )
    )


def _docling_modules() -> set[str]:
    import sys

    return {
        name
        for name in sys.modules
        if name == "docling" or name.startswith("docling.")
    }


def _imports_docling(path: Path) -> bool:
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module]
        if any(name == "docling" or name.startswith("docling.") for name in names):
            return True
    return False


def _picture_sources() -> list[Path]:
    root = Path(__file__).resolve().parents[2]
    return [
        Path(__file__),
        root / "src" / "claimledger" / "crop" / "cut.py",
        root / "src" / "claimledger" / "crop" / "attach.py",
        root / "src" / "claimledger" / "crop" / "__init__.py",
        root / "src" / "claimledger" / "openwebui" / "reply.py",
        root / "src" / "claimledger" / "period" / "difference.py",
        root / "src" / "claimledger" / "period" / "__init__.py",
        root / "src" / "claimledger" / "chart" / "series.py",
        root / "src" / "claimledger" / "chart" / "__init__.py",
    ]


def test_reply_picture_follows_card(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert [path.name for path in _picture_sources() if _imports_docling(path)] == []
    before_docling = _docling_modules()
    digest, earlier, later = _prepare_picture(tmp_path, monkeypatch)
    assert earlier != later
    assert "data:image/png;base64" in earlier

    match = reply(digest, _CONSOLIDATED_QUESTION)
    assert match == _with_agent_trailing(_consolidated_card() + "\n" + earlier)
    assert "```mermaid" not in match
    assert match.startswith(_consolidated_card() + "\n")
    assert match.endswith(ABSTENTION_TEMPLATE)
    assert match.count("data:image/png;base64") == 1
    assert later not in match
    assert _DIFFERENCE_LINE not in match

    abstain = reply(digest, _ABSTAIN_QUESTION)
    assert abstain == _with_agent_trailing(_abstain_card())
    assert abstain.endswith(ABSTENTION_TEMPLATE)
    assert "```mermaid" not in abstain
    assert "data:image" not in abstain
    assert _CONSOLIDATED_VALUE not in abstain.split(ABSTENTION_TEMPLATE)[0]
    assert _PARENT_VALUE not in abstain
    assert _DIFFERENCE_LINE not in abstain

    compare = reply(digest, _COMPARE_QUESTION)
    assert compare == _with_agent_trailing(
        _compare_card() + "\n" + earlier + "\n" + later + "\n" + _series_chart()
    )
    assert "60694190" not in compare.split("```mermaid", 1)[1].split(ABSTENTION_TEMPLATE)[0]
    card_only = compare.split("\n![crop]", 1)[0]
    assert card_only == _compare_card()
    assert "60694190" in card_only
    assert "delta" not in card_only.casefold()
    assert compare.count("data:image/png;base64") == 2
    assert _docling_modules() == before_docling


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
    assert "DEEPSEEK_API_KEY" in compose
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


def test_wave_c_still_waits() -> None:
    repo = Path(__file__).resolve().parents[2]
    packages = {
        path.name
        for path in (repo / "src" / "claimledger").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    }
    assert "crop" in packages
    assert "period" in packages
    assert "chart" in packages
    assert "orchestrate" in packages
    assert "book" in packages
    assert "agent" in packages
    assert packages.isdisjoint({"charts"})

    active = [
        path.name
        for path in (repo / "openspec" / "changes").iterdir()
        if path.is_dir() and path.name != "archive"
    ]
    assert any((repo / "openspec" / "changes" / "archive").glob("*-fase-8-crop"))
    assert "fase-8-crop" not in active
    assert any((repo / "openspec" / "changes" / "archive").glob("*-fase-11-neo4j"))
    assert "fase-11-neo4j" not in active
    assert not any(name.startswith(("fase-10", "fase-11")) for name in active)


def _kernel_allowlist() -> tuple[str, ...]:
    import ast

    repo = Path(__file__).resolve().parents[2]
    tree = ast.parse((repo / "tests" / "test_identity.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != "_kernel_scan_paths":
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "relatives" for target in stmt.targets
            ):
                return tuple(elt.value for elt in stmt.value.elts)
    raise AssertionError("kernel allowlist missing")


def _evidence_keys() -> set[str]:
    import ast

    repo = Path(__file__).resolve().parents[2]
    tree = ast.parse(
        (repo / "src" / "claimledger" / "http" / "claims.py").read_text(encoding="utf-8")
    )
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_evidence"
    )
    keys: set[str] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
    return keys


def test_query_and_card_stay_picture_free() -> None:
    import dataclasses
    import tomllib

    from claimledger.card.card import ClaimCard, render_card
    from claimledger.http.app import build_app
    from claimledger.http.claims import claims_query
    from claimledger.ledger import RECIPE_ROWS, Ledger
    from claimledger.lookup import understand
    from claimledger.query import query
    from claimledger.retrieval.drawers import Candidate

    consolidated = claims_query({"question": _CONSOLIDATED_QUESTION}, Ledger.seed())
    parent = claims_query({"question": _PARENT_QUESTION}, Ledger.seed())
    compared = claims_query({"question": _COMPARE_QUESTION}, Ledger.seed())
    for body, value in (
        (consolidated, _CONSOLIDATED_VALUE),
        (parent, _PARENT_VALUE),
    ):
        dumped = json.dumps(body)
        assert body["claim"]["value"] == value
        assert value in dumped
        assert "image" not in dumped
        assert "bbox" not in dumped
        assert "data:image" not in dumped
    compared_dump = json.dumps(compared)
    assert [item["value"] for item in compared["claims"]] == [
        _CONSOLIDATED_VALUE,
        _SECOND_QUARTER_VALUE,
    ]
    assert "60694190" not in compared_dump
    assert "mermaid" not in compared_dump
    series = claims_query({"question": _SERIES_QUESTION}, Ledger.seed())
    series_dump = json.dumps(series)
    book = claims_query({"question": _BOOK_QUESTION}, Ledger.seed())
    book_dump = json.dumps(book)
    assert book["status"] == "abstained"
    assert "21262335" not in book_dump
    assert "mermaid" not in book_dump
    assert "mermaid" not in series_dump
    assert "xychart" not in series_dump
    assert "60694190" not in series_dump
    assert "xychart" not in compared_dump
    assert "image" not in compared_dump
    assert "bbox" not in compared_dump
    assert "data:image" not in compared_dump
    assert _evidence_keys() == {"document_id", "page", "text"}

    result = query(understand(_CONSOLIDATED_QUESTION), Ledger.seed())
    card = render_card(
        (
            Candidate(drawer="tables", text=_NEIGHBOR_CONSOLIDATED, ref="#/tables/1"),
            Candidate(drawer="tables", text=_NEIGHBOR_PARENT, ref="#/tables/1"),
        ),
        result,
    )
    assert {field.name for field in dataclasses.fields(ClaimCard)} == {
        "seal",
        "chips",
        "rows",
        "values",
        "sentence",
        "reason",
        "difference",
    }
    assert card.difference == ""
    assert card.values == (_CONSOLIDATED_VALUE,)
    rendered = card_text(card)
    assert "data:image" not in rendered
    assert "bbox" not in rendered
    assert _CONSOLIDATED_VALUE in rendered

    claims = build_app()
    claim_routes = [route for route in claims.routes if getattr(route, "path", None)]
    assert [route.path for route in claim_routes] == ["/claims/query"]
    assert claim_routes[0].methods == {"POST"}

    repo = Path(__file__).resolve().parents[2]
    project = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["dependencies"] == []
    allowlist = _kernel_allowlist()
    assert len(allowlist) == 13
    assert not any("crop" in path for path in allowlist)
    assert not any("period" in path for path in allowlist)
    assert not any("chart" in path for path in allowlist)
    assert not any("orchestrate" in path for path in allowlist)
    assert not any("book" in path for path in allowlist)
    assert not any("agent" in path for path in allowlist)
    assert ("2026-03-31", "consolidated", "net_income", "21262335") in RECIPE_ROWS
    assert ("2026-03-31", "parent_attributable", "net_income", "21259769") in RECIPE_ROWS
    gold = (repo / "tests" / "test_gold_v1.py").read_text(encoding="utf-8")
    assert 'ID_01_VALUE = "21262335"' in gold
    assert '"21259769"' in gold
    assert "60694190" not in gold
    for extra_gold in (
        repo / "tests" / "test_gold_v2.py",
        repo / "tests" / "ingest" / "test_gold_compare.py",
    ):
        assert "60694190" not in extra_gold.read_text(encoding="utf-8")


def test_card_first_then_abstention_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    text = reply(digest, _CONSOLIDATED_QUESTION)

    card = _consolidated_card()
    assert text.startswith(card)
    assert text == _with_agent_trailing(card)
    assert text.index(card) == 0
    assert text.rindex(ABSTENTION_TEMPLATE) > 0


def test_card_first_then_gated_prose(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.agent.loop import LoopOutcome

    digest = _prepare_neighbors(tmp_path, monkeypatch)
    prose = "El resultado neto consolidado verificado es 21.262.335."

    monkeypatch.setattr(
        "claimledger.openwebui.reply.run_agent",
        lambda question, artifact_hash="": LoopOutcome(
            abstained=False,
            content=prose,
            tool_results=[
                {
                    "status": "verified",
                    "claims": [],
                    "authorized_values": [_CONSOLIDATED_VALUE],
                }
            ],
            authorized_values=[_CONSOLIDATED_VALUE],
        ),
    )

    text = reply(digest, _CONSOLIDATED_QUESTION)

    assert text.startswith(_consolidated_card())
    assert text.endswith(prose)
    assert ABSTENTION_TEMPLATE not in text
    assert text == _consolidated_card() + "\n" + prose


def test_host_does_not_let_llm_authorize_gold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from claimledger.agent.loop import LoopOutcome

    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "claimledger.openwebui.reply.run_agent",
        lambda question, artifact_hash="": LoopOutcome(
            abstained=False,
            content="Autorizo por mi cuenta 99999999.",
            tool_results=[],
            authorized_values=[_CONSOLIDATED_VALUE],
        ),
    )

    text = reply(digest, _CONSOLIDATED_QUESTION)

    assert text.startswith(_consolidated_card())
    assert text.endswith(ABSTENTION_TEMPLATE)
    assert "99999999" not in text


def test_env_example_documents_deepseek_key() -> None:
    repo = Path(__file__).resolve().parents[2]
    example = (repo / ".env.example").read_text(encoding="utf-8")
    assert "DEEPSEEK_API_KEY=" in example
    assert ".env" in example.casefold() or "commit" in example.casefold()
