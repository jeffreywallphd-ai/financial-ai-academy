# ADR-0015: Market Data and Portfolio Ownership with a Method Registry

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0013](../planning/decision-requests/DEC-0013-financial-analysis-portfolio-and-backtest-semantics.md)

## Context

Canonical market data, educational calculations, simulated portfolios, and
backtests share time, units, currency, calendar, adjustment, precision,
missing-data, accounting, provenance, and reproducibility semantics. If each
feature owns private versions of those rules, equivalent inputs can produce
contradictory results and provider-specific behavior can leak into domain
meaning.

A dedicated Analysis module would provide one calculation owner, but there is
not yet evidence for an independent analysis lifecycle, persistence boundary,
availability requirement, or extraction need. Creating it now would invite an
unbounded analytics container and duplicate Market data and Portfolio authority.

## Decision

Keep financial semantics in two domain owners and one platform method registry:

- **Market data** owns canonical instruments, calendars, corporate actions,
  observations, coverage, quality, provider provenance, and normalization from
  untrusted provider payloads.
- **Portfolio** owns simulated accounts, cash and transaction ledgers,
  positions, valuation, benchmarks, performance and risk results, rebalancing,
  bounded strategy/scenario definitions, backtest runs, and simulation results.
- A **platform method registry** identifies reviewed reusable pure calculations
  by stable method ID and semantic version. It is a versioned catalog and
  dependency-free implementation seam, not a third business database, workflow
  owner, or generic Analysis module.

Each registered method declares one semantic owner, required input kinds and
units, output kinds and units, time/calendar and adjustment expectations,
missing-data behavior, precision and rounding policy, assumptions, limitations,
compatibility, deterministic reference fixtures, and provenance requirements.
A method implementation has no persistence, provider, network, clock, random,
AI, host, or adapter dependency. Stateful workflows call it with validated
values and record its exact version; the owning module retains authorization,
orchestration, persistence, and result meaning.

Cross-module consumers use an owning module's public application operation or a
versioned portable finance contract. They do not import another module's domain
or persistence internals. A registry entry does not transfer ownership of an
instrument, observation, portfolio, ledger, run, or result.

The initial semantic baseline is:

- canonical observations distinguish provider/source time, effective market
  time, retrieval time, as-of use, currency, calendar, adjustment policy,
  quality, and provenance;
- observed, assumed, transformed, calculated, and simulated values remain
  distinct in records and presentation;
- units, currency conversion, calendars, corporate-action handling, price
  selection, missing-data policy, precision, rounding, benchmark, fee, and
  slippage assumptions are explicit and versioned rather than hidden defaults;
- unsupported, stale, conflicting, unlicensed, or incomplete inputs fail
  explicitly and cannot silently alter prior valid results;
- simulated portfolio state derives reproducibly from append-oriented
  transactions and exact policy/input versions; valuation and performance are
  derived results, not mutable source truth;
- backtests and stress scenarios use a closed declarative grammar, exact
  datasets and method/accounting versions, explicit timing and cost rules, and
  look-ahead controls; partial or invalid runs do not become valid results; and
- AI may explain an already recorded result but cannot supply authoritative
  numeric output, accounting state, market facts, or simulation results.

PostgreSQL retains transactional portfolio and run metadata. Versioned market
history and large immutable analytical inputs or outputs use Parquet, with
DuckDB limited to bounded analysis. Store choice never changes semantic
ownership, and raw provider data never enters a calculation or portfolio path
before provider-neutral validation and normalization.

## Consequences

- Financial analysis can reuse exact reviewed methods without introducing an
  Analysis module or duplicating formulas in feature code.
- Market data and Portfolio retain clear business ownership and persistence
  isolation while sharing compatible method and portable-record contracts.
- Method governance must assign an owner and maintain compatibility, golden
  fixtures, independent expected results, and migration behavior across every
  version.
- Changing a method or policy produces a new version and lineage; it does not
  silently rewrite historical portfolio, valuation, or backtest results.
- The initial architecture favors deterministic breadth over arbitrary user
  formulas or execution. Adding a method is an additive reviewed registration,
  not a reason to require every provider, market, or portfolio feature.

## Alternatives Rejected

- **Create an Analysis domain module now.** Rejected because there is no
  independent lifecycle or extraction evidence and the boundary could become a
  generic analytics owner. Revisit only when multiple independent owners need
  durable analysis workflows or results with distinct scaling, availability,
  or release needs.
- **Place all calculations in Portfolio.** Rejected because reusable
  educational methods and market transformations should not require a simulated
  portfolio lifecycle.
- **Let each feature or provider define formulas.** Rejected because it creates
  incompatible results, hides assumptions, and leaks provider semantics.
- **Use notebooks, AI, or arbitrary code as production calculation authority.**
  Rejected because results would not have the deterministic, bounded, portable,
  and independently testable semantics required by the platform.

## Boundaries

This decision establishes ownership, the method-registry seam, and shared
deterministic semantic requirements. It does not select a market-data provider
or license, approve redistribution, define every initial formula or accounting
election, authorize arbitrary code, establish tax or regulatory reporting,
provide suitability or advice, connect a broker, or permit live/paper trading,
custody, or autonomous portfolio action.

Exact schemas and the first method set remain CAP and slice work. Any choice
whose meaning materially varies by market, jurisdiction, provider license,
accounting convention, or product claim must be explicit and may require a
separate decision or qualified review.

## Verification Implications

- Enforce Market data and Portfolio public surfaces, persistence isolation, and
  rejection of raw provider payloads outside adapters/normalization.
- Verify every registry entry has one semantic owner, a versioned contract,
  explicit units/time/adjustment/missing/precision policy, limitations,
  provenance, compatibility, and independent golden fixtures.
- Prove pure methods are deterministic and free of persistence, provider,
  network, clock, random, AI, host, and adapter dependencies.
- Prove append-oriented transaction replay reproduces cash, positions,
  valuation, benchmark, performance, and risk under exact input and policy
  versions, including currencies and corporate actions.
- Prove closed backtest/scenario runs reject look-ahead, unsupported actions,
  invalid calendars, stale/missing inputs, and partial publication while
  retaining exact dataset, method, accounting, cost, and environment lineage.
- Verify observed, assumed, calculated, and simulated values and educational
  limitations remain distinct in APIs, exports, and accessible interfaces.
- Qualify edge cases and failure behavior independently across supported local
  and cloud profiles without requiring unrelated providers or methods.

## Supersession

Creating an Analysis module, changing Market data or Portfolio ownership,
making a method registry stateful or externally executable, allowing provider
formulas to become domain authority, or adding live financial execution requires
a superseding decision. Adding or revising a method within the accepted seam
requires versioned contracts and evidence, not necessarily a new ADR.
