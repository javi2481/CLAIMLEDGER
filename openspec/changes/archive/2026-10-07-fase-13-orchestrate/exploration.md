# Exploration: Phase 13 Fixed Plan Around the Kernel

Architecture is CLOSED. Rector §22: when the question is compound, one orchestrator plans the steps. Tools fetch. The kernel decides what is true. Identity and verification stay services.

## Gate

`docs/plan-implementacion.md`: “¿La pregunta es compuesta?” Yes for “compará el neto de los últimos 4 trimestres”. No for one claim, and no for “1T26 vs 2T26”. That compare is already one `query`. Wrapping it would add an orchestrator because the path looks agentic. The user asked to open phase 13 on 2026-10-07.

## What the single query cannot do

`understand` folds “últimos 4 trimestres” into one compare Intent. `query` then returns the two book periods and stops. It cannot name the two quarter-ends that were asked and are absent. Phase 12 can draw a hole only if a caller passes it. Nothing today passes those holes, and nothing calls the kernel once per period.

## Native stack

Pinned LlamaIndex extras are the Docling reader and the node parser. They retrieve candidates. They do not fan out `query`. A LlamaIndex Workflow package is not pinned. The rector says the financial plan is known, so an LLM must not improvise it. The gap is a fixed fan-out: resolve once, `query` once per period, stitch verified claims, pass the misses as holes to the phase 12 fence.

## Out

An agent swarm. An Identity Agent or a Verification Agent. matplotlib and Artifact. Phases 10 and 11. A new HTTP route. A chart field on `QueryResult`. Any new gold number.
