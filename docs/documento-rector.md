# CLAIMLEDGER

## Financial Claims Intelligence

Documento rector del proyecto. Leer esto **antes** de implementar. Si una decisión no suma a este texto, distrae del producto.

Fecha: 23 septiembre 2026  
Repos: CLAIMLEDGER (sin código de producto) · Claimprint v1 congelada en `C:\Users\Equipo\Claimprint`

---

## 1. Qué problema resuelve

CLAIMLEDGER existe para una sola cosa:

> Cuando alguien pregunta un número de un balance, el sistema solo responde si puede demostrar qué número es y de dónde salió. Si no puede, se abstiene.

El problema no es únicamente recuperar la página correcta.

En un estado de resultados pueden coexistir, en la misma página, cifras muy parecidas con distinto significado contable.

Ejemplo canónico — BYMA 1T26:

```text
Resultado neto del período
21.262.335

Resultado neto atribuible a la controlante
21.259.769
```

Una búsqueda puede recuperar la página y aun así elegir la fila incorrecta.

Por eso:

> **retrieval ≠ financial verification**

CLAIMLEDGER existe para resolver esa diferencia.

En Claimprint, retrieval solo (keyword / vector / hybrid) empató Recall@5 **0.35** / MRR **0.2042** (n=20). Con claims verificados, el chat acertó 10/10. El salto no es buscar mejor: es resolver identidad **antes** de responder.

---

## 2. Qué es CLAIMLEDGER

CLAIMLEDGER es un **verificador de afirmaciones financieras** y, a la vez, un **libro** de esas afirmaciones: colección estructurada y trazable. El nombre encaja: *claim* + *ledger*.

Una afirmación no es un párrafo del PDF. Es una estructura:

```text
BYMA
2026-03-31
income_statement
consolidated
net_income
=
21.262.335 ARS
```

con evidencia:

```text
documento
página 4
texto/fila fuente
span/geometry cuando exista
```

Tres dimensiones que no se mezclan:

| Dimensión | Pregunta | Ejemplo |
|-----------|----------|---------|
| Identidad | ¿Qué afirmación es? | `BYMA\|2026-03-31\|income_statement\|consolidated\|net_income` |
| Valor | ¿Cuánto es? | 21262335 ARS |
| Provenance | ¿De dónde salió? | documento, página, texto, recuadro |

`FinancialIdentity` es **Entity**. `MonetaryAmount` (valor + moneda + unidad) es **Component**. La provenance queda fuera del hash: puede acumularse sin crear otra entidad.

Las etiquetas del documento (`RESULTADO NETO DEL PERÍODO`) son localizadores, no IDs.

---

## 3. Regla principal

```text
No verified claim
        ↓
    No answer
```

Estados mínimos: `candidate` → `verified` | `rejected` | `abstained`.

El sistema puede recuperar varios candidatos. Solo responde cuando una afirmación pasa la verificación.

---

## 4. Qué NO es

No es un chatbot que “habla con PDFs”, otro buscador, otro OCR, otro parser, otra plataforma RAG ni otro knowledge graph genérico.

Tampoco es un sistema donde el LLM decide la cifra.

Definición correcta:

> La capa que determina qué significa financieramente una cifra y si esa afirmación puede demostrarse con evidencia documental.

---

## 5. Arquitectura definitiva

```text
                    PDF / XBRL / DOCX / XLSX
                               |
                               v
                         ┌───────────┐
                         │  Docling  │
                         └─────┬─────┘
                               |
                       DoclingDocument
                               |
                ┌──────────────┴──────────────┐
                v                             v
        ┌───────────────┐              ┌─────────────┐
        │ Docling Graph │              │  LlamaIndex │
        │ entities      │              │ indexing    │
        │ relations     │              │ retrieval   │
        │ identity      │              │ candidates  │
        │ merge/ledger  │              │             │
        └───────┬───────┘              └──────┬──────┘
                |                             |
                └──────────────┬──────────────┘
                               v
                   ┌──────────────────────┐
                   │   CLAIMLEDGER        │
                   │ Financial Claims Core│
                   │ identity             │
                   │ semantics            │
                   │ verification         │
                   │ provenance contract  │
                   │ abstention           │
                   │ gold / evaluation    │
                   └──────────┬───────────┘
                              |
                      verified / abstain
                              |
                              v
                       ┌────────────┐
                       │ Open WebUI │
                       └────────────┘
```

DocLang es transversal (`DoclingDocument ↔ DocLang`) y **no** es un salto de cada request.

Runtime: `DoclingDocument`. Persistencia o intercambio, si hace falta: JSON de Docling o DocLang.

