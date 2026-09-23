# Fase 0 — listo para implementar

Leer [documento-rector.md](documento-rector.md) y [north-star.md](north-star.md). Este archivo es el **contrato de arranque**. Si no está acá, no se codea en Fase 0.

Objetivo: kernel + gold + pins. **Sin** Docling, Graph, LlamaIndex, Docker, Open WebUI, agentes, VLM.

---

## Qué entra

1. Modelos: `FinancialEvidence`, `FinancialClaim`, `identity_key` de 5 campos.
2. Servicios: normalizar período, resolver identidad (lookup léxico), upsert al ledger, verificar, abstenerse.
3. Gold portado: `identity_v1` (45) + `identity_v2` (26). **Números intactos.** IDs reescritos con la tabla de alias.
4. Pins declarados (aún no se importan en tests): `docling==2.130.0`, `docling-graph==1.9.1`.
5. Tests del kernel en memoria. Cero red, cero PDF.

## Qué no entra

Docling, Evidence Adapter real, Graph, índices, API HTTP, UI, orquestador, recortes, gráficos, Neo4j, VLM, press/presentation gold (`press_v1`, `presentation_v1`). Esos evals se portan **después**.

---

## Vocabulario de estados (cerrado)

| Dónde | Estado | Significa |
|-------|--------|-----------|
| Pipeline | `candidate` | Evidencia o fila propuesta. No es verdad. |
| Ledger (ingest) | `recorded` | El contrato matcheó; está en el libro. |
| Ledger | `conflicted` | Misma identidad, otro valor. No se pisa. |
| Query | `verified` | Responde **esta** pregunta. |
| Query | `rejected` | Candidato que no es la identidad pedida (ej. controlante). |
| Query | `abstained` | No hay una sola respuesta demostrable. |

`recorded` ≠ `verified`.

---

## Identidad: alias Claimprint → CLAIMLEDGER

`identity_key = issuer|period|statement|scope|metric`

Períodos (igual que v1): `1T26` → `2026-03-31`, `2T26` → `2026-06-30`.

| v1 (`scope\|metric`) | statement | scope | metric |
|----------------------|-----------|-------|--------|
| `consolidado\|resultado_neto` | `income_statement` | `consolidated` | `net_income` |
| `controlante\|resultado_atribuible_controladora` | `income_statement` | `parent_attributable` | `net_income` |
| `consolidado\|resultado_bruto` | `income_statement` | `consolidated` | `gross_profit` |
| `consolidado\|resultado_operativo` | `income_statement` | `consolidated` | `operating_income` |
| `consolidado\|resultado_antes_impuesto` | `income_statement` | `consolidated` | `income_before_tax` |
| `consolidado\|impuesto_ganancias` | `income_statement` | `consolidated` | `income_tax` |
| `consolidado\|resultado_no_controlante` | `income_statement` | `consolidated` | `nci_income` |

Canónico del vecino:

```text
BYMA|2026-03-31|income_statement|consolidated|net_income        = 21262335
BYMA|2026-03-31|income_statement|parent_attributable|net_income = 21259769
```

Las etiquetas del PDF (`RESULTADO NETO DEL PERÍODO`) son localizadores, no IDs. El lookup sigue en español; el ID sale en inglés.

Gold con `period=*` o `expected_identity=null` se porta tal cual (abstenerse / wildcard). No reinterpretar valores (`21262335`, `81956525`, `-14950948`, …).

Impuesto a las ganancias va **con signo**. En el recipe: `-14950948` / `-32731536`. `signed_ars("(14.950.948)")` → `-14950948`.

---

## Cómo se testea (sin PDF)

Se **siembra** un ledger en memoria con las filas del recipe (`financial_statement.json`: dos EEFF, 1T26 y 2T26). Después se tiran las preguntas del gold contra `query()`.

No se parsea nada. El kernel no ve Docling.

