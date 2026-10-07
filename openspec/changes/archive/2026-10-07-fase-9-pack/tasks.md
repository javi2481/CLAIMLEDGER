# Tasks: Phase 9 Period Pack and Compare Subtraction

## Review Workload Forecast

Estimated changed lines for apply: ~255 (code ~55, tests ~200). SDD artifacts add ~500 on the branch. Risk against the 400-line review budget: Medium. Two slices: A (~140: `period/` + `tests/period/` + host guard) and B (~115: card, text, reply, their tests). Each slice fits one session.

Delivery strategy: sequential slices on the current branch. Slice B starts only after slice A is green. Chained PRs not needed.

Decision needed before apply: No
Chained PRs recommended: No
**Apply MUST NOT commit and MUST NOT open a PR unless the user asks.** Phases 10–13 stay unopened. Charts and the orchestrator wait.

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| A | Host guard + guarded subtraction | `pytest tests/period/test_difference.py tests/openwebui/test_host.py -k "wave_c or difference"` | N/A in-memory `Ledger.seed()` | Delete `period/` and `tests/period/`; revert `test_wave_c_still_waits` |
| B | Card line, text order, reply wiring | `pytest tests/card/test_render_card.py tests/openwebui/test_host.py -k "compare or difference or picture or picture_free"` | N/A in-process reply on stub sidecars | Revert `card.py`, `text.py`, `reply.py` and the edited tests |

### Closed bounds (apply MUST NOT touch)

`query.py`, `eval/measure.py`, `digits.py`, `ledger.py` (no 15th `RECIPE_ROWS` row), `http/`, `graph/`, `ingest/`, `crop/`, `openwebui/app.py`, `pyproject.toml` (`dependencies` stays `[]`), `tests/test_identity.py` (13-path allowlist stays 13, excludes `period`), gold and `cp-*` expected values, `evals/`, `_METRIC_CHIP` (`net_income` only), `AGENTS.md`. No `delta`/`difference` field on `QueryResult` or `POST /claims/query`. No second module. The `query` spec purpose sentence "until Fase 9" is NOT a task; archive handles it.

## Slice A: Kernel-free subtraction (green alone)

### Phase 1: Host guard (already red)

- [x] 1.1 Baseline: run `pytest tests/openwebui/test_host.py::test_wave_c_still_waits`. Record that it fails today because `fase-9-pack` is an active change name starting with `fase-9`.
- [x] 1.2 RED: edit `tests/openwebui/test_host.py::test_wave_c_still_waits`. Assert `"period"` in `src/claimledger` package names (keep `"crop"`). Keep `packages.isdisjoint({"chart", "charts", "orchestrator"})`. Keep the `*-fase-8-crop` archive assertion. Change the active-name guard to `range(10, 14)` so `fase-9-pack` is allowed and `fase-10` through `fase-13` stay forbidden. Run pytest. It MUST fail with `AssertionError` on `"period" in packages` (the fase-9 failure is gone). Any other failure reason is wrong.

### Phase 2: difference (RED first)

Create `tests/period/test_difference.py`. No `tests/**/__init__.py` exists; do not add one. In-memory only. No `docling`, network, PDF, Docker.