El JSON de cada parse se guarda como **artefacto inmutable**. El Core (ledger + query) se construye encima; no se re-parsea el PDF para reconstruir un claim. Detalle en §23.

---

## 6. Responsabilidad de cada componente

Las capas no son alternativas. Cada una responde una sola pregunta.

| Capa | Pregunta | Rol | Prohibido |
|------|----------|-----|-----------|
| Docling | ¿Qué hay en el documento? | Parse → `DoclingDocument` | Parser propio |
| DocLang | ¿Cómo intercambio la estructura? | Export opcional | Hop de runtime |
| Docling Graph | ¿Qué entidades y relaciones hay? | IDs, merge, ledger | Extraer el P&L / interpretar el claim |
| LlamaIndex | ¿Dónde están los candidatos y cómo se orquesta el trabajo? | Retrieval + workflows (alrededor del kernel) | Decidir el claim · Markdown · entrar al kernel |
| CLAIMLEDGER | ¿Qué afirmación verifico? | Producto | Inventar evidencia · LLM como verdad |
| Open WebUI | ¿Cómo la muestro? | UI | Lógica financiera · Pipelines |

### Docling

Parsing, PDF, OCR, layout, reading order, tablas, texto, figuras, coordenadas, `DoclingDocument`, provenance documental, serialization, chunking, XBRL.

Pin: **`docling==2.130.0`**. Publicado en PyPI el 22 sep 2026. GitHub Latest = v2.130.0. Sujeto a gold. No `>=`.

SoT de parse: JSON `DoclingDocument`. Markdown y LaTeX aplastan celdas mergeadas. Extra `xbrl` solo si hay instancia XBRL; los PDF BYMA del piloto no lo son.

### DocLang

Formato de intercambio, no parser. Estándar AI-native (WG desde 9 jun 2026). Tablas OTSL conservan la grilla. El kernel no importa tipos de la spec.

### Docling Graph

Capa de identidad de entidades y relaciones. Puede persistir un grafo; eso no es su función arquitectónica. **No es el extractor del P&L.**

En CLAIMLEDGER su trabajo es acotado:

```text
issuer + period + statement + scope + metric
        ↓
identity / nodo
        ↓
ID estable
```

`graph_id_fields` identifica la entidad. Los componentes se deduplican por contenido. Provenance determinista, bookkeeping del pipeline, **cero LLM**. Merge determinista: mismo ID se pliega; conflicto se audita; alias dudoso → HITL.

Pin: **`docling-graph==1.9.1`** (17 jul 2026).

### LlamaIndex

Dos oficios, **alrededor** del kernel, no dentro:

1. **Retrieval** — candidatos (tablas, no Markdown).
2. **Orquestación** (más adelante) — workflows: plan, paralelo, estado, HITL. No otro framework de agentes.

Regla explícita de retrieval:

```text
DoclingReader(export_type="json") → DoclingNodeParser → LlamaIndex
```

Prohibido: Docling → Markdown → LlamaIndex. El default del Reader es markdown; hay que forzarlo.

Los agentes **deciden qué hacer**. Las tools **traen**. CLAIMLEDGER **decide qué es verdad**. Detalle en §22.

### CLAIMLEDGER (producto)

Cuatro capas propias:

1. Identidad financiera  
2. Afirmación (claim)  
3. Verificación  
4. Abstención  

Más: semántica del indicador, unidad/moneda como componente, contrato de provenance, evaluación gold-first.

### Open WebUI

Interfaz. Backend OpenAI-compatible o tool OpenAPI/MCP. No Pipelines.

**Verifica CLAIMLEDGER. Dibuja Open WebUI.** La UI no calcula un número financiero. Recibe claims ya verificados (o una serie) y los muestra: ficha, recorte, gráfico.

```text
CLAIMLEDGER
    ↓
verified claims  (datos estructurados)
    ↓
Open WebUI
    ↓
ficha / recorte / gráfico
```

Tres formas nativas de dibujar, cuando haya una serie verificada:

1. **Mermaid** — torta, barras simples, dentro del chat. [MermaidJS](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/mermaid/)
2. **Python + matplotlib** — gráfico más serio; la imagen entra sola en el chat. [Python](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/python/)
3. **Artifacts** — HTML/SVG/JS (p. ej. D3) al costado de la conversación. [Artifacts](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/artifacts/)

El backend emite el **spec** (título, períodos, valores, sello). Open WebUI solo renderiza. El modelo no inventa las alturas de las barras.

---

## 7. FinancialClaim

Objeto central. Contrato conceptual (el modelo exacto se fija en Fase 0):

