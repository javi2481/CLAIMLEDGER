# Design: Native Stack Audit (on demand)

## Technical Approach

`specs/native-stack`. This change is the function. It has no wave number. Phase 1A closes the corpus. Phase 8 crops the row. Call this function when a review is needed; the call does not move either of those.

```text
audit(scope) -> runs/<YYYY-MM-DD>/audit.md
```

Default scope is `src/claimledger/`. A caller may name a smaller subtree. The return value is the verdict file. The call does not edit production code. A later step may apply one `call-native` row by deleting the custom block and calling the API that row names.

## Architecture Decisions

| Decision | Choice | Rejected | Why |
|---|---|---|---|
| Place | Standing function, this folder | `fase-8b` | The crop already owns phase 8. An audit is not a wave step |
| Repeat | New `runs/<date>/` each call | One archive, then a new phase number | The same question will come back |
| Output | Verdict table in that run | A linter; a dashboard | A script that audits the stack is the thing the rule forbids |
| Source of truth | Pinned docs and the installed API | Model memory | A remembered method can be the wrong version |
| Kernel | `keep`, gap = financial identity, verification, abstention | Replacing `query` with Docling or an LLM | The rector assigns that job to CLAIMLEDGER |
| Replacement | Separate step, one function, the named API | A wrapper module; rewriting during the call | The call's return value is the table |

## Verdict row

| Function | File | Verdict | Native API or gap | Pin cited |
|----------|------|---------|-------------------|-----------|
| filled when called | | `keep`, `call-native`, or `delete` | name | doc or symbol |

Empty until a call. First scope to open: `ingest/extract.py` grid and bbox, `ingest/classify.py`, `retrieval/drawers.py`, `graph/link.py`. `identity`, `lookup`, `query`, `ledger`, and `card` open as the expected gap, not as code to delete.

## File Changes

| File | Change |
|------|--------|
| `AGENTS.md` | Points at this change as the on-demand call |
| `runs/<date>/audit.md` | Created only when the function is invoked |
| `src/claimledger/` | Untouched by the call. A later step may replace one `call-native` function |

## Rollback

Delete the `runs/<date>/` folder for that call. Revert any later edit that names that run. The rule in `AGENTS.md` remains until the user withdraws it.
