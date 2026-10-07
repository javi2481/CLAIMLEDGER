```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:056792f22f26f06e7f43e3bbe8099980a1979f72d587d7225df4583b8952ea1c
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 22/22
test_command: python -m pytest -q
test_exit_code: 0
test_output_hash: sha256:056792f22f26f06e7f43e3bbe8099980a1979f72d587d7225df4583b8952ea1c
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-9-pack
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the full `python -m pytest -q` stdout+stderr as written by PowerShell `Tee-Object` to `%TEMP%\fase9-pack-pytest.txt` (PowerShell 5 encoding). `build_command` in `openspec/config.yaml` is empty, so no build ran; `build_output_hash` is the SHA-256 of empty output. This report does not archive the change and no commit was made.

Counted from `specs/query/spec.md` (3 requirements, 9 scenarios), `specs/claim-card/spec.md` (2, 4), `specs/openwebui-host/spec.md` (3, 7), and `specs/verify-eval/spec.md` (1, 2): **9 requirements, 22 scenarios**.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 25 |
| Tasks complete | 25 |
| Tasks incomplete | 0 |

Every checkbox in `openspec/changes/fase-9-pack/tasks.md` is `[x]` (1.1–1.2, 2.1–2.7, 3.1–3.5, 4.1–4.4, 5.1–5.4, 6.1–6.5). Engram `sdd/fase-9-pack/apply-progress` (#1115) matches.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 317 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest -q
exit 0
317 passed, 73 warnings in 24.40s
```

The 73 warnings are Docling and docling-graph deprecations in `tests/graph/`. This change added none.

