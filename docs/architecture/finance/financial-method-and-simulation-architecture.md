# Financial Method and Simulation Architecture

- Status: accepted
- Canonical for: financial calculation ownership, method registration, and simulation boundaries
- Related ADR: [ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md)

## Ownership

| Concern | Owner | Boundary |
| --- | --- | --- |
| Instruments, observations, calendars, corporate actions, coverage, quality, normalization, and provider provenance | Market data | Raw provider payloads remain untrusted adapter input and never become domain or calculation records. |
| Simulated accounts, transactions, cash, positions, valuation, benchmarks, performance/risk results, scenarios, backtests, and simulation results | Portfolio | State derives from exact canonical inputs and versioned deterministic policy; no custody, live execution, or suitability. |
| Reusable pure calculations | Platform method registry with one declared semantic owner per method | Registry entries are versioned, dependency-free, stateless calculation seams rather than a domain workflow or persistence owner. |
| Projects that refer to portfolios or results | Project | Typed references and retained provenance do not transfer Portfolio state or calculation authority. |

## Method Contract

Every registered method declares:

- a stable method ID, semantic version, and semantic owner;
- input and output kinds, units, currency behavior, and validation bounds;
- market/effective/retrieval/as-of time expectations, calendar, adjustment,
  missing-data, precision, and rounding policy;
- assumptions, limitations, compatibility posture, and provenance fields;
- deterministic golden and edge-case fixtures with independently reviewed
  expected results.

The method implementation is pure: no persistence, provider SDK, network,
clock, random source, AI call, host, or adapter. Application workflows validate
inputs, invoke the exact method version, and persist the result and lineage in
the owning module. Unsupported combinations fail explicitly.

## Simulation Contract

Portfolio transaction history is append-oriented source state. Cash, positions,
valuation, benchmark comparison, performance, and risk are reproducible derived
results tied to exact transaction, observation, method, and policy versions.
Corrections append or supersede through explicit domain behavior; they do not
silently rewrite retained results.

Backtests and scenarios consume a closed declarative definition, canonical
versioned inputs, the same applicable Portfolio accounting and method versions,
explicit timing/cost/slippage/benchmark assumptions, and look-ahead controls.
Observed, assumed, calculated, and simulated values remain distinguishable.
Invalid or partial runs never publish a valid result.

## Data and Dependency Direction

Market data normalizes external observations before publishing a public
contract. Portfolio and educational analysis consume that public contract and
registered methods; they never read Market data persistence or raw provider
payloads. PostgreSQL owns transactional portfolio and run metadata, Parquet
owns large immutable analytical history and results, and DuckDB performs bounded
analysis over those files. Store placement does not transfer semantic ownership.

Cross-module calls use public application operations or versioned portable
finance records. The web application uses generated public clients. Provider-
specific types, formulas, terms, and error shapes remain inside adapters.

## Safety and Claims

All numerical production behavior is deterministic platform policy. AI may
explain a recorded result but cannot create authoritative market facts,
accounting state, valuation, backtest output, or financial decisions. Interfaces
and exports label simulations, assumptions, data periods, costs, limitations,
and provenance and do not claim advice, suitability, prediction, or guaranteed
performance.

## Evolution

Additive reviewed methods can enter the registry independently when their
contracts and fixtures are complete. A separate Analysis module is reconsidered
only with evidence for an independent durable result lifecycle, ownership,
scaling, availability, or extraction need. Arbitrary execution, provider-owned
calculation semantics, or live financial action requires a new decision.
