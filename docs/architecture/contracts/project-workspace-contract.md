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
revision, time, and authorization are server-owned. The application operation
resolves a learning origin through public Content and Curriculum
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

Protected learning-start list and exact reads return only the approved title,
purpose, and complete immutable origin. They create no learner record and are
not a reservation or approval. Project resolves each record through public
Curriculum and Content operations; the browser never authors or guesses source
versions or digests. `POST /api/v1/projects` resolves the source again before
persistence, so stale form state fails closed.

The `/projects`, `/projects/new`, and `/projects/:projectId` browser routes use
only the generated public client. They support independent and learning-backed
creation, learner-scoped list/reopen, and one idempotency key for an unchanged
retry. A material draft change uses a new key. Primary copy uses learner terms;
exact identifiers, versions, revisions, and digests remain available in a
keyboard-reachable Technical record disclosure.

## Compatibility

Version 1 accepts only `independent` and `learning` origins. New origin kinds,
new server-authority fields, changed digest semantics, wider execution
behavior, or changed ownership require normal additive versioning and decision
review. Harmless valid text, identities, milestone/source counts within bounds,
and generated time or ID values must not depend on one fixture.

Assessment submissions and the browser workspace remain separate bounded
delivery seams. The workspace contracts, persistence, and public API behavior
are defined below; browser presentation and submission behavior remain later
work.

## Version 1 Workspace and Snapshot Meaning

The additive Project v1 workspace shapes retain the shell's ownership and
authorization semantics. A live workspace has one positive revision and
bounded ordered notes, safe HTTPS reference metadata, inert-artifact manifests,
and typed public domain-resource references. Mutations carry an idempotency key
and exact expected revision; accepted record identity, version, time, learner,
digest verification, owner validation, and persistence facts remain server
authority.

Artifact manifests admit only dataset, notebook, code, environment, result,
reflection, and supporting-file evidence. They use NFC-normalized relative
logical paths with one case-folded cross-platform comparison key and reject
reserved device aliases, including the Windows superscript-digit COM/LPT forms.
They use closed media and passive-inspection values with a maximum declared
size of 10 MiB, lowercase SHA-256 content integrity, source/license/use
provenance, assumptions, and optional external-environment evidence. Result
records distinguish observed, calculated, simulated, predicted, generated,
and narrative meaning. Validation is not code-safety, truth, suitability, or
independent-reproduction evidence.

Typed links retain owning module, resource type and identity, link meaning,
version and/or as-of evidence, public owner-reference digest, validation time,
and provenance. Only an owning public operation may produce an accepted
`available` link. The contract carries no target business state or permission
and supplies no production Portfolio adapter.

A snapshot close intent binds one exact Project and workspace revision. The
immutable snapshot material records the exact Project shell digest and record
version/digest references. Its digest is SHA-256 over compact sorted-key JSON
with direct UTF-8. A later live revision or removed live association cannot
rewrite that material. The evidence-export manifest embeds and validates the
exact snapshot and workspace records, binds each referenced record by digest,
preserves their ordered correspondence, accounts for every snapshot artifact as
included or excluded, and repeats exact
file and artifact-manifest integrity for included bytes. It is neither an
archive-import nor an execution format.

These portable shapes contain no storage coordinates, host paths, credentials
or credential-bearing URLs,
provider payloads, callbacks, archive controls, executable controls, active
renderer instructions, Assessment result, Learner-model state, copied
Portfolio aggregate, or financial advice. Browser, command-line, service, and
headless clients consume the same Project API; the contracts grant no client
durable-state authority.

## Persisted Workspace, Artifact, Snapshot, and API Seam

`project.project_workspaces` stores one revalidated JSON workspace aggregate
and positive optimistic revision per learner-owned Project. Accepted mutation
replays store the canonical request fingerprint and exact accepted workspace.
The repository locks the live workspace row, checks the expected revision, and
commits the next aggregate plus any opaque artifact reference in one
transaction. Exact retry returns the original accepted workspace; changed key
reuse and stale revision fail without overwrite.

Opening a Project with no stored workspace returns a deterministic empty
revision-one view without writing durable state. The first authorized mutation
or snapshot close initializes that exact view inside the write path, then
rechecks its expected revision before acceptance. GET therefore remains a
read-only operation, while every workspace-creating path retains write
permission and same-origin protection.

Artifact bytes are staged, verified by exact byte count and SHA-256, finalized
under a domain-separated content-addressed object key, and only then referenced
by Project metadata. A metadata failure may leave an unreferenced immutable
object for bounded reconciliation but cannot expose a partial live manifest.
Downloads recheck stored metadata and bytes and use attachment, `nosniff`, and
integrity headers. No download path invokes an interpreter, active renderer,
network client, package manager, secret source, or provider.
The same byte-integrity check runs before an idempotent upload replay can return
the previously accepted workspace; a changed byte string cannot be treated as
an exact retry merely because its manifest and key match.

`project.project_snapshots` stores the immutable snapshot document and the exact
workspace document it closes. A transaction lock confirms the expected live
workspace revision before insert; ordinary update/delete is rejected. Later
mutations advance only the live workspace. Evidence export revalidates the
closed records, includes only authorized available inert bytes, and explicitly
records restricted or unavailable content. Export is JSON-compatible evidence,
not an import, restore, archive-expansion, or execution contract.

The protected API exposes open/mutate/upload/download/close/list/read/export
operations beneath `/api/v1/projects/{project_id}`. Identity and permissions
come only from the server session. OpenAPI and the generated TypeScript client
are the common browser, command-line, service, and headless boundary. No live
domain owner is admitted yet, so a link to Portfolio or another unavailable
owner fails rather than creating a dangling association.
