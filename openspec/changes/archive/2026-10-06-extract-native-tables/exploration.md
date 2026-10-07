## Exploration: extract-native-tables

Architecture is CLOSED. This change is the replacement step named by `openspec/changes/auditoria-stack-nativo/runs/2026-10-05/audit.md`. It is not a wave number. Phase 1A stays the corpus close-out. Phases 9–13 stay unopened.

The audit found two copies of pinned Docling behavior in `src/claimledger/ingest/extract.py`:

- `_grid_from_cells` repeats `TableData.grid`. `export_to_dict` already stores that grid on `data.grid` (`docling==2.130.0`, installed `docling-core==2.99.0`).
- `_index_items`, `_ordered_items`, and `_body_tables` repeat `DoclingDocument.iterate_items`. On this install `DEFAULT_CONTENT_LAYERS` is `{ContentLayer.BODY}`, so furniture is already excluded.

Everything after that list is the product gap: which table is the consolidated income statement, which column is the quarter, which row is a recipe slot, and the clamped evidence bbox. `BoundingBox.normalized` does not replace `_normalize_bbox`.

### Current State

`extract_recipe` reads a hashed JSON dict. Tests build a small dict with `body`, `furniture`, `tables`, and `data.grid`. Real artifacts from `load_or_convert` are full `export_to_dict()` documents and already contain `data.grid`. `iterate_items` yields `TableItem` objects. The recipe readers (`_cell_text`, `_page_no`, `_normalize_bbox`) read dicts. A native walk can choose the tables, then the existing dict for that `self_ref` can feed the readers.

`tests/ingest/test_extract.py` calls `extract_recipe` on synthetic dicts and on the two quarterly EEFF. Kernel modules must stay free of a `docling` import. `parse.py` already imports Docling inside the function that needs it.

### Affected Areas

- `src/claimledger/ingest/extract.py` — delete the span loop; replace the hand walk.
- `tests/ingest/test_extract.py` — lock grid fallback and body order. Synthetic fixtures may need the minimum fields `model_validate` requires.
- `openspec/specs/docling-ingest/spec.md` — delta only, merged on archive.
- Out: gold, ledger, lookup, query, card, crop math, graph, retrieval drawers, corpus reconvert.

### Approaches

1. **Two apply steps in this change** — First delete the span loop and call `TableData.grid` only when `data.grid` is missing. Then replace the hand walk with `iterate_items`, mapped back to the stored table dict by `self_ref`. Recipe selection stays.
   - Pros: Matches the audit order. The first step does not change which tables are read. The second step is the order-sensitive one.
   - Cons: Synthetic fixtures may not validate as a `DoclingDocument` until their missing fields are filled.
   - Effort: Low — **chosen**

2. **Keep the hand walk as a fallback when validation fails** — Native call when the JSON is a full document, old walker otherwise.
   - Pros: Current fixtures would keep passing untouched.
   - Cons: The copy the audit named would remain.
   - Effort: Low — **reject**

3. **Rewrite recipe readers onto `TableCell` objects in the same edit** — One pass converts the whole function to library types.
   - Pros: No dict lookup after the walk.
   - Cons: Folds the bbox and label gap into the native swap. The audit said one function at a time.
   - Effort: Medium — **reject**

### Recommendation

Take approach **1**. Do not apply it from this planting.

### Out of Scope Confirmation

- Gold numbers, identity, verification, abstention, the card seal.
- `_normalize_bbox`, crop, graph, retrieval drawers.
- A second parser, MinerU, Markdown as source of truth.
- Reconverting the ten sample PDFs.
