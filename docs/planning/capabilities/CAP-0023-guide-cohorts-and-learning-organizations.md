---
id: CAP-0023
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0009", "CAP-0022", "CAP-0025"]
decision_gates: ["DEC-0016"]
approval_model: cap-package-v1
slice_ids: ["SLI-0094", "SLI-0095", "SLI-0096", "SLI-0097"]
---

# Capability: Guide Cohorts and Learning Organizations

## Outcome

An authorized instructor or organization leader can create and guide a bounded
cohort, assign approved learning experiences, and inspect privacy-aware
participation, progress, review needs, and outcome summaries without replacing
individual evidence or exposing unrelated learners.

## Users and Value

Instructors and organization leaders need aggregate and action-oriented views
that support teaching while learners need predictable privacy and source
meaning. Value is observable when cohort facts reconcile to authorized
individual projections and every drill-down is purpose- and role-limited.

## Scope

### In Scope

- Cohort identity, membership, role, assignment, schedule, participation,
  aggregate progress, review-need, privacy threshold, and audit behavior under
  DEC-0016.
- Versioned assignment references to existing learning experiences without
  copying curriculum or evidence.
- Aggregate-to-authorized-detail navigation, suppression, small-group handling,
  stale/freshness disclosure, and export restrictions.
- Accessible cohort and organization views with explicit limitations.

### Out of Scope

- Workforce surveillance, ranking learners, disciplinary decisions, predictive
  risk scoring, certification, HR systems, marketing analytics, billing, or
  cross-organization data sharing.

## Canonical Context

- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Security Architecture](../../security/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [CAP-0009](CAP-0009-track-progress-and-competency-evidence.md)
- [CAP-0022](CAP-0022-review-learner-evidence-and-feedback.md)
- [CAP-0025](CAP-0025-manage-identities-organizations-roles-entitlements.md)

## Decision Gates and Constraints

- DEC-0016 must establish organization/tenant identity, membership, roles,
  database/object boundaries, lifecycle, privacy, and authorization inputs.
- Aggregate views derive from authorized individual projections and never
  become a replacement source for evidence or learner state.
- Privacy thresholds, permissions, assignments, and durable administrative
  actions are deterministic and auditable.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0094 | An authorized leader creates a cohort and manages membership and roles within the DEC-0016 tenant boundary. | First after CAP-0025 and DEC-0016. | Cross-tenant membership, external HR sync, or inferred roles changes the CAP package. | captured |
| SLI-0095 | An authorized instructor assigns exact approved learning experiences and sees participation and schedule state without copying curriculum. | After SLI-0094. | Credentialing, mandatory employment action, or mutable curriculum copies changes the CAP package. | captured |
| SLI-0096 | Authorized users inspect privacy-thresholded progress, outcomes, and review needs with source freshness and bounded drill-down. | After SLI-0095 and dependencies. | Learner ranking, predictive risk, or unsuppressed small-group analytics changes the CAP package. | captured |
| SLI-0097 | Cohort behavior is qualified for tenant/role isolation, suppression, audit, assignment versioning, stale data, accessibility, and export controls. | Last; depends on SLI-0094 through SLI-0096. | Billing, HR integration, or regulatory reporting changes the CAP package. | captured |

## Capability Acceptance

- Membership, roles, assignments, aggregates, drill-down, and exports enforce
  the accepted tenant and privacy policy at every application boundary.
- Aggregate values reconcile to exact authorized projections and report source
  window, freshness, suppression, and limitations.
- Membership or role changes revoke access predictably without rewriting
  historical evidence or administrative audit.
- Accessibility, privacy, security, audit, and failure evidence covers ordinary,
  small-group, stale, and denied cases.

- Every slice includes focused failure and anti-rigidity tests; missing aggregate
  inputs or optional views isolate only affected cohorts and preserve permitted
  membership and assignment work.

## Risks and Non-Goals

Cohort analytics can become surveillance or discriminatory ranking. This CAP
excludes employment decisions, risk prediction, HR/billing integration,
certification, and cross-tenant comparison.

## Documentation Impact

Delivery will add cohort/assignment/aggregate vocabulary, tenant authorization,
privacy/suppression, projection and audit contracts, UI/accessibility behavior,
threat modeling, export policy, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 20 with manifest SLI-0094 through
  SLI-0097. DEC-0016 blocks CAP approval and delivery.

