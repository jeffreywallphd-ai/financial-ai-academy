# Context Pack: Financial Data

## Use When

Work affects instruments, market observations, provider ingestion, portfolios, valuation, backtests, features, or analytical data.

## Preserve

- Canonical records distinguish market/effective/retrieval time, currency, calendar, adjustment, quality, and provenance.
- Raw provider data is untrusted and does not enter portfolio or learning behavior directly.
- Financial calculations are deterministic and independently testable.
- Provider accessibility does not imply redistribution, commercial, caching, or training permission.
- PostgreSQL and analytical-storage responsibilities remain separate.
- Project may link to zero or more Portfolio-owned resources under ADR-0012, but it never owns or recalculates positions, transactions, valuation, performance, risk, or market-data provenance.
- ADR-0015 assigns canonical observations and normalization to Market data,
  simulated accounting/valuation/backtests to Portfolio, and reusable pure
  calculations to an owner-declared versioned platform method registry; it adds
  no Analysis module.
- ADR-0020 selects staged rights-profiled sourcing with Alpha Vantage as the
  first narrow educational adapter. Provider-neutral contracts, validated
  imports, synthetic fixtures, and default-deny profiles keep later providers
  additive and undocumented uses disabled.

## Canonical Sources

- `docs/architecture/data/data-architecture.md`
- `docs/risk-compliance/market-data-licensing-and-attribution.md`
- `docs/standards/change-impact-matrix.md`
- `docs/adr/ADR-0012-reusable-project-workspace.md`
- `docs/adr/ADR-0015-market-data-portfolio-method-registry.md`
- `docs/adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md`
- `docs/architecture/finance/financial-method-and-simulation-architecture.md`

## Stop When

Provider permissions, corporate-action/adjustment policy, valuation semantics, or financial claims are unresolved.