```text
FinancialClaim
├── issuer
├── period
├── statement
├── scope
├── metric
├── value
├── unit
├── currency
├── evidence[]          ← varias fuentes, misma identidad
└── verification_status

No es “un dato de un PDF”. Es una entidad del libro que puede acumular evidencias.
```

---

## 8. Identidad financiera

```text
graph_id_fields = ["issuer", "period", "statement", "scope", "metric"]

identity_key =
BYMA|2026-03-31|income_statement|consolidated|net_income
```

No entran al ID: value, currency, unit, provenance.

Claimprint v1 usaba 4 campos en español (`consolidado|resultado_neto`). CLAIMLEDGER nace con 5 campos canónicos en inglés. Los **números** gold no se reinterpretan.

El período se normaliza **antes** del ID: `1T26` → `2026-03-31`. Nunca usar `linea=3` como ID global.

El valor no identifica: 21.262.335 y 21.259.769 son dos claims distintos porque cambian scope/metric, no porque sean dos números.

---

## 9. Merge

EEFF, comunicado y presentación del mismo período pueden converger si resuelven al mismo `issuer|period|statement|scope|metric`.

Misma identidad + evidencia incompatible → auditar, no ocultar. HITL cuando corresponda.

---

## 10. El kernel no se toca

NO:

```text
Question → LLM → identity_v1 → answer
```

SÍ:

```text
Question → orquestador / workers → CLAIMLEDGER (determinista) → verified | abstain → UI
```

**Ningún agente se saltea el kernel.** No existe el camino pregunta → análisis → número, ni handoff que responda una cifra sin `verified` | `abstain`. Análisis y visualización solo corren **después** del juez, y solo ven esa salida.

El LLM puede ayudar a recuperar o explicar. **No crea identidad. No es fuente de verdad de la cifra.**

Si el parse no iguala gold: no cambiar expected, no inventar la identidad con un modelo, no traer MinerU. Investigar conversión, schema, template, serialización, mapeo. Un VLM puede **releer la página** más adelante; no puede **decidir** qué cifra es.

---

## 11. Herencia de Claimprint

Se conserva la tesis, no la tubería.

**Se hereda:** Financial Claim, `identity_key`, identity ≠ provenance, verification, abstention, gold, tests BYMA, neighbor-trap, candidate → verified, “No verified claim, no answer”, lookup léxico, `digits_ars`, período canónico.

**Gold congelado:** `identity_v1` = 45 casos, `identity_v2` = 26 casos. Contrato de regresión, no ejemplos.

**No se porta:** MinerU (nunca), RAGFlow como plataforma, `push_claims`, chunking RAGFlow, `select_page()` por keyword, “primer monto = current”, sidecar bbox MinerU, parser casero, extracción LLM del P&L.

MinerU queda fuera del producto. RAGFlow no se instala: mezcla demasiadas capas. De RAGFlow **sí** tomamos, más adelante, la idea de **mostrar la foto** de la zona del documento de donde salió el número.

---

## 12. Flujo de la pregunta canónica

> ¿Cuál fue el resultado neto consolidado de BYMA en 1T26?

1. LlamaIndex trae candidatos (neto 21.262.335 y controlante 21.259.769).  
2. CLAIMLEDGER resuelve la identidad pedida: BYMA / 2026-03-31 / income_statement / consolidated / net_income.  
3. Compara candidatos.  
4. Uno satisface el contrato → **VERIFIED** + evidencia (página 4, `RESULTADO NETO DEL PERÍODO`).  
5. Controlante → 21.259.769. Ambiguo → **ABSTAIN**. Nunca “probablemente”. Nunca guess.

Abstenerse si: período/scope/métrica/issuer ambiguos o ausentes, valor sin evidencia, dos candidatos incompatibles.

---

## 13. API mínima

`POST /claims/query`

```json
{
  "question": "¿Cuál fue el resultado neto consolidado de BYMA en 1T26?"
}
```

Verified: `status`, claim (issuer, period, statement, scope, metric, value, currency), evidence (document_id, page, text).  
Abstained: `{ "status": "abstained", "reason": "no_verified_claim" }`.

Más adelante la evidencia suma **recorte de página** (imagen de la fila o tabla, recuadro de Docling). El contrato chico no espera esa imagen el primer día.

Cuando la pregunta pida varios períodos (“últimos 4 trimestres”), la API responde una **serie**: lista de claims verificados (o huecos). Open WebUI dibuja esa serie. No construye los valores.

No construir una API grande antes del contrato de un claim.

---

## 14. Evaluación

