---
id: CAP-0012
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0024", "CAP-0026"]
decision_gates: ["DEC-0012", "DEC-0013"]
approval_model: cap-package-v1
slice_ids: ["SLI-0050", "SLI-0051", "SLI-0052", "SLI-0053"]
---

# Capability: Explore Canonical Market Data

## Outcome

An individual learner can retrieve, inspect, chart, compare, and export bounded
provider-neutral market observations while seeing coverage, timestamps,
currency, adjustment policy, quality, attribution, and provenance.

## Users and Value

Learners need reproducible data whose origin and limitations are visible before
using it in education or simulation. Value is observable when equivalent
canonical queries have stable meaning across admitted providers and raw payloads
never leak into downstream domain behavior.

## Scope

### In Scope

- Market-data-owned instrument, calendar, observation, corporate-action,
  quality, coverage, and provenance contracts selected by DEC-0013.
- Constrained provider admission and licensed uses selected by ADR-0020, including
  attribution, quota, retention, redistribution, and degraded behavior.
- Bounded query, compare, chart, tabular inspection, and permitted export with
  explicit source/effective/retrieval times and adjustment policy.
- Raw, canonical, derived, and published zone separation with accessible
  quality and limitation presentation.

### Out of Scope

- Trading, brokerage, real-time entitlement claims, suitability, price
  guarantees, or redistribution not explicitly licensed.
- Provider payloads as domain models, silent gap filling, portfolio accounting,
  valuation conclusions, or advice.
- Selecting a commercial provider without current terms review.

## Canonical Context

- [Data Architecture](../../architecture/data/data-architecture.md)
- [ADR-0015: Market Data and Portfolio Ownership with a Method Registry](../../adr/ADR-0015-market-data-portfolio-method-registry.md)
- [ADR-0020: Staged Market-Data Sourcing with Alpha Vantage First](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
- [Financial Method and Simulation Architecture](../../architecture/finance/financial-method-and-simulation-architecture.md)
- [Market-Data Licensing and Attribution](../../risk-compliance/market-data-licensing-and-attribution.md)
- [Module Map](../../architecture/modules/module-map.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0024](CAP-0024-connect-and-govern-replaceable-providers.md)
- [CAP-0026](CAP-0026-preserve-provenance-and-accountable-history.md)

## Decision Gates and Constraints

- ADR-0020 selects the staged hybrid and Alpha Vantage as the first narrow
  educational adapter. Technical access is never treated as license authority;
  every activated use still requires an exact current default-deny profile.
- ADR-0015 establishes Market data ownership, canonical instrument and
  observation meaning, calendars, adjustments, and consumer contracts.
- Raw provider data enters no learning, analysis, portfolio, or adaptation path
  before validation and provider-neutral normalization.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0050 | A learner searches the canonical instrument/coverage catalog and understands provider-neutral identity, availability, delay, attribution, and permitted use. | First after dependencies and both decisions; establishes canonical catalog and provider normalization. | Unreviewed provider use, live trading symbols as identity, or raw payload exposure changes the CAP package. | captured |
| SLI-0051 | The learner retrieves bounded observations with exact market/source/retrieval times, currency, calendar, adjustment, quality, and provenance. | After SLI-0050; establishes query and data-zone behavior. | Silent adjustment, fabricated gap filling, or absent lineage changes the CAP package. | captured |
| SLI-0052 | The learner compares and charts series and exports only license-permitted canonical data with retained query and provenance metadata. | After SLI-0051. | Advice, unrestricted redistribution, or downstream provider coupling changes the CAP package. | captured |
| SLI-0053 | The complete flow is qualified for normalization, calendars, adjustments, quality, license/attribution, quota/outage, export, accessibility, and local/cloud parity. | Last; depends on SLI-0050 through SLI-0052. | Portfolio accounting, a specific unapproved provider, or managed-cloud service claims changes the CAP package. | captured |

## Capability Acceptance

- Canonical records preserve source, effective-market, and retrieval times,
  currency, calendar, adjustment, quality, provider, and transformation lineage.
- Malformed, stale, unsupported, unlicensed, over-quota, or unavailable inputs
  fail boundedly without contaminating canonical history.
- Charts, comparisons, and exports distinguish observed, derived, and missing
  values and carry required attribution and restrictions.
- Contract, provider-conformance, data-quality, security, accessibility, and
  degraded-operation evidence covers every admitted path.

- Every slice includes focused failure and anti-rigidity tests so an unavailable
  provider, symbol class, or export right isolates only the affected path.

## Risks and Non-Goals

Market data can appear authoritative while being delayed, incomplete, adjusted,
or contractually restricted. This CAP does not promise real-time coverage,
grant redistribution rights, calculate portfolio results, or provide advice.

## Documentation Impact

Delivery will add market-data vocabulary, canonical schemas, provider
conformance, provenance, licensing/attribution, data-zone, query/export,
operations, accessibility, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 9 with manifest SLI-0050 through
  SLI-0053. DEC-0012 and DEC-0013 block CAP approval and delivery.
- 2026-10-15: DEC-0013 was promoted through ADR-0015; DEC-0012 remains an unresolved provider and licensed-use gate, so this CAP remains decision-blocked.
- 2026-10-16: DEC-0012 was promoted through ADR-0020. The CAP is no longer
  decision-blocked and returns to shaping for dependency and CAP-package
  readiness validation; no provider use outside an exact profile is authorized.

