# Agent Host Specification

## Purpose

Peripheral `agent/` host: verify authorizes, search finds, DeepSeek drafts/orchestrates, host gates. Verified claims = unit of truth; `authorized_values` = canonical projection. Prompt is help, not enforcement.

## Requirements

### Requirement: Verify Tool Returns Authorized Projection

`verify` MUST call `understand`/`query` on `recorded_book()` (plus existing `execute`/`ask`/`difference` paths) and return `{status, claims, authorized_values}`. Verified: claims carry kernel fields including `identity_key` and canonical digit `value`; `authorized_values` MUST project those values. Abstained: both MUST be empty. The LLM MUST NOT write `identity_key`.

#### Scenario: Verified projects values

- GIVEN kernel-verified claim value `21262335`
- WHEN `verify` runs
- THEN `status` is `verified` and `authorized_values` includes `"21262335"`

#### Scenario: Abstained empties authorization

- GIVEN kernel abstention
- WHEN `verify` runs
- THEN `claims` and `authorized_values` MUST be empty

#### Scenario: Model never writes identity_key

- GIVEN any tool-loop turn
- WHEN the host assembles output
- THEN no `identity_key` MUST come from model text

### Requirement: Search Never Authorizes

`search` MAY call `retrieve`. When that call succeeds, hits MUST be Docling-JSON text/page/ref only. When `retrieve` raises `ImportError`, `search` MUST return empty hits and MUST NOT raise. `search` MUST NOT return `verified` or `authorized_values`. Evidence and empty hits MUST NOT authorize a figure. `verify` remains the only tool that fills `authorized_values`.

#### Scenario: Search is context only

- GIVEN a hit whose text contains digits
- WHEN `search` runs
- THEN the result has text/page/ref only — never `verified`/`authorized_values`

#### Scenario: Evidence is not authorization

- GIVEN only search text with `21.262.335`
- WHEN the gate runs
- THEN that figure MUST NOT be authorized

#### Scenario: ImportError returns empty hits

- GIVEN `retrieve` raises `ImportError`
- WHEN `search` runs
- THEN hits MUST be empty
- AND `authorized_values` MUST stay empty, and the completion MUST NOT see that exception

### Requirement: Host Executes DeepSeek Tool Loop

Host MUST run `deepseek-flash` at `https://api.deepseek.com` and MUST execute model `tool_call`s. Missing/invalid `DEEPSEEK_API_KEY` MUST use the controlled abstention path and MUST NOT crash completions with a stack trace. Pytest MUST mock DeepSeek; kernel tests stay network-free.

#### Scenario: Host executes tool_call

- GIVEN mocked DeepSeek `verify` tool_call
- WHEN the loop runs
- THEN the host executes `verify` and returns structured result

#### Scenario: Missing key abstains safely

- GIVEN missing/invalid `DEEPSEEK_API_KEY`
- WHEN completion runs
- THEN controlled abstention path; no stack trace

### Requirement: Host Authorization Gate

Host MUST enforce authorization; prompt MUST NOT. Financial values MAY leave only via verified `authorized_values`. Verified: DeepSeek prose → normalize guard → allow only authorized. Unauthorized figure: reject/regenerate once; if still unauthorized → controlled abstention template (never ship unauthorized prose). Abstained (`authorized_values` empty): template only — no LLM financial prose, including word-form amounts.

#### Scenario: Authorized normalized prose passes

- GIVEN `authorized_values` `["21262335"]` and prose `21.262.335`
- WHEN gate runs
- THEN prose is allowed

#### Scenario: Unauthorized falls to template

- GIVEN verified path and unauthorized figure after one regenerate
- WHEN gate finishes
- THEN template only; unauthorized prose MUST NOT ship

#### Scenario: Abstained blocks LLM financial prose

- GIVEN empty `authorized_values` and word-form draft
- WHEN host assembles
- THEN template only; no LLM financial prose

### Requirement: Normalize Guard

Guard MUST normalize thousand dots, commas, spaces, and `$` before compare. MUST exclude dates, pages, period labels (`31/03/2026`, `página 14`, `1Q26`). Verified word-number NLP is out of MVP.

#### Scenario: Forms normalize to canonical

- GIVEN `["21262335"]` and forms `21.262.335` / `21,262,335` / `21 262 335` / `$21.262.335`
- WHEN guard normalizes
- THEN each matches the authorized value

#### Scenario: Metadata exempt

- GIVEN prose with `31/03/2026`, `página 14`, `1Q26`
- WHEN guard runs
- THEN those MUST NOT be treated as financial claims

### Requirement: Controlled Abstention Template

Template MUST be a deterministic short Spanish constant reusing host/card abstention voice (`ME ABSTENGO` lineage). MUST NOT invent marketing copy. Exact string MAY be a stable agent/host constant.

#### Scenario: Deterministic voice

- GIVEN abstained or fall-through path
- WHEN template emits
- THEN the same `ME ABSTENGO`-lineage constant appears

### Requirement: Agent Bounds Preserve Kernel

`src/claimledger/agent/` MUST be off the 13-path allowlist. MUST NOT edit `query.py`, `ledger.py`, gold, or `identity_key`. Gold stays `21262335`/`21259769`. Optional HTTP extra MAY pin; `dependencies` MUST stay `[]`.

#### Scenario: Kernel closed

- GIVEN this change
- WHEN scope is checked
- THEN `agent/` off allowlist; kernel paths untouched