Cada caso identity/neighbor: un `verified` con ese `expected_value`. Si el gold trae `reject_values`, esos números **no** pueden ser la respuesta.

Cada caso comparison: dos claims `verified` (1T y 2T), mismos scope/metric, períodos distintos. El `expected_identity` usa `*` en period:

```text
BYMA|*|income_statement|consolidated|gross_profit
```

Fase 0 **no resta**. Devuelve las dos fichas. La diferencia en código es Fase 9.

Cada caso abstention: `abstained`. Sin claim. Sin valor.

Partición `narrative` (`na-01`…): se porta con `"skip": true`. El harness de capa 2 **no** las corre. No se inventa un número para “explicá el crecimiento”.

---

## Plata (`digits_ars`)

Portar tal cual Claimprint `schemas/money.py`:

- `21.262.335` → `21262335` (puntos de miles, sin coma).
- Vacío / None → None.
- `signed_ars`: paréntesis = negativo. El impuesto del recipe ya viene con `-`.
- En el claim, `value` es string de dígitos (y `-` si aplica). No flota. No `21,26 M`.
- `currency = "ARS"` en el piloto. `unit = null`.

---

## Período

Canónico **antes** del ID: `2026-03-31` | `2026-06-30`.

Tokens (después de `fold`: minúsculas, sin tildes):

| Va a 1T26 | Va a 2T26 |
|-----------|-----------|
| `1t26`, `1t 26`, `marzo`, `2026-03-31`, `31 de marzo`, `primer trimestre` | `2t26`, `2t 26`, `junio`, `2026-06-30`, `30 de junio`, `segundo trimestre` |

Los dos en la misma pregunta → `compare=true`, `period=None`.  
Ninguno y hay dos períodos en el libro para esa métrica → `abstained` / `ambiguous_period`.

Issuer en este gold: siempre `BYMA`. El lookup no extrae emisor de la pregunta. YPF + precio → `off_corpus`.

---

## Lookup (orden, no se inventa)

`fold` la pregunta. Después, **en este orden** (tesis de Claimprint; sin press/deck identity en Fase 0):

1. YPF + precio/cierre/3 de enero → `off_corpus`
2. memoria + resultado/neto/eeff → `recipe_no_extract`
3. comunicado + neto/consolidado/controlante/bruto/impuesto → `recipe_no_extract`
4. presentación/slides/deck + esas mismas métricas de P&L → `recipe_no_extract`
5. contrato/cláusula → `recipe_no_extract`
6. narrativa (`explica`, `crecimiento de ingresos`, `politica contable`, …) **y no** pide neto → route `narrative` (skipped en gold)
7. compare si aparece compar/vs/versus/mayor/diferencia/ambos períodos
8. resolver 1T / 2T / ambos
9. métrica, en este orden: no controlante → controlante/atribuible (salvo “no el atribuible”) → bruto → operativo → antes de impuesto → impuesto a las ganancias → default **neto consolidado**

Razones de abstención (cerradas): `off_corpus` | `recipe_no_extract` | `no_matching_claim` | `incomplete_comparison` | `ambiguous_period` | `unresolved_identity`.

`rejected` no es un return del lookup. Es: el store tenía al vecino; la query no lo eligió. El gold lo chequea con `reject_values`.

---

## Forma del gold portado

Mismos `id`, `partition`, `route`, `question`, `expected_value(s)`, `expected_period(s)`, `expected_source_page`, `expected_provenance`, `reject_values`, `skip`. Solo cambia `expected_identity`.

```json
"expected_identity": "BYMA|2026-03-31|income_statement|consolidated|net_income"
```

`aliases.json` = la tabla de la sección Identidad. Un test: cada clave v1 del gold original mapea 1:1.

---

## Modelos (forma, no código final)

