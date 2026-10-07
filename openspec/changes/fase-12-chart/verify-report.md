# Verify Report: fase-12-chart

**Change**: fase-12-chart
**Date**: 2026-10-07
**Verdict**: pass
**Git commit**: not created

## Evidence

`python -m pytest -q` — 322 passed, 0 failed, 0 skipped, exit 0.

## What was checked

- Compare series copies `21262335` and `81956525` into `bar [21262335, 81956525]`.
- `60694190` stays on the card difference line and is absent from the fence and from `POST /claims/query`.
- Gap `2026-09-30` is `Hueco:` and is not a bar.
- Single-claim and abstain replies have no Mermaid fence.
- `QueryResult` still has `status`, `reason`, `claims`, `identity`.
- `chart/` imports no `docling`. `query.py` and `measure.py` do not import `claimledger.chart`.
- Allowlist stays 13 paths and excludes `chart`.

## Not done

Archive. matplotlib, Artifact, and the orchestrator stay out.
