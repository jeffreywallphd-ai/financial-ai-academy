---
id: CAP-0022
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0006", "CAP-0007", "CAP-0025", "CAP-0026"]
decision_gates: ["DEC-0016", "DEC-0020"]
approval_model: cap-package-v1
slice_ids: ["SLI-0090", "SLI-0091", "SLI-0092", "SLI-0093"]
---

# Capability: Review Learner Evidence and Provide Feedback

## Outcome

An authorized instructor can inspect only permitted learner evidence and project
snapshots, provide versioned feedback, request revision, and perform only the
explicit overrides selected by policy with reason, scope, and audit evidence.

## Users and Value

Instructors need a review workflow that supports learning without silently
rewriting learner history or bypassing deterministic grading. Learners need to
see who reviewed what, which version, what action is requested, and whether an
override affected a derived state.

## Scope

### In Scope

- Role/tenancy-authorized review queues, exact evidence/snapshot views, feedback,
  revision requests, acknowledgements, and disposition history.
- The review and override authority selected by DEC-0020 and the organization
  boundary selected by DEC-0016.
- Append-oriented instructor actions, bounded Learner-model/Assessment consumers,
  provenance, notification references, and privacy-preserving redaction.
- Accessible instructor and learner views with denial, stale, conflict, and
  unavailable behavior.

### Out of Scope

- Rewriting attempts, scores, artifacts, or prior feedback; hidden overrides;
  unrestricted learner surveillance; AI-authoritative review; certification; or
  cross-organization access.

## Canonical Context

- [Module Map](../../architecture/modules/module-map.md)
- [Security Architecture](../../security/README.md)
- [CAP-0006](CAP-0006-practice-and-demonstrate-understanding.md)
- [CAP-0007](CAP-0007-complete-applied-projects.md)
- [CAP-0025](CAP-0025-manage-identities-organizations-roles-entitlements.md)
- [CAP-0026](CAP-0026-preserve-provenance-and-accountable-history.md)

## Decision Gates and Constraints

- DEC-0016 establishes instructor membership, tenant context, permissions, and
  isolation. DEC-0020 establishes review states, overrideable projections,
  reasons, dual-control/escalation, notification, and reversal semantics.
- Source evidence remains append-oriented and owned by Assessment or Project;
  instructor actions are separate evidence, never in-place edits.
- AI may assist drafting only under a later bounded policy and cannot decide a
  review outcome or override.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0090 | An authorized instructor opens a privacy-bounded queue and exact evidence/project snapshot with provenance and no source-mutation capability. | First after dependencies and DEC-0016. | Cross-tenant visibility or direct source editing changes the CAP package. | captured |
| SLI-0091 | The instructor records versioned feedback and a revision request; the learner sees and acknowledges the exact review without losing prior state. | After SLI-0090. | Hidden feedback, destructive replacement, or arbitrary messaging changes the CAP package. | captured |
| SLI-0092 | The instructor applies only a DEC-0020-approved override with explicit reason, scope, evidence, authorization, audit, and reversible follow-up semantics. | After SLI-0091 and DEC-0020. | Score/evidence rewriting, AI authority, or unbounded override changes the CAP package. | captured |
| SLI-0093 | Review is qualified for tenant/role isolation, stale evidence, conflicts, audit, privacy, notifications, accessibility, and replay. | Last; depends on SLI-0090 through SLI-0092. | Certification or workforce surveillance changes the CAP package. | captured |

## Capability Acceptance

- Every review binds the authorized actor context, exact source version,
  purpose, feedback/disposition version, time, and audit reference.
- Denied, stale, changed, or cross-tenant evidence cannot be reviewed or leaked;
  concurrent updates produce explicit conflict behavior.
- Overrides are limited to the accepted policy and never alter immutable source
  evidence or pretend manual opinion is deterministic grading.
- Instructor and learner interfaces meet privacy, accessibility, audit, and
  failure requirements.

- Every slice includes focused failure and anti-rigidity tests so an unavailable
  evidence type, notification channel, or override policy does not block valid
  review and feedback paths.

## Risks and Non-Goals

Instructor access creates material privacy and power risks. This CAP does not
permit unrestricted surveillance, hidden feedback, source-history rewriting,
AI-decided review, credentialing, or cross-organization access.

## Documentation Impact

Delivery will add review/feedback/override vocabulary and contracts, role and
privacy policy, audit and notification behavior, UI/accessibility patterns,
threat modeling, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 19 with manifest SLI-0090 through
  SLI-0093. DEC-0016 and DEC-0020 block CAP approval and delivery.

