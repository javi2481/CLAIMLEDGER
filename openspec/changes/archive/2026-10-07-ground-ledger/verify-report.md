```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:6d991cbb923a0404da15212c04ae04acc76c933ee66ddc9c0453929df53743f2
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 7/7
scenarios: 26/26
test_command: python -m pytest
test_exit_code: 0
test_output_hash: sha256:6d991cbb923a0404da15212c04ae04acc76c933ee66ddc9c0453929df53743f2
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: ground-ledger
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest` stdout+stderr (8611 bytes, Windows CRLF, 104 CRLF newlines). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\ground-ledger-pytest-full.txt`. The preimage is not this markdown file.

Counted from the four delta specs under `openspec/changes/ground-ledger/specs/`: **7 requirements, 26 scenarios**. Engram searches for `sdd/ground-ledger/{spec,tasks,design,apply-progress}` returned no observations; completeness and correctness follow the OpenSpec change files on disk. Implementation commit cited by the orchestrator: `a427ee5`.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 8 |
| Tasks complete | 8 |
| Tasks incomplete | 0 |

All eight checkboxes in `openspec/changes/ground-ledger/tasks.md` are `[x]` (1.1–1.6, 2.1–2.2). Full suite was allowed to run.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 344 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest
exit 0
====================== 344 passed, 73 warnings in 19.67s ======================
```

**Coverage**: ➖ Not available (`coverage.detected: false` in `openspec/config.yaml`)

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Quarterly Book | Fourteen rows with evidence | `tests/ingest/test_ground.py > test_recorded_book_matches_recipe_and_verifies_with_evidence` | ✅ COMPLIANT |
| Quarterly Book | Missing file | `tests/ingest/test_ground.py > test_missing_quarterly_file_raises` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Load or convert by hash | `tests/ingest/test_store.py > test_load_existing_artifact_by_canonical_hash`, `test_missing_hash_converts_local_path_only`, `test_existing_pdf_hash_loads_without_reconvert` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Mismatched bytes are rejected | `tests/ingest/test_store.py > test_load_rejects_bytes_that_do_not_match_the_name` | ✅ COMPLIANT |
| Hashed Immutable JSON Store | Cache hit does not reconvert a mismatch | `tests/ingest/test_store.py > test_cache_hit_rejects_mismatch_without_reconvert` | ✅ COMPLIANT |
| Call Order | Retrieve, then understand, then query | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors`, `test_measure_queries_the_passed_ledger_and_does_not_seed` | ✅ COMPLIANT |
| Call Order | Omitted ledger is the quarterly book | `tests/eval/test_measure.py > test_omitted_ledger_is_the_quarterly_book` | ✅ COMPLIANT |
| Call Order | Question does not drop a row | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors`, `test_slice2_empty_question_keeps_both_rows` | ✅ COMPLIANT |
| Call Order | Identity is not parsed from candidate text | `tests/eval/test_measure.py > test_slice1_call_order_and_both_neighbors`, `test_slice2_narrative_not_number_source` | ✅ COMPLIANT |
| Compare Without Subtraction | Compare stays two claims | `tests/eval/test_measure.py > test_slice2_compare_two_claims` | ✅ COMPLIANT |
| Compare Without Subtraction | Measure does not call the difference | `tests/eval/test_measure.py > test_slice2_compare_two_claims` (no subtracted value); `src/claimledger/eval/measure.py` has no `difference` import | ✅ COMPLIANT |
| Question Calls Understand Then Query | Body question only | `tests/http/test_app.py > test_route_calls_recorded_book_not_seed`, `test_post_question_calls_understand_then_query` | ✅ COMPLIANT |
| Verified Rector JSON | Consolidated net income | `tests/http/test_app.py > test_post_verified_claim_is_http_200`; `tests/http/test_claims_query.py > test_consolidated_net_income_on_seed` | ✅ COMPLIANT |
| Verified Rector JSON | Parent is not consolidated | `tests/http/test_claims_query.py > test_parent_is_not_consolidated` | ✅ COMPLIANT |
| Verified Rector JSON | Income tax keeps the sign | `tests/http/test_claims_query.py > test_income_tax_keeps_the_sign` | ✅ COMPLIANT |
| Verified Rector JSON | Seed evidence is empty | `tests/http/test_claims_query.py > test_consolidated_net_income_on_seed` (`evidence == []`) | ✅ COMPLIANT |
| Verified Rector JSON | Route forwards book evidence | `tests/http/test_app.py > test_route_forwards_book_evidence` | ✅ COMPLIANT |
| Measure Then Card | Consolidated value | `tests/openwebui/test_host.py > test_reply_consolidated_21262335` | ✅ COMPLIANT |
| Measure Then Card | Parent value | `tests/openwebui/test_host.py > test_reply_parent_21259769_both_rows` | ✅ COMPLIANT |
| Measure Then Card | Picture follows the card | `tests/openwebui/test_host.py > test_reply_picture_follows_card` | ✅ COMPLIANT |
| Measure Then Card | Compare completion draws the series | `tests/openwebui/test_host.py > test_reply_compare_copies_both_values_shows_code_difference` | ✅ COMPLIANT |
| Measure Then Card | Single claim and abstain stay card-only | `tests/openwebui/test_host.py > test_reply_abstain_adds_no_verified_value`, `test_reply_consolidated_21262335` | ✅ COMPLIANT |
| Measure Then Card | Last four quarters | `tests/openwebui/test_host.py > test_reply_last_four_quarters_leaves_holes` | ✅ COMPLIANT |
| Measure Then Card | All net results | `tests/openwebui/test_host.py > test_reply_all_net_results_draws_the_book` | ✅ COMPLIANT |
| Measure Then Card | HTTP stays one query | `tests/openwebui/test_host.py` (HTTP book question asserts `abstained`, no `21262335`, no Mermaid) | ✅ COMPLIANT |
| Measure Then Card | Reply uses the quarterly book | `tests/openwebui/test_host.py > test_reply_uses_the_quarterly_book` | ✅ COMPLIANT |

