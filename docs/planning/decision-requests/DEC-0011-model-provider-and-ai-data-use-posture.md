---
id: DEC-0011
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

# Decision Request: Set the Model-Provider and AI Data-Use Posture

## Decision Needed

Choose the initial admitted model-provider classes and data-use policy for local
and external models, including capabilities, retention, redaction, consent,
cost, safety, logging, disablement, and fallback.

## Why Now

Grounded tutoring, AI/ML experiments, provider governance, local operation, and
usage administration cannot safely send learner or licensed data to a model
without a reviewed posture.

## Current Authority and Constraints

All model access uses platform-owned ports; provider-specific types stay out of
domains; models have no authority over grades, eligibility, financial facts,
permissions, or durable state; sensitive inputs require redaction/retention
controls and deterministic fallback.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Explicit per-provider opt-in with local and external adapters | Supports community choice and cloud capability while requiring declared data classes, no-training/retention terms, redaction, quotas, and disablement per adapter. | Higher conformance and terms-review burden; capability varies by provider. | Model manifest/port, consent, execution record, secret/config, cost/usage, evaluation, outage behavior. | Medium-high; adapters can be disabled while records preserve provider/version. |
| B. Local-model-only initial posture | Minimizes external data transfer and provider terms exposure. | Hardware variability, weaker capability, larger support burden, and no managed external baseline. | Local runtime/provider contract, capability discovery, support and performance qualification. | High; external adapters can be admitted later. |

## Recommendation

Option A with no provider enabled by default in community, explicit setup-time
selection, per-data-class permission, and a deterministic no-model fallback.
Final provider admission still requires current terms and security evidence.

## Evidence Required

- Current provider terms/data-use/cost comparison and local-model feasibility.
- Threat model for prompts, retrieval, output, secrets, and logs.
- Redaction/retention/consent policy and conformance/evaluation corpus.
- Cost, latency, outage, disablement, and safe-fallback qualification.

## Required Authority

Product and AI/ML authority with privacy/security, legal/provider-terms,
operations, cost, and education-risk review.

## Decision Record and Promotion

Promote the accepted posture to an ADR, AI/ML governance, provider contracts,
security guidance, and decision readiness.

## Dependent Planning Updates

Reconcile CAP-0011, CAP-0016, CAP-0024, CAP-0027, and CAP-0029.

## Planning History

- 2026-10-15: Captured as a shared gate for model-dependent catalog outcomes.

