# Stack: investigación y oportunidades

23 septiembre 2026. Parallel sobre Docling 2.130, Graph 1.9.1, LlamaIndex, Open WebUI, DocLang.

Este archivo es la investigación de esa fecha. El estado de cada fase está en [plan-implementacion.md](plan-implementacion.md). Las fases 8, 9, 11, 12 y 13 cerraron más angostas que este borrador. La 10 sigue diferida.

El north star no cambia: kernel determinista, gold congelado, no LLM sobre identidad.

---

## Docling 2.130.0 — usar al máximo (estable)

Ya en el pin ([PyPI 2.130.0](https://pypi.org/project/docling/), 22 sep 2026):

- Un solo modelo: `DoclingDocument` (texts, tables, pictures, key_value_items, `body` vs `furniture`, jerarquía, bbox, provenance). El reading order es el árbol `body`. [Docling document](https://docling-project.github.io/docling/concepts/docling_document/)
- Export lossless JSON; Markdown/HTML/DocLang también. JSON es canónico. [Docling GitHub](https://github.com/docling-project/docling)
- Tablas de primera clase. CLI `--table-structure-engine` y `--layout-engine` desde 2.120. `compact_tables` desde 2.122 (para HTML de revisión, no para identidad). Pipeline PDF nativo desde 2.126. [CHANGELOG](https://github.com/docling-project/docling/blob/main/CHANGELOG.md)
- Chunkers nativos: `HierarchicalChunker` (un chunk por elemento + metadata), `HybridChunker` (tokens + `repeat_table_header`), `LineBasedTokenChunker` (respeta líneas de tabla). [Chunking](https://docling-project.github.io/docling/concepts/chunking/)
- CLI puede emitir chunks JSONL (2.111). PPTX: charts nativos como pictures con datos (2.113) — útil para decks BYMA. [CHANGELOG](https://github.com/docling-project/docling/blob/main/CHANGELOG.md)
- XBRL extra, ejecución local. [PyPI](https://pypi.org/project/docling/)

**Adoptar en Fase 1:** JSON + grid de tablas + furniture fuera del body + A/B de table-structure-engine. Hierarchical/LineBased para filas. HybridChunker solo para narrativa.

**Fase 10 — diferida:** pipeline VLM de Docling como **segundo lector** de páginas difíciles o de gráficos. Sigue siendo parse: el resultado se compara con gold. Si pierde, no se cambia gold. No hay GPU para abrirlo.

**No:** MinerU. Markdown como evidencia. VLM que escriba `identity_v1` / `identity_v2`.

---

## Docling Graph 1.9.1 — usar el grafo, no el extractor

Estable ([PyPI 1.9.1](https://pypi.org/project/docling-graph/), 17 jul):

- Templates Pydantic: `graph_id_fields` / `is_entity=False`. MonetaryAmount es el ejemplo oficial de component. [Entities vs Components](https://docling-project.github.io/docling-graph/fundamentals/schema-definition/entities-vs-components)
- Merge determinista, 0 LLM, conflictos auditados, alias → HITL. [merge](https://docling-project.github.io/docling-graph/usage/cli/merge-command/)
- Ledger `__provenance__` + `provenance.json` (chunk text, page, bbox). Token cost cero. [Provenance](https://docling-project.github.io/docling-graph/fundamentals/graph-management/provenance)
- Export JSON/CSV/Cypher + `inspect` HTML. [PyPI](https://pypi.org/project/docling-graph)
- `convert` por defecto usa backend LLM. DocLang como input al LLM es más caro (~25–45% menos contenido por chunk). [Document conversion](https://docling-project.github.io/docling-graph/fundamentals/extraction-process/document-conversion/)

**Adoptar:** escribir nodos **desde** el kernel (IDs ya resueltos) y usar merge/ledger/inspect. Templates Issuer/Period/Document/Section.

**Fase 11 — hecha en el export:** `CypherExporter` escribe el script. El lookup sigue siendo la verdad de la cifra. No se levantó una base Neo4j.

**No:** `docling-graph convert --extraction-contract dense` sobre EEFF BYMA. Neo4j no reemplaza la verificación.

---

## LlamaIndex — candidatos con geometría

- Integración oficial: Reader (JSON lossless o Markdown lossy) + Node Parser. [Docling ↔ LlamaIndex](https://docling-project.github.io/docling/integrations/llamaindex/)
- Default del Reader = markdown. JSON + `DoclingNodeParser` deja `page_no` y `bbox` en metadata (`DocMeta`, `doc_items`). [RAG example](https://docling-project.github.io/docling/_generated/examples/rag_llamaindex/)
- El parser parte por elementos (párrafo, heading, tabla) y acepta un `chunker` (default `HierarchicalChunker`). [DoclingNodeParser API](https://developers.llamaindex.ai/python/framework-api-reference/node_parser/docling/)
- Reader PyPI **0.5.0** (31 ago 2026). [llama-index-readers-docling](https://pypi.org/project/llama-index-readers-docling)

**Adoptar:** `ExportType.JSON` + NodeParser + filtro metadata `label=table`. Dos índices si hace falta (tabla vs narrativa).

**Pin tentativo:** `llama-index-readers-docling==0.5.0` (validar contra Docling 2.130 en Fase 3).

**Fase 13 — hecha sin esos workflows.** El plan de cuatro trimestres es código que llama a `query`. Los patrones [AgentWorkflow, Orchestrator, Custom planner](https://developers.llamaindex.ai/python/framework/understanding/agent/multi_agent/) y el fan-out de [LlamaIndex](https://developers.llamaindex.ai/python/llamaagents/workflows/concurrent_execution/) quedaron como investigación. Identidad y verificación siguen siendo servicios.

---

## Open WebUI — presentación, no RAG

- Cualquier backend OpenAI-compatible. [docs](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/)
- MCP nativo desde 0.6.31; también OpenAPI tools. El modelo tiene que saber usar tools; si falla, no es (solo) la UI. [MCP](https://docs.openwebui.com/features/extensibility/mcp)
- Citas nativas: eventos `citation` / sources desde tool results. [middleware](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/utils/middleware.py)

**Adoptar (Fase 7):** un “modelo” CLAIMLEDGER que es nuestro `/v1/chat/completions` y emite citas (página + texto). Alternativa más robusta: Action/botón que llama `POST /claims/query` sin tool-calling. La primera UI es una **ficha** (sello + chips + texto de fila).

**Fase 8 — hecha:** recorte propio de la zona de la página (bbox de Docling) junto al claim.

**Fase 12 — primer peldaño hecho:** el backend emite un fence [Mermaid](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/mermaid/). [matplotlib](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/python/) y [Artifact / D3](https://docs.openwebui.com/features/chat-conversations/chat-features/code-execution/artifacts/) no se adoptaron. La UI no calcula.

**No:** Knowledge/RAG interno de Open WebUI para números. No Pipelines. No MinerU. No Mermaid con cifras inventadas por el modelo. No Code Interpreter para “sacar el balance”.

---

## Sugerencias, ya ordenadas (contrato en el rector §20)

| Fase | Idea | Qué ve el usuario |
|------|------|-------------------|
| 4 | La demo enseña el fallo | Dos filas; se verificó la consolidada |
| 5 | Eval de dos historias | ¿Trajo ambas? ¿Eligió la correcta? |
| 7 | Ficha, no burbuja | Sello + chips + texto. El chat después |
| 8 | Recorte de evidencia. Hecho | Foto de la fila, idea propia |
| 9 | Pack de período + comparar. Hecho | Varias fuentes; 1T vs 2T lo resta el código |
| 10 | VLM segundo lector. Diferido | Mira páginas difíciles; no decide la cifra |
| 11 | Export Cypher, sin Neo4j. Hecho | Preguntar al libro, no al modelo |
| 12 | Fence Mermaid. Hecho | CLAIMLEDGER verifica; Open WebUI dibuja |
| 13 | Plan determinista. Hecho | Una verificación por trimestre, alrededor del kernel |
| Después | XBRL, datos de slides, aire-gap | Segunda firma, sin internet |

Si el A/B de parse falla: no se relaja gold, no se inventa identidad, no vuelve MinerU.
