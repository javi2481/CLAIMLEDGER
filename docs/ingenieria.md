# Ingeniería

Cómo se construye CLAIMLEDGER. La tesis está en el [rector](documento-rector.md). Esto es el oficio.

## Spec-driven (SDD)

Cambio activo: ninguno. La fase 10 queda diferida. El estado de cada fase está en [plan-implementacion.md](plan-implementacion.md). La fase 0 está archivada en `openspec/changes/archive/2026-09-23-fase-0-kernel/`.

Orden de trabajo: [plan-implementacion.md](plan-implementacion.md).

Orden: explore → propose → spec → design → tasks → apply → verify → archive.

Artefactos SDD en inglés. Docs de producto en español. Config: `openspec/config.yaml` (`strict_tdd: true`).

## Test-driven (TDD)

Rojo → verde → refactor. No hay “código primero, tests después”.

- Kernel: `pytest`, en memoria, sin red, sin PDF.
- Prohibido importar `docling` en tests del kernel.
- Gold `identity_v1` / `identity_v2`: los **números** no se tocan.
- Un test que falle si el kernel importa Docling no es opcional: guarda la tesis.

## Diseño

- Contratos chicos (identity, ledger, lookup, query).
- Estados explícitos: `recorded` ≠ `verified`.
- Architecture Gate antes de sumar una pieza.
- Dos planos: verdad (determinista) e interacción (después del juez).
- Tool ≠ Agent.

## Qué se presenta (y qué no)

Se presenta: el problema de las dos filas, el kernel que se abstiene, el gold como contrato, el SDD que impide hinchar el sistema.

No se presenta: un enjambre de agentes, un chat que “habla con PDFs”, MinerU, un grafo que extrae el P&L.
