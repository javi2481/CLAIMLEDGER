# Plan de implementación

Arquitectura **cerrada**. Este archivo es el **orden de trabajo**, no un rediseño.

Contratos: [rector §15](documento-rector.md) · [fase-0.md](fase-0.md) · [ingenieria.md](ingenieria.md) · fase 0 archivada en [`2026-09-23-fase-0-kernel`](../openspec/changes/archive/2026-09-23-fase-0-kernel/).

TDD estricto. Rojo → verde → refactor. Un slice = un commit = un PR encadenado. Tests van **con** el comportamiento.

---

## Estado (2026-10-07)

Este archivo sigue siendo el orden en que se construyó. El trabajo de las oleadas A y B está cerrado. De la oleada C, la fase 10 no se abrió.

Cambio SDD activo: ninguno. Specs vigentes: `openspec/specs/`. La auditoría del stack nativo es una función a pedido, no una fase: `openspec/changes/auditoria-stack-nativo/runs/2026-10-07/audit.md`.

| Fase | Estado | En el código | Límite respecto del borrador |
|------|--------|--------------|------------------------------|
| 0–7 | Cerradas | Kernel, PDF, grafo, dos cajones, verify, HTTP, ficha | — |
| 1A, tablas nativas | Cerradas | Corpus y grilla leída con la API de Docling | — |
| 8 | Cerrada | Recorte propio del PNG de la página | — |
| 9 | Cerrada | Resta en `period/difference.py`, fuera del kernel | — |
| 10 | Diferida | El cambio no existe | Hace falta una GPU para el segundo lector VLM |
| 11 | Cerrada | `CypherExporter` escribe `graph.cypher`. Los períodos salen de ese script. Cada cifra sale de `query` | No hay servidor Neo4j ni driver |
| 12 | Cerrada | Fence Mermaid `xychart-beta`. Un trimestre sin cifra es la línea `Hueco:` | Sin matplotlib y sin Artifact |
| 13 | Cerrada | `orchestrate/plan.py` llama a `query` una vez por trimestre, con `compare` en falso | No es un workflow de LlamaIndex ni un agente |

---

## Tres oleadas

| Oleada | Qué es | Listo cuando |
|--------|--------|----------------|
| **A — Kernel** | Fase 0. Libro + juez en memoria. Sin PDF. | `pytest` verde. Vecino + abstención. Sin importar Docling. |
| **B — MVP** | Fases 1–7. PDF real → ficha. | `21.262.335 ≠ 21.259.769` en Open WebUI. |
| **C — Gate** | Fases 8–13. | Solo si el gate de §24 dice sí. |

No se empieza B si A no cierra. No se empieza C si B no cierra.

---

## Registro — arranque de la fase 0 (cerrado)

El repo ya es git. La fase 0 está archivada. Estos cuatro pasos fueron el arranque; no hay que repetirlos.

1. `git init`.
2. Rama `fase-0-kernel` (o commits sobre `main` si no hay remoto).
3. Cadena: **8 PRs / 8 commits**, un slice cada uno. No un monstruo de 1500 líneas.
4. Estrategia: `feature-branch-chain` si hay GitHub; si no, 8 commits locales con el mismo criterio de review.

---

## Oleada A — Fase 0 (`fase-0-kernel`)

Cambio SDD archivado: explore → propose → spec (63 escenarios) → design → [tasks](../openspec/changes/archive/2026-09-23-fase-0-kernel/tasks.md).

`sdd-apply` **por slice**. No aplicar las 16 tareas de un saque.

| Slice | Commit | RED luego GREEN | Test |
|-------|--------|-----------------|------|
| 1 | Esqueleto + pins declarados | Módulos vacíos; ningún `import docling` | `pytest tests/test_identity.py -k pins` |
| 2 | Identidad, período, `digits_ars`, aliases | Claves del vecino; 21.262.335 → 21262335 | `pytest tests/test_identity.py` |
| 3 | Claim + evidence | Key inconsistente falla; no `verification_status` | idem |
| 4 | Ledger upsert | 14 filas; 22362983 no es neto current; `recorded` ≠ `verified` | `pytest tests/test_ledger.py` |
| 5 | Lookup | Orden de frases; YPF/memoria/comunicado se abstienen | `pytest tests/test_lookup.py` |
| 6 | Query | Consolidado 21262335; comparar = 2 claims, **sin resta** | `pytest tests/test_query.py` |
| 7 | Gold v1 (45) | `id-01`; `na-*` skip; scan anti-docling | `pytest tests/test_gold_v1.py` |
| 8 | Gold v2 (26) | Impuesto `-14950948`; sin press/deck | `pytest tests/test_gold_v2.py` |

**Cierre A:** `pytest` verde. Demo de portfolio = esa corrida + las dos filas. Sin HTTP.

Después: `sdd-verify` → `sdd-archive` de `fase-0-kernel`.

---

## Oleada B — MVP (un cambio SDD por fase)

Cada fase: explore → propose → spec → design → tasks → apply (TDD) → verify. Architecture Gate en el propose.

| Fase | Cambio (nombre tentativo) | Cierre | Fuera |
|------|---------------------------|--------|-------|
| 1 | `fase-1-docling-adapter` | PDF BYMA → JSON hasheado → filas. Vs gold. Sin MinerU. | VLM, Markdown |
| 2 | `fase-2-graph-ingest` | Graph **simple** al ingerir (Document/Issuer/Period/Statement). Claim **fuera** del Graph. | Dense/LLM, rebuild por pregunta |
| 3 | `fase-3-retrieval` | Reader **JSON** + dos cajones | Markdown default |
| 4–5 | `fase-4-verify-eval` | Retrieval → query. Trampa del vecino medida | Relajar gold |
| 6 | `fase-6-http` | `POST /claims/query` | API grande |
| 7 | `fase-7-ficha` | Open WebUI → API. Sello + chips + texto. **Sin orquestador** | Pipelines, Knowledge RAG |

**Cierre B (MVP):** alguien pregunta el neto consolidado y ve 21.262.335 verificado. Pregunta ambigua → me abstengo. Eso se puede mostrar.

---

## Oleada C — gates ya respondidos

La tabla de Estado, arriba, es el resultado. Estas preguntas fueron el filtro. La fase 10 sigue en espera.

| Fase | Gate (pregunta que tiene que ser “sí”) |
|------|----------------------------------------|
| 8 Recorte | ¿La ficha ya convence sin foto? |
| 9 Pack / resta | ¿Hace falta más de un documento / restar en código? |
| 10 VLM | ¿El parse estándar **falló** gold? |
| 11 Neo4j | ¿El libro ya tiene historia que consultar? |
| 12 Gráfico | ¿Ya hay serie verificada? |
| 13 Orquestador | ¿La pregunta es **compuesta**? |

Si la respuesta es “porque queda lindo” → no.

---

## Cómo se trabaja cada slice

```text
test que falla
    → pytest (rojo, por la razón correcta)
    → mínimo código
    → pytest verde
    → refactor
    → commit (tests + código juntos)
```

Si un test de A pide un PDF o `import docling`: el slice está mal. Parar.

---

## Demo que se cuenta, por oleada

| Cuándo | Qué se muestra |
|--------|----------------|
| Fin A | `pytest` : consolidado ≠ controlante; YPF se abstiene |
| Fin B | Ficha en Open WebUI. Misma tesis, PDF de verdad |
| Fin C | Solo lo que el gate habilitó (recorte, 4 trimestres, gráfico, …) |

Nunca se cuenta: “usé cinco frameworks”. Se cuenta: *el problema está entre buscar y afirmar; esta capa lo resuelve; 71 casos no se tocan.*