| Capa | Qué se mide |
|------|-------------|
| Retrieval | Recall@k, MRR, candidate coverage |
| Identity | issuer, period, statement, scope, metric |
| Verification | value, identity, evidence, abstention correctness |
| E2E | question → retrieval → candidates → verified claim → answer → evidence |

La métrica del producto es si se identificó y demostró el claim correcto, no si se recuperó texto parecido.

---

## 15. Plan de implementación

CLAIMLEDGER nace vacío. La primera fase **no** es el PDF. Es el contrato del kernel.

**MVP (camino crítico, fases 0–7).** Solo esto tiene que funcionar: `21.262.335 ≠ 21.259.769`, con identidad, valor, evidencia, verified y un caso de abstención.

```text
BYMA PDFs → Docling → evidencia → CLAIMLEDGER → LlamaIndex retrieve → Open WebUI
```

Graph, orquestador, VLM, Neo4j, recortes y gráficos **no** están en ese request. Entran por el gate (§24).

| Fase | Plano | Qué | Cierre |
|------|-------|-----|--------|
| **0** | Verdad | Contrato Ledger + Query, gold, pins | Tests sin Docling / Docker / modelo / UI |
| **1** | Verdad | PDF → JSON inmutable → Evidence Adapter | Vs gold. Cero claims inventados. Sin MinerU |
| **2** | Verdad | Graph **simple** en ingest (Document / Issuer / Period / Statement). `FinancialClaim` **fuera** del Graph | Merge/IDs. No extraer el P&L. No corre en cada pregunta |
| **3** | Verdad | Indexar JSON (dos cajones) | Candidatos, no respuesta |
| **4–5** | Verdad | Verify + eval 45+26 + trampa + abstención | Gold intacto. Demo de las dos filas |
| **6–7** | Interacción **nivel 1** | `POST /claims/query` → ficha. **Sin orquestador** | UI no decide |
| 8 | Interacción | Recorte de la fila | Gate: ¿la ficha ya convence sin foto? |
| 9 | Verdad + query | Pack / comparar (código resta) | Gate: ¿hace falta más de un documento? |
| 10 | Verdad | VLM segundo lector | Gate: ¿el parse estándar falló gold? |
| 11 | Verdad | Neo4j / Cypher | Gate: ¿el libro ya tiene varios períodos? |
| 12 | Interacción **nivel 3** | Gráficos de serie verificada | Gate: ¿ya hay Claim Query de serie? |
| 13 | Interacción **nivel 2–3** | Orquestador + tools (no un agente por función) | Gate: ¿la pregunta es compuesta? |
| Después | — | XBRL, slides, aire-gap, multi-agent real (nivel 4) | No es el primer día |

---

## 16. Pins

```toml
docling = "==2.130.0"
docling-graph = "==1.9.1"
```

No `>=`, `^`, `*` ni `latest`. Primero pin → gold → tests → validación. Después se actualiza a propósito.

Python ≥3.11 (Fase 0). El ecosistema Docling admite ≥3.10; este repo no baja de 3.11.

---

## 17. Principios

1. No reimplementar el ecosistema.  
2. No reemplazar el kernel determinista por extracción LLM.  
3. Retrieval no es verification.  
4. Identity no es provenance.  
5. El valor no identifica el claim.  
6. La evidencia debe mantenerse estructurada (JSON, no Markdown canónico).  
7. Ante conflicto, abstenerse antes que adivinar.  
8. Un modelo puede recuperar, **leer** una página (VLM) o explicar; no es la verdad del dato.  
9. Open WebUI **dibuja**; no calcula ni decide el claim.  
10. Los gold tests son un contrato, no material de ajuste.  
11. MinerU no entra.  
12. Neo4j consulta el libro; no decide el claim.  
13. La foto de evidencia es prueba visual, no identidad.  
14. No copiar el truco de otra plataforma. Usar recorte propio, gráfico propio, ficha propia.  
15. Un gráfico sin serie verificada no se dibuja (o se dibuja con huecos), nunca se rellena.  
16. Los agentes orquestan el trabajo; no reemplazan el kernel. No llamar “agente” a identidad ni a verificación.  
17. LlamaIndex crece **alrededor** de CLAIMLEDGER, no adentro.  
18. **Ningún agente se saltea el kernel.** Toda cifra, gráfico o explicación financiera pasa por verified | abstain.  
19. El Core no inventa claims al parsear. El ledger se alimenta de evidencia; el claim aparece cuando se cumple el contrato.  
20. Ingest y Query son dos operaciones. La pregunta no crea el claim.  
21. El JSON de Docling se guarda como artefacto inmutable. El ledger apunta a él; no se re-parsea el PDF para reconstruir provenance.  
22. Dos planos: **Verdad** (determinista, ingest) e **Interacción** (agentes/UI). No se mezclan en el mismo salto.  
23. Graph se construye en ingest y se **consulta**. No se regenera en cada pregunta.  
24. **Architecture Gate:** no se agrega un componente “porque los sistemas modernos lo usan”. Tiene que resolver un problema concreto que el actual no resuelve.  
25. Tool ≠ Agent. El MVP es un request simple, sin orquestador.

