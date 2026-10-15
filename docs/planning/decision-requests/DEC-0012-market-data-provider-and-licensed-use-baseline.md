---
id: DEC-0012
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: null
---

# Decision Request: Set the Market-Data Provider and Licensed-Use Baseline

## Decision Needed

Choose the initial market-data source/use combinations and their permitted local
and cloud retrieval, caching, transformation, display, export, retention,
attribution, redistribution, and commercial use.

## Why Now

Market exploration, financial analysis, portfolios, experiments, provider
governance, and local/cloud operation all depend on data that may be technically
accessible but contractually restricted.

## Current Authority and Constraints

Provider terms remain authoritative and time-sensitive; each admitted use needs
current review. Raw payloads require permission to retain, canonical records
preserve provenance, and technical access never establishes redistribution or
commercial rights.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Reviewed free/open provider baseline plus per-adapter use profiles | Enables useful community data with explicit coverage, delay, attribution, cache, export, and cloud limitations. | Terms may differ or change; cloud/commercial rights may remain unavailable. | Provider manifests, source register, cache/retention, attribution UI, export and conformance tests. | Medium; adapters can be disabled, but retained data needs policy handling. |
| B. User-supplied local imports only | Avoids a built-in provider commitment and keeps acquisition with the user. | Poorer onboarding, harder provenance validation, no common live query behavior, and still requires import rights guidance. | Import contract, local storage, provenance, validation, export restrictions. | High; providers can be added later. |

## Recommendation

Defer the final option until current provider terms and intended community versus
managed uses are documented by qualified review. Architecture should support
both without treating either as permission.

## Evidence Required

- Current terms and source-authority review for candidate datasets/providers.
- Coverage, quality, rate, outage, attribution, caching, retention, export, and
  commercial-use comparison.
- Local/cloud threat, cost, and operational qualification.

## Required Authority

Product/data authority with qualified legal/licensing, risk, security,
operations, and commercial review.

## Decision Record and Promotion

Promote each accepted provider/use profile to an ADR or source register plus
licensing/attribution guidance and decision readiness.

## Dependent Planning Updates

Reconcile CAP-0012, CAP-0016, CAP-0024, CAP-0027, and any exports that include
market data.

## Planning History

- 2026-10-15: Captured as a shared gate for market-data-dependent capabilities.
