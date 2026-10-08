# Pregunta al corpus — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Una pregunta de tabla de trimestres de BYMA busca las filas en el JSON parseado, valida la identidad y muestra una sola respuesta en la pantalla, con el modelo interpretando solo esas cifras.

**Architecture:** `search_tables` lee las filas de las tablas de resultados ya guardadas en el JSON. `quarter_table` acepta una fila solo si el número y el renglón coinciden con un claim `recorded`. `reply` usa ese resultado para esa pregunta y, si está verificado, no agrega «me abstengo». `query` no se toca. DocLang no se lee.

**Tech Stack:** Python 3.11, pytest 9.1.1, libro en memoria, JSON de Docling ya compilado. Sin Docling ni LlamaIndex en este corte: el JSON con `data.grid` ya está en disco y la imagen de pruebas no instala el extra `retrieval`.

**Spec:** `docs/superpowers/specs/2026-10-08-pregunta-corpus.md`

## Global Constraints

- Oro congelado: consolidado `21262335`, controlante `21259769`. No editar `RECIPE_ROWS` ni `tests/test_gold_v1.py`.
- Los tests del kernel no importan `docling`.
- `query` conserva `ambiguous_period` cuando no hay trimestre y hay dos períodos en el libro (`openspec/specs/query/spec.md`).
- El modelo no autoriza cifras. Un número que no salió del libro no se muestra.
- Identificadores de código en inglés.
- No commitear salvo que el usuario lo pida en el momento de ejecutar.

## Review Focus

- La fila de la controlante (`21.259.769` / `21259769`) no puede colarse en la tabla consolidada. Lo cubre la tarea 2.
- Una ficha `VERIFICADO` no puede terminar en `ME ABSTENGO`. Lo cubre la tarea 1.
- Si el modelo escribe `99999999`, ese número no aparece. Lo cubre la tarea 1.
- «resultado neto consolidado» sin trimestre sigue en `ambiguous_period` dentro de `query`. No hay tarea que lo cambie; la tarea 2 no llama a `query` para la tabla.
- Si el JSON no contiene el número, esa cifra no se muestra. Lo cubre la tarea 2.
- Pedir los últimos 4 trimestres no debe tomar el camino de la tabla. Lo cubre la tarea 2.

---

### Task 1: Una sola voz en la pantalla

**Files:**
- Modify: `src/claimledger/openwebui/reply.py`
- Test: `tests/openwebui/test_host.py`

**Interfaces:**
- Consumes: `QueryResult`, `ABSTENTION_TEMPLATE`, `run_agent`, `gate_prose`, `_chip` en `claimledger.card.card`
- Produces: `verified_sentence(result: QueryResult) -> str`. Texto exacto: `Verificado. ` + chips unidos por `; ` + cada uno con `: ` y el `value`, y un punto final. Ejemplo: `Verificado. BYMA · 1T26 · Consolidado · Resultado neto: 21262335.`

Cuando `result.status != "verified"`, `reply` devuelve solo `ABSTENTION_TEMPLATE`. No agrega el sello, ni `recipe_no_extract`, ni una segunda copia.

Cuando está verificado y el modelo no devuelve una frase autorizada, `reply` devuelve la ficha, un salto de línea y `verified_sentence`. No agrega `ABSTENTION_TEMPLATE`.

Cuando el modelo devuelve una frase cuyos números están autorizados, esa frase reemplaza a `verified_sentence`. Si la frase trae un número de más, se descarta y queda `verified_sentence`.

- [ ] **Step 1: Write the failing test**

En `tests/openwebui/test_host.py`, cambiar el final esperado de las respuestas verificadas. Donde hoy se exige `text.endswith(ABSTENTION_TEMPLATE)` después de una ficha verificada, exigir que `ABSTENTION_TEMPLATE not in text` y que el texto termine en la frase fija.

Caso consolidado, sin clave del modelo:

```python
def test_verified_card_does_not_abstain_underneath(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    text = reply(digest, _CONSOLIDATED_QUESTION)

    assert text.startswith(_consolidated_card() + "\n")
    assert text.endswith(
        "Verificado. BYMA · 1T26 · Consolidado · Resultado neto: 21262335."
    )
    assert ABSTENTION_TEMPLATE not in text
    assert _PARENT_VALUE not in text
```

Caso abstención, una sola vez:

```python
def test_abstain_is_one_sentence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)

    text = reply(digest, _ABSTAIN_QUESTION)

    assert text == ABSTENTION_TEMPLATE
    assert "recipe_no_extract" not in text
    assert _CONSOLIDATED_VALUE not in text
    assert "VERIFICADO" not in text
```

Caso modelo inventando un número (reemplaza el assert de `test_host_does_not_let_llm_authorize_gold` que hoy espera el template al final):

```python
    assert "99999999" not in text
    assert ABSTENTION_TEMPLATE not in text
    assert text.endswith(
        "Verificado. BYMA · 1T26 · Consolidado · Resultado neto: 21262335."
    )
```

Actualizar en el mismo archivo los otros `endswith(ABSTENTION_TEMPLATE)` que siguen a una ficha que empieza con `VERIFICADO` (controlante, comparar, últimos 4, libro). Esos pasan a terminar en `verified_sentence` del resultado que ya muestran. El comparar tiene dos chips, en este orden, unidos por `; `:

```text
Verificado. BYMA · 1T26 · Consolidado · Resultado neto: 21262335; BYMA · 2T26 · Consolidado · Resultado neto: 81956525.
```

Dejar `test_card_first_then_gated_prose` como está: si el modelo dice solo `21.262.335`, esa frase sigue al final y el template no aparece.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/openwebui/test_host.py::test_verified_card_does_not_abstain_underneath tests/openwebui/test_host.py::test_abstain_is_one_sentence -v`

Expected: FAIL porque el texto sigue terminando en `ABSTENTION_TEMPLATE`.

- [ ] **Step 3: Write minimal implementation**

En `src/claimledger/openwebui/reply.py`:

```python
def verified_sentence(result: QueryResult) -> str:
    from claimledger.card.card import _chip

    bits = [f"{_chip(claim)}: {claim.value}" for claim in result.claims]
    return "Verificado. " + "; ".join(bits) + "."


def _narration(question: str, artifact_hash: str, result: QueryResult) -> str:
    if result.status != "verified":
        return ABSTENTION_TEMPLATE
    outcome = run_agent(question, artifact_hash=artifact_hash)
    if outcome.abstained or not outcome.authorized_values:
        return verified_sentence(result)
    gated = gate_prose(
        outcome.content,
        outcome.authorized_values,
        regenerate=lambda: run_agent(question, artifact_hash=artifact_hash).content,
    )
    if not gated.allowed:
        return verified_sentence(result)
    return gated.text
```

`reply` arma el cuerpo de la ficha solo si `result.status == "verified"`. Si no, devuelve `ABSTENTION_TEMPLATE` y no llama a la ficha. Si sí, devuelve `body + "\n" + _narration(...)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/openwebui/test_host.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

No commitear salvo pedido explícito del usuario.

---

### Task 2: La tabla de trimestres valida identidad

**Files:**
- Create: `src/claimledger/corpus/quarter.py`
- Create: `src/claimledger/corpus/__init__.py` (vacío)
- Test: `tests/corpus/test_quarter.py`

**Interfaces:**
- Consumes: `understand`, `Ledger`, `identity_key`, `fold`, `signed_ars`, `FinancialClaim`, `QueryResult`
- Produces:
  - `asks_quarter_table(question: str) -> bool`
  - `row_supports(claim: FinancialClaim, row_text: str) -> bool`
  - `quarter_table(question: str, ledger: Ledger, rows: tuple[str, ...]) -> QueryResult | None`

`asks_quarter_table` es verdadero si el texto plegado contiene `trimestre` y (`tabla` o `todos`), y no contiene `ultimo`. Así «últimos 4 trimestres» sigue en el plan que ya existe.

`quarter_table` devuelve `None` si no es esa pregunta, o si `understand` no deja `metric == "net_income"`. No llama a `query`.

Si es la pregunta y el alcance es el de `understand` (consolidado, o controlante si la frase lo dice), recorre `2026-03-31` y `2026-06-30`. Se queda con el claim `recorded` solo cuando alguna fila de `rows` pasa `row_supports`. Si no queda ninguno, devuelve `QueryResult(status="abstained", reason="no_matching_claim")`. Si queda alguno, `status="verified"` y la identidad `BYMA|*|income_statement|<scope>|net_income`.