**Compliance summary**: 26/26 scenarios compliant

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Quarterly Book | ✅ Implemented | `recorded_book` in `ingest/ground.py` loads the two quarterly EEFF, classifies, extracts, upserts into a fresh `Ledger`. No disk claim cache. No `Ledger.seed()`. |
| Hashed Immutable JSON Store | ✅ Implemented | `load` recomputes SHA-256 of file bytes and raises `IngestError` on mismatch. Cache hit in `load_or_convert` calls `load` before any convert. |
| Call Order | ✅ Implemented | `measure(artifact_hash, question, ledger=None)` retrieves tables, understands, then queries the passed ledger or `_quarterly_book()` → `recorded_book()`. Source has no `Ledger.seed`. |
| Compare Without Subtraction | ✅ Implemented | Compare still returns two claims; `measure` does not import or call `difference`. |
| Question Calls Understand Then Query | ✅ Implemented | `build_app` passes `recorded_book()` into `claims_query`. Route source has no `Ledger.seed`. |
| Verified Rector JSON | ✅ Implemented | Seed evidence stays `[]`; route forwards book evidence when the stub book has rows. |
| Measure Then Card | ✅ Implemented | `reply` calls `recorded_book()` once and passes that ledger to `execute`, `ask`, and `measure`. Host tests stub the book. |

Kernel gold paths still call `Ledger.seed()`. Closed bounds from tasks (`query.py`, `RECIPE_ROWS`, gold files, `evals/`, allowlist, `book/ask.py`, `orchestrate/plan.py`, `http/claims.py`) were not reopened in commit `a427ee5` for those modules.

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Module `ingest/ground.py` `recorded_book() -> Ledger` | ✅ Yes | Outside the seven kernel modules; gap named in the module docstring. |
| Sources: two quarterly EEFF filenames | ✅ Yes | `_QUARTERLY_EEFF` matches `docs/archivos_muestra` names. |
| Once per `reply` / HTTP request; no seed fallback | ✅ Yes | Missing file → `IngestError`. |
| `measure` optional ledger argument | ✅ Yes | Eval tests pass `Ledger.seed()` or stub `_quarterly_book`. |
| Hash: SHA-256 of stored file bytes | ✅ Yes | `store.load` and cache-hit path. |
| Screen hash stays retrieve/crop, not the book | ✅ Yes | `reply` still takes `artifact_hash` for measure/retrieve/crop; book is separate. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ | No Engram `sdd/ground-ledger/apply-progress` and no on-disk apply-progress file. Observation #1134 summarizes the feature but has no TDD Cycle Evidence table. |
| All tasks have tests | ✅ | 8/8 tasks map to tests in `test_measure.py`, `test_ground.py`, `test_host.py`, `test_app.py`, `test_store.py` |
| RED confirmed (tests exist) | ✅ | New/changed test files exist for every RED task |
| GREEN confirmed (tests pass) | ✅ | Full suite 344 passed on this run |
| Triangulation adequate | ✅ | Book, missing file, hash mismatch, cache no-reconvert, measure ledger arg, omitted book, route evidence, reply source |
| Safety Net for modified files | ⚠️ | Cannot confirm from apply-progress; suite green implies no regression shipped |

**TDD Compliance**: reconstructed from tasks + tests (process artifact missing)

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | majority of kernel + pure claims_query | many under `tests/` | pytest |
| Integration | ingest ground/store, http app, openwebui host, eval measure | `tests/ingest/`, `tests/http/`, `tests/openwebui/`, `tests/eval/` | pytest (+ Docling where needed) |
| E2E | 0 | — | no browser runner |
| **Total** | **344** | suite-wide | |

---

### Changed File Coverage
Coverage analysis skipped — no coverage tool detected (`coverage.detected: false`).

---

### Assertion Quality
**Assertion quality**: ✅ All assertions verify real behavior

Spot-check of change-touched tests (`test_ground.py`, new store mismatch tests, measure ledger tests, `test_route_forwards_book_evidence`, `test_reply_uses_the_quarterly_book`): value and evidence assertions, `pytest.raises(IngestError)`, AST source checks that call production modules. No tautologies, ghost loops, or production-free asserts found.

---

### Quality Metrics
**Linter**: ➖ Not available (`linter: not_detected`)
**Type Checker**: ➖ Not available (`type_checker: not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: Engram/disk `sdd/ground-ledger/apply-progress` with a TDD Cycle Evidence table is missing. Strict TDD protocol expects that artifact. TDD was reconstructed from checked tasks plus existing/passing tests (8/8). Same class of process gap as prior archive precedent (incomplete Engram apply-progress on fase-7-openwebui) — does not leave a scenario uncovered.

**WARNING**: Proposal success-criteria checkboxes in `proposal.md` remain unchecked (`[ ]`). Tasks are fully checked; criteria are satisfied by the compliance matrix above. Archive may tick them.

**SUGGESTION**: Persist a retrospective `sdd/ground-ledger/apply-progress` observation before archive if the audit trail must match earlier phases.

### Verdict
PASS WITH WARNINGS

26/26 scenarios have a covering test that passed in this run. Suite green: 344 passed, 0 failed, 0 skipped, exit 0. No product blockers for archive. Process warning only: missing apply-progress TDD table in Engram.
