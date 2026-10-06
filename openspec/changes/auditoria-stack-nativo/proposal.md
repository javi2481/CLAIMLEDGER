# Proposal: Native Stack Audit (on demand)

## Intent

Keep one complete procedure that can be executed whenever someone needs to separate native stack behavior from code we had to write. It is not phase 8 and it is not a step between the other phases. A call reads the current code, compares it to the pinned APIs, and leaves a dated verdict. It does not add a program to do that reading.

## Scope

### In Scope

- The policy spec: custom code only for a named gap; otherwise call the pin.
- The function contract: input, output path, repeat rule, and the two steps (verdict, then optional replacement).
- On each call: one verdict per custom function in the requested scope. `keep` names the gap. `call-native` or `delete` names the pinned API.
- Comparison source: the pinned version's own docs and API.
- The kernel (identity, verification, abstention, gold) stays a named gap unless a verdict shows a pinned API that already does that exact job.

### Out of Scope

- A place in the wave table (phases 0–13). Phase 8 stays the crop. Phase 1A stays the corpus.
- An audit script, linter, or new package.
- Running the function during this planting.
- Rewrites before that call's verdict exists.
- Gold edits, MinerU, Markdown as source of truth, an LLM writing identity.

## Capabilities

### New Capabilities

- `native-stack`: Custom code is allowed only for a named gap. A job the pinned stack already does MUST be a library call. The check is this on-demand function, not a new tool.

### Modified Capabilities

- None.

## Approach

Approach 1. The procedure in `tasks.md` is the function. Leave it unrun until a call is requested. Each call writes `runs/<date>/audit.md`. A replacement, if any, is a later step that only touches rows marked `call-native`, one function at a time.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `AGENTS.md` | Pointer | Names this change as the on-demand call |
| `src/claimledger/` | Read on call | Verdicts, not a drive-by rewrite |
| `runs/<date>/audit.md` | New on call | The return value of that call |
| `openspec/specs/native-stack` | New on archive | The policy. The function remains callable |
| Kernel gold and HTTP contracts | Unchanged | The gap the product owns |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Audit deletes the kernel | Med | Identity and abstention are a named gap unless a pin proves otherwise |
| Verdict from memory | Med | Cite the pinned doc or API, or leave the row unchecked |
| Treating the call as phase 8 | Med | This folder has no wave number. Phase 8 stays `fase-8-crop` |
| Inventing a checker script | Low | Approach 2 is rejected |

## Rollback Plan

Delete a single `runs/<date>/` folder to drop that call. Revert any call-site edit tied to that run. Leave `fase-1a-corpus-parse` and `fase-8-crop` untouched. The rule in `AGENTS.md` stays unless the user withdraws it.

## Dependencies

- Pins: `docling==2.130.0`, `docling-graph==1.9.1`, LlamaIndex docling reader and node parser `0.5.0`, `starlette==1.0.0`, Open WebUI `v0.11.4-slim`.
- No new dependency.

## Success Criteria

- [x] A call can be made without opening phase 8 or phase 9.
- [x] That call writes `runs/<date>/audit.md` and does not add a script.
- [x] Every row in that file is `keep` with a gap, or `call-native` / `delete` with a pinned API.
- [ ] A second call writes a new run and leaves the previous one in place.
- [x] Kernel tests still do not import `docling`. Gold numbers are unchanged.