`row_supports`: el `value` del claim está entre los importes de la fila (`signed_ars` sobre tokens `\(?\d{1,3}(?:\.\d{3})+\)?`). Si el alcance es `parent_attributable`, la fila plegada tiene `controlante` o `atribuible`. Si el alcance es `consolidated`, la fila tiene `resultado neto` o `neto del`, y no tiene `atribuible` ni `controlante`.

- [ ] **Step 1: Write the failing test**

`tests/corpus/test_quarter.py`:

```python
from claimledger.ledger import Ledger

TABLE = "armá una tabla con todos los trimestres de BYMA"
PARENT_TABLE = "armá una tabla con todos los trimestres de la controlante"
LAST_FOUR = "Compará el resultado neto consolidado de los últimos 4 trimestres"
ROWS = (
    "RESULTADO NETO DEL PERÍODO 21.262.335",
    "Resultado neto atribuible a la sociedad controlante 21.259.769",
    "RESULTADO NETO DEL PERÍODO 81.956.525",
)


def test_quarter_table_lists_both_consolidated_and_skips_parent() -> None:
    from claimledger.corpus.quarter import quarter_table

    result = quarter_table(TABLE, Ledger.seed(), ROWS)

    assert result is not None
    assert result.status == "verified"
    assert [claim.value for claim in result.claims] == ["21262335", "81956525"]
    assert all(claim.scope == "consolidated" for claim in result.claims)
    assert "21259769" not in [claim.value for claim in result.claims]


def test_parent_table_does_not_take_the_group_number() -> None:
    from claimledger.corpus.quarter import quarter_table

    result = quarter_table(PARENT_TABLE, Ledger.seed(), ROWS)

    assert result is not None
    assert [claim.value for claim in result.claims] == ["21259769"]


def test_missing_row_drops_the_number() -> None:
    from claimledger.corpus.quarter import quarter_table

    result = quarter_table(
        TABLE,
        Ledger.seed(),
        ("RESULTADO NETO DEL PERÍODO 21.262.335",),
    )

    assert result is not None
    assert [claim.value for claim in result.claims] == ["21262335"]


def test_last_four_is_not_the_table() -> None:
    from claimledger.corpus.quarter import asks_quarter_table, quarter_table

    assert asks_quarter_table(LAST_FOUR) is False
    assert quarter_table(LAST_FOUR, Ledger.seed(), ROWS) is None


def test_empty_rows_abstain() -> None:
    from claimledger.corpus.quarter import quarter_table

    result = quarter_table(TABLE, Ledger.seed(), ())

    assert result is not None
    assert result.status == "abstained"
    assert result.claims == ()
```

`Ledger.seed()` ya tiene los dos trimestres consolidados y el de la controlante en 1T26. El 2T26 de la controlante también está en `RECIPE_ROWS` (`81946993`). La prueba de la controlante, con una sola fila de controlante, debe devolver solo `21259769`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/corpus/test_quarter.py -v`

Expected: FAIL con `ModuleNotFoundError: claimledger.corpus`

- [ ] **Step 3: Write minimal implementation**

Crear `src/claimledger/corpus/__init__.py` vacío y `src/claimledger/corpus/quarter.py` con las tres funciones de la interfaz. Importes de `signed_ars` desde `claimledger.digits`. Períodos: `PERIOD_1T26` y `PERIOD_2T26` desde `claimledger.identity`. No importar `docling`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/corpus/test_quarter.py tests/test_query.py::test_ambiguous_period_abstains -v`

Expected: PASS. El segundo confirma que `query` sigue callando si no hay trimestre.

- [ ] **Step 5: Commit**

No commitear salvo pedido explícito del usuario.

---

### Task 3: Buscar las filas en el JSON parseado

**Files:**
- Create: `src/claimledger/corpus/search.py`
- Modify: `src/claimledger/ledger.py` (un método de lectura)
- Test: `tests/corpus/test_search.py`
- Test: `tests/test_ledger.py` (el método nuevo)

**Interfaces:**
- Consumes: `Ledger.claims() -> tuple[FinancialClaim, ...]`, `load` de `claimledger.ingest.store`, `_body_tables`, `_table_grid`, `_is_consolidated_income_table`, `_row_label`, `_cell_text` de `claimledger.ingest.extract`
- Produces: `search_tables(question: str, claims: tuple[FinancialClaim, ...]) -> tuple[str, ...]`

`Ledger.claims` devuelve los claims del libro, en un orden estable (el de inserción). No escribe.

