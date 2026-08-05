---
id: CAP-0001
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-08-04
parent: null
depends_on: []
decision_gates: []
---

# Capability: Complete a Structured Introductory Lesson

## Outcome

An individual learner can complete one versioned introductory financial-learning lesson, receive deterministic feedback on an embedded knowledge check, resume the activity, and review retained evidence of the attempt and completion.

## Users and Value

The primary user is an individual learner beginning a structured financial-learning pathway. The capability provides the first complete learning loop: engage with approved educational material, demonstrate understanding, and return later without losing the evidence of work already completed.

Value is observable when a learner can reopen the same lesson and see an accurate, explainable completion state derived from append-oriented evidence tied to the exact lesson and assessment versions.

## Scope

### In Scope

- Access one approved, versioned introductory lesson in a defined curriculum context.
- Present structured educational content, source attribution, examples, and one bounded knowledge check.
- Score the knowledge check through deterministic assessment rules and provide understandable feedback.
- Record append-oriented attempt, response, score, and completion evidence with timestamps and content-version provenance.
- Derive and display a minimal completion state without making a mastery prediction.
- Resume or reopen the lesson and review the retained attempt and completion evidence.
- Preserve shared domain and contract semantics for community and managed-cloud profiles.
- Provide equivalent accessible behavior in light, dark, and system themes when a learner interface is delivered.

### Out of Scope

- Curriculum search, enrollment, broad prerequisite navigation, or individualized pathway recommendations.
- Content authoring, review, publication workflows, package import/export tooling, or external learning-standard interoperability.
- Complex assessments, instructor review, manual grading, overrides, credentials, or certification.
- Mastery estimation, competency projection, adaptive ranking, experiments, or engagement optimization.
- AI tutoring, generated lesson content, model-provider selection, or AI-authored grading.
- Market data, valuation, portfolio simulation, backtesting, financial AI/ML labs, or investment recommendations.
- Organization tenancy, cohort management, enterprise identity, billing, or managed-cloud operations.
- Comprehensive learner-record export, backup products, or recovery guarantees.
- Brokerage, trade execution, custody, suitability decisions, or personalized financial advice.

## Canonical Context

- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Product Capability Catalog](../../product/capability-catalog.md)
- [Community and Commercial Editions](../../product/community-and-commercial-editions.md)
- [Initial Glossary](../../domain/glossary.md)
- [Initial Module Map](../../architecture/modules/module-map.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Local and Cloud Capability Parity](../../architecture/deployment/local-cloud-capability-parity.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [Interface Design System](../../design/README.md)
- [Interface Design Standards](../../standards/interface-design-standards.md)
- [Decision Readiness](../../adr/decision-readiness.md)

## Decision Gates and Constraints

- **Resolved by [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) — learning module ownership:** preserve distinct Content, Curriculum, Assessment, Learner model, and Audit ownership for the first loop.
- **Resolved by [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md) — learner identity:** use one setup-selected identity adapter behind the accepted provider-neutral learner-context contract.
- **Resolved by [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) — versioned lesson package:** preserve the platform-owned directory package, immutable semantic versions and digest, constrained CommonMark, declared assets, and Assessment ownership.
- **Resolved by [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) — community evidence protection and recovery:** preserve the private-host boundary, coordinated user-invoked recovery set, empty-target restore, restored-session/recovery revocation, and no community RPO/RTO claim.
- Assessment scoring, completion eligibility, authorization, and durable state changes remain deterministic. AI output cannot supply or override them.
- Learning evidence remains append-oriented; displayed completion is a projection and must not replace or silently rewrite its source evidence.
- Completing the lesson must not be described as mastery, certification, investment competence, or evidence of expected investment performance.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies | Planning status |
| --- | --- | --- | --- |
| Candidate A | A learner opens one approved, versioned introductory lesson and can identify its objectives, sources, and version. | Accepted ADR-0007 content-package contract | proposed |
| Candidate B | A learner submits one deterministic knowledge check and receives feedback while append-oriented attempt and score evidence is retained. | Candidate A | proposed |
| Candidate C | A learner closes and reopens the lesson and sees an accurate completion state and evidence history derived from the retained evidence. | Candidate B; ADR-0008 boundary and later executable recovery qualification where recovery claims are delivered | proposed |

These are candidates only. No slice is selected or approved by this capability artifact.

## Capability Acceptance

The capability is acceptable when evidence demonstrates that:

- an authorized individual learner can open the intended lesson and see its objectives, educational sources, and version;
- the learner can submit the bounded knowledge check and receive deterministic, reproducible scoring and feedback;
- attempt, response, score, and completion evidence records the learner context, activity and assessment versions, time, and provenance required by accepted contracts;
- closing and reopening the experience reproduces the correct completion view from retained evidence without claiming mastery;
- malformed responses, missing learner context, unauthorized access, duplicate submissions, and stale content versions fail safely without creating false completion evidence;
- local and managed-cloud profiles can use the same domain rules, application behavior, contract versions, and evidence meaning;
- delivered interfaces preserve equivalent content and actions in light and dark modes and meet applicable keyboard, focus, contrast, zoom, responsive, and assistive-technology expectations; and
- no part of the experience presents educational completion or feedback as personalized financial advice, certification, or an investment-performance claim.

## Risks and Non-Goals

- Implementation could broaden ADR-0007's package, markup, media, or assessment profile without the required compatibility and security review.
- Persisting evidence outside ADR-0008's accepted protection boundary or presenting unqualified backup/restore behavior as supported could create false privacy, deletion, or recovery expectations.
- Combining content, assessment evidence, and completion projection in one implementation boundary would violate ADR-0005.
- Treating completion as mastery would collapse evidence and learner-state semantics and overstate what one knowledge check establishes.
- Expanding the first capability into adaptive recommendations, AI tutoring, broad curriculum management, or financial tools would obscure the bounded learning outcome.
- Example financial material must remain educational and sourceable; it must not include personalized buy, sell, hold, or suitability recommendations.

## Documentation Impact

Delivery slices are expected to refine the applicable domain rules for learning activities and evidence; accepted module ownership; learning and assessment contracts; content versioning; identity and security decisions; interface behavior; verification maps; and local/cloud qualification guidance. Derived context packs must be updated only after their canonical sources change.

## Planning History

- 2026-08-04: Capability shaped from the proposed product capability catalog.
- 2026-08-04: Decision-gate review classified four readiness areas and created DEC-0001 through DEC-0004.
- 2026-08-04: ADR-0005 established the first-loop module ownership boundary.
- 2026-08-04: ADR-0006 established the setup-selectable learner-identity boundary.
- 2026-08-04: ADR-0007 and the content-package contract established the versioned lesson-package boundary. CAP-0001 remains decision-blocked only by DEC-0004.
- 2026-08-04: ADR-0008 established the community learner-evidence protection and recovery boundary. All named capability decision gates are resolved, and CAP-0001 moved to `ready` for vertical-slice selection.
