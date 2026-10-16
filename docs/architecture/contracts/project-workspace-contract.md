# Project Workspace Contract

- Status: accepted first contract seam
- Canonical for: Project shell and origin ownership and version 1 semantic rules
- Related decisions: [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md), [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md)
- Executable shapes: [`contracts/learning/project/v1`](../../../contracts/learning/project/v1/README.md)

## Ownership

Content owns an approved learning-project brief as immutable source material.
Curriculum owns the exact placement of that brief in an approved learning
path and binds the placement to an existing exact Curriculum graph and lesson
activity whose reference names the same Content package. Project owns the
learner's Project identity, charter, accepted origin, lifecycle, and revision.
A learning-started Project can continue beyond a lesson without moving Content
or Curriculum authority into Project.

An independent Project makes no claim about Curriculum placement, learning
completion, mastery, Portfolio suitability, or Assessment evidence. A
learning-origin Project retains exact package, brief, Curriculum, and placement
identities, semantic versions, and digests. It also retains the approved safe
brief title and purpose so that the origin remains understandable if a newer
source version later exists.

## Version 1 Meaning

The brief is a closed object with one through twenty milestones and one through
twenty approved source references. Its digest is lowercase SHA-256 over the
nested brief object serialized as compact sorted-key JSON and encoded directly
as UTF-8. Producers normalize source text before contract creation if their
authoring system can represent equivalent Unicode with different code points;
the contract performs no implicit Unicode normalization.

A create intent contains only an idempotency key, learner-visible title and
charter, and one origin. Learner identity, Project identity, lifecycle,
revision, time, and authorization are server-owned. A future application
operation must resolve a learning origin through public Content and Curriculum
operations and correlate the complete retained brief summary before creating
durable state.

The public shell adds server-owned identity, active lifecycle, positive
revision, and canonical UTC times. It contains no storage path, credential,
provider payload, executable control, artifact bytes, Assessment response,
score, completion, mastery, recommendation, market observation, copied
Portfolio aggregate, or financial advice.

## Persisted Shell and Headless Access

The parser and projector remain transport-neutral, framework-free, and side-
effect free. The Project application service now composes them with owned
clock, identifier, repository, Content-brief, and Curriculum-placement ports.
Independent creation performs no learning lookup. Learning creation must match
every exact placement and brief reference before the Project transaction.

`project.project_shells` retains one learner-owned active shell, immutable
origin, canonical request fingerprint, and server-issued identity/times.
Exact learner/idempotency replay returns the original shell; changed reuse
conflicts. Repository reads revalidate the shell contract, list by creation
time then Project ID, and do not query another module's schema.

The protected POST/list/read API uses the same Project operations for generated
browser clients, command-line clients, services, and future headless AI
clients. Headless access does not create a second domain core or grant AI
authority over eligibility, authorization, grading, financial calculations,
or durable state changes.

## Compatibility

Version 1 accepts only `independent` and `learning` origins. New origin kinds,
new server-authority fields, changed digest semantics, wider execution
behavior, or changed ownership require normal additive versioning and decision
review. Harmless valid text, identities, milestone/source counts within bounds,
and generated time or ID values must not depend on one fixture.

Artifact manifests, workspace resources, snapshots, typed domain links,
Assessment submissions, and browser Project behavior are separate bounded
delivery seams. ADR-0011 continues to require inert data if artifact contracts
are introduced later.