- [x] 2.1 RED: `test_net_income_difference_is_later_minus_earlier`. `difference(query(understand("Comparar resultado neto consolidado 1T26 vs 2T26"), Ledger.seed()))` returns `"60694190"` (`81956525` minus `21262335`). Result is `str`, not `FinancialClaim`, no `identity_key`. Assert the `query` result itself has no `60694190` in claim values. Run pytest. It MUST fail with `ModuleNotFoundError: claimledger.period` (import of `difference`). Not a collection typo.
- [x] 2.2 RED: `test_signed_pair_keeps_minus`. Build a verified `QueryResult` from the seed `income_tax` claims (`Ledger.seed().get(identity_key("BYMA", period, "income_statement", "consolidated", "income_tax"))`, `-14950948` for 2026-03-31, `-32731536` for 2026-06-30). Expect `"-17780588"`. No leading `+` on a positive result. Equal values yield `"0"`. Do not relax `-14950948`. Same `ModuleNotFoundError` is the right failure until 3.2.
- [x] 2.3 RED: `test_order_follows_period_not_tuple_order`. Pass claims in reverse tuple order. Same `"60694190"`.
- [x] 2.4 RED: `test_mismatch_returns_none`. Using `dataclasses.replace` on the seed claims, change one of `scope`, `metric`, `unit` (use `unit="thousands"` or another non-`None` value) and expect `None` for each. Also `issuer` and `statement`. `currency` mismatch is unreachable through `validate_claim` (ARS only): do NOT write a currency test; the guard stays in code and is covered by the unit test.
- [x] 2.5 RED: `test_non_pair_returns_none`. Same period on both claims, `status="abstained"` (with `reason="incomplete_comparison"`), one claim, three claims, zero claims, and a claim with `ledger_status="conflicted"` each return `None`.
- [x] 2.6 RED: `test_rows_and_imports_stay_closed`. `len(RECIPE_ROWS) == 14`. AST: `src/claimledger/query.py` and `src/claimledger/eval/measure.py` do not import `claimledger.period`. AST: every `.py` file under `src/claimledger/period/` imports no `docling`, and `difference.py` imports only `QueryResult` from `claimledger.query` (plus `__future__`). `QueryResult` still has exactly `status`, `reason`, `claims`, `identity`.
- [x] 2.7 Run `pytest tests/period/test_difference.py`. Every test above MUST fail for a right reason (`ModuleNotFoundError` for behavior tests). 2.6 may pass in part where the files already satisfy it; the `period/` assertions MUST fail on missing files. Do not write production code before this run.

### Phase 3: difference (GREEN)

- [x] 3.1 GREEN: create empty `src/claimledger/period/__init__.py`.
- [x] 3.2 GREEN: create `src/claimledger/period/difference.py` with `difference(result: QueryResult) -> str | None` (≈25 lines). Gate: `status == "verified"`; exactly two claims; equal `issuer`, `statement`, `scope`, `metric`, `currency`, `unit`; `period` differs; both `ledger_status == "recorded"`; else `None`. `earlier, later = sorted(claims, key=lambda c: c.period)`. Return `str(int(later.value) - int(earlier.value))`. Imports only `QueryResult`. No `Decimal`, no datetime, no parsing helper, no `FinancialClaim` construction. Do not edit `digits.py`.
- [x] 3.3 Run `pytest tests/period/test_difference.py`. MUST be green.
- [x] 3.4 Run `pytest tests/openwebui/test_host.py::test_wave_c_still_waits`. MUST be green (`period/` now exists).
- [x] 3.5 REFACTOR only while green. Run full `pytest`. Slice A MUST be green on its own: `tests/test_query.py`, `tests/eval/test_measure.py`, gold tests, `tests/test_identity.py`, and the allowlist (13 paths, no `period`) unchanged. `pyproject.toml` `dependencies == []`.

## Slice B: Display (after A is green)

### Phase 4: Card line (RED first)

- [x] 4.1 RED: edit `tests/card/test_render_card.py`. Replace `test_compare_shows_both_values_without_delta` with: verified compare, `render_card(_neighbor_rows(), result, "60694190")` sets `card.difference == "Diferencia entre las dos cifras verificadas: 60694190"`. Values stay `(21262335, 81956525)`. Line contains no `segundo trimestre`, `trimestre aislado`, or `claims`. `"delta"` still not a `ClaimCard` field. `_METRIC_CHIP` still `{"net_income": "Resultado neto"}`.
- [x] 4.2 RED: same file. `test_compare_without_string_has_no_line`: `render_card(_neighbor_rows(), result)` and `render_card(..., None)` give `card.difference == ""`, and `60694190` is absent from every visible field. Add `card.difference` to the `_visible` helper.
- [x] 4.3 RED: same file. `test_abstain_and_single_ignore_passed_string`: abstained result and single verified claim, each with `"60694190"` passed, give `card.difference == ""`. Extend the no-kernel-call spy test so `difference` (the function) is not in the names `render_card` calls and `claimledger.period` is not imported by `card.py` (AST).
- [x] 4.4 Run `pytest tests/card/test_render_card.py`. Failures MUST be `TypeError` (unexpected third positional argument) or `AttributeError: difference`. Any other reason: fix the test first.

