# Context Pack: Financial Data

## Use When

Work affects instruments, market observations, provider ingestion, portfolios, valuation, backtests, features, or analytical data.

## Preserve

- Canonical records distinguish market/effective/retrieval time, currency, calendar, adjustment, quality, and provenance.
- Raw provider data is untrusted and does not enter portfolio or learning behavior directly.
- Financial calculations are deterministic and independently testable.
- Provider accessibility does not imply redistribution, commercial, caching, or training permission.
- PostgreSQL and analytical-storage responsibilities remain separate.

## Canonical Sources

- `docs/architecture/data/data-architecture.md`
- `docs/risk-compliance/market-data-licensing-and-attribution.md`
- `docs/standards/change-impact-matrix.md`

## Stop When

Provider permissions, corporate-action/adjustment policy, valuation semantics, or financial claims are unresolved.