**Coverage** (extra run, not the hashed preimage): `python -m pytest tests/period/test_difference.py tests/card/test_render_card.py tests/openwebui/test_host.py --cov=claimledger.period --cov=claimledger.card.card --cov=claimledger.openwebui.text --cov=claimledger.openwebui.reply --cov-branch` exited 0, 36 passed.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Compare Returns Two Claims Without Delta | Net income both quarters | `tests/test_query.py > test_compare_returns_two_claims_without_delta` (values `21262335`, `81956525`; `60694190` and `-60694190` not in values; no `delta`/`difference` attr); `tests/period/test_difference.py > test_net_income_difference_is_later_minus_earlier` (query values lack `60694190`) | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | QueryResult keeps four fields | `tests/period/test_difference.py > test_rows_and_imports_stay_closed` (fields exactly `status`, `reason`, `claims`, `identity`); `tests/test_query.py > test_query_result_is_frozen_dataclass` | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | Compare identity keeps wildcard period | `tests/test_query.py > test_compare_identity_keeps_wildcard_period` | ✅ COMPLIANT |
| Compare Returns Two Claims Without Delta | One-sided compare abstains | `tests/test_query.py > test_one_sided_compare_abstains_incomplete` | ✅ COMPLIANT |
| Compare Difference Outside Query | Net income difference | `tests/period/test_difference.py > test_net_income_difference_is_later_minus_earlier` (`query(understand(...), Ledger.seed())` → `difference` = `"60694190"`, `str`, not `FinancialClaim`, no `identity_key`) | ✅ COMPLIANT |
| Compare Difference Outside Query | Negative side keeps its sign | `tests/period/test_difference.py > test_signed_pair_keeps_minus` (seed `-14950948` / `-32731536` → `"-17780588"`; positive has no `+`; equal → `"0"`); `test_order_follows_period_not_tuple_order` | ✅ COMPLIANT |
| Compare Difference Outside Query | Mismatched pair yields no number | `tests/period/test_difference.py > test_mismatch_returns_none` (issuer, statement, scope, metric, unit) | ✅ COMPLIANT (currency: see note) |
| Compare Difference Outside Query | Same period, abstain, or one claim yields no number | `tests/period/test_difference.py > test_non_pair_returns_none` (same period, abstained, one, three, zero, `conflicted`) | ✅ COMPLIANT |
| Query and Pack Stay Separate | No second merger and fourteen rows | `tests/period/test_difference.py > test_rows_and_imports_stay_closed` (`len(RECIPE_ROWS) == 14`; `query.py` and `measure.py` do not import `claimledger.period`; `period/` holds only `__init__.py` and `difference.py`; `difference.py` imports only `QueryResult`) | ✅ COMPLIANT (merger: static evidence) |
| Compare Card | Two values and the passed difference | `tests/card/test_render_card.py > test_compare_shows_both_values_and_difference` (exact line `Diferencia entre las dos cifras verificadas: 60694190`; no `segundo trimestre`, `trimestre aislado`, `claims`; no `delta` field; `_METRIC_CHIP` net_income only) | ✅ COMPLIANT |
| Compare Card | No string, no line | `tests/card/test_render_card.py > test_compare_without_string_has_no_line` (default and `None`; empty-string path goes through the same falsy guard) | ✅ COMPLIANT |
| Compare Card | Abstain and single cards unchanged | `tests/card/test_render_card.py > test_abstain_and_single_ignore_passed_string` | ✅ COMPLIANT |
| Pure Display | No kernel calls | `tests/card/test_render_card.py > test_render_card_does_not_call_kernel` (spy; AST: `difference` not called, `claimledger.period` not imported) | ✅ COMPLIANT |
| Measure Then Card | Consolidated value | `tests/openwebui/test_host.py > test_reply_consolidated_21262335` | ✅ COMPLIANT |
| Measure Then Card | Parent value | `tests/openwebui/test_host.py > test_reply_parent_21259769_both_rows` | ✅ COMPLIANT |
| Measure Then Card | Picture follows the card | `tests/openwebui/test_host.py > test_reply_picture_follows_card` | ✅ COMPLIANT |
| Always That Card | Abstain is the reply | `tests/openwebui/test_host.py > test_reply_picture_follows_card` (abstain == card, no `data:image`, no difference line), `test_reply_abstain_adds_no_verified_value` | ✅ COMPLIANT |
| Always That Card | Compare shows the code difference | `tests/openwebui/test_host.py > test_reply_compare_copies_both_values_shows_code_difference` (exact `_compare_card()` text, `60694190` present, no `+60694190`, no `delta`), `test_reply_picture_follows_card` (card first, then two pictures in claim order) | ✅ COMPLIANT |
| Closed Bounds | Allowlist and kernel bans | `tests/openwebui/test_host.py > test_query_and_card_stay_picture_free` (allowlist 13, excludes `crop` and `period`; `dependencies == []`; gold `21262335`/`21259769`; `60694190` absent from gold v1, v2, `test_gold_compare.py`), `test_host_stays_off_claims_route_and_allowlist`; `tests/test_identity.py > test_kernel_modules_importable`, `test_pins_declared_but_unused` | ✅ COMPLIANT |
| Closed Bounds | Later phases wait | `tests/openwebui/test_host.py > test_wave_c_still_waits` (`period` and `crop` present; no `chart`/`charts`/`orchestrator`; no active `fase-10`..`fase-13`); `tests/http/test_claims_query.py > test_compare_returns_two_claims_without_delta`; `tests/openwebui/test_host.py > test_query_and_card_stay_picture_free` (`60694190` absent from `claims_query` compare body) | ✅ COMPLIANT |
| Compare Without Subtraction | Compare stays two claims | `tests/eval/test_measure.py > test_slice2_compare_two_claims` (values `21262335`, `81956525`; `60694190` not in values) | ✅ COMPLIANT |
| Compare Without Subtraction | Measure does not call the difference | `tests/period/test_difference.py > test_rows_and_imports_stay_closed` (AST: `measure.py` does not import `claimledger.period`); `measure.py` contains no `period`, `delta`, or `difference` token | ✅ COMPLIANT |

**Compliance summary**: 22/22 scenarios compliant.

