```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c68fe06a9804ef9b81b176c9b195cfe1249bfeb2c16fa550cf6032cfe25e605b
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 3/3
scenarios: 10/10
test_command: python -m pytest -q --tb=line
test_exit_code: 0
test_output_hash: sha256:a542717560d26ee039e991efb234ede4be019d06b2de21cf0c1efd7bda981948
build_command: python -c "from claimledger.ingest.extract import extract_recipe; from claimledger.ingest.ground import recorded_book; print('ok')"
build_exit_code: 0
build_output_hash: sha256:9f2a59a60e65fbcd5a3e1b7248adf92890ce3a32b19e43fb4751c2657196de13
```

## Verification Report

**Change**: runtime-json-book
**Version**: docling-ingest delta (Import-Free Recipe Extract Path + Native Table Grid / Pin MODIFY)
**Mode**: Strict TDD

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 14 |
| Tasks complete | 14 |
| Tasks incomplete | 0 |

All checklist items in `openspec/changes/runtime-json-book/tasks.md` are `[x]` (A.1–A.6, B.1–B.3, C.1–C.3, D.1–D.2).

### Build & Tests Execution

**Build**: ✅ Passed (no project build tool; extract/ground import smoke)

```text
python -c "from claimledger.ingest.extract import extract_recipe; from claimledger.ingest.ground import recorded_book; print('ok')"
ok
exit 0
```

**Tests**: ✅ 383 passed / ❌ 0 failed / ⚠️ 0 skipped (73 third-party warnings)

```text
python -m pytest -q --tb=line
383 passed, 73 warnings in 56.99s
EXIT:0
```

Focused gold: `python -m pytest tests/ingest/test_gold_compare.py -q` → **15 passed**.

**Coverage**: ➖ Not available (`openspec/config.yaml` `coverage.detected: false`)

### Spot checks (change gates)

| Check | Result |
|-------|--------|
| `extract.py` text/AST bans `docling` / `docling_core` / `torch` / `PINNED_DOCLING` | ✅ No matches; AST import scan `[]` |
| `ground.py` bans same tokens | ✅ No matches |
| Gold `21262335` / `21259769` | ✅ Unchanged; gold compare green; no gold/artifact git diffs |
| `reply.py` / `retrieval/*` / Dockerfile | ✅ Unchanged (0-line diff) — reply/DoclingReader gap preserved |
| `pyproject` `ingest=[httpx==0.28.1]`; httpx stripped from `docling` | ✅ |
| CI matrix product without Docling; heavy has `ingest`+`docling`+… | ✅ |

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Import-Free Recipe Extract Path | Extract sources ban Docling imports | `tests/ingest/test_extract.py` > `test_extract_source_bans_docling_torch_and_pin` | ✅ COMPLIANT |
| Import-Free Recipe Extract Path | Book path stays Docling-free at import time | `tests/ingest/test_ground.py` > `test_book_path_sources_ban_docling_torch_and_pin` + `test_recorded_book_api_unchanged_and_cache_hit_serve_free` | ✅ COMPLIANT |
| Import-Free Recipe Extract Path | Reply retrieval remains deferred | Static: no diff on `reply.py` / `retrieval/*` / Dockerfile; design Known gap | ✅ COMPLIANT |
| Docling Pin Without Graph | Pin and graph ban | Existing convert/store/compose pin tests (`test_convert_local*`, graph bans) | ✅ COMPLIANT |
| Docling Pin Without Graph | extract_recipe must not use docling_core | `test_extract_source_bans_*` + AST/import scan | ✅ COMPLIANT |
| Native Table Grid and Body List | Stored grid is used as saved | `test_extract_source_reads_grid_not_markdown` + EEFF recipe extract/gold | ✅ COMPLIANT |
| Native Table Grid and Body List | Missing grid is an error | `test_cells_without_grid_raise_ingest_error` | ✅ COMPLIANT |
| Native Table Grid and Body List | Body list skips furniture | `test_body_tables_come_from_json_walk_not_iterate_items` + `test_furniture_recipe_row_is_ignored` | ✅ COMPLIANT |
| Native Table Grid and Body List | Nested body refs are resolved | `test_body_tables_come_from_json_walk_not_iterate_items` (body→groups→tables) | ✅ COMPLIANT |
| Native Table Grid and Body List | Recipe choice stays local | `test_the_two_eeff_keep_distinct_net_income` + `test_gold_compare` (`21262335`) | ✅ COMPLIANT |

