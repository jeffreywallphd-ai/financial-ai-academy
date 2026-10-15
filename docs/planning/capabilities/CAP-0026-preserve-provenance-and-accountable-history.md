---
id: CAP-0026
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0106", "SLI-0107", "SLI-0108", "SLI-0109"]
---

# Capability: Preserve Provenance and Accountable History

## Outcome

Learners, authorized reviewers, and operators can trace the origin, version,
transformation, decision context, and integrity of learning evidence,
recommendations, content, market data, datasets, model output, simulations, and
administrative actions without Audit becoming a second business database.

## Users and Value

Users need to distinguish source facts from derived results and understand how a
state came to exist. Value is observable when each supported record can produce
a bounded provenance chain and accountable history that survives projection
rebuilds and provider replacement.

## Scope

### In Scope

- A platform provenance envelope and module-owned source/version/transformation
  references compatible across learning, finance, AI, project, and operator
  domains.
- Audit integrity references for security- and administration-relevant events,
  append behavior, idempotency, redaction, authorization, retention class, and
  exportable bounded views.
- Lineage traversal, incomplete-chain and tamper diagnostics, projection rebuild
  verification, and observed/calculated/simulated/predicted/generated labels.
- Reusable contracts and conformance kits that later CAPs extend without a
  central mutable provenance god object.

### Out of Scope

- Copying every domain record into Audit, blockchain or immutable-infrastructure
  claims, unlimited retention, legal compliance guarantees, or public disclosure.
- Defining provider licenses, tenant policy, business metrics, or domain rules.

## Canonical Context

- [Data Architecture](../../architecture/data/data-architecture.md)
- [Module Map](../../architecture/modules/module-map.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)

## Decision Gates and Constraints

- Owning modules retain authoritative business records. Audit stores bounded
  integrity/accountability references and cannot become a cross-module query
  database.
- External, derived, and generated records retain exact source, version,
  transformation, producer, time, status, and validation provenance appropriate
  to their type.
- Redaction and authorization apply to lineage views; provenance is not a reason
  to expose protected content or retain it indefinitely.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0106 | A consumer receives a versioned provider-neutral provenance envelope and bounded lineage for existing learning content and evidence. | First after CAP-0001; generalizes existing source/integrity patterns without changing ownership. | Centralizing business data or exposing protected payloads changes the CAP package. | captured |
| SLI-0107 | Financial, project, dataset, model, simulation, recommendation, and administrative owners can extend the envelope through conformance-tested typed references. | After SLI-0106; adapters may develop in parallel with owning CAPs. | Provider-specific lineage or a shared mutable aggregate changes the CAP package. | captured |
| SLI-0108 | Authorized users inspect accountable history, transformation chains, missing links, validation status, and tamper diagnostics with purpose-limited redaction/export. | After SLI-0107. | Unlimited audit access, compliance guarantees, or history mutation changes the CAP package. | captured |
| SLI-0109 | Provenance is qualified for idempotency, replay, projection rebuild, tamper/conflict, redaction, retention hooks, accessibility, scale bounds, and local/cloud semantics. | Last; depends on SLI-0106 through SLI-0108. | Selecting tenant retention, legal policy, or immutable infrastructure changes the CAP package. | captured |

## Capability Acceptance

- Every supported chain retains stable owner, source/version, transformation,
  producer/policy, time, validation, and integrity references without copying
  another module's authoritative state.
- Replay is idempotent, conflicts and broken links remain explicit, and
  projection rebuilds can verify exact source-set identity.
- Authorization and redaction prevent lineage from leaking protected content;
  retention/export are explicit and bounded.
- Cross-domain conformance, performance bounds, accessibility, and local/cloud
  semantics are directly verified.

- Every slice includes focused failure and anti-rigidity tests; an unknown or
  incomplete lineage adapter isolates that chain and does not serialize or
  disable unrelated domain records.

## Risks and Non-Goals

Provenance can become a universal database or an unverifiable immutability
claim. This CAP keeps facts with owners and does not promise blockchain,
unlimited retention, legal compliance, or universal public audit.

## Documentation Impact

Delivery will add provenance/audit vocabulary, envelopes and extension rules,
lineage/integrity/redaction/retention/export contracts, module adapters,
operations, accessibility, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 23 with manifest SLI-0106 through
  SLI-0109. The package awaits one CAP planning approval and provides an early
  cross-cutting dependency without forcing all domain slices into lockstep.

