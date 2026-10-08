# Tasks: Reply Without Retrieval

## Review Workload Forecast

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

Estimated changed lines: 280-400. Delivery strategy: ask-on-risk. Split: single PR.

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Evidence rows without retrieve | single PR | `python -m pytest tests/card tests/eval tests/openwebui tests/agent tests/ingest/test_extras_ci.py` | N/A — pytest only; no browser runner | Revert candidate, measure, reply, drawers, tools, Dockerfile, and those tests |

## Phase 1: Move Candidate

- [x] 1.1 RED: import `Candidate` from `claimledger.card.candidate`. Confirm `ImportError` while it lives in `src/claimledger/retrieval/drawers.py`. Spec: "Card owns Candidate".
- [x] 1.2 GREEN: frozen `Candidate` (`drawer` `tables`|`narrative`, `text`, `ref`) in `src/claimledger/card/candidate.py`. `drawers.py` re-exports it. No helper. No `card/__init__.py` re-export.
- [x] 1.3 `tests/retrieval/test_drawers.py` still sees that type. Refactor while green.

## Phase 2: Evidence helper

- [x] 2.1 RED: `candidates_from_claims` is missing. `()` if empty. One `tables` row: `text` else `label`, `ref` = `artifact_hash`. Shared hash adds no neighbor. No `docling`. Spec: "Blank text uses the label".
- [x] 2.2 GREEN: add `candidates_from_claims` only in `src/claimledger/card/candidate.py`. Refactor only while green.

## Phase 3: Measure without retrieve

- [x] 3.1 RED: `tests/eval/test_measure.py`: `measure(question, ledger)` only. `understand` then `query`. No `retrieve`, `recorded_book`, or `Ledger.seed`. Seed rows `()`. Gold `21262335`, `21259769`, `81956525`; no `60694190`. `21.262.335` is one tables row. No narrative, rank, or `docling`.
- [x] 3.2 GREEN: `src/claimledger/eval/measure.py` returns the helper only if `status == "verified"`. Drop `_quarterly_book` and `retrieve`. Update the `reply` call signature only. Refactor while green.

## Phase 4: Reply without retrieve

- [x] 4.1 RED: `tests/openwebui/test_host.py` drops the DoclingReader stub. `21.262.335` and `21262335` omit the two-row sentence. Parent `21259769` invents no neighbor. Bar `[21262335, 81956525]`; `60694190` only on the difference line. No `retrieve`. `recorded_book` once. Card stays first.
- [x] 4.2 GREEN: both branches in `src/claimledger/openwebui/reply.py` use `candidates_from_claims`. Else calls `measure(question, book)`. `artifact_hash` only for `attach()`. Refactor while green.

## Phase 5: Card imports and fewer than two rows

- [x] 5.1 RED: `tests/card/test_render_card.py` imports `claimledger.card.candidate`. One row seals `VERIFICADO` (`21262335` / `21259769`) without the two-row sentence. Two rows keep it. No retrieval, `DoclingReader`, `starlette`, `docling`, `llama_index`, or `open_webui`. `dependencies` stays `[]`. Off the allowlist.
- [x] 5.2 GREEN: `src/claimledger/card/card.py` imports `Candidate` from `card.candidate`. `_sentence` only when `len(rows) == 2`. `card/__init__.py` does not re-export.

## Phase 6: Search ImportError

- [x] 6.1 RED: `tests/agent/test_tools.py`: `retrieve` raises `ImportError` → `{"hits": []}`. `authorized_values` empty. Hits are text/page/ref. `21.262.335` does not authorize.
- [x] 6.2 GREEN: `search` in `src/claimledger/agent/tools.py` imports `retrieve` inside the function and returns `{"hits": []}` on `ImportError`. Only `verify` fills `authorized_values`.

## Phase 7: Dockerfile and CI

- [x] 7.1 RED: `tests/ingest/test_extras_ci.py` requires Dockerfile `.[http,deepseek]` and no `retrieval` install. Keep `--extra retrieval` in `.github/workflows/pytest.yml` for `tests/retrieval`. Confirm the Dockerfile assertion fails.
- [x] 7.2 GREEN: `Dockerfile` installs `.[http,deepseek]`. Leave `.github/workflows/pytest.yml`, the `retrieval` extra, `retrieval/` tests, and `dependencies = []` unchanged.

## Phase 8: Green suite

- [x] 8.1 Run `python -m pytest` until green. No `docling` in kernel tests. Gold stays frozen.
