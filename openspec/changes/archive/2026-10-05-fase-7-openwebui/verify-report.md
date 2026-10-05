```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:ae8248e18d1b1e34536984cc2fb1f071681d78f7cda5af02787f59cdf9645d50
verdict: pass
blockers: 0
critical_findings: 0
requirements: 6/6
scenarios: 11/11
test_command: python -m pytest tests/
test_exit_code: 0
test_output_hash: sha256:ae8248e18d1b1e34536984cc2fb1f071681d78f7cda5af02787f59cdf9645d50
build_command: ""
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: fase-7-openwebui
**Version**: N/A
**Mode**: Strict TDD

`evidence_revision` and `test_output_hash` are the SHA-256 of the raw `python -m pytest tests/` stdout+stderr (8107 bytes, Windows CRLF, 97 CRLF newlines, 0 bare LF). `build_command` in `openspec/config.yaml` is empty, so no build process was started. `build_output_hash` is the SHA-256 of empty output. `build_exit_code: 0` records that absence, not a compiler run.

Canonical verification-evidence bytes are that pytest capture, preserved at `C:\Users\Equipo\AppData\Local\Temp\fase7-openwebui-pytest-reverify.bin`. The preimage is not this markdown file. This re-verify replaces the previous capture (`sha256:008bc086868db31956056cfde839c70dfa01ad791732195192ffb9d5dc86b91b`, 296 passed). The previous CRITICAL (Wave C waits UNTESTED) does not remain.

Counted from `openspec/changes/fase-7-openwebui/specs/openwebui-host/spec.md`, matching Engram `sdd/fase-7-openwebui/spec` (#1076): **6 requirements, 11 scenarios**.

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 9 |
| Tasks complete | 9 |
| Tasks incomplete | 0 |

All nine checkboxes in `openspec/changes/fase-7-openwebui/tasks.md` are `[x]` (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1). Full suite was allowed to run.

Engram `sdd/fase-7-openwebui/tasks` (#1078) still stops before slices 3–5. Completeness here follows the change file.

### Build & Tests Execution
**Build**: ➖ No build command configured (`build_command: ""`)

**Tests**: ✅ 297 passed / 0 failed / 0 skipped (73 warnings)
```text
python -m pytest tests/
exit 0
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Equipo\CLAIMLEDGER
configfile: pyproject.toml
plugins: anyio-4.13.0, Faker-40.23.0, hypothesis-6.167.1, asyncio-1.4.0, cov-7.1.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 297 items

tests\card\test_render_card.py ..........                                [  3%]
tests\eval\test_measure.py ............                                  [  7%]
tests\graph\test_conflict.py .....                                       [  9%]
tests\graph\test_fold.py .....                                           [ 10%]
tests\graph\test_period.py ............                                  [ 14%]
tests\graph\test_store.py ....                                           [ 16%]
tests\http\test_app.py ..................                                [ 22%]
tests\http\test_claims_query.py .................                        [ 27%]
tests\ingest\test_classify.py ................                           [ 33%]
tests\ingest\test_extract.py ................                            [ 38%]
tests\ingest\test_gold_compare.py ...............                        [ 43%]
tests\ingest\test_store.py ..........                                    [ 47%]
tests\openwebui\test_host.py ................                            [ 52%]
tests\retrieval\test_drawers.py .......                                  [ 54%]
tests\retrieval\test_read.py ...                                         [ 55%]
tests\test_gold_v1.py ...........                                        [ 59%]
tests\test_gold_v2.py ...........                                        [ 63%]
tests\test_identity.py ...........................................       [ 77%]
tests\test_ledger.py ........                                            [ 80%]
tests\test_lookup.py ..........................................          [ 94%]
tests\test_query.py ................                                     [100%]

