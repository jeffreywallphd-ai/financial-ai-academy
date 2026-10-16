# Deterministic Navigation-State Contract

- Status: implemented for the deterministic application and API boundary
- Canonical for: Adaptation-owned deterministic activity eligibility meaning
- Related ADR: [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)

## Ownership

Curriculum owns the immutable graph, activity identity, branch meaning, and
prerequisite direction. Learner model owns completion projections and retains
their source-evidence references. Adaptation consumes only those public
meanings and owns the deterministic eligibility decision and explanation.
Neither the API host nor the browser recomputes the policy.

## Closed State Dimensions

Navigation state keeps four dimensions separate:

- completion is `completed`, `incomplete`, or `unavailable`;
- eligibility is `eligible`, `locked`, or `unavailable`;
- requirement is `required`, `optional`, or `unassigned`; and
- exact activity-source availability is `available` or `unavailable`.

An optional activity can be independently locked, eligible, complete, or
unavailable. Completion does not imply mastery. An unassigned activity is not
silently treated as required or optional. Unavailable completion or activity
input cannot produce a positive eligibility result.

## Deterministic Rule Baseline

The v1 policy validates the exact Curriculum graph and requires one unique
typed source fact for every activity. It evaluates only explicit
`activity_prerequisite` relationships. Each edge points from prerequisite
source to dependent target. Competency relationships do not become activity
gates without a separately accepted mapping rule.

An activity is unavailable when its exact activity or completion source cannot
be evaluated safely, locked when at least one prerequisite is not complete,
and eligible otherwise. Reasons are closed reviewed records ordered by policy
phase and graph relationship order. Every unmet or satisfied prerequisite
receives its own bounded reason, so the policy does not impose an arbitrary
single-predecessor or small-predecessor shape.

The result preserves graph activity order rather than presentation hints.
Absent or partial hints, multiple entries, multiple prerequisites, same-kind
shared branches, unbranched activities, and sibling reordering remain valid.

## Provenance and Replay

Every result binds the exact curriculum identity/version/digest, policy
identity/version, explicit evaluation time, canonical source-set digest, and
projection digest. The source digest normalizes facts into graph order. The
projection digest covers the complete output except its own field. Both use
documented compact sorted-key UTF-8 JSON and the bounded timestamp profile.

No learner identity, answer, score interpretation, raw upstream error,
provider payload, model output, engagement signal, recommendation, approval,
or persistence reference belongs in the portable contract.

## Current Boundary

The executable JSON Schemas and compatibility corpus live under
`contracts/learning/adaptation/v1/` and
`contracts/compatibility/adaptation-navigation/v1/`. The Python core is pure
and transport-neutral. A framework-free application service opens the exact
graph and exact activity sources through a Curriculum public gateway, obtains
lesson completion through a Learner-model public gateway, evaluates with an
injected UTC clock, and returns only a complete projection. Activity-source
availability and completion degrade independently. Assessment completion is
explicitly unavailable until a separate accepted public projection exists.

The protected exact-version GET requires the server-issued
`adaptation.navigation.read` capability, derives the learner only from the
opaque session, and is published as `getCurriculumNavigationState` in the
reviewed OpenAPI and generated TypeScript client. The browser presents only the
returned state, reason, reference, policy, and provenance facts across its peer
list and map views; it does not recompute eligibility or projection digests.
The composed live qualification proves exact retained-completion transition,
API/UI parity, missing-version and authorization confidentiality, accessible
presentation, and isolated PostgreSQL/Python/static-browser execution. Durable
recommendation records, model ranking, experiments, and managed-cloud adapters
remain outside the current qualification.
