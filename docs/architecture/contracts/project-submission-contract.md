# Project Learning-Submission Contract

- Status: accepted transport-neutral contract and pure policy
- Canonical for: exact Project snapshot submission, deterministic structural closure, immutable Assessment evidence, and safe event/history meaning
- Ownership: [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md)
- Execution constraint: [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md)
- Executable schemas: [Assessment Project v1](../../../contracts/learning/assessment/project/v1/README.md)
- Compatibility corpus: [Assessment Project v1 corpus](../../../contracts/compatibility/assessment-project/v1/README.md)

## Ownership and Boundary

Project owns the live workspace, inert artifact manifests, validated domain
links, and immutable snapshot. Content owns the approved brief and its ordered
milestones. Curriculum owns exact placement. Assessment consumes only public,
learner-safe facts and owns the submission intent, structural validation,
immutable evidence, and completion signal. Learner model and Audit can consume
a later typed public replay; neither may read Assessment or Project tables.

Only a learning-started Project can produce this evidence. The candidate fixes
the exact package, brief, Curriculum, placement, Project, snapshot, policy,
milestones, and resource set. An independent origin cannot be represented.
Changing a source version or digest requires a newly assembled candidate; the
policy never falls forward to a newer source.

## Deterministic Closure

A submission maps every exact milestone once to one or more resources already
closed in the named snapshot. Notes and safe sources retain integer record
versions and digests. Inert artifacts also retain manifest/content digests and
byte counts. Domain resources retain the validated owner-reference digest and
exact version or as-of time. Missing, repeated, unknown, stale, live-only, or
cross-snapshot facts fail closed with bounded safe issues.

This proves only structural closure. It does not inspect or execute bytes,
reproduce a result, determine truth or quality, grade a learner, infer mastery
or competency, assess suitability, calculate Portfolio meaning, or provide
financial advice.

## Canonical Identity and Evidence

The request fingerprint hashes compact sorted-key UTF-8 JSON with
`ensure_ascii=false`. Before hashing, mappings follow the exact brief sequence
and each resource set follows its complete canonical JSON value. JSON object
order and those permitted array-order variations have one identity; changing a
submission ID, source selector, milestone, version, digest, or evidence fact
changes identity.

An accepted pure result plus bounded server metadata produces immutable
Assessment evidence. The server supplies learner/evidence identity, occurrence,
accepted sequence, canonical UTC time, and any forward supersession reference.
A later occurrence points to a prior submission without altering it. Ordered
history requires one learner-bound Project stream, unique evidence/submission
identities, increasing accepted sequence, non-regressing canonical UTC server
time, contiguous occurrences, and a valid prior reference. Learner identity is
removed only after those cross-record checks pass.

The safe `assessment.project.completed@1.0.0` event omits learner identity and
artifact-level mappings. It carries only exact correlation and provenance
needed by later authorized projections. Neither event nor history is a public
sharing or grading record.

## Current Delivery Boundary

The current implementation is deliberately side-effect free: closed schemas,
compatibility records, immutable Python values, a port, and pure parsing,
validation, fingerprinting, and projection. It has no clock, UUID source,
repository, migration, transaction, cross-module gateway, API, OpenAPI client,
browser, consumer, provider, queue, execution adapter, or managed-cloud
profile. Those seams require later bounded packets and must consume rather
than redefine this contract.
