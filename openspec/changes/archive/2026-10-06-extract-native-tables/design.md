# Design: Native Table Grid and Body Walk

## Technical Approach

`specs/docling-ingest` delta. This change applies two `call-native` / `delete` rows from `auditoria-stack-nativo/runs/2026-10-05/audit.md`. It does not move the wave. The recipe gap stays in `extract_recipe` after the table list exists.

Pins opened on the installed tree:

- `TableData.grid` (`docling-core==2.99.0`, pulled by `docling==2.130.0`) expands `table_cells` into a grid. `export_to_dict` already writes that grid.
- `DoclingDocument.iterate_items` walks the document. `DEFAULT_CONTENT_LAYERS` is `{ContentLayer.BODY}`.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Grid | Read `data.grid`. If it is missing, lazy-call `TableData.model_validate(data).grid` | Keep `_grid_from_cells` | The helper is a copy of the computed field |
| Walk | `model_validate` then `iterate_items`. Keep the JSON dict whose `self_ref` matches | Rewrite `_cell_text` and `_normalize_bbox` onto `TableCell` in this change | Those readers are the evidence gap. `BoundingBox.normalized` does not clamp or drop origin |
| Import | Inside the function, same as `parse.py` | Module-level `import docling` | Kernel tests must stay free of that import |
| Order | Two steps: grid, then walk | One edit of all five functions | The walk can change which duplicate row is kept. The grid step cannot |
| Fallback walker | None | Hand walk when `model_validate` fails | That fallback is the code this change removes |
| Fixture | Add the minimum fields validation requires | A second synthetic schema | Tests must describe a document the pin accepts |

`iterate_items` yields library objects. Recipe code keeps reading dicts. The walk records `self_ref` values and looks them up in the stored `tables` array. Default layers exclude furniture, which is the current skip of `content_layer == "furniture"` and parent `#/furniture`.

## Data Flow

1. `extract_recipe` loads the hashed JSON.
2. A `DoclingDocument` is validated from that JSON. `iterate_items()` yields body items. Tables are kept, in that order, as the original dicts.
3. Each dict's `data.grid` is the grid. A missing grid becomes `TableData.grid`.
4. `_is_consolidated_income_table`, `_value_column`, and `_recipe_slot` run unchanged.
5. The first claim for each `(scope, metric)` is the one that stays.

## File Changes

| File | Change |
|------|--------|
| `src/claimledger/ingest/extract.py` | Delete `_grid_from_cells`. Replace the three walk helpers with the library call |
| `tests/ingest/test_extract.py` | Cells-only grid. Source no longer contains the span loop or the hand index. EEFF values unchanged |
| Kernel, gold, crop, graph, retrieval | Untouched |

## Rollback

Revert the two files. The audit report stays. Artifact hashes stay.