Currency note: a currency mismatch cannot be built. `dataclasses.replace(claim, currency="USD")` raises `ClaimError: currency must be ARS` from `validate_claim` (probe run during this verify). The guard stays in `_GATE_FIELDS`, and `difference.py` has 100% line and branch coverage.

Merger note: `src/` has one merger, the native `GraphMerger` in `graph/build.py`. `graph/` has no diff. The new package is pinned to two files by test. No test scans the whole `src/` tree for a second merger.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Compare Returns Two Claims Without Delta | ✅ Implemented | `query.py` has no diff. `QueryResult` is `status`, `reason`, `claims`, `identity`. No subtraction. No `period` import. |
| Compare Difference Outside Query | ✅ Implemented | `period/difference.py`: `verified`, exactly two claims, equal `issuer`, `statement`, `scope`, `metric`, `currency`, `unit`, different `period`, both `recorded`; else `None`. Sort by ISO period; `str(int(later.value) - int(earlier.value))`. Returns a plain `str`. No upsert. Imports only `QueryResult`. `digits.py` unchanged. |
| Query and Pack Stay Separate | ✅ Implemented | No pack reimplementation. `RECIPE_ROWS` 14. `ledger.py`, `graph/`, `ingest/` unchanged. |
| Compare Card | ✅ Implemented | `_DIFFERENCE_LABEL = "Diferencia entre las dos cifras verificadas"`. Line set only when verified, `len(claims) == 2`, and the string is truthy (so `None` and `""` give no line). The card does not parse digits or import `claimledger.period`. `_METRIC_CHIP` unchanged. |
| Pure Display | ✅ Implemented | `render_card(candidates, result, difference=None)`. The argument shadows the function name, but `card.py` never imports the function. |
| Measure Then Card | ✅ Implemented | `reply`: `measure` → `difference(result)` → `render_card` → `card_text` → `attach`. One string; card text first, crops after. No LLM in the path. |
| Always That Card | ✅ Implemented | `card_text` order: seal, chips, rows, values, difference, sentence, reason. |
| Closed Bounds | ✅ Implemented | `pyproject.toml` `dependencies = []`, `starlette==1.0.0`. `tests/test_identity.py` unchanged (13 paths). `http/` and `openwebui/app.py` unchanged. `evals/` unchanged; `cp-*` expected values are still the pairs (`cp-01` = `["21262335", "81956525"]`). `60694190` appears nowhere under `src/` or `evals/`. |
| Compare Without Subtraction | ✅ Implemented | `eval/measure.py` has no diff and does not subtract. |

