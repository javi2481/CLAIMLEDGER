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

Diseño cerrado. Kernel **aún no implementado**. El primer cambio SDD es `fase-0-kernel` (TDD estricto, sin Docling).

Pins a declarar: `docling==2.130.0` · `docling-graph==1.9.1`. Python ≥3.11.

## Leer

| Doc | Para qué |
|-----|----------|
| [North star](docs/north-star.md) | Filtro: ¿esta decisión suma o distrae? |
| [Documento rector](docs/documento-rector.md) | Tesis, stack, planos, gate |
| [Fase 0](docs/fase-0.md) | Contrato de arranque del kernel |
| [Plan de implementación](docs/plan-implementacion.md) | Oleadas A/B/C y slices TDD |
| [Ingeniería](docs/ingenieria.md) | SDD + TDD |
| [OpenSpec](openspec/changes/fase-0-kernel/) | explore → propose → spec → design → tasks |
| [AGENTS.md](AGENTS.md) | Contrato para agentes |

## Cómo se construye

```text
PDF → Docling → evidencia → CLAIMLEDGER (juez) → Open WebUI
```

El juez es determinista. Los agentes, si aparecen, **piden**; no escriben la cifra. Graph se arma al ingerir, no en cada pregunta. MVP = esas dos filas + abstenerse.

Hereda de Claimprint la tesis y 71 casos de prueba. No hereda MinerU ni RAGFlow.

## Barra

Académico y de portfolio: el valor está en **dónde** se pone la inteligencia, no en cuántos modelos se encadenan.
