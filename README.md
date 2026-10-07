# CLAIMLEDGER

Libro de afirmaciones financieras verificadas.

**Si no hay una afirmación verificada, no hay respuesta.**

Recuperar la página correcta **no** equivale a identificar el dato correcto. En BYMA 1T26, la misma página tiene:

| Fila | Valor |
|------|--------|
| Resultado neto del período | **21.262.335** |
| Resultado atribuible a la controlante | **21.259.769** |

CLAIMLEDGER es la capa que falta entre buscar evidencia y afirmar un número. No es un chatbot de PDFs.

## Estado

Diseño cerrado. Fases 0–9 y 11–13 implementadas. La fase 10 (VLM) está diferida hasta que haya una GPU. El cambio activo es `ground-ledger`: el juez lee el libro armado desde los dos estados de resultados.

La fase 11 escribe `graph.cypher` y no levanta Neo4j. La fase 12 dibuja un fence Mermaid de una serie ya verificada. La fase 13 es un plan determinista que llama a `query` una vez por trimestre. El detalle está en el [plan](docs/plan-implementacion.md).

Pins: `docling==2.130.0` · `docling-graph==1.9.1` · LlamaIndex docling `0.5.0` · `starlette==1.0.0` · Open WebUI `v0.11.4-slim`. Python ≥3.11.

## Leer

| Doc | Para qué |
|-----|----------|
| [North star](docs/north-star.md) | Filtro: ¿esta decisión suma o distrae? |
| [Documento rector](docs/documento-rector.md) | Tesis, stack, planos, gate |
| [Fase 0](docs/fase-0.md) | Contrato de arranque del kernel |
| [Plan de implementación](docs/plan-implementacion.md) | Estado de cada fase, oleadas y slices TDD |
| [Ingeniería](docs/ingenieria.md) | SDD + TDD |
| [Specs](openspec/specs/) | Contratos vigentes |
| [Fase 0 archivada](openspec/changes/archive/2026-09-23-fase-0-kernel/) | Primer cambio SDD, ya cerrado |
| [AGENTS.md](AGENTS.md) | Contrato para agentes |

## Cómo se construye

```text
PDF → JSON hasheado → candidatos y recorte en pantalla

Dos estados de resultados trimestrales → libro en memoria → CLAIMLEDGER (juez) → Open WebUI
```

El juez lee ese libro, no una lista fija. La lista fija queda en las pruebas del núcleo. Los agentes, si aparecen, **piden**; no escriben la cifra. Graph se arma al ingerir, no en cada pregunta. MVP = esas dos filas + abstenerse.

Hereda de Claimprint la tesis y 71 casos de prueba. No hereda MinerU ni RAGFlow.

## Barra

Académico y de portfolio: el valor está en **dónde** se pone la inteligencia, no en cuántos modelos se encadenan.