```text
USAR EL ECOSISTEMA
        ↓
NO REIMPLEMENTAR EL ECOSISTEMA
        ↓
CONSTRUIR LA VERTICAL FINANCIERA
```

---

## 18. North star

```text
DOCUMENT
    ↓
EVIDENCE
    ↓
FINANCIAL IDENTITY
    ↓
CLAIM
    ↓
VERIFICATION
    ↓
VERIFIED → ANSWER
ABSTAIN  → NO ANSWER
```

CLAIMLEDGER no pregunta “¿qué dice este PDF?”. Pregunta:

> ¿Qué afirmación financiera representa este dato y puedo demostrar que es correcta?

---

## 19. Documentación oficial a consultar

- Docling: https://docling-project.github.io/docling/  
- Docling Document: https://docling-project.github.io/docling/concepts/docling_document/  
- Serialization: https://github.com/docling-project/docling/blob/main/docs/concepts/serialization.md  
- DocLang: https://doclang.ai/ · spec https://github.com/doclang-project/doclang/blob/main/spec.md  
- Docling Graph: https://github.com/docling-project/docling-graph  
- Entities vs Components: https://docling-project.github.io/docling-graph/fundamentals/schema-definition/entities-vs-components  
- Provenance: https://docling-project.github.io/docling-graph/fundamentals/graph-management/provenance  
- Merge: https://docling-project.github.io/docling-graph/usage/cli/merge-command  
- LlamaIndex + Docling: https://docling-project.github.io/docling/integrations/llamaindex/  
- DoclingReader: https://developers.llamaindex.ai/python/framework-api-reference/readers/docling/  
- Open WebUI OpenAI-compatible: https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/  
- MCP: https://docs.openwebui.com/features/extensibility/mcp/  
- Mermaid: https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/mermaid/  
- Python / matplotlib: https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/python/  
- Artifacts: https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/artifacts/

Los JSON Parallel en `research/` son contexto histórico. La implementación sigue las APIs oficiales del momento, no un extracto.

Claimprint local a portar: `schemas/claim.py`, `schemas/lookup.py`, `evals/identity_v1.json`, `evals/identity_v2.json`, `recipes/financial_statement.json`.

---

## 20. Sugerencias, en orden (qué entra y cuándo)

Esto no cambia el north star. Solo dice **en qué momento** se usa cada idea.

**Ahora no (Fase 0).** Solo el contrato y los casos de prueba. Sin PDF, sin modelo, sin pantalla.

**Cuando leamos el PDF (Fase 1).** Usar la estructura de Docling: la tabla como tabla, no como texto plano; ignorar encabezados y pies que ensucian emisor/fecha. Comparar dos formas de leer tablas. MinerU no se instala. El VLM todavía no: primero el lector estándar.

**Cuando armamos el libro (Fase 2).** Escribir nodos con IDs que el kernel ya resolvió. Fusionar EEFF + comunicado + presentación del mismo período. El conflicto se muestra, no se tapa.

**Cuando buscamos (Fase 3).** Dos cajones: uno de tablas (números) y uno de narrativa (explicar después). Mezclarlos es cómo un chat se come la fila de al lado.

**Cuando verificamos (Fase 4–7).** La pantalla enseña el error: “encontré estas dos filas; verifiqué la consolidada”. Ficha con sello VERIFICADO / ME ABSTENGO, chips (BYMA · 1T26 · Consolidado · Resultado neto) y el texto de la fila. El chat, si existe, habla **después** de la ficha.

**Más adelante (Fase 8).** Recorte propio: la zona de la página que Docling ya marcó, junto al claim. No es “el visor de otra plataforma”. Es nuestra prueba visual.

**Más adelante (Fase 9).** Pack de período (varios documentos, misma identidad). Comparar 1T vs 2T: dos claims verificados, lado a lado; la diferencia la calcula código.

**Más adelante (Fase 10).** VLM: un modelo que **mira** la página cuando el lector estándar se traba (tabla rara, gráfico de una presentación). Entrega la misma estructura. El kernel sigue decidiendo. Si no iguala los casos de prueba, no se cambian los casos de prueba.

