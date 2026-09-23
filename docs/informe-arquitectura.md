# CLAIMLEDGER — Informe de kickoff

Leer primero: [documento-rector.md](documento-rector.md) (canónico) y [north-star.md](north-star.md) (filtro corto). Este archivo es el detalle técnico de investigación.

Fecha: 23 septiembre 2026  
Repos: `CLAIMLEDGER` (vacío) · `Claimprint` (v1 congelada en `C:\Users\Equipo\Claimprint`)

## Veredicto

No reemplazar el kernel determinista de Claimprint por extracción LLM. Adoptar el **modelo de identidad** de Docling Graph (`graph_id_fields`, entity vs component, fusión determinista, provenance que nunca inventa ubicación). Docling Graph es la **capa de identidad de entidades y relaciones**, no un fichero ni el intérprete contable. Usar **Docling pinneado** como parse estructurado y **DocLang / OTSL** como formato de intercambio **cuando aporte valor**, para que la grilla de la tabla no muera al exportar Markdown o HTML plano.

El lookup exacto y el gold `identity_v1` / `identity_v2` (45 + 26 casos) son **contrato de regresión congelado**, no ejemplos. RAG y chat siguen siendo consumidores. **No hay etapa LLM para crear identidad.** El kernel es determinista; el LLM solo puede ayudar a recuperar candidatos.

CLAIMLEDGER es un proyecto **nuevo**. El nombre significa un **libro** de afirmaciones financieras verificadas: colección estructurada y trazable, no solo “claims sueltos”. El producto propio es esa capa: identidad, verificación, abstención, evaluación.

Tesis: **el retrieval encuentra evidencia; CLAIMLEDGER la convierte en una afirmación financiera verificable.**

Principio: **No verified claim, no answer.**

---

## Estado de los repos

| Repo | Estado |
|------|--------|
| CLAIMLEDGER | Vacío. No hay código, lockfile ni tests. |
| Claimprint | v1.0.0 shipped. Kernel en `schemas/`, gold en `evals/`, fixtures MinerU, RAGFlow opcional pin 0.26.4. |

Claimprint **se congela**. No se copia su arquitectura MinerU + RAGFlow. Se portan tesis, contrato, gold y trampas de vecinos.

---

## Pins (verificado 23 sep 2026)

