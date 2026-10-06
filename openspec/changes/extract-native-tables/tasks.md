# Tasks: Native Table Grid and Body Walk

## Review Workload Forecast

Estimated changed lines: under 200, all in `extract.py` and `test_extract.py`. Delivery strategy: two apply steps. No rector edit. No corpus reconvert. No commit unless the user asks.

Decision needed before apply: No
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Grid from the pin | One function | `pytest tests/ingest/test_extract.py -q` | Lazy `TableData` only when `grid` is absent | Revert the grid helpers |
| 2 | Body list from the pin | The walk, one step | `pytest tests/ingest/test_extract.py tests/test_identity.py tests/test_ledger.py -q` | `iterate_items` on the synthetic document and the two EEFF | Revert the walk only |

## Phase 1: Stored grid

- [x] 1.1 Add a failing test: a table with `table_cells` and no `grid` yields the same recipe claims as the same table with `data.grid`. Assert `extract.py` names `TableData` and does not define a span loop (`start_row_offset_idx`). Run pytest. It MUST fail because the loop is still there.
- [x] 1.2 Delete `_grid_from_cells`. `_table_grid` returns `data.grid` when it is a non-empty list. Otherwise lazy-import `TableData` and return `TableData.model_validate(data).grid` as plain dicts the current cell readers accept (`model_dump` of each cell). Do not import Docling at module level.
- [x] 1.3 Re-run `pytest tests/ingest/test_extract.py -q`. The new test passes. Quarterly values stay `21262335` and `21259769`.

## Phase 2: Body list

- [x] 2.1 Add a failing test: `extract.py` calls `iterate_items` and no longer defines `_index_items` or `_ordered_items`. Furniture still yields no claim. Run pytest. It MUST fail because the hand walk is still there.
- [x] 2.2 Replace the hand walk with `DoclingDocument.model_validate` and `iterate_items()`, mapped to stored table dicts by `self_ref`. If validation rejects the synthetic fixture, add only the fields the error names. Do not restore the hand walk.
- [x] 2.3 Re-run the extract tests. The two EEFF still emit seven recipe claims per period, with the same values. Furniture stays empty.
- [x] 2.4 Run `pytest tests/test_identity.py tests/test_ledger.py tests/test_query.py -q`. Those modules still do not import `docling`. Gold is untouched.

## Out of this apply

- [ ] 3.1 Do not edit `_recipe_slot`, `_value_column`, `_normalize_bbox`, the ledger, the card, the crop, the graph, or the drawers.