**Más adelante (Fase 11).** Neo4j / Cypher para preguntarle al libro: “todos los resultados netos de BYMA”. No para inventar el número.

**Más adelante (Fase 12).** Gráficos de series verificadas. Pregunta: “compará el neto de los últimos 4 trimestres”. CLAIMLEDGER verifica Q1…Q4. Open WebUI dibuja barras / torta / línea. Debajo: Sources → claims → documentos → páginas. Si un trimestre se abstiene, esa barra queda vacía. Nadie inventa el 4º número para que el gráfico “se vea lindo”.

**Más adelante (Fase 13).** Orquestador + ejecutores. El orquestador arma el plan (cuatro trimestres, en paralelo). Los ejecutores buscan y explican. El kernel verifica. No un enjambre que “sepa contabilidad”. Ver §22.

**Todavía más tarde.** Segunda firma XBRL. Datos de gráficos de PowerPoint. Todo el parse puede correr sin internet.

---

## 21. CLAIMLEDGER verifica; Open WebUI visualiza

Esto es producto propio, no el chat-con-PDF de nadie.

Pregunta de ejemplo:

> Compará el resultado neto de los últimos 4 trimestres.

```text
CLAIMLEDGER
  verifica Q1
  verifica Q2
  verifica Q3
  verifica Q4
        ↓
serie estructurada  (o huecos)
        ↓
Open WebUI
  Mermaid / matplotlib / Artifact
        ↓
gráfico + sello
        ↓
Sources → claims → documentos → páginas
```

Reglas del gráfico:

- Cada barra/porción **es** un claim verificado. No un promedio, no un “aprox”.
- Si faltan claims, el gráfico tiene **huecos** (o no se dibuja). Nunca se interpola un trimestre para rellenar.
- Una torta de patrimonio solo si las partes y el total están verificados. Si no cierran, no hay torta: hay abstención o un “no explicado” explícito.
- Un ratio (margen, variación %) lo calcula **código** sobre dos claims verificados. matplotlib no “saca el %” del PDF.
- El backend manda el spec (`title`, `points[]`, `status`). La UI no pisa los `value`.
- Debajo del dibujo, la cadena: fuente → afirmación → documento → página. Click en una barra abre esa ficha.

Escalera de dibujo (de menos a más):

| Cuándo | Herramienta | Para qué |
|--------|-------------|----------|
| Serie chica, demo | Mermaid | Torta o barras simples en el chat |
| Escalas, ejes, varios años | matplotlib | Imagen seria, inline |
| Tablero vivo | Artifact (HTML/SVG, D3 si hace falta) | Click en barra → ficha; sello ✓ / △ 3 de 4 |

Lo que no hacemos: dejar que el modelo escriba un Mermaid con números de su cabeza; encender Code Interpreter para “calcular el balance”; copiar el visor o el pipeline de otra plataforma.

---

## 22. Orquestador y ejecutores (alrededor del kernel)

Sí: cuando la pregunta pide **varios pasos** (cuatro trimestres, un gráfico, una explicación), hace falta alguien que arme el plan. No: convertir todo CLAIMLEDGER en un enjambre de agentes.

La frase:

> Los agentes deciden **qué hacer**. Las tools **traen**. CLAIMLEDGER decide **qué es verdad**.

LlamaIndex crece **alrededor** del kernel, no adentro. No hace falta otro framework de agentes para arrancar.

### Tres pisos (no llamar “agente” a todo)

```text
ORQUESTADOR          (workflow / plan)
        ↓
AGENTES / WORKERS    (retrieval, análisis, visualización)
        ↓
SERVICIOS            (identidad, verificación, stores)
        ↓
CLAIMLEDGER KERNEL   (determinista)
```

| Pieza | Tipo | Hace | No hace |
|-------|------|------|---------|
| Orchestrator | workflow (a veces LLM de plan) | ¿Qué operaciones hacen falta? ¿En paralelo? | Contabilidad, cifra |
| Retrieval worker | tool / agente de búsqueda | Candidatos por período | Verificar |
| Analysis Agent | LLM | Explicar evolución **después** | Calcular o inventar valores |
| Visualization Agent | LLM / tool | Elegir barra/torta/línea sobre un spec | Inventar alturas |
| Identity Resolver | **servicio** | `issuer\|period\|statement\|scope\|metric` | “Creer” la identidad |
| Verification Engine | **servicio** | candidate + identity + evidence → verified / abstain | Adivinar |
| Identity / Evidence store | **servicio** | Guardar IDs y origen | Interpretar el P&L |

