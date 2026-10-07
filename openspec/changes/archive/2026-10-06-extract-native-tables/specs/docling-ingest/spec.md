# Docling-Ingest Specification (delta)

## ADDED Requirements

### Requirement: Native Table Grid and Body List

`extract_recipe` MUST read each table grid from the grid Docling already stored on that table. When that grid is absent and cells are present, it MUST obtain the grid from `TableData.grid` in the `docling==2.130.0` install. It MUST NOT keep a second span expansion. The list of body tables MUST come from `DoclingDocument.iterate_items` on that same install, with that method's default content layers. Furniture MUST stay out of the recipe. The function MUST still decide which table is the consolidated income statement, which column is the quarter, and which row is a recipe slot. It MUST NOT import `docling` at module level. Kernel tests MUST NOT import `docling`. Gold numbers MUST NOT change.

#### Scenario: Stored grid is used as saved

- GIVEN a table whose `data.grid` is already present
- WHEN `extract_recipe` reads that table
- THEN it MUST use that grid
- AND it MUST NOT rebuild the grid from cell spans

#### Scenario: Missing grid uses the library

- GIVEN a table with `table_cells` and no `grid`
- WHEN `extract_recipe` reads that table
- THEN the grid MUST be `TableData.grid` from the pinned install

#### Scenario: Body list skips furniture

- GIVEN a furniture table and a body table in one document
- WHEN `extract_recipe` lists tables
- THEN only the body table MAY yield a recipe claim
- AND the list MUST come from `iterate_items`

#### Scenario: Recipe choice stays local

- GIVEN the body tables of a quarterly EEFF
- WHEN a recipe claim is built
- THEN the income-statement test, the quarter column, and the row slot MUST remain local code
- AND the consolidated net income for 2026-03-31 MUST remain `21262335`
