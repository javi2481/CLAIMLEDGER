## Verification Report

**Change**: extract-native-tables
**Date**: 2026-10-06
**Mode**: Strict TDD
**Verdict**: PASS WITH WARNINGS

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 8 |
| Tasks complete | 8 |
| Tasks incomplete | 0 |

Tasks 1.1–1.3, 2.1–2.4, and 3.1 are `[x]`. `_recipe_slot`, `_value_column`, and `_normalize_bbox` stayed. The ledger, card, crop, graph, and drawers were not rewritten.

### Build & Tests

No build command is configured.

`python -m pytest tests/ -q` exited 0: 309 passed, 0 failed, 73 warnings, 18.56s.

The first full run in this close exited 1: 9 failed, 300 passed. Graph and retrieval tests hit `WinError 1114` on `torch\lib\c10.dll` after `extract_recipe` imported Docling before torch. The same Windows order is already guarded in `parse.convert_pdf`. `_load_pinned_docling` now imports torch before Docling. The suite then passed.

`test_wave_c_still_waits` still required the active folder `fase-8-crop` after that change was archived. It now requires the archived folder and rejects an active `fase-8-crop`. Phases 9–13 stay absent.

### Requirements

The delta has 1 requirement and 4 scenarios.

| Scenario | Result |
|----------|--------|
| Stored grid is used as saved | `extract.py` reads `data.grid` and does not define `start_row_offset_idx` |
| Missing grid uses the library | `test_cells_without_grid_match_stored_grid` calls `TableData` |
| Body list skips furniture | `test_body_tables_come_from_iterate_items` and `test_furniture_recipe_row_is_ignored` |
| Recipe choice stays local | Quarterly EEFF still emit `21262335` and `21259769` |

Docling is imported inside the function, not at module level. Kernel tests do not import `docling`. Gold numbers were not edited.
