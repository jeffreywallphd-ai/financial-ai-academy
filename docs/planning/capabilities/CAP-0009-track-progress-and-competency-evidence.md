---
id: CAP-0009
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0001", "CAP-0006"]
decision_gates: ["DEC-0009"]
approval_model: cap-package-v1
slice_ids: ["SLI-0038", "SLI-0039", "SLI-0040", "SLI-0041"]
---

# Capability: Track Progress and Competency Evidence

## Outcome

An individual learner can inspect an explainable, versioned view of completion,
attempt, feedback, and competency evidence, understand what each projection does
and does not establish, and identify supported review needs without losing the
append-oriented source history.

## Users and Value

Learners need one trustworthy account of work completed, evidence retained, and
areas needing review. Value is observable when every displayed state traces to
exact source evidence and deterministic projection policy rather than an opaque
score or mutable summary.

## Scope

### In Scope

- A Learner-model-owned progress projection over authorized Assessment,
  Project, Curriculum, and review evidence.
- Exact source references, version and policy identity, projection freshness,
  uncertainty, and rebuild behavior.
- Learner-visible history, strengths, review needs, and bounded competency or
  mastery language selected by DEC-0009.
- Accessible filtering, comparison, empty, stale, denied, and unavailable
  states with equivalent local/cloud semantics.

### Out of Scope

- Credentials, accreditation, employability or investment-competence claims.
- Adaptive ranking, automatic next-step selection, instructor overrides, cohort
  analytics, or model-authoritative mastery.
- Mutating or deleting Assessment, Project, Curriculum, or review evidence.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Initial Glossary](../../domain/glossary.md)
- [Module Map](../../architecture/modules/module-map.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [ADR-0014: Governed Adaptive-Learning Research Plane](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
- [ADR-0019: Append-Only Bounded Learner-Projection Overrides](../../adr/ADR-0019-append-only-bounded-projection-overrides.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)
- [CAP-0006](CAP-0006-practice-and-demonstrate-understanding.md)

## Decision Gates and Constraints

- Learner model owns derived progress; source modules retain their evidence and
  Audit retains integrity references rather than becoming a second business
  database.
- Completion does not silently become mastery. ADR-0014 requires a governed
  probabilistic estimate, deterministic publication policy, explicit
  uncertainty/freshness, abstention to evidence-only progress, and replayable
  correction behavior.
- Authorization, evidence inclusion, projection policy, and durable state
  changes are deterministic. AI output cannot create or override evidence.
- ADR-0019 leaves this CAP's reproducible base projection unchanged. A later
  CAP-0022 overlay must remain distinguishable and cannot become source evidence
  or model-training truth.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0038 | A learner receives one rebuildable progress timeline over exact authorized completion and practice evidence with source and version references. | First after CAP-0001 and CAP-0006; establishes evidence-query and projection contracts. | Copying source facts, hiding provenance, or making progress client-authoritative changes the CAP package. | captured |
| SLI-0039 | The learner sees bounded competency evidence, strengths, uncertainty, and review needs under the policy selected by DEC-0009. | After SLI-0038 and DEC-0009. | A model-authoritative mastery score, credential claim, or engagement-only measure changes the CAP package. | captured |
| SLI-0040 | The learner filters and compares evidence over time and follows exact review references without altering source history. | After SLI-0039; may consume later project/reviewer evidence through versioned optional adapters. | Adaptive ranking, instructor override, or evidence deletion changes the CAP package. | captured |
| SLI-0041 | The complete progress experience is qualified for replay, stale and conflicting evidence, authorization, explanation, accessibility, and local/cloud semantic parity. | Last; depends on SLI-0038 through SLI-0040. | Certification, cohort analytics, managed-cloud recovery, or new evidence authority changes the CAP package. | captured |

## Capability Acceptance

- Every displayed state reproduces from exact, authorized, versioned source
  evidence and reports projection policy and freshness.
- Missing, malformed, stale, cross-learner, or unauthorized evidence fails
  closed without rewriting valid history.
- Competency language and uncertainty conform to DEC-0009 and never overstate
  completion, score, or model inference.
- Projection rebuilds are deterministic and learner views meet keyboard,
  focus, contrast, zoom, responsive, forced-color, and theme requirements.

- Every slice includes focused failure and anti-rigidity tests proving that an
  unavailable unrelated evidence adapter does not block its bounded outcome.

## Risks and Non-Goals

The main risk is compressing heterogeneous evidence into an unjustified single
score. This CAP preserves source-specific meaning and does not create
credentials, predictions, cohort surveillance, or adaptive authority.

## Documentation Impact

Delivery will refine learner-state and competency vocabulary, projection and
portable-record contracts, module boundaries, evidence traceability,
accessibility behavior, architecture verification, and known gaps.

## Planning History

- 2026-10-15: Shaped from catalog candidate 6 with the complete provisional
  manifest SLI-0038 through SLI-0041. DEC-0009 blocks CAP approval and delivery.
- 2026-10-15: DEC-0009 was promoted through ADR-0014; the CAP returned to shaping for package revalidation before CAP-level approval.
- 2026-10-15: ADR-0019 preserved this CAP's base projection as immutable and
  assigned any effective instructor overlay to later CAP-0022.

