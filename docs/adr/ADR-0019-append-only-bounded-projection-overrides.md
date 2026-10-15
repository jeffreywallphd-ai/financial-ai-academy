# ADR-0019: Append-Only Bounded Learner-Projection Overrides

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0020](../planning/decision-requests/DEC-0020-instructor-review-and-override-authority.md)
- Related decision: [ADR-0014](ADR-0014-governed-adaptive-learning-research-plane.md)

## Context

Instructor review can provide valuable feedback, request revision, and correct
or waive a derived learner-state projection in exceptional cases. Without a
precise boundary, an override could silently rewrite a deterministic score,
erase source evidence, bypass authorization or prerequisites, become an
unreviewed credential, or hide a materially different view from the learner.

Assessment and Project retain immutable source evidence. Learner model owns
derived completion, progress, and competency projections. ADR-0014 separates
versioned competency estimates from deterministic learner-facing publication.
An instructor action therefore must be a visible append-only overlay on a base
projection, never a mutation of the estimate, publication policy, or evidence.

The organization tenancy and exact role model remain deferred to DEC-0016.
This decision can define override meaning and minimum authorization properties
without choosing tenant placement or mapping the capability to a named role.

## Decision

Permit append-only bounded overrides of explicitly enumerated Learner-model
projection fields under an instructor-review workflow.

### Immutable Source and Base Projection

An override never changes or replaces:

- an Assessment definition, attempt, response, deterministic score, feedback,
  completion evidence, or event;
- a Project workspace, artifact, immutable snapshot, or submission;
- Curriculum content, prerequisite definitions, or placement history;
- a competency estimate, model output, evidence cutoff, calibration record, or
  deterministic publication-policy result; or
- prior feedback, review, override, notification, appeal, or audit evidence.

Learner model retains the reproducible base projection and calculates an
effective learner-facing view by applying the currently active override ledger.
The base and override are always distinguishable in APIs, interfaces, exports,
replay, and audit.

### Initial Overrideable Fields

The initial policy may enumerate only:

- a named activity or requirement's derived completion projection; and
- a named competency's learner-facing publication label or separate
  `review_due` condition under ADR-0014.

Each policy entry fixes permitted source and target values, direction,
educational scope, maximum duration, whether it can affect a named learning
eligibility rule, and required evidence/reason classes. An absent policy entry
means the field is not overrideable.

An override cannot create a score or grade, alter a prerequisite definition,
grant an application permission or entitlement, create a credential or
certification, assert professional or investment competence, affect employment,
or authorize a financial action. Any effect on learning navigation is limited
to a specifically enumerated educational eligibility rule and remains visibly
override-derived.

### Review and Activation Lifecycle

Every override records the learner and exact projection identity/version,
source-evidence set/digest and cutoff, base value, proposed effective value,
enumerated field and policy version, bounded reason code and learner-visible
explanation, supporting evidence references, scope, proposer context, times,
review-by and expiration, notification fact, and audit references.

The lifecycle is append-only:

1. An authorized reviewer proposes an override against the current exact base.
2. A distinct authorized reviewer confirms or rejects the same unchanged
   proposal. Self-confirmation is prohibited.
3. Confirmation activates the overlay only if source, projection, policy,
   authorization, and conflict checks are still current.
4. Expiration, reversal, supersession, or appeal disposition adds a new action;
   it never edits or deletes the earlier record.

Two-person activation applies only to the exceptional override action. Evidence
review, feedback, revision requests, acknowledgements, and ordinary projection
rebuilds do not require it. If the deployment cannot supply two distinct
authorized actor contexts, feedback and revision remain available but override
activation is unavailable.

DEC-0016 will define organization membership, tenancy, roles, and exact
permission mapping. At minimum, evidence read, feedback, override proposal,
override confirmation, reversal, and policy administration are distinct
authorization capabilities and are rechecked at proposal, confirmation, and
effective publication.

### Visibility, Notification, and Reversal

The learner-facing projection displays that an override is active, the base and
effective bounded meanings, learner-visible reason, scope, issuer class, start,
expiration/review date, evidence references permitted to the learner, and
challenge/support route. History remains available after expiration or reversal
subject to accepted retention policy.

Activation atomically creates a durable learner-visible history entry and a
notification outbox fact. Delivery through an optional notification channel may
retry and report failure without erasing the active history or blocking access
to it. A hidden override is invalid.

Every override is time-bounded and can be reversed by a new authorized action.
When it expires or is reversed, Learner model reveals the current rebuilt base
projection rather than restoring a stale cached value.

## Consequences

- Exceptional corrections and educational waivers are possible without
  corrupting deterministic source evidence or model provenance.
- Learners and downstream consumers can distinguish observed/calculated state
  from an instructor-authorized overlay.
- Two-person activation, stronger permissions, visible history, expiration,
  and appeal reduce abuse but add workflow and support cost.
- Normal feedback and revision remain usable even when override activation,
  notification delivery, or one projection type is unavailable.
- CAP-0022 remains decision-blocked on DEC-0016; this ADR does not infer tenant,
  membership, role, or cross-organization authority.

## Alternatives Rejected

- **Feedback and revision requests only.** Retained as the normal path but
  rejected as the complete target because bounded exceptional correction or
  waiver would remain impossible.
- **Mutate the source evidence or base projection.** Rejected because it breaks
  replay, provenance, accountability, and deterministic scoring ownership.
- **Single opaque administrator flag.** Rejected because it hides field,
  reason, scope, evidence, expiration, conflicts, and learner visibility.
- **AI-decided override.** Rejected because model output cannot supply review,
  authorization, or protected-state authority.
- **Make all review require dual control.** Rejected as unnecessary rigidity;
  dual control is limited to activation of the exceptional override overlay.

## Boundaries

This decision does not define an instructor role, organization membership,
tenant boundary, database row policy, cross-organization access, exact API or
schema fields, retention duration, notification provider, appeal staffing,
certification, accreditation, employment use, or high-stakes assessment.

DEC-0016 remains unresolved and controls who may see evidence or exercise the
separate capabilities. No implementation or CAP approval may use this ADR to
infer that missing authorization boundary.

## Verification Implications

- Prove source evidence and base projections are byte/record unchanged before,
  during, and after proposal, activation, expiration, reversal, and replay.
- Reject unsupported fields/values, stale source or projection digests,
  conflicting active overlays, self-confirmation, missing or lost permission,
  malformed reasons/evidence, expired proposals, and hidden notification state.
- Prove exact rebuild yields the same base while effective state applies only
  the current valid ledger under its policy version.
- Prove learner views and exports distinguish base and effective values and show
  bounded reason/history, expiry, reversals, and appeal/support path.
- Prove notification-channel failure does not hide history or corrupt the
  override and that feedback/revision workflows remain usable without override
  capability.
- Prove no override can change grades/scores, credentials, permissions,
  entitlements, financial state, or source artifacts.
- Add privacy, fairness, abuse, conflict, accessibility, retention, and
  local/cloud parity qualification after DEC-0016 supplies the actor boundary.

## Supersession

Adding an overrideable field, removing two-person activation, permitting an
unbounded or hidden override, mutating source evidence, extending to credentials
or high-stakes outcomes, or granting AI authority requires a superseding or
extending ADR. Changing exact UI or storage while preserving this meaning does
not necessarily require supersession.
