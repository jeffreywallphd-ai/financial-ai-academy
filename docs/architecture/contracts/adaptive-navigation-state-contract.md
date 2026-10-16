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

## Activity-Launch Boundary

The transport-neutral `activity-launch-v1` seam consumes one validated exact
Curriculum graph, its complete matching Navigation-state v1 projection, and
one activity ID. Adaptation rechecks graph/projection identity, graph-ordered
state closure, bounded state types, timestamp, and projection digest before it
trusts the selected state. It then requires the activity to be available and
eligible. Completed lessons remain reopenable because completion and
eligibility are independent dimensions.

Version 1 resolves lesson references only. It derives the destination as
`/learn/placements/{placement_id}` from the exact graph reference and returns
the exact graph, projection, placement, and package provenance. Unknown,
locked, unavailable, malformed, or assessment activities fail with bounded
errors and no destination. No learner identity, durable grant, completion
evidence, recommendation, model output, provider payload, arbitrary URL, or
repository access crosses this seam.

The executable schema lives beside the Navigation-state schemas under
`contracts/learning/adaptation/v1/`; its independent compatibility corpus is
under `contracts/compatibility/adaptation-activity-launch/v1/`. The public
application operation opens one fresh exact graph, observes current completion,
evaluates Navigation state once, and resolves the launch against that matching
pair. The protected bodyless GET requires both existing navigation-read and
lesson-read permissions and is published as `getCurriculumActivityLaunch` in
the reviewed OpenAPI and generated TypeScript client.

The learning-path browser consumes only that generated operation for eligible
lesson start and review controls. It validates the closed launch response
against the exact graph, selected activity, lesson placement/package, and
derived same-origin path before navigation. Because launch performs a fresh
evaluation, its bounded evaluation time and projection digest may be newer than
the state already on screen; the browser validates their contract shapes but
does not demand stale equality or recompute policy. Locked, unavailable, and
assessment activities expose no launch control, while a direct attempt still
fails at the server boundary.

The lesson carries an optional all-or-none exact curriculum/activity return
context. It derives a same-origin graph path rather than accepting an arbitrary
URL. Returning reloads the exact graph and current Navigation state; a selected
activity is marked in visible text plus `aria-current` only when the fresh graph
contains it. That URL state is disposable presentation context, not a durable
position, evidence record, launch grant, or source of authorization.

The isolated composed qualification exercises the same public launch operation
both directly and through the generated browser client. It proves exact lesson
opening, return after retained completion, fresh complete/current display,
bounded denial confidentiality, and two coexisting graph versions. An activity
that deliberately reuses the exact placement/package source may observe its
retained completion; an activity whose version changes the placement remains
incomplete. This is exact source identity, not inferred equivalence or a
cross-version migration.

The same isolated qualification also exercises a headless consumer through the
public session, exact graph, Navigation-state, and activity-launch APIs. After
the visible journey creates accepted Assessment evidence, the qualifier stops
the application, clears only the two rebuildable Learner-model completion
tables in its ephemeral PostgreSQL database, and restarts the normal host
against the same database and object root without fixture seeding. A fresh
public Navigation-state read rebuilds the projection through Assessment's
public replay source. Exact graph, policy, source-set, ordered activity-state,
reason, and launch-resource semantics remain stable, while Assessment evidence
counts remain unchanged and derived rows reappear. Observation timestamps and
digests that incorporate them are not incorrectly treated as durable identity.

This is recovery and API portability evidence for the shared core, not a
production reset API, backup/restore claim, managed-cloud qualification, or
separate AI execution mode. Browser and future non-browser consumers share the
same protected public operations; neither receives permission to select learner
identity, eligibility, completion, destination, or policy output.