Identidad y verificación **no** se llaman agentes. Si se llaman agentes, alguien termina metiendo un modelo en el juez.

### Flujo

```text
USER
  “Compará el neto consolidado de BYMA 1T26…4T25 y graficalo”
        │
        ▼
 ORQUESTADOR
  1. proponer issuer / 4 períodos   (plan, no verdad)
  2. disparar retrieval en paralelo
  3. cada lote de candidatos → KERNEL
  4. serie verificada (o huecos)
  5. Visualization Agent / Analysis Agent
        │
        ▼
 Open WebUI
```

El orquestador puede **proponer** “issuer = BYMA, cuatro períodos”. El Identity Resolver **confirma**. Si no confirma, no hay claim.

Q1/Q2/Q3/Q4 se buscan en paralelo. Se **verifican** de a uno (o en paralelo, pero cada uno pasa por el mismo motor). Recién la serie entra al gráfico.

### Qué da LlamaIndex (no inventar otro stack)

Tres patrones oficiales ([multi-agent](https://developers.llamaindex.ai/python/framework/understanding/agent/multi_agent/)):

1. **AgentWorkflow** — handoff entre agentes. Sirve para prototipar análisis/chat. El handoff **no** puede responder una cifra: el workflow termina en el kernel o no termina.
2. **Orchestrator** — un agente de plan que llama sub-agentes como tools y vuelve siempre al centro. Mejor control.
3. **Custom Workflow** — fan-out / fan-in, `num_workers`, estado, HITL (`InputRequiredEvent`). Para “cuatro trimestres” esto es lo más serio: el plan es conocido, no hace falta que un LLM lo improvise.

También: ejecución concurrente ([concurrent](https://developers.llamaindex.ai/python/llamaagents/workflows/concurrent_execution/)), human-in-the-loop ([HITL](https://developers.llamaindex.ai/python/framework/understanding/agent/human_in_the_loop/)).

Para CLAIMLEDGER: **Workflow custom** para la pregunta financiera (plan fijo: resolver → retrieve N → **kernel N** → serie). LLM solo en plan sucio (“cómo le fue a BYMA este año”), análisis y tipo de gráfico — **después** del juez.

**Ningún agente se saltea el kernel.** Ni el orquestador, ni retrieval, ni analysis, ni visualization. No hay atajo a Open WebUI con un número que no salió de `verified` | `abstain`.

### Cuándo

No en Fase 0–7. Esas fases son **nivel 1**: Open WebUI → API → retrieve → verify → ficha. Sin orquestador.

Nivel 2 (pregunta compuesta) y 3 (análisis/gráfico) entran en 12–13. Nivel 4 (multi-agent real) solo con necesidad concreta. Tool ≠ Agent: no hay Identity Agent ni Verification Agent.

Sin kernel sólido, el orquestador es un chat que finge oficios. Ningún agente escribe el ledger sin pasar por el contrato del Core. Graph no se reconstruye en cada pregunta.

---

## 23. Financial Claims Core: ledger + query

El Core **no** inventa claims mientras Docling parsea. El parse produce evidencia. El claim aparece cuando esa evidencia cumple el contrato financiero.

```text
PDF
  → Docling
  → DoclingDocument JSON  (artefacto inmutable)
  → Evidence Adapter      (técnica, no negocio)
  → Financial Evidence    (fila + número + página + recuadro)
  → Candidate             (todavía no es verdad)
  → Identity Resolver     (servicio)
  → Ledger upsert
       misma identidad + mismo valor  → sumar evidencia
       misma identidad + otro valor   → conflicto, no overwrite
  → (más tarde) Claim Query → verified | abstain
```

Un PDF puede producir documentos, entidades y evidencia **y cero claims**. Una memoria institucional, un deck sin el indicador, una identidad irresoluble: está bien. El pipeline no está obligado a “encontrar un número”.

### Dos productos internos

| | Claim Ledger (ingest) | Claim Query (consulta) |
|--|----------------------|-------------------------|
| Entrada | PDF / artefacto JSON | pregunta o identidad pedida |
| Hace | evidencia → candidato → ID → upsert | ID pedida → candidatos → verify |
| LlamaIndex | solo **indexa** lo ya estructurado | **busca** candidatos |
| Resultado | claim `recorded` o `conflicted` (o nada) | `verified` \| `abstained` |

La pregunta **no crea** el claim. El libro puede existir antes de que alguien pregunte.

La trampa de las dos filas vive sobre todo en **Query**: dos entradas válidas en el libro; el verifier elige la identidad pedida. En ingest, las dos filas de la página 4 son **dos claims distintos** (cambia scope/metric), no un empate.

“Verified” de producto = “responde esta pregunta”. “Recorded” = “entró al libro porque el recipe/contrato matcheó”. No confundirlos.

### Evidence Adapter

Toma `TableItem` / `TableData.grid` / `ProvenanceItem` (spans intactos) y lo pasa a formato interno. Suma **contexto de documento** (emisor, período del pack o de la tapa): la fila sola no dice “BYMA”. Ignora furniture. No aplana a Markdown. No interpreta consolidado vs controlante: eso es el resolver + recipe (el lookup de Claimprint, no un modelo).

No toda fila se vuelve candidato. Solo las que el contrato/recipe reconoce.

### Cómo se va creando, PDF a PDF

```text
PDF EEFF 1T26     → recorded  consolidado / net_income = 21262335
PDF EEFF 1T26     → recorded  controlante / net_income = 21259769   (otro claim)
PDF comunicado    → recorded  consolidado / EBITDA = …
PDF presentación  → misma identidad consolidado/net_income → evidence[] += slide
```

El claim no es “un dato de un PDF”. Es la entidad del libro, con `evidence[]`.

### El LLM queda fuera del ledger

Los agentes piden al Claim Query. No escriben el libro. El orquestador puede decir “necesito cuatro netos”; el Core decide cuáles existen y cuáles se verifican.

### Desde el primer día

Guardar el JSON de Docling hasheado. El ledger apunta a `#/tables/n` + bbox. Si hay que reconstruir un claim, se lee el artefacto, no se vuelve a parsear el PDF.

---

## 24. Dos planos y Architecture Gate (bajar riesgo)

El riesgo no es “tener cinco tecnologías”. Es hacer que las cinco **decidan en el mismo request**.

### Plano A — Verdad (determinista)

```text
PDF → Docling → JSON inmutable → (Graph ingest) → Claims Core → Ledger
```

Acá vive la verdad. Sin agentes. Graph se **escribe** acá y después solo se consulta.

### Plano B — Interacción

```text
User → Open WebUI → (nivel 1: API directa | nivel 2+: orquestador + tools) → Claim Query → ficha / gráfico
```

Acá vive la conversación. Los agentes son **consumidores** del Core. Llaman `get_claim` / `query`. No escriben el libro.

Prohibido: User → Agent → Docling → Graph → Agent → LlamaIndex → Agent → Core → Agent → UI.

### Niveles de interacción (no saltar)

| Nivel | Cuándo | Qué hay |
|-------|--------|---------|
| 1 | Una pregunta, un claim | UI → API → retrieve → verify. **Sin orquestador** |
| 2 | Varios períodos | Un orquestador + tools deterministas |
| 3 | Explicar / graficar | + analysis / viz **después** del verify |
| 4 | Multi-agent real | Solo con necesidad concreta. No “porque sí” |

Tool ≠ Agent. Una función Python que consulta el índice no se llama “Retrieval Agent”.

### Architecture Gate

Antes de agregar una pieza:

> ¿Qué problema concreto resuelve que lo actual no puede?

| Pieza | Pasa el gate si… | No pasa si… |
|-------|------------------|-------------|
| Graph | Identity estable + merge entre documentos | “Hay que tener un grafo” |
| LlamaIndex | Retrieval sobre estructura | “Hay que tener RAG” |
| Orquestador | La pregunta es **compuesta** | “Los sistemas modernos son agentic” |
| Segundo agente | Un oficio que el orquestador+tools no cubre | Un agente por función |
| VLM | El parse estándar **falló** gold | Por si acaso |
| Neo4j | El libro ya tiene historia que consultar | Desde el día uno |

`FinancialClaim` queda **fuera** del Graph en el MVP. Graph, si entra, es Document / Issuer / Period / Statement.

### Camino crítico (lo único que tiene que existir para que el proyecto sea fuerte)

```text
DOC → DOCLING → CLAIMLEDGER → OPEN WEBUI
```

Alrededor, no encadenado: DocLang (intercambio), Graph (IDs en ingest), LlamaIndex (retrieval), agentes (orquestación cuando haga falta).

---

## 25. Arranque de implementación

El pulido que faltaba para codear es el contrato de **Fase 0**, no más capas.

Canónico de arranque: [fase-0.md](fase-0.md).

Ahí están: estados (`recorded` ≠ `verified`), tabla de alias v1→5 campos, esqueleto del repo, qué se porta de Claimprint, criterio de cierre y orden de commits. Si no está en ese archivo, no se implementa en Fase 0.
