---
id: CAP-0011
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0018", "CAP-0020", "CAP-0024"]
decision_gates: ["DEC-0011"]
approval_model: cap-package-v1
slice_ids: ["SLI-0046", "SLI-0047", "SLI-0048", "SLI-0049"]
---

# Capability: Learn with Grounded AI Assistance

## Outcome

An individual learner can ask for assistance grounded in approved educational
sources, inspect citations and limitations, control whether assistance is used,
and recover safely when retrieval or model service is unavailable without AI
becoming grading, financial, authorization, or durable-state authority.

## Users and Value

Learners gain contextual explanation and question support while retaining a
clear line between sourced educational material and generated interpretation.
Value is observable when claims are traceable, unsupported output is contained,
and deterministic learning flows remain usable without a model.

## Scope

### In Scope

- AI-orchestration-owned retrieval, model invocation, validation, citation, and
  execution records behind platform-owned provider ports.
- Learner-controlled assistance preferences, disclosure, bounded conversation
  retention, redaction, quotas/cost visibility, safe fallback, and disablement.
- Grounding only in approved, versioned educational sources permitted by the
  provider/data-use posture selected in DEC-0011.
- Accessible answer, source, limitation, refusal, unavailable, and degraded
  experiences.

### Out of Scope

- Authoritative grading, mastery, eligibility, authorization, financial
  calculations, advice, suitability, portfolio action, or content publication.
- Hidden prompt/provider coupling, unrestricted web retrieval, autonomous tools,
  or sending learner data to an unapproved model.
- Claims of correctness or equivalent local/cloud model capability.

## Canonical Context

- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [AI/ML Governance](../../ai-ml/README.md)
- [ADR-0013: Explicit Model-Provider Opt-In](../../adr/ADR-0013-explicit-model-provider-opt-in.md)
- [Product Non-Goals](../../product/non-goals.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0018](CAP-0018-set-learning-goals-and-preferences.md)
- [CAP-0020](CAP-0020-understand-platform-methods-and-limitations.md)
- [CAP-0024](CAP-0024-connect-and-govern-replaceable-providers.md)

## Decision Gates and Constraints

- All model access passes through AI orchestration; domain modules import no
  provider SDK, prompt, model name, response, or billing type.
- ADR-0013 permits local and external provider classes only through explicit
  per-provider opt-in and per-data-class permission. No community provider is
  enabled by default, and each concrete adapter still requires current terms,
  security, capability, cost, and conformance evidence before admission.
- Deterministic learning behavior and source access remain authoritative; model
  output is versioned, validated, observable input only.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0046 | A learner explicitly opens assistance for one approved context and sees source scope, data-use disclosure, capability limits, and current preference before any invocation. | First after dependencies and DEC-0011; establishes consent, request, and provider-neutral execution contracts. | Implicit data transfer, unrestricted retrieval, or provider-specific domain types changes the CAP package. | captured |
| SLI-0047 | The learner receives a validated grounded response with exact citations, generated-content labeling, limitations, and a durable redacted execution record. | After SLI-0046; adds retrieval and model orchestration. | Uncited authority, grading/advice output, or storing unredacted sensitive prompts changes the CAP package. | captured |
| SLI-0048 | The learner continues or clears bounded conversation context and receives safe refusal, disablement, quota, timeout, and deterministic fallback behavior. | After SLI-0047; depends on preference and provider health contracts. | Autonomous tools, hidden retention, or essential-flow dependence on a model changes the CAP package. | captured |
| SLI-0049 | Assistance is qualified for grounding, citation integrity, injection and leakage resistance, provider failure, redaction, cost controls, accessibility, and local/cloud capability honesty. | Last; depends on SLI-0046 through SLI-0048. | General agent execution or authoritative model action changes the CAP package. | captured |

## Capability Acceptance

- Every invocation is learner-controlled, policy-authorized, provider-neutral,
  versioned, bounded, redacted, observable, and tied to permitted source inputs.
- Citations resolve to exact approved sources; unsupported, unsafe, or malformed
  output is refused or clearly contained without changing protected state.
- Model and retrieval failure leaves deterministic learning flows available and
  reports capability differences honestly.
- Security, evaluation, accessibility, theme, responsive, and cost evidence
  covers direct success plus adversarial and degraded cases.

- Every slice includes focused failure and anti-rigidity tests proving that
  absent model capability degrades locally without blocking deterministic
  learning flows.

## Risks and Non-Goals

Grounded output can still be wrong or manipulated. This CAP does not create a
general agent, execute tools, replace educational sources, grade learners, or
provide personalized financial advice.

## Documentation Impact

Delivery will add AI execution, retrieval, citation, evaluation, redaction,
retention, preference, provider, UI, security, operations, and known-gap
documentation with exact versioned contracts.

## Planning History

- 2026-10-15: Shaped from catalog candidate 8 with manifest SLI-0046 through
  SLI-0049. DEC-0011 blocks CAP approval and delivery.
- 2026-10-15: DEC-0011 was promoted through ADR-0013; the CAP returned to shaping for package revalidation before CAP-level approval.
