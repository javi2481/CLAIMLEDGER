# Tasks: Native Stack Audit (on demand)

## How to call it

This file is the function. It is complete and it stays unrun until a call is asked for. A call does not start phase 8, phase 1A, or phase 9.

```text
audit(scope) -> runs/<YYYY-MM-DD>/audit.md
```

Default scope: `src/claimledger/`. Say a narrower path to audit one area.

## Review Workload Forecast

One call writes a verdict file and does not edit production code. A replacement after that call is a separate step, one function at a time. No audit script. No corpus parse. No crop. No commit unless the user asks.

Decision needed before a call: No
400-line budget risk: Low for the verdict. High if several replacements are folded into the same call. Do not fold them in.

### Work units per call

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Verdict file for this date | None | N/A (read) | Pinned docs | Delete that `runs/<date>/` folder |
| 2 | One native replacement, only if a row requires it and a later step is asked | Later, per row | The existing test for that function | N/A | Revert that function only |

## Step 1: Verdict (the return value)

- [x] 1.1 List custom functions in the requested scope that are not a direct call into Docling, docling-graph, LlamaIndex, Starlette, or Open WebUI.
- [x] 1.2 For each, check the pinned API. Write `runs/<date>/audit.md` with `keep` plus the gap, or `call-native` / `delete` plus the API name and the pin you cited. Do not add a script to build the list.
- [x] 1.3 Treat identity, verification, abstention, and the card seal as `keep` unless a pinned API does that exact job. Do not relax gold.
- [x] 1.4 Do not apply `fase-1a-corpus-parse` or `fase-8-crop` from this call.

2026-10-05 call: `runs/2026-10-05/audit.md`. Step 2 stays open.

2026-10-06 call: `runs/2026-10-06/audit.md`. The five 2026-10-05 `delete` and `call-native` rows are now library calls. This run has no new `call-native` row. The earlier file stays.

## Step 2: Replacements (only after the file exists, and only if asked)

The 2026-10-05 rows for the grid and the body walk are planned in `openspec/changes/extract-native-tables/`. That change applies them. This file does not.

- [ ] 2.1 For each `call-native` row, replace the custom block with the named call. One function per step. Existing tests must fail first if behavior would change.
- [ ] 2.2 Leave every `keep` row in place.

## Repeat

A later call creates a new `runs/<date>/` folder. It does not edit the previous run and it does not allocate a new wave number.
