---
id: CAP-0018
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0001"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0074", "SLI-0075", "SLI-0076", "SLI-0077"]
---

# Capability: Set Learning Goals and Preferences

## Outcome

An individual learner can record and revise learning goals, experience,
interests, accessibility needs, theme, AI-assistance and notification choices,
and appropriate privacy controls, then understand where each setting applies.

## Users and Value

Learners need control over how the platform presents and supports learning.
Value is observable when preferences are explicit, portable, reversible,
privacy-preserving, and consumed only by capabilities that declare their use.

## Scope

### In Scope

- Learner-model-owned goals, experience, interests, accessibility and assistance
  preferences; platform-owned theme and local notification settings.
- Purpose, scope, default, version, validation, change history, reset, export,
  and unsupported-capability behavior.
- Deterministic use by later navigation, adaptation, AI, and interface features
  without turning a preference into permission or evidence.
- Accessible settings and disclosure behavior across supported profiles.

### Out of Scope

- Organization policy, guardian controls, marketing consent, billing,
  enterprise identity, medical diagnosis, or inferred sensitive traits.
- Hidden personalization, automatic goal changes, or using engagement as
  evidence of mastery or suitability.

## Canonical Context

- [Initial Glossary](../../domain/glossary.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [Interface Design System](../../design/README.md)
- [Security Architecture](../../security/README.md)
- [CAP-0001](CAP-0001-complete-structured-introductory-lesson.md)

## Decision Gates and Constraints

- Learner model owns learning goals/preferences; the platform design system owns
  theme behavior. Consumers use public contracts rather than shared tables.
- Defaults are conservative, purpose-limited, and explicit. A preference cannot
  waive authorization, prerequisite, scoring, privacy, or safety policy.
- Organization, commercial, and provider-specific consent remain outside this
  local learner boundary.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0074 | A learner records versioned goals, experience, and interests and can inspect, revise, reset, and export them. | First after CAP-0001; establishes ownership and preference contracts. | Inferred sensitive traits or organization policy changes the CAP package. | captured |
| SLI-0075 | The learner sets accessibility, theme, and presentation preferences with immediate accessible preview and safe defaults. | After SLI-0074; reuses the design system. | Feature-local theme maps or preferences that weaken accessibility changes the CAP package. | captured |
| SLI-0076 | The learner controls AI-assistance and local notification preferences and sees purpose, unavailable capability, and downstream-use disclosures. | After SLI-0074; may proceed with SLI-0075 if scopes are disjoint. | Provider consent, marketing, or permission bypass changes the CAP package. | captured |
| SLI-0077 | Preferences are qualified for validation, history, reset/export, privacy, consumer isolation, accessibility, and local/cloud semantic parity. | Last; depends on SLI-0074 through SLI-0076. | Organization administration or hidden behavioral profiling changes the CAP package. | captured |

## Capability Acceptance

- Preferences have stable identity, purpose, scope, version, safe default,
  validation, change history, reset, and portable representation.
- Consumers can use only declared values through public contracts and cannot
  convert preferences into authorization, evidence, or irreversible action.
- Missing, stale, malformed, unavailable, or conflicting settings degrade
  safely and disclose what is or is not applied.
- Keyboard, labels, focus, contrast, theme parity, zoom, reflow, reduced motion,
  and forced colors are verified.

- Every slice includes focused failure and anti-rigidity tests so unsupported
  downstream consumers do not block viewing, changing, resetting, or exporting
  otherwise valid preferences.

## Risks and Non-Goals

Preferences can become covert profiling or a policy bypass. This CAP avoids
inferred traits, organization policy, marketing consent, and opaque automatic
changes.

## Documentation Impact

Delivery will add goal/preference vocabulary, contracts, privacy/purpose
guidance, design-system consumption, downstream adapter rules, export,
accessibility, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 15 with manifest SLI-0074 through
  SLI-0077. The package awaits one CAP planning approval.

