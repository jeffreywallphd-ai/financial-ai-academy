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
immutable evidence, and completion signal. Learner model and Audit consume the
typed public replay; neither reads Assessment or Project tables.

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

The safe `assessment.project.completed@1.0.0` portable envelope omits learner
identity and artifact-level mappings. It carries only exact correlation and provenance
needed by later authorized projections. Neither event nor history is a public
sharing or grading record.

## Protected API Boundary

The local composition root now wires Project, Content, and Curriculum public
operations into Assessment's project-submission source and supplies the same
contract adapter to the application service and PostgreSQL repository. The
protected API exposes exact candidate read, snapshot submission, complete
history read, exact evidence read, and the reconciled Project-activity
completion projection under the Project resource. Learner
identity comes only from the opaque server session; reads require the existing
`project.read` permission and submission requires `project.write`. Route/body
Project or snapshot mismatch fails before persistence, and query-selected
learner authority is rejected.

HTTP responses are closed projections of the v1 contract. Candidate and exact
evidence expose only the current session-bound safe facts needed for
correlation, while ordered history omits learner identity and every Project
body or artifact byte. The completion read first verifies the learner-owned
Project, reconciles Audit from the public Assessment replay, and opens the
Learner-model projection. It carries only bounded completion meaning, exact
correlation/provenance references, required projection version, source digest,
and rebuild time; it does not
claim quality, mastery, competency, or advice. A deterministic validation refusal is a bounded normal
response with no evidence and no write. The reviewed OpenAPI and generated
TypeScript client are the common browser and headless boundary; neither defines
an alternate AI authority path.

## Current Delivery Boundary

The shared application core now assembles the candidate through public
Project, Content, and Curriculum operations, validates the exact closed
submission, and commits accepted immutable evidence plus its safe outbox event
atomically in Assessment-owned PostgreSQL tables. Project supplies only safe
facts from the exact workspace retained with the snapshot. Brief descriptions
longer than the assessment title field receive a deterministic display-label
projection; milestone identity and version remain exact. Refusals have no
persistence side effect, exact replay preserves original server metadata, and
later snapshots append superseding history without mutation. The repository
enforces the complete-history contract's 100-item bound before commit and
serializes occurrence with a non-regressing authoritative submission time.

The protected HTTP routes, reconciled completion read, and reviewed
OpenAPI/generated client are delivered.
Assessment now also exposes retained events through a typed, read-only public
replay operation for one server-supplied learner and Project. Learner model
rebuilds bounded Project-activity completion, while Audit appends integrity/
provenance references; exact replay is idempotent and neither consumer copies
workspace state or reads another module's tables. The browser now uses those
same generated operations to select candidate-owned evidence for every
milestone, retain a stable retry identity, display bounded refusals, reopen
exact accepted evidence, and show non-mastery completion meaning. Every
learning-evidence route rejects independent Projects before requesting a
completion projection. Candidate choices use distinguishable saved-resource
labels, while accessible disclosures retain the complete safe resource,
snapshot, brief, placement, policy, sequence, and supersession provenance.
Dispatcher,
provider, execution adapter, and managed-cloud profile remain later bounded
work and must consume rather than redefine this contract.
