# Proposal: Native Table Grid and Body Walk

## Intent

Stop copying two jobs Docling already does inside `extract_recipe`. Read the grid Docling saved. Ask Docling for the body tables. Keep the code that decides which row is a verified financial claim.

## Scope

### In Scope

- Delete `_grid_from_cells`. When `data.grid` is missing, call `TableData.grid` from the `docling==2.130.0` install.
- Replace `_index_items`, `_ordered_items`, and `_body_tables` with `DoclingDocument.iterate_items`. Default content layers stay in force (body only on this install).
- Map each yielded table back to the stored JSON dict by `self_ref`, so label, amount, and bbox code keep reading dicts.
- Spec delta on `docling-ingest`. Tests fail first. Kernel modules stay free of a `docling` import.
- Confirm the two quarterly EEFF still emit the same recipe values, including `21262335` and `21259769`.

### Out of Scope

- Recipe slot rules, column picking, `_normalize_bbox`, gold, the ledger, lookup, query, the card, crop, graph, and retrieval drawers.
- Reconverting PDFs. Changing artifact hashes.
- A new package or a walker script.
- Phases 9–13. Archiving phase 1A or the audit from this change.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `docling-ingest`: Body tables and their grids MUST come from the pinned Docling document API. Hand-copied span expansion and a hand-copied document walk MUST NOT remain. Recipe selection stays custom.

## Approach

Approach 1. Two apply steps. Step 1 deletes the span loop. Step 2 replaces the walk. Each step has a failing test before production code. The import of Docling stays inside the function that needs it, as `parse.py` already does.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `ingest/extract.py` | Edit | Grid read and body walk |
| `tests/ingest/test_extract.py` | Edit | Fallback grid and walk order |
| `docling-ingest` spec | Delta | Native grid and native body list |
| Kernel, gold, crop, graph | None | The gap stays |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `iterate_items` order differs from the hand walk, so the first kept claim changes | Med | Step 2 compares claims on the two quarterly EEFF before the swap is accepted. Existing tests must fail first if values move |
| Synthetic fixtures fail `model_validate` | Med | Add only the fields that call requires. Do not restore the hand walk |
| A top-level Docling import reaches a kernel test | Low | Import inside the function. Kernel module list stays untouched |

## Rollback Plan

Revert `ingest/extract.py` and the extract tests. Hashes, gold, and the ledger stay as they are. The audit run `runs/2026-10-05/audit.md` stays.

## Dependencies

- `docling==2.130.0` (installed `docling-core==2.99.0` for `TableData` and `DoclingDocument`).
- No new dependency.

## Success Criteria

- [x] `_grid_from_cells` is gone. A cells-only table uses `TableData.grid`.
- [x] Body tables come from `iterate_items`. The hand index is gone.
- [x] Furniture tables still produce no recipe claim.
- [x] The two quarterly EEFF still yield the same seven recipe values per period.
- [x] Kernel tests still do not import `docling`. Gold numbers are unchanged.
