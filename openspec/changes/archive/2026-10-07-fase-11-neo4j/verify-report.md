# Verify Report: fase-11-neo4j

**Change**: fase-11-neo4j
**Date**: 2026-10-07
**Verdict**: pass
**Git commit**: not created

## Evidence

`python -m pytest -q` — 334 passed, 0 failed, 0 skipped, exit 0.

## What was checked

- `build` writes `graph.cypher` with `CypherExporter` and `n.period = "2026-03-31"`.
- The script does not contain `21262335` or `81956525`.
- “todos los resultados netos de BYMA” calls `query` twice with `compare` false. Values stay `21262335` then `81956525`.
- The parent question uses `21259769` then `81946993`.
- `2026-09-30` is a gap. `60694190` is not a claim value.
- The host fence is `bar [21262335, 81956525]` and has no `60694190`. Without a script the reply abstains.
- `POST /claims/query` for that question stays `abstained` and has no Mermaid fence.
- `book/` imports no `docling` and no `neo4j`. Allowlist stays 13 paths and excludes `book`.

## Not done

Archive. A live Neo4j server. Phase 10.