**Compliance summary**: 10/10 scenarios compliant

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Import-Free Recipe Extract Path | ✅ Implemented | Pure JSON extract; book path import-scanned |
| Docling Pin Without Graph (MODIFY) | ✅ Implemented | extract no longer MAY use docling_core/pin |
| Native Table Grid and Body List (MODIFY) | ✅ Implemented | DFS `$ref` from `body`; `data.grid` only / `IngestError` |
| Proposal OOS (reply/retrieval/gold) | ✅ Honored | Gap documented; gold frozen |
| Phase C extras/CI | ✅ Implemented | `test_extras_ci.py` locks pyproject + workflow |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| DFS from `payload["body"]`; never furniture | ✅ Yes | `_body_tables` stack walk |
| Non-empty `data.grid` else `IngestError` | ✅ Yes | `_table_grid` |
| Delete pin/torch/`TableData` helpers | ✅ Yes | No PINNED / TableData in extract |
| Reply / Docker unchanged | ✅ Yes | Known gap in design.md |
| `ingest=[httpx]`; strip from docling | ✅ Yes | CI heavy includes `--extra ingest` |

### TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | `sdd/runtime-json-book/apply-progress` TDD Cycle Evidence table |
| All tasks have tests | ✅ | A/B/C code tasks map to test files; D docs N/A |
| RED confirmed (tests exist) | ✅ | `test_extract.py`, `test_ground.py`, `test_extras_ci.py`, `test_gold_compare.py` |
| GREEN confirmed (tests pass) | ✅ | Full suite 383 passed |
| Triangulation adequate | ✅ | Nested+furniture; cells+empty grid; product vs heavy extras |
| Safety Net for modified files | ✅ | Apply reported safety nets on extract/ground |

**TDD Compliance**: 6/6 checks passed

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | covering change scenarios | `test_extract.py`, `test_ground.py`, `test_extras_ci.py`, `test_gold_compare.py` | pytest |
| Integration | suite includes ingest/book paths | same pytest command | pytest |
| E2E | 0 | — | not installed |
| **Total (full suite)** | **383** | — | pytest |

### Changed File Coverage

Coverage analysis skipped — no coverage tool detected.

### Assertion Quality

**Assertion quality**: ✅ All assertions verify real behavior (banned-token source scans, `IngestError` raises, gold values, extras matrix string checks — no tautologies found)

### Quality Metrics

**Linter**: ➖ Not available  
**Type Checker**: ➖ Not available

### Issues Found

**CRITICAL**: None

**WARNING**:
1. Optional D.2 manual smoke (cache-hit `recorded_book`+`query` **without** Docling wheel installed) was not executed in this verify pass — pytest ran in an environment that still has Docling available for heavy/graph tests.
2. Proposal `Success Criteria` checkboxes remain unchecked in `proposal.md` despite implementation (hygiene; does not block runtime).
3. Cursor plan `.cursor/plans/runtime_json_book_followups.plan.md` todos still show in_progress/pending while `tasks.md` is fully `[x]` (plan not edited per verify instructions).

**SUGGESTION**:
1. Archive should restate reply/`DoclingReader`/Dockerfile `.[retrieval]` follow-up (already in design Known gap).
2. Design open question “Product job adds `--extra ingest`…” still unchecked; CI already keeps ingest on heavy job only — close the checkbox at archive.
3. 73 pytest warnings are third-party Docling/Pydantic deprecations; unrelated to this change.

### Verdict

**PASS WITH WARNINGS**

14/14 tasks complete; 10/10 spec scenarios compliant; full pytest **383 passed** (exit 0); `extract.py` has zero Docling/torch/pin imports; gold `21262335` / `21259769` unchanged. Warnings are process/hygiene and optional wheel-absent smoke only.
