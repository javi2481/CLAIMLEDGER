# Archive Report: fase-12-chart

**Change**: fase-12-chart
**Archived to**: `openspec/changes/archive/2026-10-07-fase-12-chart/`
**Date**: 2026-10-07
**Persistence**: hybrid
**Verdict**: archived and closed
**Git commit**: not created (the user asked to archive, not to commit)
**Review lineage**: none in this change folder

## Gates

| Gate | Result | Evidence |
|------|--------|----------|
| Task completion | 12/12 `[x]` | `tasks.md` tasks 1.1, 2.1–2.6, 3.1–3.2, 4.1–4.3. No `- [ ]` remains |
| Verify | pass | `verify-report.md`: `python -m pytest -q` 322 passed, 0 failed, 0 skipped, exit 0 |
| Destructive merge | none on gold | See below |

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| chart | Added | New `openspec/specs/chart/spec.md`. Series spec copies claim values, a missing period is a hole, Mermaid fence does not calculate |
| openwebui-host | Modified | Purpose names the fence. Added scenarios “Compare completion draws the series” and “Single claim and abstain stay card-only”. Features Off allows a fence after the card and pictures. Allowlist scenario excludes `chart` |

Not touched: `gold-regression`, `query`, `claim-card`, `http-query`, `document-graph`.

The phase 12 host delta also said the orchestrator package MUST NOT exist and phases 10, 11, and 13 MUST NOT start. Phase 13 superseded that bound. Those sentences are not copied into the main spec. `openspec/specs/openwebui-host/spec.md` keeps the phase 13 bound: phases 10 and 11 MUST NOT start, and `orchestrate/` stays off the allowlist.

## What did not move

- Gold numbers stay frozen: `21262335`, `21259769`, `81956525`, and `-14950948`.
- `60694190` stays a display string on the compare card. It is not a bar height and not a gold expected value.
- `QueryResult` still has `status`, `reason`, `claims`, `identity`.
- Rector and north-star untouched.

## AGENTS.md

The archive of phase 13 in the same session owns the closing status line. This report does not set it.

## Archive Contents

- proposal.md
- exploration.md
- specs/chart/spec.md
- specs/openwebui-host/spec.md
- design.md
- tasks.md (12/12 complete)
- verify-report.md
- archive-report.md (this file)

Active path `openspec/changes/fase-12-chart/` no longer exists after the move.