====================== 297 passed, 73 warnings in 14.68s ======================
```

`tests/openwebui/test_host.py`: 16 passed, including `test_wave_c_still_waits`. The 73 warnings are Docling and docling-graph deprecations inside graph tests. Host tests added none. The hashed preimage includes those warning bodies; this block shows the session and the summary line.

Gold numbers stayed frozen in this run. `src/claimledger/ledger.py` still seeds `21262335`, `21259769`, `-14950948`, and `81956525`. `tests/test_gold_v1.py` and `tests/test_gold_v2.py` passed in this suite. The six kernel test files do not import `docling`, `docker`, `starlette`, or `claimledger.openwebui`. `dependencies = []`. The HTTP extra pin is `starlette==1.0.0`. `src/claimledger/__init__.py` is empty. `Dockerfile` `CMD` is still `manual.ui:build_manual_app`.

**Coverage**: `claimledger.openwebui` tool total 93% (81 statements, 4 missed, 24 branches, 3 partial). Config threshold is 0. Cached `openspec/config.yaml` still says coverage was not detected; pytest-cov 7.1.0 is installed and was used for this extra run only.

A second command, `python -m pytest tests/openwebui/test_host.py --cov=claimledger.openwebui --cov-branch --cov-report=term-missing -q --tb=no`, also exited 0 (16 passed, 0.75s). That run is not the hashed preimage.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Measure Then Card | Consolidated value | `tests/openwebui/test_host.py > test_reply_consolidated_21262335`, `test_completions_returns_only_the_card` | ✅ COMPLIANT |
| Measure Then Card | Parent value | `tests/openwebui/test_host.py > test_reply_parent_21259769_both_rows` | ✅ COMPLIANT |
| Always That Card | Abstain is the reply | `tests/openwebui/test_host.py > test_reply_abstain_adds_no_verified_value` | ✅ COMPLIANT |
| Always That Card | Compare has no delta | `tests/openwebui/test_host.py > test_reply_compare_copies_both_values_without_delta` | ✅ COMPLIANT |
| No Invented Rows | Unreadable hash | `tests/openwebui/test_host.py > test_reply_bad_hash_raises_and_invents_no_rows`, `test_bad_hash_is_400_and_skips_render`, `test_bad_body_is_400_and_skips_measure`, `test_missing_env_hash_is_400` | ✅ COMPLIANT |
| No Invented Rows | Stubbed reader | `tests/openwebui/test_host.py > test_reply_consolidated_21262335` (`_install_parsed_reader` stubs `read_hashed_json`; artifacts are written under `tmp_path`) | ✅ COMPLIANT |
| Features Off | One card only | `tests/openwebui/test_host.py > test_completions_returns_only_the_card`, `test_stream_is_one_card_then_done` | ✅ COMPLIANT |
| Features Off | Models lists no card | `tests/openwebui/test_host.py > test_models_lists_only_claimledger_card` | ✅ COMPLIANT |
| Slim Screen | Pinned slim image | `tests/openwebui/test_host.py > test_compose_pins_slim_screen` | ✅ COMPLIANT |
| Closed Bounds | Allowlist and kernel bans | `tests/openwebui/test_host.py > test_host_stays_off_claims_route_and_allowlist`; `tests/card/test_render_card.py > test_card_stays_off_kernel_allowlist`; `tests/http/test_app.py > test_http_extra_pins_starlette_only`, `test_http_stays_off_kernel_allowlist`; `tests/test_identity.py > test_import_scan_stays_clean`, `test_kernel_modules_importable` | ✅ COMPLIANT |
| Closed Bounds | Wave C waits | `tests/openwebui/test_host.py > test_wave_c_still_waits` | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios compliant

`test_wave_c_still_waits` reads `src/claimledger` and asserts the package names are disjoint from `crop`, `chart`, `charts`, and `orchestrator`. It asserts the only active OpenSpec change directory is `fase-7-openwebui`, and that none of `fase-8` through `fase-13` is active. It passed inside this suite. No production module was added for it. Subtraction has no package-name check; the active-change ban for fases 8–13 is what keeps that phase from being in scope.

`test_reply_consolidated_21262335` calls `reply` on a stubbed reader and asserts seal `VERIFICADO`, the consolidated chip, both neighbor rows, value `21262335`, and the consolidated sentence. `21259769` is absent. `test_reply_parent_21259769_both_rows` asserts value `21259769`, chip `Controlante`, and both rows. `test_reply_compare_copies_both_values_without_delta` asserts `21262335` and `81956525` and rejects the subtracted delta. `test_host_stays_off_claims_route_and_allowlist` asserts `POST /claims/query` is the only product route, host routes are `GET /v1/models` and `POST /v1/chat/completions`, the allowlist length is 13, and `openwebui` is not on it. Those tests passed inside this suite.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Measure Then Card | ⚠️ Partial | Host lives in `src/claimledger/openwebui/`, outside `http/`. `reply` calls `measure` then `render_card` then `card_text`. Consolidated and parent fixtures copy seal, chips, both rows, and the kernel value. `card_text` does not parse digits. `_ficha_rows` copies rows only when there are exactly two non-empty rows and each is at most 240 characters. Any other row shape is dropped. The written scenarios use that two-row fixture and passed. |
| Always That Card | ✅ Implemented | Abstain text is `ME ABSTENGO` plus the two neighbor rows and `recipe_no_extract`, with no `21262335` or `21259769`. Compare copies both values and does not append a delta. Completions JSON is one assistant message. |
| No Invented Rows | ✅ Implemented | A bad hash raises from `reply` and the HTTP host returns 400 `{"error":"unreadable_artifact"}` without calling `render_card`. A missing env hash with `build_host(None)` is the same 400. Host tests stub `read_hashed_json` and write JSON only under `tmp_path`. |
| Features Off | ✅ Implemented | `GET /v1/models` returns only `claimledger-card`. `POST /v1/chat/completions` content is the card. `stream: true` is one SSE object then `data: [DONE]`. Compose sets Ollama, titles, follow-ups, tags, and autocomplete to false. The compose text has no Knowledge, MCP, or Pipelines entry. |
| Slim Screen | ✅ Implemented | `docker-compose.yml` image is `ghcr.io/open-webui/open-webui:v0.11.4-slim` on `8080:8080`. `claimledger` publishes no port and runs `claimledger.openwebui.app:build_host --factory`. `Dockerfile` CMD stays `manual.ui:build_manual_app`. The compose file does not use `latest` or `main`. |
| Closed Bounds | ✅ Implemented | `dependencies = []`, `starlette==1.0.0`, allowlist length 13, empty root `__init__.py`, and frozen gold are covered by passing tests. Kernel tests do not import `docling` or Docker. Host tests use in-process `testserver` with port `None`. `test_wave_c_still_waits` passed in this run. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Location `src/claimledger/openwebui/`, not a route on `http/app.py` | ✅ Yes | Product route remains `POST /claims/query`. |
| `reply` → `measure` → `render_card` → `card_text` | ✅ Yes | `reply.py` is those two calls. No catch, no digit parse, no Starlette. |
| Copy `values` in order | ✅ Yes | Consolidated `21262335`. Parent `21259769`. Compare copies both value strings. |
| One choice; content is `card_text` | ✅ Yes | `_completion` has one assistant message. |
| Bad hash is 400 `unreadable_artifact` and skips `render_card` | ✅ Yes | Caught in `post_completions`, not in `reply`. |
| `MODEL_ID = "claimledger-card"` | ✅ Yes | Models payload matches the design object. |
| Slim image is the only published port | ✅ Yes | `ports:` appears once. |
| No `pyproject.toml` edit; HTTP extra stays `starlette==1.0.0` | ✅ Yes | uvicorn is not pinned. |
| In-process ASGI, stubbed reader, no Docker in tests | ✅ Yes | |
| `card_text` joins every non-empty row | ❌ No | `_ficha_rows` returns the rows only for a pair of strings each ≤ 240 characters. Otherwise it returns `()`. No scenario requires the other shapes. |
| Compose hash default `${CLAIMLEDGER_ARTIFACT_HASH:-}` | ❌ No | Compose sets a concrete fallback digest `7b7b624ade1011f9fd75931968312ef5c0fa19fe6061bb2cc5eb1491ffaa364f`. |
| Wave C waits | ✅ Yes | `test_wave_c_still_waits` passed. No crop, chart, charts, or orchestrator package. The only active change is `fase-7-openwebui`. |
| Starlette imported only inside `build_host` | ✅ Yes | AST check in `test_host_stays_off_claims_route_and_allowlist` passed. |
| `Dockerfile` CMD stays `manual.ui:build_manual_app` | ✅ Yes | |

### TDD Compliance
| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ⚠️ | Engram `sdd/fase-7-openwebui/apply-progress` (#1079) has a TDD table for tasks 1.1–2.2 only. Tasks 3.1–4.2 and 5.1 are `[x]` in `tasks.md` and have no Engram row. Task 5.1 records on disk that the new test passed on the first run because the absence already held. |
| All tasks have tests | ✅ | 9/9 tasks name `tests/openwebui/test_host.py`, which exists (16 tests). |
| RED confirmed (tests exist) | ⚠️ | Test file exists. Recorded RED: slice 1 `ModuleNotFoundError: No module named 'claimledger.openwebui'` (pytest exit 4); slice 2 `ModuleNotFoundError: No module named 'claimledger.openwebui.reply'` (pytest exit 2). Slices 3–5 have no recorded failing RED. Historical RED was not re-run. Task 5.1's first run passed; that is a lock on an absence that already held, not a tautology. |
| GREEN confirmed (tests pass) | ✅ | This run: 16/16 host tests passed inside `python -m pytest tests/` (297 passed, exit 0). |
| Triangulation adequate | ✅ | Reply has five cases. Routes cover models, one card, 400 bodies, stream, and a missing env hash. Compose is one scenario and one test. Wave C waits is one scenario and one test. |
| Safety Net for modified files | ⚠️ | Slice 2 records a pre-edit `test_card_text_copies_fields` exit 0. Later slices edited the same test file and have no recorded safety-net run. |

**TDD Compliance**: 3/6 checks passed, 3 partial

The first-run pass of `test_wave_c_still_waits` is recorded. It is not treated as a protocol failure: the test reads the package tree and the active change directory, and it would fail if `crop`, `chart`, `charts`, `orchestrator`, or `fase-8` through `fase-13` were present.

---

### Test Layer Distribution
| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit | 2 | 1 | pytest |
| Integration | 14 | 1 | pytest, starlette.testclient (in-process) |
| E2E | 0 | 0 | not installed |
| **Total** | **16** | **1** | |

Unit tests are `test_card_text_copies_fields` and `test_card_text_omits_whole_tables`. Integration tests call `reply` through `measure` with `read_hashed_json` stubbed, call `build_host` via `TestClient` (`testserver`, port `None`), read `docker-compose.yml` as text, or read the package tree and `openspec/changes`. No browser, bound port, Docker daemon, network, or PDF.

---

### Changed File Coverage
| File | Line % | Branch % | Uncovered Lines | Rating |
|------|--------|----------|-----------------|--------|
| `src/claimledger/openwebui/__init__.py` | 100% | 100% | — | ✅ Excellent |
| `src/claimledger/openwebui/reply.py` | 100% | 100% | — | ✅ Excellent |
| `src/claimledger/openwebui/text.py` | 100% | 87.5% (1/8 partial) | branch 19→21 | ✅ Excellent |
| `src/claimledger/openwebui/app.py` | 92.6% (50/54) | 2/16 partial | L18, L65, L71–72 | ⚠️ Acceptable |

**Average changed file coverage**: 96.75% (mean of the pytest-cov Cover column: 100, 91, 100, 96). Tool total for the package: 93%.

`tests/openwebui/test_host.py` and `docker-compose.yml` are not production modules. Coverage command was the extra pytest-cov run above, not the hashed suite. No changed production file is under 80%.

---

### Assertion Quality
| File | Line | Assertion | Issue | Severity |
|------|------|-----------|-------|----------|
| `tests/openwebui/test_host.py` | 468 | `assert "false" in compose` | Runs once per feature flag but does not check that flag's value. Any other `false` in the file satisfies it. | WARNING |

**Assertion quality**: 0 CRITICAL, 1 WARNING

`test_wave_c_still_waits` reads the real package directory and the active change directory. The package set is non-empty because the assertion is disjointness against names that are absent, and the active-change assertion requires exactly `fase-7-openwebui`. No tautology, no assertion that skips the tree, no ghost loop.

The other host assertions call `card_text`, `reply`, or `build_host` and check seal, chips, rows, values, status codes, or route lists.

---

### Quality Metrics
**Linter**: ➖ Not available (cached capabilities: `linter: not_detected`)
**Type Checker**: ➖ Not available (cached capabilities: `type_checker: not_detected`)

### Issues Found
**CRITICAL**: None

**WARNING**: `card_text` drops every row unless the card has exactly two non-empty rows of at most 240 characters. Design says each non-empty row is copied. Consolidated, parent, abstain, and compare scenarios use that two-row fixture, and those tests passed. `test_card_text_omits_whole_tables` locks the narrower behavior.

**WARNING**: Compose default for `CLAIMLEDGER_ARTIFACT_HASH` is a concrete digest. Design says `${CLAIMLEDGER_ARTIFACT_HASH:-}` (empty).

**WARNING**: Engram tasks (#1078) and apply-progress (#1079) were not updated for slices 3–5. `tasks.md` on disk is fully checked, including 5.1. Recorded RED exists only for slices 1 and 2.

**WARNING**: `test_compose_pins_slim_screen` does not bind each feature flag to `false`.

**SUGGESTION**: `app.py` does not cover a non-list `messages` value (L18), a non-empty `CLAIMLEDGER_ARTIFACT_HASH` when the argument is `None` (L65), or a JSON decode error (L71–72). The Wave C test does not look for a package directory named `subtraction`; fases 8–13 are banned as active changes instead.

### Verdict
PASS WITH WARNINGS
11/11 scenarios have a covering test that passed in this run. The suite is green (297 passed, 0 failed, 0 skipped, exit 0). The previous Wave C UNTESTED finding is closed by `test_wave_c_still_waits`. Four warnings remain. They do not leave a scenario uncovered and they do not block archive.
