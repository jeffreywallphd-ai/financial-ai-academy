# Deterministic Assessment Contract

- Status: accepted for the initial single-select contract family
- Canonical for: Assessment v1 definition, presentation, submission, retained evidence, and completion-event meaning
- Ownership decision: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- Executable learning schemas: [Assessment v1](../../../contracts/learning/assessment/v1/README.md)
- Executable event schema: [Assessment completion event v1](../../../contracts/events/assessment/v1/README.md)
- Compatibility evidence: [Assessment v1 corpus](../../../contracts/compatibility/assessment/v1/README.md)
- Additive practice schemas: [Assessment practice v1](../../../contracts/learning/assessment/practice/v1/README.md)
- Additive practice evidence: [Assessment practice v1 corpus](../../../contracts/compatibility/assessment-practice/v1/README.md)

## Boundary and Authority

Assessment is the sole runtime owner of item meaning, attempts, responses,
deterministic scores, reviewed feedback selection, and bounded knowledge-check
completion evidence. Content transports an opaque immutable definition file;
Curriculum may retain an exact Assessment reference; neither grades a response.
Learner model and Audit consume the public completion event through
Assessment's typed replay operation without reading Assessment persistence or
replacing its evidence.

Version 1 supports one required `single_select` item with two to six ordered
options and exactly one selected option. The only supported policy is
`single-select-exact-match@1.0.0`: the declared correct option produces `1/1`
and reviewed correct feedback; every other declared option produces `0/1` and
reviewed corrective feedback. There is no partial credit, retake, mastery,
manual review, AI grading, randomization, or client-side scoring authority.

The additive practice-v1 family extends Assessment ownership without changing
the knowledge-check-v1 shapes. One immutable practice carries 1 through 20
ordered items. It closes response meaning to single-select exact match (2-8
options), multiple-select exact set (3-12 options, no partial credit), and
numeric exact value or inclusive range over canonical fixed-decimal strings at
scale 0 through 6. Every item is worth one point. The attempt policy is visible
contract metadata; pure scoring does not enforce attempt counts, and later
application packets retain that authority.

## Immutable Identity and Safe Presentation

The private definition identifies its assessment, semantic version, item and
item version, scoring-policy ID/version, and definition digest. The definition
digest is SHA-256 over compact, sorted-key UTF-8 JSON for the private
`assessment` object. The package manifest independently fixes the complete
definition file's size and digest. Changing item meaning, options, correct
answer, policy, or feedback requires a new immutable definition and package
version; consumers never substitute `latest`.

The learner presentation repeats only public exact-version tokens, prompt, and
ordered option IDs/labels. It excludes the correct option, feedback, and the
private scoring-policy object. Plain-text prompts, labels, and feedback reject
HTML-significant characters and control characters and have explicit length
and count limits.

Practice presentation repeats its exact placement, package, definition,
practice, item, policy, source, and review-reference provenance. It excludes
correct option identities, accepted numeric values/ranges, the private policy
object, and all feedback branches. The pure parser/projector returns immutable
typed values and performs no persistence, network, clock, or scoring side
effect. Its presentation value is transport-neutral. The protected HTTP route,
reviewed OpenAPI snapshot, generated TypeScript client, and future supported
clients all map the same public operation rather than create a browser-owned
contract.

## Submission and Evidence

A submission contains an opaque UUID, placement and exact package tokens,
exact Assessment/item/policy tokens, and one selected option ID. Learner
identity and time are server-supplied. A stale token, unknown option, malformed
shape, unsupported version/type/policy, or private-field expansion fails
closed.

The result contract is also the bounded retained-evidence record. It carries
opaque attempt/evidence/learner/submission IDs, exact placement/content/
Assessment/item/policy provenance, the selected option, deterministic score,
correctness, reviewed feedback ID/text, and server timestamp. It does not
claim lesson completion, mastery, suitability, performance, or advice.

Practice submission is a separate additive whole-attempt record. It carries
one response per exact definition item and no learner identity or time.
Response array order is semantically irrelevant; item IDs correlate the set,
multiple selections are exact unordered sets, and results return in definition
order. The canonical request fingerprint sorts responses by item ID and
multiple selections by option ID before hashing compact sorted-key UTF-8 JSON.
Equivalent ordering therefore has one request identity.

Single select is exact option match, multiple select is exact set with no
partial credit, and numeric entry uses `Decimal` against the exact value or
inclusive range at the declared canonical scale. Each item is zero or one; the
activity result sums them and reports `all_correct` or `review_needed`. Only the
applicable reviewed feedback and references are returned. Correct answer
values, numeric ranges, private evaluator objects, mastery, suitability, and
advice remain absent.

The transport-neutral `submit_placed_practice` application operation accepts
server-resolved learner context, one route-bound placement ID, and the exact
versioned submission document. It resolves Curriculum and Content only through
their public facades, re-parses the exact private definition, supplies server
IDs and canonical UTC time, and invokes the accepted parser/scorer. The
protected HTTP host and reviewed generated client expose this operation to
browser, command-line, service, and future headless consumers instead of
letting any caller own scoring, replay, or persistence.

`POST /api/v1/curriculum/placements/{placement_id}/practice/submissions`
accepts the closed versioned submission body and resolves learner identity only
from the opaque server session. The route and body placement must match. The
response returns exact public provenance, submitted values, deterministic
scores, applicable feedback, review references, evidence IDs, and UTC time,
while omitting learner identity, the internal request fingerprint, correct
answers, private evaluator declarations, and diagnostics. OpenAPI is the
reviewed source for the TypeScript client, so direct and browser callers share
one contract. This does not define an AI-specific mode, protocol, credential,
tool surface, or autonomous authority.

