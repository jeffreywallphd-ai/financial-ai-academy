---
id: DEC-0013
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0015-market-data-portfolio-method-registry.md
---

# Decision Request: Establish Financial Analysis, Portfolio, and Backtest Semantics

## Decision Needed

Choose module ownership and the initial deterministic semantic baseline for
canonical instruments/observations, reusable financial methods, simulated
portfolio accounting/valuation, and historical or stress simulation.

## Why Now

CAP-0012 through CAP-0015 share timing, units, currency, calendars, adjustments,
precision, missing-data, accounting, and reproducibility rules. Allowing each
feature to invent them would create contradictory results and provider leakage.

## Current Authority and Constraints

Market data and Portfolio are proposed module boundaries; PostgreSQL owns
transactions, Parquet analytical history, DuckDB bounded analysis; raw provider
data must be normalized; deterministic policy owns financial calculations; no
live trading, custody, suitability, or guaranteed outcomes are allowed.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Market data and Portfolio owners plus a platform method registry | Keeps observations with Market data, transactions/valuation/simulations with Portfolio, and shares versioned pure calculation methods without a new domain module. | Method governance spans owners and needs strict dependency rules. | Module map, finance schemas, method/version contracts, storage split, fixtures and API ownership. | Medium-high while contracts are versioned. |
| B. Add an Analysis module for reusable methods and results | Clear owner for calculations reused outside Portfolio and explicit analytical result lifecycle. | Adds a boundary before extraction evidence and risks a generic analytics god module. | Module map/ADR, analysis contracts, events, persistence and dependencies. | Medium; later consolidation/extraction requires migrations. |

## Recommendation

Option A for the initial modular monolith. Use dependency-free pure method
components and versioned contracts; revisit a distinct Analysis module only when
multiple owners and lifecycle evidence justify it.

## Evidence Required

- Initial method/accounting semantic specification and golden fixtures.
- Boundary prototype covering data normalization through portfolio/backtest.
- Calendar, currency, corporate-action, precision, missing-data, timing,
  cost/slippage, benchmark, and failure review.
- Architecture fitness rules preventing cross-module persistence access.

## Required Authority

Product/domain finance authority with architecture, data, risk, testing, and
operations review.

## Decision Record and Promotion

[ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md)
establishes Option A: Market data and Portfolio remain the domain owners, while
a versioned dependency-free platform method registry provides reusable pure
calculations without introducing an Analysis module.

## Dependent Planning Updates

Reconcile CAP-0012, CAP-0013, CAP-0014, and CAP-0015 before CAP approval.

## Planning History

- 2026-10-15: Captured while shaping the financial and analytical catalog lane.
- 2026-10-15: ADR-0015 established Market data and Portfolio ownership with a versioned platform method registry and no initial Analysis module.

