# CLAIMLEDGER — agent contract

Architecture is **closed**. Canonical: `docs/documento-rector.md`. Filter: `docs/north-star.md`. Fase 0: `docs/fase-0.md`. SDD: `openspec/`.

## Language

- Chat with the user: Spanish.
- OpenSpec / SDD artifacts: English.
- Code identifiers: English. User-facing claim labels may stay Spanish.

## Strict TDD

`openspec/config.yaml` has `strict_tdd: true`.

1. Write a failing test.
2. Run `pytest`. It MUST fail for the right reason.
3. Write the minimum production code.
4. Refactor only while green.

Kernel tests MUST NOT import `docling`. No network. No PDF. No Docker.

## Architecture Gate

Do not add a component because “modern systems use it”. It must solve a problem the current design cannot.

Never: MinerU, Markdown as retrieval source of truth, LLM-written `identity_v1`/`identity_v2`, an agent that skips the kernel, relaxing gold numbers.

## Change workflow

`sdd-explore` → `sdd-propose` → `sdd-spec` → `sdd-design` → `sdd-tasks` → `sdd-apply` → `sdd-verify` → `sdd-archive`.

Active change: `openspec/changes/fase-7-openwebui/`. Archived: `openspec/changes/archive/2026-10-04-fase-7-ficha/`, `openspec/changes/archive/2026-10-04-fase-6-http/`, `openspec/changes/archive/2026-10-04-fase-4-verify-eval/`, `openspec/changes/archive/2026-10-04-fase-3-retrieval/`, `openspec/changes/archive/2026-10-04-fase-2-graph-ingest/`, `openspec/changes/archive/2026-10-04-fase-1-docling-adapter/`, `openspec/changes/archive/2026-09-23-fase-0-kernel/`.
