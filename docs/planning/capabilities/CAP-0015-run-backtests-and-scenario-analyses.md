---
id: CAP-0015
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0012", "CAP-0013", "CAP-0014"]
decision_gates: ["DEC-0013"]
approval_model: cap-package-v1
slice_ids: ["SLI-0062", "SLI-0063", "SLI-0064", "SLI-0065"]
---

# Capability: Run Backtests and Scenario Analyses

## Outcome

An individual learner can define a bounded historical strategy or stress
scenario, run a reproducible simulation over exact inputs and assumptions,
inspect results and limitations, and compare runs without confusing simulation
with observed performance or a forecast.

## Users and Value

Learners need a disciplined way to test hypotheses and understand sensitivity,
data leakage, timing, and transaction assumptions. Value is observable when a
run is fully reproducible and invalid or biased configurations are visible
rather than silently accepted.

## Scope

### In Scope

- Portfolio-owned versioned strategy/scenario definitions, run records,
  assumptions, datasets, code/method identity, results, and limitations under
  DEC-0013.
- A bounded initial non-executable strategy grammar and deterministic historical
  and stress engines using canonical data and portfolio accounting.
- Transaction cost, slippage, timing, benchmark, corporate-action, missing-data,
  and look-ahead controls.
- Accessible setup, progress, result comparison, provenance, export, and failure
  behavior.

### Out of Scope

- Arbitrary code/notebook/plugin execution, live or paper trading, optimization
  sold as prediction, guarantees, advice, or provider-specific strategy APIs.
- Model-authored authoritative inputs or results.
- Treating simulated returns as observed portfolio performance.

## Canonical Context

- [Initial Glossary](../../domain/glossary.md)
- [Data Architecture](../../architecture/data/data-architecture.md)
- [ADR-0015: Market Data and Portfolio Ownership with a Method Registry](../../adr/ADR-0015-market-data-portfolio-method-registry.md)
- [Financial Method and Simulation Architecture](../../architecture/finance/financial-method-and-simulation-architecture.md)
- [Inert Applied-Project Artifacts](../../adr/ADR-0011-inert-applied-project-artifacts.md)
- [CAP-0012](CAP-0012-explore-canonical-market-data.md)
- [CAP-0013](CAP-0013-perform-financial-and-quantitative-analysis.md)
- [CAP-0014](CAP-0014-build-and-evaluate-simulated-portfolios.md)

## Decision Gates and Constraints

- ADR-0015 establishes Portfolio ownership of backtests/scenarios and their
  timing, accounting, reproducibility, result, and compatibility semantics.
- The initial engine consumes a closed declarative grammar; executable project
  artifacts remain inert under ADR-0011.
- Financial calculations, accounting, validation, and durable run state are
  deterministic; AI output cannot override them.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0062 | A learner defines a bounded versioned strategy or stress scenario and sees required data, timing, costs, assumptions, and known limitations before running it. | First after dependencies and DEC-0013. | Arbitrary execution, provider strategy payloads, or hidden defaults changes the CAP package. | captured |
| SLI-0063 | The learner runs a deterministic simulation that records exact data, portfolio/accounting, method, and environment provenance and rejects leakage or invalid timing. | After SLI-0062. | Live execution, model-authoritative computation, or unverifiable run state changes the CAP package. | captured |
| SLI-0064 | The learner compares runs, inspects risk and sensitivity, and exports results clearly labeled as simulation with limitations. | After SLI-0063. | Prediction or guarantee claims, observed/simulated conflation, or advice changes the CAP package. | captured |
| SLI-0065 | Backtest/scenario behavior is qualified for reproducibility, leakage, timing, corporate actions, costs, failures, provenance, accessibility, and local/cloud parity. | Last; depends on SLI-0062 through SLI-0064. | Managed arbitrary execution or production trading changes the CAP package. | captured |

## Capability Acceptance

- Identical approved inputs and versions reproduce run outputs and digests;
  changed data, method, or assumption produces explicit new lineage.
- Look-ahead, missing data, unsupported actions, stale prices, invalid calendars,
  and partial runs are denied or visibly bounded.
- Results and exports distinguish observations, calculations, simulations,
  assumptions, and generated interpretation.
- Golden, metamorphic, failure, security, accessibility, and portability tests
  cover the complete closed grammar and run lifecycle.

- Every slice includes focused failure and anti-rigidity tests; closed strategy
  extensions remain additive and unrelated scenarios do not require a global
  runtime or full provider set.

## Risks and Non-Goals

Backtests invite overfitting and hindsight bias. This CAP teaches those limits;
it does not execute arbitrary code, optimize for guaranteed returns, place
orders, or produce personalized investment recommendations.

## Documentation Impact

Delivery will add scenario/backtest vocabulary, declarative schemas, run and
result contracts, leakage and limitation guidance, reproducibility/export,
security, operations, UI, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 12 with manifest SLI-0062 through
  SLI-0065. DEC-0013 blocks CAP approval and delivery.
- 2026-10-15: DEC-0013 was promoted through ADR-0015; the CAP returned to shaping for package revalidation before CAP-level approval.
