```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:4d8f5038d1a7c0b8f1e42a39401086a672d44ad7c907feef183e2824aef0226b
verdict: pass
blockers: 0
critical_findings: 0
requirements: 25/25
scenarios: 63/63
test_command: pytest tests/
test_exit_code: 0
test_output_hash: sha256:3c2cf9733f46538cbae28f5e3016fb88a07a3586664b07db3b93d628da14dbb2
build_command: python -m compileall -q src tests
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-0-kernel
**Version**: Fase 0 kernel (identity, ledger, lookup, query, gold-regression)
**Mode**: Strict TDD
**Persistence**: hybrid
**Branch**: fase-0-kernel

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 16 |
| Tasks complete | 16 |
| Tasks incomplete | 0 |

All tasks `[x]` in `openspec/changes/fase-0-kernel/tasks.md` and Engram `sdd/fase-0-kernel/tasks` (#1004). Apply-progress (#1009) reports work units 1–8 complete.

### Build & Tests Execution
**Build**: ✅ Passed
```text
python -m compileall -q src tests
exit 0
(empty stdout/stderr)
```

**Tests**: ✅ 128 passed / ❌ 0 failed / ⚠️ 0 skipped
```text
pytest tests/
........................................................................ [ 56%]
........................................................                 [100%]
128 passed in 0.44s
```

**Coverage**: ➖ Not available — `openspec/config.yaml` `testing.coverage.detected: false`

Canonical verification-evidence bytes (preimage of `evidence_revision`):

```text
test_command: pytest tests/
........................................................................ [ 56%]
........................................................                 [100%]
128 passed in 0.44s
build_command: python -m compileall -q src tests
```

### Spec Compliance Matrix

#### identity (5 requirements / 14 scenarios)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Five-Field Identity Key | Consistent key constructs | `tests/test_identity.py > test_claim_consistent_key_constructs` | ✅ COMPLIANT |
| Five-Field Identity Key | Inconsistent key is rejected | `tests/test_identity.py > test_claim_inconsistent_key_is_rejected` | ✅ COMPLIANT |
| Five-Field Identity Key | Neighbor values are distinct identities | `tests/test_identity.py > test_identity_key_neighbor_parent_is_distinct` | ✅ COMPLIANT |
| Claimprint Alias Mapping | Canonical neighbor alias | `tests/test_identity.py > test_apply_alias_consolidado_neto_is_canonical_neighbor` | ✅ COMPLIANT |
| Claimprint Alias Mapping | Alias table is one-to-one | `tests/test_identity.py > test_aliases_table_is_one_to_one` | ✅ COMPLIANT |
| Claimprint Alias Mapping | Wildcard and null identities port | `tests/test_gold_v1.py > test_cp_01_wildcard_identity_and_two_values`; `test_null_identity_ports_as_null` | ✅ COMPLIANT |
| Canonical Period Before Identity | First quarter tokens | `tests/test_identity.py > test_normalize_period_1t26_tokens` | ✅ COMPLIANT |
| Canonical Period Before Identity | Second quarter tokens | `tests/test_identity.py > test_normalize_period_2t26_tokens` | ✅ COMPLIANT |
| Digit and Signed Money | Thousand dots collapse | `tests/test_identity.py > test_digits_ars_collapses_thousand_dots` | ✅ COMPLIANT |
| Digit and Signed Money | Parentheses are negative | `tests/test_identity.py > test_signed_ars_parentheses_are_negative` | ✅ COMPLIANT |
| Digit and Signed Money | Empty money is null | `tests/test_identity.py > test_digits_ars_empty_or_none_is_none` | ✅ COMPLIANT |
| Digit and Signed Money | Compact millions are forbidden | `tests/test_identity.py > test_claim_rejects_compact_millions_value` | ✅ COMPLIANT |
| Frozen Evidence and Claim Shape | Recorded claim without verification field | `tests/test_identity.py > test_claim_has_no_verification_status` | ✅ COMPLIANT |
| Frozen Evidence and Claim Shape | Invalid bbox is rejected | `tests/test_identity.py > test_evidence_invalid_bbox_is_rejected` | ✅ COMPLIANT |

#### ledger (5 requirements / 10 scenarios)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| In-Memory Upsert Book | First upsert is recorded | `tests/test_ledger.py > test_first_upsert_is_recorded` | ✅ COMPLIANT |
| In-Memory Upsert Book | Same identity and value appends evidence | `tests/test_ledger.py > test_same_identity_and_value_appends_evidence` | ✅ COMPLIANT |
| Conflict Preserves Both Evidences | Other value marks conflict | `tests/test_ledger.py > test_other_value_marks_conflicted_and_keeps_both_evidences` | ✅ COMPLIANT |
| Conflict Preserves Both Evidences | Conflict keeps both evidences | `tests/test_ledger.py > test_other_value_marks_conflicted_and_keeps_both_evidences` | ✅ COMPLIANT |
| Query Does Not Mutate the Book | Verified answer leaves recorded intact | `tests/test_query.py > test_verified_answer_leaves_recorded_intact` | ✅ COMPLIANT |
| Query Does Not Mutate the Book | Abstention leaves the book unchanged | `tests/test_query.py > test_abstention_leaves_the_book_unchanged` | ✅ COMPLIANT |
| Recipe Seed Without Prior as Current | Fourteen recipe rows are present | `tests/test_ledger.py > test_seeded_ledger_has_fourteen_recipe_rows` | ✅ COMPLIANT |
| Recipe Seed Without Prior as Current | Prior figure is not current net income | `tests/test_ledger.py > test_prior_figure_is_not_current_net_income` | ✅ COMPLIANT |
| Recorded Is Not Verified | Ingest never stamps verified | `tests/test_ledger.py > test_ingest_never_stamps_verified` | ✅ COMPLIANT |
| Recorded Is Not Verified | Conflicted is not a verified answer | `tests/test_query.py > test_conflicted_claim_is_not_verified_from_ingest_status` | ✅ COMPLIANT |

#### lookup (5 requirements / 14 scenarios)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Fold Then Closed Phrase Order | Accents fold before matching | `tests/test_lookup.py > test_accents_fold_before_matching` | ✅ COMPLIANT |
| Fold Then Closed Phrase Order | YPF rule wins over default neto | `tests/test_lookup.py > test_ypf_rule_wins_over_default_neto` | ✅ COMPLIANT |
| Issuer Is Always BYMA | YPF close is off corpus | `tests/test_lookup.py > test_ypf_close_is_off_corpus_even_when_text_mentions_byma` | ✅ COMPLIANT |
| Issuer Is Always BYMA | Ordinary EEFF question stays BYMA | `tests/test_lookup.py > test_ordinary_eeff_question_stays_byma` | ✅ COMPLIANT |
| Non-EEFF Sources Refuse to Invent | Comunicado plus neto abstains | `tests/test_lookup.py > test_comunicado_plus_neto_abstains` | ✅ COMPLIANT |
| Non-EEFF Sources Refuse to Invent | Deck plus P&L abstains | `tests/test_lookup.py > test_deck_plus_pnl_abstains` | ✅ COMPLIANT |
| Non-EEFF Sources Refuse to Invent | Memoria and contract abstain | `tests/test_lookup.py > test_memoria_and_contract_abstain` | ✅ COMPLIANT |
| Narrative Route Invents No Number | Growth narrative is narrative | `tests/test_lookup.py > test_growth_narrative_is_narrative` | ✅ COMPLIANT |
| Narrative Route Invents No Number | Neto ask is not narrative | `tests/test_lookup.py > test_neto_ask_is_not_narrative` | ✅ COMPLIANT |
| Compare, Period, and Metric Resolution | Versus marks compare | `tests/test_lookup.py > test_versus_marks_compare` | ✅ COMPLIANT |
| Compare, Period, and Metric Resolution | Single quarter binds period | `tests/test_lookup.py > test_single_quarter_binds_period` | ✅ COMPLIANT |
| Compare, Period, and Metric Resolution | Default metric is consolidated net income | `tests/test_lookup.py > test_default_metric_is_consolidated_net_income` | ✅ COMPLIANT |
| Compare, Period, and Metric Resolution | Parenthetical controlante wins unless excluded | `tests/test_lookup.py > test_parenthetical_controlante_wins`; `test_no_el_atribuible_keeps_consolidated_net_income` | ✅ COMPLIANT |
| Compare, Period, and Metric Resolution | Rejected is not a lookup return | `tests/test_lookup.py > test_rejected_is_not_a_lookup_return` | ✅ COMPLIANT |

#### query (5 requirements / 12 scenarios)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Verified Single Claim or No Answer | Canonical consolidated net income | `tests/test_query.py > test_canonical_consolidated_net_income_is_verified` | ✅ COMPLIANT |
| Verified Single Claim or No Answer | Missing claim abstains | `tests/test_query.py > test_missing_claim_abstains` | ✅ COMPLIANT |
| Neighbor Is Not Chosen | Consolidated neighbor trap | `tests/test_query.py > test_consolidated_neighbor_trap_does_not_choose_parent` | ✅ COMPLIANT |
| Neighbor Is Not Chosen | Parent question chooses the neighbor | `tests/test_query.py > test_parent_question_chooses_the_neighbor` | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | Net income both quarters | `tests/test_query.py > test_compare_returns_two_claims_without_delta` | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | Compare identity keeps wildcard period | `tests/test_query.py > test_compare_identity_keeps_wildcard_period` | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | One-sided compare abstains | `tests/test_query.py > test_one_sided_compare_abstains_incomplete` | ✅ COMPLIANT |
| Closed Abstention | YPF price abstains off corpus | `tests/test_query.py > test_ypf_price_abstains_off_corpus` | ✅ COMPLIANT |
| Closed Abstention | Comunicado P&L abstains as recipe no extract | `tests/test_query.py > test_comunicado_pnl_abstains_recipe_no_extract` | ✅ COMPLIANT |
| Closed Abstention | Ambiguous period abstains | `tests/test_query.py > test_ambiguous_period_abstains` | ✅ COMPLIANT |
| Query Return Shape and Demo Surface | No rejected query status | `tests/test_query.py > test_query_never_returns_rejected` | ✅ COMPLIANT |
| Query Return Shape and Demo Surface | Pytest is the demo | runtime `pytest tests/` 128 passed; no HTTP/REPL in kernel | ✅ COMPLIANT |

#### gold-regression (5 requirements / 13 scenarios)
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Frozen Numeric Contracts | v1 identity case keeps the neighbor number | `tests/test_gold_v1.py > test_id_01_keeps_neighbor_number_and_aliased_identity` | ✅ COMPLIANT |
| Frozen Numeric Contracts | v2 tax keeps the minus sign | `tests/test_gold_v2.py > test_v2_id_04_keeps_minus_sign_and_aliased_identity` | ✅ COMPLIANT |
| Frozen Numeric Contracts | Relaxing a gold number is forbidden | `tests/test_gold_v1.py > test_harness_runs_non_skip_cases_and_skips_narrative`; `tests/test_gold_v2.py > test_frozen_numbers_are_intact` | ✅ COMPLIANT |
| Alias-Only Identity Rewrite | Alias file is the rewrite table | `tests/test_identity.py > test_aliases_table_is_one_to_one` | ✅ COMPLIANT |
| Alias-Only Identity Rewrite | Comparison wildcard identity | `tests/test_gold_v1.py > test_cp_01_wildcard_identity_and_two_values` | ✅ COMPLIANT |
| Alias-Only Identity Rewrite | Null identity ports as null | `tests/test_gold_v1.py > test_null_identity_ports_as_null`; `tests/test_gold_v2.py > test_null_identity_ports_as_null` | ✅ COMPLIANT |
| Partition Contracts | Neighbor rejects prior and parent | `tests/test_gold_v1.py > test_nb_01_rejects_parent_and_prior` | ✅ COMPLIANT |
| Partition Contracts | Comparison does not invent a delta | `tests/test_gold_v1.py > test_cp_01_wildcard_identity_and_two_values`; `tests/test_gold_v2.py > test_v2_compare_cases_return_two_claims_without_delta` | ✅ COMPLIANT |
| Partition Contracts | Narrative stays skipped | `tests/test_gold_v1.py > test_narrative_cases_are_skipped` | ✅ COMPLIANT |
| Prior Figure Stays Non-Current | Prior appears only as reject | `tests/test_gold_v1.py > test_prior_figure_is_never_current_net_income_expected_value` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Import scan stays clean | `tests/test_gold_v1.py > test_import_scan_stays_clean`; `tests/test_gold_v2.py > test_import_scan_stays_clean`; `tests/test_identity.py > test_pins_declared_but_unused` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Pins are declared metadata | `tests/test_identity.py > test_pins_declared_but_unused` | ✅ COMPLIANT |
| Docling-Free Pytest Demo | Press and deck gold stay out | `tests/test_gold_v1.py > test_press_and_deck_gold_stay_out`; `tests/test_gold_v2.py > test_press_and_deck_gold_stay_out` | ✅ COMPLIANT |

**Compliance summary**: 63/63 scenarios compliant

### Gate checks (requested)
| Check | Result | Evidence |
|-------|--------|----------|
| `id-01` = `21262335` | ✅ | `evals/identity_v1.json` + `test_id_01_keeps_neighbor_number_and_aliased_identity` |
| `v2-id-04` = `-14950948` | ✅ | `evals/identity_v2.json` + `test_v2_id_04_keeps_minus_sign_and_aliased_identity` |
| Kernel tests do not import docling | ✅ | AST scan in identity/gold tests; `docling`/`docling_graph` absent from `sys.modules` after kernel import |
| No `press_v1` / `presentation_v1` | ✅ | `evals/` contains only `aliases.json`, `identity_v1.json`, `identity_v2.json` |
| `recorded` ≠ `verified` | ✅ | `FinancialClaim.ledger_status ∈ {recorded, conflicted}`; ingest rejects `verified`; query writes no status onto claims |
| Compare has no subtraction | ✅ | `query.py` has no `delta`/`difference`/`subtract`; compare returns two claims; gold harness forbids subtracted amount |

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Five-field `identity_key` | ✅ Implemented | `identity.py` `issuer\|period\|statement\|scope\|metric`; value excluded |
| Alias table 1:1 | ✅ Implemented | `evals/aliases.json` 7 rows; `apply_alias` |
| Period + money normals | ✅ Implemented | `normalize_period`; `digits_ars` / `signed_ars` |
| Frozen claim/evidence | ✅ Implemented | dataclasses + `validate_*`; no `verification_status` |
| Thin in-memory Ledger | ✅ Implemented | `Ledger._book: dict[str, FinancialClaim]`; no `store.py`; no disk write |
| Recipe seed 14 rows | ✅ Implemented | Prior `22362983` not current `net_income` |
| Lookup 9-step order | ✅ Implemented | `understand()`; issuer always `BYMA`; press/deck → `recipe_no_extract` |
| Query verified/abstained | ✅ Implemented | Read-only `Ledger.get`; compare two claims; closed reasons |
| Gold v1 45 / v2 26 | ✅ Implemented | Alias-only identity rewrite; numbers frozen; `na-*` skip |
| Docling-free kernel | ✅ Implemented | Pins only in `pyproject.toml` optional-deps; not imported |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Thin `Ledger` over `dict[str, FinancialClaim]` | ✅ Yes | Isolated instances; no module-level book |
| Exact 7 modules + empty `__init__.py` | ✅ Yes | No `intent.py`, `seed.py`, `models.py`, `store.py`, `conftest.py` |
| Frozen dataclasses + `validate_*` | ✅ Yes | No Pydantic |
| `ledger_status` only (not rector §7 `verification_status`) | ✅ Yes | |
| Press/deck identity rejected | ✅ Yes | `recipe_no_extract`; no press/deck gold |
| Compare two claims, no delta | ✅ Yes | Fase 9 subtraction not present |
| Intent in `lookup.py`; QueryResult in `query.py` | ✅ Yes | |
| No Docling / network / PDF / HTTP | ✅ Yes | |
| 8-step TDD order | ✅ Yes | Apply-progress work units 1–8 |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Found in Engram `sdd/fase-0-kernel/apply-progress` (#1009) |
| All tasks have tests | ✅ | 16/16 tasks have test files |
| RED confirmed (tests exist) | ✅ | `test_identity.py`, `test_ledger.py`, `test_lookup.py`, `test_query.py`, `test_gold_v1.py`, `test_gold_v2.py` exist |
| GREEN confirmed (tests pass) | ✅ | 128/128 pass on this execution |
| Triangulation adequate | ✅ | Multi-case identity/lookup/gold; single-scenario tasks have matching spec width |
| Safety Net for modified files | ✅ | Later slices report N/N prior green; new files `N/A (new)` |

**TDD Compliance**: 7/7 checks passed (16/16 tasks have complete TDD evidence)

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 106 | 4 (`test_identity.py` 40, `test_ledger.py` 8, `test_lookup.py` 42, `test_query.py` 16) | pytest |
| Integration | 22 | 2 (`test_gold_v1.py` 11, `test_gold_v2.py` 11) | pytest in-memory seed |
| E2E | 0 | 0 | not installed (Fase 0 demo is green pytest) |
| **Total** | **128** | **6** | |

---

### Changed File Coverage
Coverage analysis skipped — no coverage tool detected (`openspec/config.yaml` coverage.detected: false)

---

### Assertion Quality
**Assertion quality**: ✅ All assertions verify real behavior

No tautologies, ghost loops, or production-free tests. Empty-collection asserts (`forbidden == {}`, abstention `claims == ()`) have companion non-empty / status / identity value checks. Compact-millions `!=` on `digits_ars` is paired with claim-level rejection.

---

### Quality Metrics
**Linter**: ➖ Not available
**Type Checker**: ➖ Not available (`python -m compileall -q src tests` used as syntax/build stand-in; exit 0)

### Issues Found
**CRITICAL**: None
**WARNING**: None
**SUGGESTION**:
- `openspec/config.yaml` context still says the repo is docs-only / pytest planned-not-detected; stale relative to this implemented kernel.
- On-disk `tasks.md` forecast header still shows `ask-on-risk` / `Chain strategy: pending`; Engram tasks artifact records the resolved `auto-chain` / `feature-branch-chain`. Does not affect task completeness.

### Verdict
PASS
16/16 tasks complete, 25/25 requirements and 63/63 scenarios compliant, `pytest tests/` 128 passed, compileall green, gold numbers intact, docling-free, no press/deck gold, recorded ≠ verified, compare has no subtraction.