`docling==2.130.0` está publicado. [GitHub Latest = v2.130.0](https://github.com/docling-project/docling/releases/tag/v2.130.0) (22 sep 15:33 UTC). [PyPI 2.130.0](https://pypi.org/project/docling/2.130.0/) subió el 22 sep 2026. El pin anterior 2.129.0 queda **superado**. El pin es `==2.130.0`, **sujeto a que pase el gold**. No flotar `>=`.

| Paquete | Pin | Fecha | Fuente |
|---------|-----|-------|--------|
| `docling` | **==2.130.0** | 22 sep 2026 | [PyPI 2.130.0](https://pypi.org/project/docling/2.130.0/) · [tag v2.130.0](https://github.com/docling-project/docling/releases/tag/v2.130.0) |
| `docling-graph` | **==1.9.1** | 17 jul 2026 | [PyPI](https://pypi.org/project/docling-graph/) |
| DocLang WG | intercambio opcional | 9 jun 2026 | [LF AI & Data](https://www.linuxfoundation.org/press/lf-ai-data-foundation-launches-doclang-specification-working-group-to-advance-an-open-standard-for-ai-native-documents) |

Python: Docling ≥3.10. Extra `xbrl` solo si hay instancias XBRL, no para los PDF BYMA del piloto.

Los tests del **kernel** no importan Docling. El pin entra en Fase 0 como dependencia declarada; el A/B de parse es Fase 1.

---

## Cómo se apilan las piezas

No son alternativas. Son capas.

```
                 DOCUMENTO
                    │
                    ▼
                ┌───────┐
                │Docling│
                └───┬───┘
                    │
           estructura + evidencia
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   Docling Graph           LlamaIndex
   identidad/contexto       candidatos
         │                     │
         └──────────┬──────────┘
                    ▼
             ┌──────────────┐
             │ CLAIMLEDGER  │
             │ Financial    │
             │ Claim        │
             │ Verification │
             │ Abstention   │
             └──────┬───────┘
                    │
             verified / abstain
                    │
                    ▼
              Open WebUI
```

DocLang es transversal (`DoclingDocument ↔ DocLang`) y **no** es un salto obligatorio.

| Capa | Pregunta | Pin / rol | Prohibido |
|------|----------|-----------|-----------|
| Docling | ¿Qué hay en el documento? | 2.130.0 · JSON `DoclingDocument` | Parser propio · Markdown como SoT |
| DocLang / OTSL | ¿Cómo intercambio la grilla sin aplastarla? | Intercambio opcional | Etapa artificial de cada request |
| Docling Graph | ¿Qué entidades y relaciones hay? | 1.9.1 · capa de identidad, no fichero | Interpretar el claim contable / extraer P&L con LLM |
| LlamaIndex | ¿Dónde están los candidatos relevantes? | `DoclingReader` JSON + `DoclingNodeParser` | Decidir el claim · export markdown default |
| CLAIMLEDGER | ¿Qué afirmación financiera es y puedo demostrarla? | Producto · libro de claims | Inventar provenance · responder sin claim |
| Open WebUI | ¿Cómo se lo muestro al usuario? | OpenAI-compatible o MCP/OpenAPI | Pipelines · lógica financiera en la UI |

RAGFlow **queda fuera**. Eso **supersede** la arquitectura de hoy que lo dejaba como consumidor. Motivo: ya mezcla parse, chunk, retrieval, agents y UI; y el caso vivo demostró que aplana tablas HTML y concatena celdas (`21.259.7692.566…`).

---

## Qué hay que conservar de Claimprint

Leído en código, no en slides.

### Contrato actual (`schemas/claim.py`)

```text
identity_key = issuer|period|scope|metric
ejemplo     = BYMA|2026-03-31|consolidado|resultado_neto
```

- `Claim` es dataclass frozen. `validate_claim` exige value y period no vacíos, `source_page` null o > 0, `identity_key` consistente, bbox 0–1 si existe.
- Provenance (`source_page`, `source_text`, `document_id`, `parse_artifact_hash`, `source_bbox`) **está fuera** de la identidad.
- El projector `claims_from_financial_statement` emite dos claims distintos: consolidado/neto y controlante/atribuible. Un valor vacío no emite claim (no hay cascada).

### Lookup (`schemas/lookup.py`)

Capa 2 léxica. Cero embeddings.

- Default “resultado neto / ganancia neta / utilidad neta” → consolidado / `resultado_neto`.
- “controlante / atribuible / propietarios” → controlante / `resultado_atribuible_controladora`.
- “no controlante” es otra métrica (`2566` en 1T26), no el neto.
- Comunicado o deck pidiendo P&L → `abstain` / `recipe_no_extract`.
- Periodo ausente + varios periodos en store → `ambiguous_period`.
- Comparación con un solo periodo → `incomplete_comparison`.

### Gold

- `evals/identity_v1.json` — 45 casos. Neto vs controlante, 1T26 vs 2T26, abstenciones.
- `evals/identity_v2.json` — 26 casos. Filas vecinas P&L (bruto, operativo, EBT, impuesto, NCI).
- Recipe gold `recipes/financial_statement.json`: 1T26 consolidado `21262335`, controlante `21259769`, prior a ignorar `22362983`.

### Provenance (`schemas/provenance.py`)

`match_bbox()` es best-effort. Sin sidecar match → `source_bbox=null`. **Nunca inventa página.** Eso ya es la escalera fail-empty de Graph.

### Tesis medida (README / evaluation)

Retrieval solo (keyword / vector / hybrid) empata Recall@5 **0.35** / MRR **0.2042** (n=20). Con claims inyectados, chat 10/10 en valor, cita, evidencia y abstención. El salto no es mejor retrieval: es identidad resuelta **antes** de generar.

Portar: tesis, identity, lookup, gold, recipes-como-contrato, `digits_ars`, periodo canónico, abstención, neighbor trap.

---

## Qué no hay que copiar

| Dejar atrás | Motivo |
|-------------|--------|
| MinerU como SoT de parse | Benchmark histórico. No dependencia arquitectónica. |
| RAGFlow + `push_claims` | El flatten mató consolidado/controlante. |
| `select_page()` por keyword | Primera página con keyword. No es ranking de layout. |
| Primer monto = current, segundo = comparativo | Heurística posicional BYMA. |
| Bbox vía sidecar MinerU / chunks RAGFlow | Reemplazar por ledger Docling/Graph. |
| `vendor/ragflow-docker` | Stack de demo, ≥16 GB. |

---

## Identidad en CLAIMLEDGER

Claimprint v1 usa 4 campos en español (`consolidado`, `resultado_neto`). El brief nuevo propone 6: `issuer + period + statement + scope + metric + unit + currency`.

Graph lo dice explícito: una persona, un documento o una **línea de P&L** son **entities**; un monto, una unidad o una moneda son **components** (`is_entity=False`) y se deduplican por contenido. [Entities vs Components](https://docling-project.github.io/docling-graph/fundamentals/schema-definition/entities-vs-components).

Recomendación para repo nuevo:

```text
graph_id_fields = ["issuer", "period", "statement", "scope", "metric"]
identity_key    = BYMA|2026-03-31|income_statement|consolidated|net_income
```

| Campo | Rol | ¿En el ID? | Nota |
|-------|-----|------------|------|
| issuer | entity | sí | `BYMA`, canónico |
| period | entity | sí | `2026-03-31`, nunca `1T26` crudo |
| statement | entity | sí (nativo v2) | `income_statement` |
| scope | entity | sí | `consolidated` vs `parent_attributable` |
| metric | entity | sí | `net_income` — no recortar |
| value + currency + unit | `MonetaryAmount` component | no | El monto no identifica |
| page / bbox / span / refs | `__provenance__` | no | Fail-empty |

Por qué no meter `unit`/`currency` en el ID: Graph trata montos como component. Meterlos parte el mismo claim si la moneda falta o se infiere. Si más adelante el mismo indicador aparece en ARS y USD, entonces `currency` entra al ID y se versiona el gold.

Por qué 5 campos está bien aunque Graph pida 1–2 en dense: esa cautela es para que el **LLM reproduzca** IDs. En CLAIMLEDGER los campos los escribe el recipe / lookup, no un modelo. No recortar `scope` ni `metric`.

Etiquetas en español (`RESULTADO NETO DEL PERÍODO`, `consolidado`) son **localizadores y sinónimos**, no identidad. Tabla de alias → IDs canónicos en inglés.

`__provenance__` no entra al hash: dos evidencias del mismo claim son el mismo nodo. [Data Grounding & Provenance](https://docling-project.github.io/docling-graph/fundamentals/graph-management/provenance): escalera verbatim → observed → document-scope → unresolved. **Nunca fabrica página.** Token cost cero.

Merge (1T26 + 2T26 + comunicado + deck): mismo ID se pliega; conflicto de valor se audita (`keep-first` / `keep-all` / `variants`); alias de emisor → HITL, no auto-merge. Identidades solo locales (`linea=3`) se parten entre documentos no emparentados. El compuesto issuer|period|statement|scope|metric es globalmente único: correcto. [merge command](https://docling-project.github.io/docling-graph/usage/cli/merge-command).

---

## Docling — parse, no chat

Docling convierte PDF/Office/XBRL a `DoclingDocument` y exporta JSON, HTML, DocLang, Markdown. [Docling](https://docling-project.github.io/docling/) · [GitHub](https://github.com/docling-project/docling).

Lo que importa para EEFF BYMA:

- **Tablas de primera clase.** `TableData.grid` guarda `row_span`, `col_span` y offsets. JSON y DocTags/OTSL conservan spans. Markdown y LaTeX **aplanan**. Si el workflow depende de celdas mergeadas, no exportar a Markdown. [Serialization](https://github.com/docling-project/docling/blob/main/docs/concepts/serialization.md).
- Extra `xbrl` existe. Útil cuando llegue una instancia; los PDF BYMA del piloto no lo son.
- Ritmo alto (2.124 → 2.130 en tres semanas). Pinnear `==2.130.0`.

SoT local de parse: **JSON `DoclingDocument`**. DocLang es interchange. Markdown/HTML re-chunkeado **nunca** es identidad.

---

## DocLang — la tabla es el producto

DocLang no es un parser. Es el formato de intercambio. PDF dice dónde dibujar píxeles; DocLang dice qué es el contenido. [doclang.ai](https://doclang.ai/).

- Cada componente: rol semántico + bbox + reading order.
- Tablas OTSL: ~5 tokens estructurales vs ~28 en HTML. Continuaciones de celda (L/U/X) son el antídoto al flatten.
- Working group: IBM, NVIDIA, Red Hat, ABBYY, HumanSignal. Gobernanza JDF / LF AI & Data. Lanzamiento 9 jun 2026.
- Spec viva, no ISO. El kernel **no** importa tipos de la spec.

DocLang **no** es un salto obligatorio de cada request. `DoclingDocument` puede circular internamente. Se exporta DocLang cuando hay persistencia, interoperabilidad o un consumidor que lo pida.

---

## LlamaIndex — candidatos, no verdad

Integración oficial: [Docling ↔ LlamaIndex](https://docling-project.github.io/docling/integrations/llamaindex/).

`DoclingReader` extrae a Document LlamaIndex como Markdown **o** JSON nativo. Default: **`export_type=markdown`**. [API DoclingReader](https://developers.llamaindex.ai/python/framework-api-reference/readers/docling/).

Regla explícita de CLAIMLEDGER:

```text
DoclingReader(export_type="json") + DoclingNodeParser
```

El JSON serializa `DoclingDocument` con `export_to_dict()`. Markdown aplana spans. Prohibido: PDF → Docling → Markdown → LlamaIndex.

El ejemplo oficial `rag_llamaindex` lo dice: JSON + `DoclingNodeParser` conserva grounding (página, bbox). Markdown usa un parser genérico y pierde estructura.

LlamaIndex no decide el claim. Recupera candidatos. Claimprint verifica.

---

## Open WebUI — solo presentación

Conecta a cualquier backend OpenAI-compatible (`/v1/models`, chat completions). [OpenAI-compatible](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/).

MCP nativo desde **v0.6.31**. OpenAPI tool servers también. [MCP](https://docs.openwebui.com/features/extensibility/mcp/).

Pipelines **siguen documentados** (no aparecen como “legacy” en la página de plugins del 23 sep). Aun así: “You likely won't need pipelines unless you're dealing with super-advanced setups.” [Tools & Functions](https://docs.openwebui.com/features/extensibility/plugin/). Para CLAIMLEDGER: **no Pipelines**. Preferir:

1. Endpoint OpenAI-compatible en el backend (más simple para el MVP).
2. Tool OpenAPI / MCP que llame `POST /claims/query` si hace falta tool-calling.

La UI muestra VERIFIED / ABSTAINED. No reimplementa identidad. Más adelante **dibuja** series ya verificadas (Mermaid, matplotlib, Artifact). No calcula el número. No copiamos el visor de otra plataforma.

---

## Qué no hace Graph (y no hay que copiar)

Docling Graph es la **capa de identidad de entidades y relaciones**. Puede persistir o exportar un grafo; eso no reduce su rol a un fichero. Nos da contexto e identidad de entidades. **No** interpreta el claim contable.

Graph extrae con LiteLLM / vLLM / Ollama. Dense es skeleton-then-flesh para documentos largos. Sirve para química, finanzas y legal **como framework de entidades**, no como extractor del P&L ya contratado con recipes.

No copiar ahora:

- Pipeline LLM/VLM **sobre** `identity_v1` (el VLM puede releer páginas más adelante; no escribe identidad)
- Dense sobre el gold BYMA
- Template-from-docs para una clase que ya tiene recipe

Sí, más adelante (no el primer día):

- VLM de Docling como segundo lector de páginas difíciles
- Neo4j / Cypher para consultar el libro (el lookup sigue siendo la verdad)
- Recortes de página junto al claim (idea visual de RAGFlow, sin instalar RAGFlow)

Graph en v2 temprano: templates para `Document`, `Issuer`, `ReportingPeriod`, `Section`. **No** meter `FinancialClaim` dentro del Graph hasta que el A/B de parse pase gold.

---

## Caso de uso inicial (inalterable)

Misma página, dos vecinos:

```text
RESULTADO NETO DEL PERÍODO                 21.262.335
RESULTADO ATRIBUIBLE A CONTROLANTE         21.259.769
```

Pregunta: ¿Cuál fue el resultado neto consolidado de BYMA en 1T26?

```text
PDF → Docling → DoclingDocument
        ├─ Graph: issuer / period / section
        └─ LlamaIndex: candidatos de tabla/fila
                ↓
        CLAIMLEDGER (claim + verify + abstain)
        issuer=BYMA period=2026-03-31
        statement=income_statement
        scope=consolidated metric=net_income
        value=21262335
                ↓
        VERIFIED + evidencia  |  ABSTAIN
                ↓
        Open WebUI
```

Abstenerse si: métrica inexistente, scope irresoluble, periodo ambiguo, issuer desconocido, valor sin evidencia, candidatos incompatibles.

---

## Evaluación (no “RAG accuracy”)

| Capa | Métrica |
|------|---------|
| Retrieval | Recall@k, MRR, candidate coverage |
| Identity | match issuer / period / statement / scope / metric |
| Verification | value + identity + evidence + abstention correctness |
| E2E | question → verified claim → answer → evidence |

La métrica del producto es si se identificó y verificó el claim correcto, no si se recuperó texto parecido.

Portar `identity_v1` / `identity_v2` con IDs canónicos nuevos. No mezclar con `rag_chat_v1` (eso era RAGFlow).

---

## API mínima

Solo esto en el MVP:

`POST /claims/query`

Verified:

```json
{
  "status": "verified",
  "answer": "21262335",
  "claim": {
    "issuer": "BYMA",
    "period": "2026-03-31",
    "statement": "income_statement",
    "scope": "consolidated",
    "metric": "net_income",
    "value": "21262335",
    "currency": "ARS"
  },
  "evidence": [
    {
      "document_id": "...",
      "page": 4,
      "text": "RESULTADO NETO DEL PERÍODO"
    }
  ]
}
```

Abstained:

```json
{
  "status": "abstained",
  "reason": "no_verified_claim"
}
```

---

## Orden de implementación

Fase 0 declara el contrato y los pins. Los tests del kernel son **independientes de Docling**. El A/B de parse viene después.

| Fase | Qué | Criterio de cierre |
|------|-----|--------------------|
| 0 — Contrato | `FinancialClaim` / identity + gold v1/v2 congelado + `docling==2.130.0` + `docling-graph==1.9.1` | Tests del kernel verdes **sin importar Docling** |
| 1 — Parse A/B | PDF BYMA → Docling 2.130 → JSON canónico. Sin MinerU | Claves y montos = gold. Si falla: no cambiar expected, no inventar identidad |
| 2 — Graph entities | IDs issuer/period/statement/scope/metric — no extraer el P&L | Nodo estable + ledger. 0 modelo sobre identity |
| 3 — Retrieval | `DoclingReader(export_type="json")` + `DoclingNodeParser` + dos índices | Candidatos, no respuesta |
| 4 — Verify | candidate → identity → verified \| abstain. Demo de las dos filas | Neighbor trap 21262335 ≠ 21259769 |
| 5 — Eval | 45+26 + “¿trajo ambas?” | Gold intacto |
| 6 — API | `POST /claims/query` | Contrato chico, aún sin foto |
| 7 — UI ficha | Open WebUI: sello + chips + texto | Lógica fuera de la UI |
| 8 — Recorte | Foto de la zona de la página (bbox Docling) | Prueba visual propia |
| 9 — Pack / comparar | Merge 1T+comunicado+deck; 1T vs 2T | Conflicto visible; resta en código |
| 10 — VLM | Segundo lector de páginas difíciles | Sigue perdiendo vs gold. No crea identidad |
| 11 — Neo4j | Cypher sobre el libro | Lookup sigue siendo SoT |
| 12 — Gráficos | Serie verificada → Mermaid / matplotlib / Artifact | Open WebUI dibuja; hueco si un trimestre se abstiene |
| 13 — Orquestador | LlamaIndex Workflows alrededor del kernel | Identidad/verificación son servicios, no agentes |
| Después | XBRL, datos de slides, aire-gap | No es MVP |

Si el A/B falla se investiga: conversión Docling, schema, template, serialización, mapeo al grafo. **No** se relaja el gold. **No** vuelve MinerU.

---

## Riesgos

1. **LLM sobre identity_v1.** Rompe check/gold y la tesis. Si el A/B no pasa, se ajusta parse/template, no se relaja el contrato.
2. **Docling se mueve cada pocos días.** Pin. No `>=`.
3. **DocLang joven.** Útil como export. El kernel no importa la spec.
4. **Default Markdown de LlamaIndex.** Forzar JSON o se repite el flatten de RAGFlow.
5. **Normalización de period.** Fusionar `1T26` con `2026-03-31` exige la misma forma canónica **antes** del ID.
6. **Identidades locales.** Nunca usar `linea=3` como ID global.

---

## Respuesta a la pregunta de siguiente paso

Fase 0 (contrato en schemas + gold + pins), no Fase 1 (A/B Docling).

Es local, no toca Docker, y deja el contrato listo para el A/B. El primer commit útil es exactamente eso.

Si querés arrancar, el movimiento es: contrato de identidad + gold v1/v2 congelado + `docling==2.130.0` + `docling-graph==1.9.1`, tests del kernel **sin** Docling, **sin cambiar un expected numérico**.

---

## North star

Canónico: [north-star.md](north-star.md).

```
USAR EL ECOSISTEMA
        ↓
NO REIMPLEMENTAR EL ECOSISTEMA
        ↓
CONSTRUIR LA VERTICAL FINANCIERA
```

El retrieval encuentra evidencia. CLAIMLEDGER la convierte en una afirmación financiera verificable. Docling no resuelve qué significa financieramente una cifra.

---

## Sources

- [Docling home](https://docling-project.github.io/docling/)
- [docling PyPI 2.130.0](https://pypi.org/project/docling/2.130.0/) (22 sep 2026)
- [Docling v2.130.0](https://github.com/docling-project/docling/releases/tag/v2.130.0)
- [Docling serialization / table spans](https://github.com/docling-project/docling/blob/main/docs/concepts/serialization.md)
- [docling-graph PyPI 1.9.1](https://pypi.org/project/docling-graph/) (17 jul 2026)
- [Docling Graph docs](https://docling-project.github.io/docling-graph)
- [Entities vs Components](https://docling-project.github.io/docling-graph/fundamentals/schema-definition/entities-vs-components)
- [Data Grounding & Provenance](https://docling-project.github.io/docling-graph/fundamentals/graph-management/provenance)
- [merge command](https://docling-project.github.io/docling-graph/usage/cli/merge-command)
- [DocLang](https://doclang.ai/)
- [LF AI DocLang Working Group](https://www.linuxfoundation.org/press/lf-ai-data-foundation-launches-doclang-specification-working-group-to-advance-an-open-standard-for-ai-native-documents) (9 jun 2026)
- [Docling ↔ LlamaIndex](https://docling-project.github.io/docling/integrations/llamaindex/)
- [LlamaIndex DoclingReader](https://developers.llamaindex.ai/python/framework-api-reference/readers/docling/)
- [Open WebUI OpenAI-compatible](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/)
- [Open WebUI MCP](https://docs.openwebui.com/features/extensibility/mcp/)
- [Open WebUI Tools & Functions](https://docs.openwebui.com/features/extensibility/plugin/)
- Claimprint local: `schemas/claim.py`, `schemas/lookup.py`, `schemas/provenance.py`, `evals/identity_v1.json`, `evals/identity_v2.json`, `recipes/financial_statement.json`, `docs/architecture.md`

JSON Parallel de esta investigación: `docling-2130.json`, `docling-graph-191.json`, `doclang-spec.json`, `llamaindex-docling.json`, `openwebui.json` (raíz de CLAIMLEDGER).