Assessment retains each accepted practice aggregate in separate additive
attempt, ordered-response, item-score, completion-result, and practice-outbox
tables in one PostgreSQL transaction. `(learner_id, submission_id)` plus the
canonical request fingerprint provides idempotent replay. A matching replay
returns the original complete result; conflicting reuse fails, and a distinct
submission after the same placed practice version completes is denied until
the retry slice supplies explicit policy. Every accepted row rejects ordinary
update/delete. No Content, Curriculum, host, client, or future AI consumer may
read or write these private tables.

## Completion Event

`assessment.knowledge-check.completed@1.0.0` is owned by Assessment. Its event
ID is the delivery deduplication identity; its idempotency key and source
reference equal the durable evidence ID; its aggregate is the attempt. The
bounded payload contains exact learning context and score but excludes the
selected option, correct answer, feedback, and private definition. Learner
model and Audit synchronously replay this event through the Assessment public
query for the initial completion-history path. The event contract does not
select a queue, broker, dispatcher, background worker, checkpoint, or delivery
guarantee.

`assessment.practice.completed@1.0.0` is the additive practice event contract.
It correlates server-issued event, attempt, evidence, learner, submission,
placement, definition, and time metadata to one bounded score/provenance
summary. Submitted values and feedback stay in Assessment's result boundary
instead of being broadcast to consumers. The pure mapper validates this
correlation but does not persist, dispatch, publish, or make the event a
mastery signal. Result and event timestamps use canonical UTC RFC 3339 text
ending in `Z`; equivalent non-zero offsets are not accepted contract forms.

## Compatibility and Diagnostics

The compatibility corpus fixes correct and incorrect chains, canonical
definition and package digests, the immutable `intro-risk-return@1.1.0`
successor, and stable bounded denial codes:

- `assessment.unsupported_version`
- `assessment.unsupported_item_type`
- `assessment.unsupported_policy`
- `assessment.unsupported_event_version`
- `assessment.schema_invalid`
- `assessment.definition_digest_mismatch`
- `assessment.invalid_definition`
- `assessment.presentation_leak`
- `assessment.stale_reference`
- `assessment.unknown_option`
- `assessment.inconsistent_evidence`
- `assessment.inconsistent_event`
- `assessment.practice.unsupported_version`
- `assessment.practice.unsupported_item_type`
- `assessment.practice.unsupported_policy`
- `assessment.practice.schema_invalid`
- `assessment.practice.definition_digest_mismatch`
- `assessment.practice.invalid_definition`
- `assessment.practice.invalid_decimal`
- `assessment.practice.presentation_leak`
- `assessment.practice.stale_reference`
- `assessment.practice.invalid_response`
- `assessment.practice.result_leak`
- `assessment.practice.invalid_server_metadata`

Diagnostics identify only a bounded field/reference and stable code. They do
not echo learner responses, correct answers, fixture bytes, paths, stack
traces, or provider data.

## Implemented Core and Remaining Gaps

The focused Python conformance suite directly validates all five Draft 2020-12
schemas, cross-record invariants, independent `0/1` outcomes, answer secrecy,
denial behavior, canonical digests, and preservation of the accepted 1.0.0
lesson bytes. The implemented Python module additionally validates exact
Content/Curriculum public resolution, generates the safe presentation, scores
both outcomes, and commits append-oriented attempt/response/score/completion
evidence plus the outbox event in one PostgreSQL transaction. Unique database
constraints and application results distinguish exact replay, conflicting
reuse, and a new submission after completion; accepted tables reject ordinary
update/delete.

Direct tests cover real PostgreSQL 18.4 migration/reapply/teardown, concurrent
duplicate submission, transactional rollback before outbox insertion, event
confidentiality, and the unchanged lesson-read database path. The protected
HTTP/generated-client path, answer-safe browser submission, Learner-model
rebuild, Audit reconciliation, and private-host live close/reopen path are also
directly covered. Background delivery, recovery, managed cloud, built-in/OIDC,
production database roles, and broader Assessment families remain gaps.

Practice v1 now has executable private-definition and safe-presentation
schemas plus whole-attempt submission, result, and completion-event schemas; a
canonical compatibility corpus; additive package admission; exact Content
retrieval; immutable Curriculum placement; a production parser/projector and
public open operation; protected HTTP/OpenAPI; a generated TypeScript client;
browser opening; and real-PostgreSQL composition evidence. Its pure submission
adapter now validates closed responses, canonicalizes request identity, scores
all three item types, selects reviewed feedback, and maps a safe correlated
event without side effects. The transport-neutral application operation now
resolves the exact definition, supplies server authority, and commits a
complete append-only aggregate plus practice outbox atomically. Real-
PostgreSQL evidence covers migration/reapply/teardown, exact and reordered
replay, conflict, one-attempt enforcement, concurrency, rollback, restart,
confidentiality, and mutation denial without changing knowledge-check storage.
Repeated opening remains read-only and returns no answer or feedback branch.
Authorization host composition, the public POST, reviewed OpenAPI, generated
client, bounded denials, and direct non-browser result confidentiality are now
covered. Browser result flow, retry enforcement, history/replay consumers, and
live local submission remain unqualified until their owning packets deliver
them. No separate AI/headless mode is defined; the shared public API remains
the supported non-browser seam and keeps a future consumer possible without
creating another domain core.

Assessment now also exposes a typed, read-only completion-event replay query
for one server-supplied learner and exact placement. It validates retained
outbox documents against this executable schema, rejects malformed,
unsupported, or inconsistent envelopes, filters without cross-module access,
and returns stable occurrence/event-ID ordering. Repeated reads do not mutate
or acknowledge evidence. This is an application query for deterministic
consumer replay; it does not choose a queue, dispatcher, worker, checkpoint,
delivery guarantee, or managed-cloud topology.