`git diff --quiet` on `query.py`, `eval/`, `ledger.py`, `digits.py`, `http/`, `openwebui/app.py`, `pyproject.toml`, `evals/`, `tests/test_identity.py`, `tests/test_query.py`, `tests/eval/`, and both gold files exited 0.

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| `period/difference.py`; `difference(result) -> str \| None` | ✅ Yes | |
| Gate on six fields, period differs, both `recorded` | ✅ Yes | |
| `sorted(claims, key=period)`; later minus earlier | ✅ Yes | Reverse tuple order tested. |
| `str(int) - int`; no `Decimal`, no datetime, no parse helper | ✅ Yes | |
| Plain `str`; no `identity_key`; never upserted; not read by gold | ✅ Yes | |
| `ClaimCard.difference: str = ""` last field; card owns the label | ✅ Yes | `text.py` has no label text. |
| Text order seal → chips → rows → values → difference → sentence → reason | ✅ Yes | |
| Caller is `reply` only; not `measure`, `render_card`, `app.py`, `POST /claims/query` | ✅ Yes | |
| Pack satisfied by native stack; no second merger; 14 rows | ✅ Yes | |
| `query` purpose sentence "until Fase 9" left for archive | ✅ Yes | Still present at `openspec/specs/query/spec.md` line 5. |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram `sdd/fase-9-pack/apply-progress` (#1115) has a TDD Cycle Evidence table for 1.1–6.5. |
| All tasks have tests | ✅ | Tests in `tests/period/test_difference.py`, `tests/card/test_render_card.py`, `tests/openwebui/test_host.py` exist. |
| RED confirmed (tests exist) | ✅ | Recorded reds: `ModuleNotFoundError: claimledger.period` (2.x), `AssertionError` on `"period" in packages` (1.2), `TypeError` third positional argument (4.4), `AssertionError` missing line/field (5.4). These are the reasons the tasks require. |
| GREEN confirmed (tests pass) | ✅ | 36 focused, 317 full, exit 0 in this run. |
| Triangulation adequate | ✅ | Positive, negative, zero, reversed order, five mismatches, six non-pair cases; card with string, without, `None`, abstain, single. |
| Safety Net for modified files | ✅ | Apply recorded 9 card tests and 15 host tests passing before edits. `test_difference.py` is new. |

**TDD Compliance**: 6/6 checks passed

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 10 | 2 | pytest |
| Integration (in-process host) | 4 | 1 | pytest |
| E2E | 0 | 0 | not installed |
| **Total** | **14** | **3** | |

Unit: six in `tests/period/test_difference.py` and four new or changed in `tests/card/test_render_card.py`. Integration: the four changed host tests (`test_reply_compare_copies_both_values_shows_code_difference`, `test_reply_picture_follows_card`, `test_wave_c_still_waits`, `test_query_and_card_stay_picture_free`). They call `reply` or `claims_query` in-process. No bound port, Docker, network, or PDF.

---

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/period/__init__.py` | 100% | — | — | ✅ Excellent |
| `src/claimledger/period/difference.py` | 100% | 8/8 | — | ✅ Excellent |
| `src/claimledger/card/card.py` | 100% | 6/6 | — | ✅ Excellent |
| `src/claimledger/openwebui/text.py` | 100% | 9/10 | branch 19→21 (empty seal; pre-existing) | ✅ Excellent |
| `src/claimledger/openwebui/reply.py` | 100% | — | — | ✅ Excellent |

**Average changed file coverage**: 99% (91 statements, 0 missed; 24 branches, 1 partial).

---

### Assertion Quality
| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/period/test_difference.py` | 78 | `assert not hasattr(outcome, "identity_key")` | Always true on a `str`. It sits beside the value assertion `outcome == "60694190"`, so it is redundant, not empty. | SUGGESTION |

**Assertion quality**: 0 CRITICAL, 0 WARNING. Loops over mismatches and period sources are guarded by length or exact-list asserts. No tautology. No ghost loop.

---

### Quality Metrics
**Linter**: ➖ Not available
**Type Checker**: ➖ Not available

### Issues Found
**CRITICAL**: None

**WARNING** (archive): `openspec/specs/query/spec.md` purpose sentence still says compare "MUST NOT subtract until Fase 9". The delta names where subtraction lives (outside `query`, in the sibling difference function). Archive must rewrite that sentence when it merges the delta. This is not an apply failure.

**WARNING**: `AGENTS.md` has an uncommitted status-line edit ("Active change: `openspec/changes/fase-9-pack/` (apply done; verify next)"). `tasks.md` lists `AGENTS.md` in the apply closed bounds. The edit is bookkeeping, not code. The orchestrator should confirm it owns that line before the archive commit.

**WARNING**: Currency mismatch has no runtime test. It cannot be constructed, because `validate_claim` pins `ARS`. The guard is in code. Design accepted this.

**WARNING**: "No second merger" rests on static evidence (one `GraphMerger` in unchanged `graph/build.py`, `period/` pinned to two files). No test scans all of `src/`.

**SUGGESTION**: The host path is tested only with the positive `60694190`. A negative difference through `reply` is covered by the unit test, not the host test.

### Verdict
PASS WITH WARNINGS

22/22 scenarios have a covering test that passed in this run. Full suite 317 passed, 0 failed, exit 0. No blocker for archive. Archive must rewrite the `query` purpose sentence ("until Fase 9") and should confirm the `AGENTS.md` status edit.
