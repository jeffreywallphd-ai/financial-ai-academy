---
id: CAP-0006
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0026", "SLI-0027", "SLI-0028", "SLI-0029"]
---

# Capability: Practice and Demonstrate Understanding

## Outcome

An individual learner can complete repeatable diagnostic and formative
financial-learning questions, bounded scenarios, and structured exercises,
receive deterministic source-backed feedback and targeted review guidance, and
inspect append-oriented evidence for every attempt without the system claiming
mastery or delegating grading authority to AI.

## Users and Value

Learners need more than one embedded lesson check to practice concepts, discover
gaps, review relevant material, and try again. Value is observable when a
learner can understand how an answer was evaluated, see what evidence was
retained, follow a deterministic review route, and make another attempt without
the previous result being overwritten.

Authors and instructors benefit indirectly from versioned assessment semantics
and evidence that later review workflows can consume without sharing private
module persistence or inventing a second grading authority.

## Scope

### In Scope

- Platform-owned versioned definitions for a bounded initial set of structured
  diagnostic and formative questions, scenario decisions, and exercises whose
  responses can be validated and scored deterministically.
- Assessment-owned attempt lifecycle, response validation, scoring, feedback,
  targeted review references, retry policy, completion evidence, and immutable
  provenance tied to exact content and assessment versions.
- Learner-controlled practice sessions that may be interrupted and resumed,
  with idempotent submission, explicit in-progress/submitted states, and no
  silent replacement of prior attempts.
- Deterministic feedback that explains the applied rule, identifies approved
  review material, and clearly distinguishes formative practice from formal
  certification, financial advice, or mastery.
- Attempt history and bounded Learner-model practice/completion projections that
  retain source-evidence references and can be rebuilt after interruption.
- Safe malformed, duplicate, stale-version, unauthorized, unavailable, and
  partial-failure behavior.
- Accessible responsive light/dark/system-theme practice, feedback, review, and
  history experiences through generated public clients.

### Out of Scope

- AI-authored questions, model grading, generative feedback, model-provided
  answer authority, or AI determination of completion or mastery.
- Open-ended essay grading, instructor review, manual overrides, peer review,
  credentialing, proctoring, high-stakes examinations, or accreditation.
- Arbitrary code, notebook, spreadsheet macro, plugin, shell, or external-tool
  execution as part of a response.
- Adaptive ranking, personalized next-activity recommendations, mastery models,
  experimentation, or engagement optimization.
- Content authoring and publication workflow, external assessment standards, or
  provider-specific item banks.
- Organization tenancy, cohorts, entitlements, billing, or managed-cloud
  operations and recovery.
