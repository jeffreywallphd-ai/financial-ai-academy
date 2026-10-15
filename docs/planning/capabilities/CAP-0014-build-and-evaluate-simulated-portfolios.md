---
id: CAP-0014
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0012", "CAP-0013"]
decision_gates: ["DEC-0013"]
approval_model: cap-package-v1
slice_ids: ["SLI-0058", "SLI-0059", "SLI-0060", "SLI-0061"]
---

# Capability: Build and Evaluate Simulated Portfolios

## Outcome

An individual learner can create an educational simulated portfolio, record
allocations and transactions, choose a benchmark, rebalance under explicit
policy, inspect reproducible performance and risk measures, and record decisions
without implying custody, live execution, suitability, or guaranteed outcomes.

## Users and Value

Learners need a safe accounting model for practicing portfolio concepts and
connecting decisions to evidence. Value is observable when holdings and results
reconcile from append-oriented transactions, canonical prices, and deterministic
policies with clear simulation labels and limitations.

## Scope

### In Scope

- Portfolio-owned simulated account, cash, position, transaction, allocation,
  benchmark, valuation, rebalance, decision, and result semantics selected by
  DEC-0013.
- Deterministic accounting, currency, price-selection, calendar, corporate
  action, fee/slippage assumption, rounding, and error behavior.
- Learner-controlled create/edit/snapshot flows and typed Project references
  that do not transfer Portfolio authority.
- Accessible holdings, allocation, performance, risk, provenance, limitation,
  empty, stale, and unavailable views.

### Out of Scope

- Brokerage, custody, live orders, suitability, personalized recommendations,
  guarantees, tax lots for legal reporting, or autonomous rebalancing.
- Raw provider data, model-authoritative accounting, historical strategy
  backtests, or managed execution.
- Project ownership of portfolio state.

## Canonical Context

- [Module Map](../../architecture/modules/module-map.md)
- [Data Architecture](../../architecture/data/data-architecture.md)
- [Reusable Project Workspace](../../adr/ADR-0012-reusable-project-workspace.md)
- [Product Non-Goals](../../product/non-goals.md)
- [CAP-0012](CAP-0012-explore-canonical-market-data.md)
- [CAP-0013](CAP-0013-perform-financial-and-quantitative-analysis.md)

## Decision Gates and Constraints

- DEC-0013 establishes Portfolio ownership and deterministic transaction,
  valuation, benchmark, performance, and risk semantics.
- Portfolio consumes canonical market data and platform-owned calculation
  methods; it never reads raw provider payloads or delegates accounting to AI.
- Project links retain stable references and provenance only; Portfolio remains
  independently authoritative.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0058 | A learner creates a simulated portfolio, records cash and allocations, and sees reconciled positions under exact accounting policy. | First after dependencies and DEC-0013; establishes portfolio ledger contracts. | Custody, live brokerage, Project-owned state, or model accounting changes the CAP package. | captured |
| SLI-0059 | The learner values holdings against exact canonical observations and benchmark inputs with quality, freshness, currency, and provenance. | After SLI-0058 and CAP-0012. | Raw provider pricing, silent stale substitution, or hidden FX policy changes the CAP package. | captured |
| SLI-0060 | The learner rebalances through simulated transactions and inspects performance, risk, assumptions, and decision history without suitability claims. | After SLI-0059 and CAP-0013. | Automated execution, advice, guarantee, or backtest strategy engine changes the CAP package. | captured |
| SLI-0061 | Portfolio behavior is qualified for accounting invariants, corporate actions, currencies, benchmark/risk methods, replay, provenance, accessibility, and failure recovery. | Last; depends on SLI-0058 through SLI-0060. | Live integration, tax reporting, or managed execution changes the CAP package. | captured |

## Capability Acceptance

- Append-oriented simulated transactions reproduce cash, positions, valuation,
  benchmark, performance, and risk under exact policy versions.
- Missing, stale, conflicting, or unsupported market inputs fail explicitly and
  never mutate prior valid portfolio history.
- Every view and export distinguishes simulation, observed prices, calculated
  values, assumptions, and generated explanation.
- Project references, accessibility, security, and shared local/cloud semantics
  are verified without implying live financial authority.

- Every slice includes focused failure and anti-rigidity tests so one missing
  metric, benchmark, or data series does not lock unrelated portfolio work.

## Risks and Non-Goals

Simulation can be mistaken for a real account or forecast. This CAP does not
hold assets, execute trades, determine suitability, promise performance, or
silently approximate missing financial facts.

## Documentation Impact

Delivery will add portfolio/accounting vocabulary, contracts and fixtures,
market-data consumption policy, project-link behavior, simulation labeling,
security, UI, export, operations, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 11 with manifest SLI-0058 through
  SLI-0061. DEC-0013 blocks CAP approval and delivery.

