---
id: CAP-0013
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0012"]
decision_gates: ["DEC-0013"]
approval_model: cap-package-v1
slice_ids: ["SLI-0054", "SLI-0055", "SLI-0056", "SLI-0057"]
---

# Capability: Perform Financial and Quantitative Analysis

## Outcome

An individual learner can run bounded educational financial and quantitative
calculations, compare results, vary explicit assumptions, and reproduce every
result from versioned methods and traceable canonical inputs.

## Users and Value

Learners need calculations that teach method and limitations rather than hide
assumptions behind a number. Value is observable when the same method version,
inputs, units, calendar, and rounding policy reproduce the result and when
observed data remains distinguishable from calculation and interpretation.

## Scope

### In Scope

- A bounded initial method catalog for descriptive statistics, returns,
  compounding, risk measures, comparisons, and selected valuation concepts.
- Deterministic method/version, units, currency, calendar, missing-data,
  adjustment, rounding, assumption, and provenance contracts under DEC-0013.
- Learner-controlled scenarios and comparisons with reproducible result records
  and educational explanations and limitations.
- Accessible tables/charts plus export of inputs, assumptions, method identity,
  outputs, and provenance.

### Out of Scope

- Personalized valuation conclusions, recommendations, guarantees, tax/legal
  advice, execution, custody, or opaque model-computed financial facts.
- Portfolio transaction accounting, strategy backtests, or unbounded notebook
  and code execution.
- Treating missing or estimated data as observed without explicit labeling.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Data Architecture](../../architecture/data/data-architecture.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [CAP-0012](CAP-0012-explore-canonical-market-data.md)

## Decision Gates and Constraints

- DEC-0013 fixes ownership and the initial method, units, timing, adjustment,
  precision, reproducibility, and compatibility posture.
- Financial calculations are deterministic platform policy. AI may explain a
  recorded result but cannot supply authoritative numeric output.
- Every result identifies observed inputs separately from assumptions,
  transformations, simulated values, and generated interpretation.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0054 | A learner selects one reviewed method and sees required inputs, units, assumptions, method version, and educational limitations. | First after CAP-0012 and DEC-0013; establishes method catalog and validation. | Open-ended formulas, advice framing, or model-authored calculations changes the CAP package. | captured |
| SLI-0055 | The learner calculates a reproducible result from canonical observations and explicit assumptions with complete input and method provenance. | After SLI-0054. | Hidden defaults, nondeterministic arithmetic, or provider-specific calculation semantics changes the CAP package. | captured |
| SLI-0056 | The learner compares alternatives, varies assumptions, and exports a result bundle that distinguishes observed, calculated, simulated, and explanatory content. | After SLI-0055. | Portfolio bookkeeping, strategy execution, or suitability comparison changes the CAP package. | captured |
| SLI-0057 | The analysis flow is qualified against golden calculations, edge cases, units/currency/calendar policy, reproducibility, provenance, accessibility, and local/cloud parity. | Last; depends on SLI-0054 through SLI-0056. | Unbounded analytical execution or new regulatory claims changes the CAP package. | captured |

## Capability Acceptance

- Reviewed fixtures reproduce results across supported profiles and include
  invalid, boundary, missing-data, precision, calendar, and currency cases.
- Inputs, assumptions, transformations, method version, outputs, limitations,
  and provenance remain inspectable and portable.
- The application refuses unsupported combinations rather than silently
  guessing and never presents results as personalized advice.
- Accessible comparison and export behavior retains full semantic distinctions.

- Every slice includes focused failure and anti-rigidity tests; unsupported
  methods fail narrowly and do not make unrelated reviewed methods unusable.

## Risks and Non-Goals

Numerical polish can conceal weak assumptions or licensing gaps. This CAP is an
educational method workbench, not an adviser, forecasting oracle, portfolio
ledger, tax calculator, or arbitrary execution environment.

## Documentation Impact

Delivery will add method vocabulary, deterministic calculation contracts,
fixtures, assumption/provenance records, education-versus-advice guidance,
analysis UI behavior, exports, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 10 with manifest SLI-0054 through
  SLI-0057. DEC-0013 blocks CAP approval and delivery.