`search_tables` junta los `artifact_hash` de `claim.evidence`. Por cada hash, `load`. Si `load` lanza `IngestError`, saltea ese hash. De cada tabla de cuerpo que `_is_consolidated_income_table` acepte, emite una cadena por fila: etiqueta y textos de celda, separados por espacio. No abre archivos `.dclg`. El argumento `question` no descarta la fila vecina: las dos filas del resultado neto salen juntas. La identidad la decide `row_supports`.

- [ ] **Step 1: Write the failing test**

`tests/test_ledger.py`, junto a los tests de `upsert`:

```python
def test_claims_returns_what_was_upserted() -> None:
    ledger = Ledger()
    first = _claim("consolidated", "1")
    second = _claim("parent_attributable", "2")
    ledger.upsert(first)
    ledger.upsert(second)

    assert [item.scope for item in ledger.claims()] == [
        "consolidated",
        "parent_attributable",
    ]
```

Usar el helper `_claim` que ese archivo ya tenga. Si el helper no existe, construir dos `FinancialClaim` con `identity_key` distinto y el mismo patrón que `Ledger.seed`.

`tests/corpus/test_search.py` arma un JSON mínimo y un claim cuyo `artifact_hash` apunta a ese archivo, parcheando `artifacts_dir`:

```python
def test_search_returns_both_neighbor_rows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from claimledger.corpus.search import search_tables
    from claimledger.ingest import store as ingest_store

    digest = "abc"
    payload = {
        "body": {"children": [{"$ref": "#/tables/0"}]},
        "tables": [
            {
                "data": {
                    "grid": [
                        [{"text": "RESULTADO BRUTO"}, {"text": "1"}],
                        [{"text": "RESULTADO NETO DEL PERÍODO"}, {"text": "21.262.335"}],
                        [
                            {"text": "Resultado neto atribuible a la sociedad controlante"},
                            {"text": "21.259.769"},
                        ],
                    ]
                }
            }
        ],
    }
    folder = tmp_path / "docling"
    folder.mkdir()
    (folder / f"{digest}.json").write_text(
        __import__("json").dumps(payload), encoding="utf-8"
    )
    monkeypatch.setattr(ingest_store, "artifacts_dir", lambda: folder)
    claim = _claim_with_hash(digest)

    rows = search_tables("tabla de trimestres", (claim,))

    assert any("21.262.335" in row and "controlante" not in row.casefold() for row in rows)
    assert any("21.259.769" in row for row in rows)
```

`_is_consolidated_income_table` exige una etiqueta plegada igual a `resultado bruto` y otra con `participacion controlante`. El JSON de arriba no alcanza: la fila de la controlante tiene que ser exactamente la que `_is_parent_label` reconoce (`participacion controlante` y sin `no controlante`). Ajustar esa celda a `Participación controlante en el resultado neto` antes de dar el test por bueno, y dejar la fila `RESULTADO NETO DEL PERÍODO` como la consolidada. Si `_is_consolidated_income_table` sigue en falso, el test falla por la razón correcta y el JSON se corrige hasta que la tabla sea la de resultados. No relajar el detector.