- Portfolio, valuation, market-data, backtesting, or investment-suitability
  assessment.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Initial Glossary](../../domain/glossary.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Versioned Lesson Package](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- [Community Evidence Protection and Recovery](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
- [Module Map](../../architecture/modules/module-map.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [Content-Package Contract](../../architecture/contracts/content-package-contract.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Interface Design System](../../design/README.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)

## Decision Gates and Constraints

- CAP-0001 supplies the first exact-version deterministic knowledge-check,
  learner-context, evidence, projection, and browser seams. CAP-0006 expands the
  practice outcome without replacing or broadening CAP-0001 history.
- ADR-0005 makes Assessment authoritative for definitions, responses, attempts,
  deterministic scores, review state, and bounded completion evidence. Learner
  model owns rebuildable derived views; Content/Curriculum own review-resource
  identity and placement; Audit holds integrity references.
- ADR-0007 permits structured assessment definitions inside the package but
  leaves runtime scoring to Assessment. New response types require explicit
  schema, semantic, compatibility, and denial evidence; package transport never
  becomes grading authority.
- Authorization, response validation, scoring, feedback selection, retry policy,
  completion, and durable state changes remain deterministic and server-owned.
- ADR-0008 bounds community evidence protection and recovery; this CAP cannot
  claim managed-cloud recovery or protect against a compromised host.
- No unresolved durable decision is needed for the bounded structured response
  types and deterministic grading path. AI/model grading, arbitrary execution,
  external item providers, high-stakes testing, or mastery semantics would be a
  material change requiring separate decisions.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0026 | A learner opens one versioned practice activity containing a bounded initial set of structured items and can see purpose, instructions, expected response shape, source/review references, attempt policy, and exact version before answering. | First after CAP-0001; establishes assessment-definition semantics, compatibility, public operations, and safe rendering for the selected structured response types. | AI-generated items, arbitrary executable responses, external item-bank authority, high-stakes testing, or unbounded item types changes the CAP package. | captured |
| SLI-0027 | The learner submits a practice attempt and receives deterministic item and activity feedback while idempotent response, score, and completion evidence is retained against exact versions. | After SLI-0026; extends the CAP-0001 evidence seam to multi-item practice and scenario rules. | Model/manual grading, mutable result history, hidden scoring, or client-authoritative completion changes the CAP package. | captured |
| SLI-0028 | The learner follows targeted approved review references, resumes after interruption, retries within explicit policy, and compares attempts without overwriting evidence or inferring mastery. | After SLI-0027; adds review routing, retry state, history projection, and replay/rebuild behavior. | Adaptive ranking, personalized recommendation, instructor override, mastery projection, or deleting adverse evidence in place changes the CAP package. | captured |
| SLI-0029 | The complete practice flow is qualified across definition compatibility, deterministic scoring, idempotency, interruption/resume, evidence replay, authorization, accessibility, responsive/theme parity, community protection, and shared local/cloud semantics. | Last; depends on SLI-0026 through SLI-0028. | Qualifying AI grading, arbitrary execution, external providers, proctoring, certification, or managed-cloud recovery changes the CAP package. | captured |

## Capability Acceptance

The capability is complete only when evidence demonstrates that:

- every supported item and response type has an executable versioned contract,
  deterministic scoring fixture, compatibility policy, and malformed or
  unsupported denial corpus;
- an authorized learner sees the exact practice purpose, attempt policy,
  response requirements, and review-source provenance before submission;
- valid attempts produce reproducible item/activity results and bounded
  source-backed feedback, while invalid, stale, incomplete, duplicate, replayed,
  or unauthorized submissions create no contradictory business evidence;
- interruption and retry preserve immutable prior attempts, explicit attempt
  state, idempotency, and exact content/assessment versions;
- targeted review references are selected by deterministic rules and never
  presented as an adaptive recommendation, mastery judgment, or personalized
  financial advice;
- Learner-model projections and attempt history rebuild from Assessment evidence
  without mutating or replacing it, and Audit retains only trace/integrity facts;
- local and cloud adapters can share assessment, evidence, projection, and API
  semantics while unsupported deployment qualification remains explicit; and
- practice, feedback, review, and history views meet keyboard, focus, labeling,
  error association, non-color state, zoom/reflow, reduced-motion, forced-color,
  light/dark, and assistive-technology expectations.

## Risks and Non-Goals

- Adding item types casually can create ambiguous scoring or unsafe renderer and
  resource behavior; the initial type set must stay closed and versioned.
- Feedback can become de facto financial advice if examples or explanations are
  personalized to a learner's holdings or decisions.
- Retry policy can encourage answer fishing or hide evidence unless prior
  attempts and applicable limitations remain visible.
- Derived history can become a second evidence store unless replay and source
  references remain testable.
- CAP-0006 is not instructor review, adaptive learning, mastery estimation,
  credentialing, proctoring, or an arbitrary project/notebook execution system.

## Documentation Impact

Delivery is expected to refine assessment and evidence vocabulary, executable
learning and event contracts, Assessment/Learner-model/Audit public seams,
persistence and replay rules, API/generated-client behavior, accessible practice
patterns, security/recovery evidence, module READMEs, verification maps, and
known gaps.

## Planning History

- 2026-10-15: Shaped from the catalog candidate “Practice and demonstrate
  understanding” as a complete `cap-package-v1` manifest. It depends only on
  CAP-0001 and may proceed in parallel with CAP-0004 and CAP-0005 after that
  foundation is complete, subject to just-in-time file-scope compatibility.
