# ADR-0010: Extend Learning-Loop Ownership to Applied Projects

- Status: superseded
- Date: 2026-10-15
- Decision request: [DEC-0007](../planning/decision-requests/DEC-0007-applied-project-lifecycle-ownership.md)
- Superseded by: [ADR-0012](ADR-0012-reusable-project-workspace.md)

## Context

Applied projects add long-lived learner work, milestones, artifact manifests,
submissions, and completion evidence to the learning loop. The existing module
boundaries already separate immutable learning resources, curriculum placement,
assessment evidence, derived learner state, and audit references. Introducing a
new Project or Workspace module before the first applied-project slice would add
another owner for closely related evidence without usage or operational evidence
that the new boundary is independently cohesive.

The selected boundary must keep mutable in-progress work distinct from immutable
submissions, preserve exact project and curriculum versions, and leave a viable
extraction path if applied projects later develop distinct scale, collaboration,
retention, or operational needs.

## Decision

Extend the accepted learning-loop owners to the initial applied-project lifecycle:

- **Content** owns immutable versioned project instructions, objectives,
  supplied-resource declarations, source provenance, expected artifact types,
  reflection prompts, limitations, and publication state.
- **Curriculum** owns exact project placement, prerequisites, required and
  optional milestone identities and ordering, and the curriculum rules for when
  the project is available.
- **Assessment** owns authorized learner project instances, their lifecycle,
  mutable in-progress artifact manifests, milestone evidence, immutable closed
  submission manifests, deterministic requirement validation, and bounded
  project-completion evidence. Assessment-owned storage references remain
  private implementation details.
- **Learner model** owns rebuildable project completion and progress projections
  derived from Assessment evidence. A projection never replaces source evidence
  or turns project completion into mastery or certification.
- **Audit** owns append-oriented trace and integrity references for project
  lifecycle transitions and source events without duplicating project business
  state.

Assessment may move an authorized project instance through explicitly contracted
states such as active, submitted, completed, withdrawn, or invalidated. Exact
state names and wire shapes belong to executable contracts, but a submission is
always an immutable, digest-bound closure over the exact project definition,
curriculum placement, learner context, milestone evidence, and artifact manifest.
Later work creates a new version or superseding evidence; it never edits the
closed submission in place.

Modules collaborate only through published application operations or registered
versioned events. They may retain stable identifiers owned elsewhere but may not
import another module's internals or read or mutate another module's persistence.

## Consequences

- CAP-0007 can reuse the Content, Curriculum, Assessment, Learner-model, and
  Audit seams established by earlier learning capabilities.
- Assessment gains a broader, longer-lived evidence workflow and must keep
  mutable in-progress manifests visibly separate from immutable submissions.
- Project definitions, placement, learner work, source evidence, projections,
  and trace records each retain one semantic owner.
- Stable public identifiers and versioned events preserve a later extraction
  path without requiring a premature module.
- Real-time collaboration, broad personal workspaces, instructor review, and
  independently operated project services remain outside this decision.

## Alternatives Rejected

- **Introduce a dedicated Project module.** Rejected for the initial capability
  because it adds a new persistence and event boundary before project behavior
  demonstrates independent operational cohesion.
- **Split Workspace artifacts from Assessment submissions.** Rejected because
  it pulls the broader personal-workspace capability forward and creates a
  difficult snapshot boundary before collaborative or cross-activity workspace
  requirements exist.

## Boundaries

This decision does not authorize artifact execution, a notebook runtime,
external providers, collaborative editing, instructor grading, organization
tenancy, credentials, public sharing, or live financial actions. Artifact and
execution effects are governed separately by ADR-0011.

Extraction into a Project or Workspace module requires a superseding ADR and a
contract, event, persistence, and migration analysis. Evidence that may justify
extraction includes independently scaling artifact workloads, materially
different retention, real-time collaboration, cross-activity workspace reuse,
or a separately operated service boundary.

## Verification Implications

- Enforce public module surfaces and reject cross-module internal or persistence
  access.
- Prove exact Content and Curriculum version retention across project start,
  resume, submission, replay, and export.
- Prove immutable closed submissions, idempotent transitions, interruption-safe
  mutable work, and deterministic validation.
- Rebuild Learner-model projections from Assessment evidence and prove Audit
  retains references rather than business-state copies.
- Exercise extraction-oriented contract and event compatibility before any
  future ownership change.

## Supersession

[ADR-0012](ADR-0012-reusable-project-workspace.md) supersedes this decision by
introducing a reusable Project-owned workspace and immutable snapshot boundary
for learning-initiated and independent projects while retaining Assessment
ownership of learning submissions and completion evidence.
