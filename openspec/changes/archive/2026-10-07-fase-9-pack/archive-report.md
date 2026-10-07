# Archive Report: fase-9-pack

**Change**: fase-9-pack
**Archived to**: `openspec/changes/archive/2026-10-07-fase-9-pack/`
**Date**: 2026-10-07
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (the user asked to archive, not to commit; no PR opened)
**Review lineage**: none in this change folder

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 25/25 `[x]` | `tasks.md` tasks 1.1–1.2, 2.1–2.7, 3.1–3.5, 4.1–4.4, 5.1–5.4, 6.1–6.5. No `- [ ]` remains in the archived file |
| Verify | PASS WITH WARNINGS | `verify-report.md`: `python -m pytest -q` 317 passed, 0 failed, 0 skipped, exit 0. Requirements 9/9. Scenarios 22/22. 0 blockers, 0 critical findings. Evidence `sha256:056792f22f26f06e7f43e3bbe8099980a1979f72d587d7225df4583b8952ea1c` |
| Destructive merge | intentional, warned | See "Destructive merge warning" below |

## Destructive merge warning

This merge retires the old "must not subtract" display sentences on purpose. That is the change, not an accidental destructive merge. The retired wording:

- `query` purpose: "Compare MUST return two claims and MUST NOT subtract until Fase 9."
- `claim-card` Compare Card: "It MUST NOT subtract or show a delta." and scenario "Two values, no delta".
- `openwebui-host` Always That Card: "a compare that shows both claims and no delta" and scenario "Compare has no delta".
- `openwebui-host` Closed Bounds: "Subtraction, charts, and the orchestrator MUST wait", "Phases 9–13 MUST NOT start", and "`claim-card` ... `verify-eval` MUST stay unchanged".
- `verify-eval` Compare Without Subtraction: bare "MUST NOT subtract".

What did not move:

- Gold numbers stay frozen: `21262335` (consolidated), `21259769` (parent), and `-14950948` (consolidated `income_tax`, 1T26) are unchanged. The `cp-*` pairs stay `21262335` / `81956525`.
- `60694190` is not a gold expected value. It is a code-computed display string (`81956525` minus `21262335`). It is not a `FinancialClaim`, has no `identity_key`, is never upserted, and appears in no gold file, no `evals/` file, no `query` result, and no `measure` output.
- `query` still never subtracts. `QueryResult` still has exactly `status`, `reason`, `claims`, `identity`.
- Rector and north-star untouched.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| query | Modified + Added | Purpose sentence rewritten (see below). "Compare Returns Two Claims Without Delta" now forbids a `delta`/`difference` field and adds the "QueryResult keeps four fields" scenario. Added "Compare Difference Outside Query" (4 scenarios) and "Query and Pack Stay Separate" (1 scenario) |
| claim-card | Modified | "Compare Card" now allows one labelled line, "Diferencia entre las dos cifras verificadas", only when code produced the string. Scenarios: passed difference, no string no line, abstain and single unchanged. "Pure Display" takes an optional difference string and must not call the difference function |
| openwebui-host | Modified | "Measure Then Card" lets the host pass code's difference to `render_card`. "Always That Card" shows the difference line in compare. Scenario "Compare has no delta" became "Compare shows the code difference". "Closed Bounds": charts and orchestrator wait, phases 10–13 do not start, `http-query` and `gold-regression` stay unchanged. Scenario "Wave C waits" became "Later phases wait" |
| verify-eval | Modified | "Compare Without Subtraction": `measure` does not subtract and does not call the difference function. Added scenario "Measure does not call the difference" |

Not touched: `gold-regression`, `http-query`, `document-graph`, `ledger`, `lookup`.

### Purpose sentence fix (done in this archive)

The verify report flagged that `openspec/specs/query/spec.md` still said "Compare MUST return two claims and MUST NOT subtract until Fase 9." The clause is now: "Compare still returns two claims; subtraction lives outside `query`, and `QueryResult` has no delta field." No "until Fase 9" remains under `openspec/specs/`.

## Verify warnings (all non-blocking)

1. **Query purpose sentence** still said "until Fase 9". Fixed in this archive (above).
2. **`AGENTS.md` status line** carried an orchestrator edit made during the change, while `tasks.md` listed `AGENTS.md` in the apply closed bounds. The archive owns the closing line and set it (see below).
3. **Currency mismatch has no runtime test.** It cannot be built: `validate_claim` pins `ARS` and `dataclasses.replace(claim, currency="USD")` raises `ClaimError: currency must be ARS`. The guard stays in `difference.py` (100% line and branch coverage) and the test covers issuer, statement, scope, metric, and unit mismatches. Design accepted this. Currency stays untested.
4. **"No second merger" rests on static evidence.** `src/` has one merger, the native `GraphMerger` in unchanged `graph/build.py`. `period/` is pinned to two files by test. No test scans all of `src/`. No second merger was added and none was needed.

Verify also logged one SUGGESTION: the host path is tested only with the positive `60694190`; a negative difference is covered by the unit test (`-17780588`).

## AGENTS.md

Closing status line set by the archive:

> Active change: none. Next: phase 10, VLM second reader, not opened. Pending: `openspec/changes/auditoria-stack-nativo/` (on demand, not a wave step); phases 11–13 not opened. Archived: `openspec/changes/archive/2026-10-07-fase-9-pack/`, then the existing archive list in its original order.

The rest of `AGENTS.md` is unchanged. Phase 10 is named as next and is not opened as work, so the pending sentence lists 11–13 only.

## Archive Contents

- proposal.md
- exploration.md
- specs/query/spec.md
- specs/claim-card/spec.md
- specs/openwebui-host/spec.md
- specs/verify-eval/spec.md
- design.md
- tasks.md (25/25 complete)
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/fase-9-pack/` no longer exists.

## Traceability (Engram, project `claimledger`)

| Artifact | Observation |
|----------|-------------|
| exploration / approach accepted | #1110 |
| proposal decisions (label, display, no plus sign) | #1111 |
| spec deltas | #1112 |
| design call chain | #1113 |
| tasks | #1114 |
| apply-progress | #1115 (slice A #1116, slice B #1117) |
| verify-report | #1118 (decision note #1119) |
| archive-report | `sdd/fase-9-pack/archive-report` |

Proposal and spec have no observation with the `sdd/fase-9-pack/proposal` or `/spec` topic key; their content is the files in this folder, and #1111 / #1112 record the decisions.

## What stays pending

- Phase 10 (VLM second reader) is named as next and is not opened.
- `openspec/changes/auditoria-stack-nativo/` stays pending as an on-demand call. It is not a wave number and was not part of this archive.
- Phases 11–13 are not opened. Charts and the orchestrator still wait.