Agregar una fila `.dclg` al lado y assert de que `search_tables` no la lee: el test espía no hace falta si el código solo llama a `load` del JSON. Un comentario en el test nombra el `.dclg` y el assert es que las filas salen del grid.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/corpus/test_search.py tests/test_ledger.py::test_claims_returns_what_was_upserted -v`

Expected: FAIL porque `claims` y `search_tables` no existen.

- [ ] **Step 3: Write minimal implementation**

`Ledger.claims` devuelve `tuple(self._book.values())`.

`search_tables` como en la interfaz. Un hash que falla `load` se saltea. No importar `docling`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/corpus/test_search.py tests/test_ledger.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

No commitear salvo pedido explícito del usuario.

---

### Task 4: La respuesta de la pantalla usa búsqueda y tabla

**Files:**
- Modify: `src/claimledger/openwebui/reply.py`
- Test: `tests/openwebui/test_host.py`

**Interfaces:**
- Consumes: `search_tables`, `quarter_table`, `verified_sentence`, `candidates_from_claims`, `render_card`, `card_text`
- Produces: el mismo `reply(artifact_hash: str, question: str) -> str`

Si `quarter_table` no devuelve `None`, ese `QueryResult` es el de la pantalla. No se llama a `execute`, `ask` ni `measure`. No se llama a `difference`. No se llama a `draw`. Las filas de la ficha salen de la evidencia de los claims aceptados.

Si devuelve `None`, sigue el camino que ya existe (últimos 4, libro con el archivo Cypher, o `measure`).

- [ ] **Step 1: Write the failing test**

```python
def test_quarter_table_question_shows_both_periods_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    digest = _prepare_neighbors(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "claimledger.openwebui.reply.search_tables",
        lambda question, claims: (
            "RESULTADO NETO DEL PERÍODO 21.262.335",
            "Resultado neto atribuible a la sociedad controlante 21.259.769",
            "RESULTADO NETO DEL PERÍODO 81.956.525",
        ),
    )
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    text = reply(digest, "armá una tabla con todos los trimestres de BYMA")

    assert text.startswith("VERIFICADO\n")
    assert "BYMA · 1T26 · Consolidado · Resultado neto" in text
    assert "BYMA · 2T26 · Consolidado · Resultado neto" in text
    assert _CONSOLIDATED_VALUE in text
    assert _SECOND_QUARTER_VALUE in text
    assert _PARENT_VALUE not in text
    assert "21259769" not in text
    assert ABSTENTION_TEMPLATE not in text
    assert "```mermaid" not in text
    assert "Diferencia entre las dos cifras" not in text
    assert text.endswith(
        "Verificado. BYMA · 1T26 · Consolidado · Resultado neto: 21262335; "
        "BYMA · 2T26 · Consolidado · Resultado neto: 81956525."
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/openwebui/test_host.py::test_quarter_table_question_shows_both_periods_once -v`

Expected: FAIL. Hoy esa frase cae en `ambiguous_period` o en el silencio, y no lista los dos trimestres.

- [ ] **Step 3: Write minimal implementation**

Al inicio de `reply`, después de `book = recorded_book()`:

```python
listed = quarter_table(question, book, search_tables(question, book.claims()))
if listed is not None:
    result = listed
    candidates = (
        candidates_from_claims(result.claims) if result.status == "verified" else ()
    )
    if result.status != "verified":
        return ABSTENTION_TEMPLATE
    body = card_text(render_card(candidates, result, None))
    return body + "\n" + _narration(question, artifact_hash, result)
```

El resto de `reply` queda para cuando `listed is None`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/openwebui/test_host.py tests/corpus -v`

Expected: PASS. Las preguntas de un solo trimestre, la comparación y los últimos 4 siguen en su camino.

- [ ] **Step 5: Commit**

No commitear salvo pedido explícito del usuario.

---

### Task 5: El gráfico de una comparación arranca en cero

**Files:**
- Modify: `src/claimledger/chart/series.py` (`draw`)
- Test: `tests/chart/test_series.py`
- Test: `tests/openwebui/test_host.py` (el texto del eje en `_series_chart`)

**Interfaces:**
- Consumes: `ChartSpec` ya existente
- Produces: la misma `draw(spec) -> str`, con el eje `y-axis "ARS" 0 --> <máximo>`

La tabla de trimestres no dibuja gráfico. Este paso solo corrige la comparación, que hoy pone el piso del eje en `21262335` y deja la barra de marzo pegada al piso.

- [ ] **Step 1: Write the failing test**

En `tests/chart/test_series.py`, reemplazar el assert del eje:

```python
assert 'y-axis "ARS" 0 --> 81956525' in text
```

El mismo texto en `_series_chart` de `tests/openwebui/test_host.py`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/chart/test_series.py -v`

Expected: FAIL porque el eje dice `21262335 --> 81956525`.

- [ ] **Step 3: Write minimal implementation**

En `draw`, la línea del eje usa el literal `0` como piso y `high.value` como techo. No cambiar las barras ni las etiquetas.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/chart/test_series.py tests/openwebui/test_host.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

No commitear salvo pedido explícito del usuario.

---

## Self-review

- Circuito del spec: tarea 3 busca, tarea 2 verifica identidad, tarea 4 muestra una respuesta, tarea 1 hace hablar al modelo solo con cifras autorizadas.
- `query` y el oro no tienen tarea que los edite.
- DocLang no se abre: la tarea 3 solo llama a `load` del JSON.
- La captura (verificado + me abstengo + gráfico + diferencia + controlante) queda cubierta por la tarea 4.
- No hay marcadores `TBD`. El JSON de la tarea 3 depende de `_is_parent_label`; el step lo dice para no dar por verde un grid que el detector rechaza.