### Phase 5: Host text and reply (RED first)

- [x] 5.1 RED: edit `tests/openwebui/test_host.py`. `_compare_card()` gains the line `"Diferencia entre las dos cifras verificadas: 60694190"` after the two kernel values (order: seal, chips, rows, values, difference, sentence, reason; compare has no sentence). Replace `_COMPARE_DELTA` usage so the expected compare text includes `60694190` and no `+`. Update `test_reply_compare_copies_both_values_without_delta` (rename to `..._shows_code_difference`): exact text equals the new `_compare_card()` shape; drop `_COMPARE_DELTA not in text`; keep the no-`"delta"` word check and `f"{_SECOND_QUARTER_VALUE}-{_CONSOLIDATED_VALUE}"` not in text. Consolidated, parent, and abstain cards stay without the line.
- [x] 5.2 RED: same file, `test_reply_picture_follows_card`. Compare equals `_compare_card() + "\n" + earlier + "\n" + later`; `card_only == _compare_card()` and contains `60694190`; two pictures still follow; abstain and single-claim replies have no line. `_picture_sources()` adds `src/claimledger/period/difference.py` and `src/claimledger/period/__init__.py`; docling check stays empty and `sys.modules` unchanged.
- [x] 5.3 RED: same file, `test_query_and_card_stay_picture_free`. The `ClaimCard` field set becomes seven: add `"difference"`; `card.difference == ""` for the consolidated render. Allowlist stays 13 and now excludes both `crop` and `period`. Same assertion in `test_host_stays_off_claims_route_and_allowlist` style: `not any("period" in path for path in allowlist)`. Gold stays `21262335`/`21259769`; `60694190` not in `claims_query` compare body and not in gold files.
- [x] 5.4 Run `pytest tests/openwebui/test_host.py`. Failures MUST be `AssertionError` (missing difference line, missing `difference` field). Do not write production code before this run.

### Phase 6: Display GREEN

- [x] 6.1 GREEN: `src/claimledger/card/card.py`. Add `_DIFFERENCE_LABEL = "Diferencia entre las dos cifras verificadas"`. Add `difference: str = ""` as the last `ClaimCard` field. Change `render_card(candidates, result, difference: str | None = None)`. For verified, exactly two claims, and a non-empty string: `difference=f"{_DIFFERENCE_LABEL}: {difference}"`. Abstain and single-claim ignore it. No digit parsing, no `period` import. `_METRIC_CHIP` unchanged.
- [x] 6.2 GREEN: `src/claimledger/openwebui/text.py`. After the values, `if card.difference: parts.append(card.difference)`, before the sentence. No label text in `text.py`.
- [x] 6.3 GREEN: `src/claimledger/openwebui/reply.py`. Import `difference` from `claimledger.period.difference`. Body: `candidates, result = measure(...)`; `text = card_text(render_card(candidates, result, difference(result)))`; `images = attach(...)`; same return. `app.py` and `http/` unchanged. `measure` does not import `period`.
- [x] 6.4 Run `pytest tests/card/test_render_card.py tests/openwebui/test_host.py tests/period/test_difference.py`. MUST be green.
- [x] 6.5 REFACTOR only while green. Run full `pytest`. Confirm: `QueryResult` four fields; `POST /claims/query` has no `delta`; `60694190` appears nowhere in `query`, gold, `evals/`, or `measure` output; `dependencies == []`; 13-path allowlist unchanged; kernel tests docling-free, no network, no PDF, no Docker; no commit made.
