# Exploration: Phase 11 Cypher Export of the Book

Architecture is CLOSED. Rector §20 and principle 12: Neo4j consults the book. It does not decide the claim. The lookup stays the truth of the number.

## Gate

`docs/plan-implementacion.md`: “¿El libro ya tiene historia que consultar?” Yes. The graph already has two quarterly periods, `2026-03-31` and `2026-06-30`, for issuer `BYMA` and statement `income_statement`. The user deferred phase 10 on 2026-10-07 because there is no GPU for the VLM second reader, and asked to open phase 11 next.

The question this phase is for: “todos los resultados netos de BYMA”.

## What the book already is

Ingest writes one `artifacts/graph/graph.json` through `JSONExporter`. Nodes are only Document, Issuer, Period, and Statement. `FinancialClaim`, scope, metric, and value are absent. A question does not rebuild the graph. `query` still returns one identity, or two claims on a named compare. Phase 13’s plan covers one fixed window of four quarter-ends. Neither path is a book query for every net-income period of one issuer.

## Native stack

`docling-graph==1.9.1` already exports Cypher. `CypherExporter.export(graph, output_path)` writes a cypher-shell script. The default style is `merge`: nodes are MERGEd on id, so a second load does not duplicate the book. The same call is how `JSONExporter` is used in `graph/build.py`. The exporter does not open a Neo4j connection. Loading the file is `cypher-shell -f`.

No pinned extra is a Neo4j driver. Adding one, or a Docker service, to answer the question inside pytest would invent a runtime the pin does not provide. Kernel tests must stay free of Docker, network, and PDF.

## Gap

Nothing calls `CypherExporter`. The phase 2 store test forbids the name `CypherExporter` and the substring `cypher` inside `src/claimledger/graph/`, and `document-graph` says Neo4j MUST be absent. That ban was correct for phase 2. Phase 11 is the change that allows the exporter call and still forbids a Neo4j driver, `run_pipeline`, and `FinancialClaim` in that package.

The script can list issuer, period, statement, and document. It cannot contain `21262335` or `81956525`, because those digits are claims and claims stay out of the graph. The book question therefore has two steps, and only the first is Cypher: which periods of BYMA income statements exist. Each number still comes from `query`. Neo4j does not store the answer and does not choose it.

Custom code is the call to `CypherExporter` plus the split above. A hand-written Cypher generator is the job the exporter already does.

## Out

A live Neo4j server, the Neo4j Python driver, and Docker in the kernel suite. Putting `FinancialClaim` or a value on a node. A new gold number. An LLM that writes the Cypher or the digits. Phase 10. A new HTTP route. Rebuilding the graph on the question.