```text
FinancialEvidence
  document_id
  artifact_hash      ← JSON Docling, vacío en Fase 0
  page
  text
  bbox               ← opcional; si existe, 0–1, x0≤x1, y0≤y1
  label              ← fila fuente

FinancialClaim
  identity_key
  issuer, period, statement, scope, metric
  value              ← dígitos, sin puntos (digits_ars)
  currency           ← ARS en el piloto
  unit               ← null o "ARS"
  evidence[]
  ledger_status      ← recorded | conflicted
```

Query no muta el ledger. Devuelve `verified` + un claim, o `verified` + dos claims si `compare`, o `abstained` + reason. No hay endpoint `rejected`: el vecino queda en el libro y no se elige.

Semilla mínima del ledger (recipe, dos PDFs):

| period | scope | metric | value |
|--------|-------|--------|-------|
| 2026-03-31 | consolidated | net_income | 21262335 |
| 2026-03-31 | parent_attributable | net_income | 21259769 |
| 2026-03-31 | consolidated | gross_profit | 60144176 |
| 2026-03-31 | consolidated | operating_income | 70223471 |
| 2026-03-31 | consolidated | income_before_tax | 36213283 |
| 2026-03-31 | consolidated | income_tax | -14950948 |
| 2026-03-31 | consolidated | nci_income | 2566 |
| 2026-06-30 | consolidated | net_income | 81956525 |
| 2026-06-30 | parent_attributable | net_income | 81946993 |
| 2026-06-30 | consolidated | gross_profit | 122610546 |
| 2026-06-30 | consolidated | operating_income | 143236114 |
| 2026-06-30 | consolidated | income_before_tax | 114688061 |
| 2026-06-30 | consolidated | income_tax | -32731536 |
| 2026-06-30 | consolidated | nci_income | 9532 |

Más, si el gold v1 lo pide: prior 1T26 `22362983` **no** es current. No se siembra como net_income del período.

`artifact_hash` / bbox pueden ir vacíos. `page=4`, `text` = etiqueta del recipe (`RESULTADO NETO DEL PERÍODO`, etc.).

---

## Esqueleto del repo

```text
pyproject.toml          # name=claimledger, python>=3.11, pytest
src/claimledger/
  identity.py           # identity_key, alias, normalize_period
  claim.py              # FinancialClaim + validación
  evidence.py
  ledger.py             # upsert: same id+value → append evidence; same id+other value → conflicted
  lookup.py             # pregunta → Intent (portar tesis de Claimprint)
  query.py              # Intent + ledger → verified | abstain
  digits.py             # digits_ars
evals/
  identity_v1.json      # IDs nuevos, valores iguales
  identity_v2.json
  aliases.json          # tabla de arriba
tests/
  test_identity.py
  test_ledger.py
  test_lookup.py
  test_query.py
  test_gold_v1.py
  test_gold_v2.py
```

Dependencias de Fase 0: pytest. **No** docling, llama-index, neo4j.

Portar de Claimprint (leer, no copiar el repo): `schemas/claim.py`, `schemas/lookup.py`, `evals/identity_v1.json`, `evals/identity_v2.json`, `recipes/financial_statement.json` (solo gold numérico + frases).

---

## Criterio de cierre

- `pytest` verde **sin** importar docling.
- `identity_key` inconsistente con los 5 campos → error.
- Vecino: pregunta consolidado → `21262335` verified; controlante no se elige.
- Pregunta ambigua / sin período cuando hay dos → `abstained`.
- Mismo ID, otro valor → `conflicted`, las dos evidencias quedan.
- Pins en `pyproject.toml` como metadata/opcional, no importados.

---

## Orden de commits (cuando se pida implementar)

1. `pyproject.toml` + esqueleto vacío + pins declarados.
2. identity + period + digits + aliases.
3. claim + evidence + validación.
4. ledger upsert.
5. lookup (frases de neto / controlante / períodos).
6. query verify / abstain.
7. gold v1 portado + tests.
8. gold v2 portado + tests.

Un paso por vez. Si un test pide Docling, está mal de fase.
