# Deterministic Assessment Contract

- Status: accepted for the initial single-select contract family
- Canonical for: Assessment v1 definition, presentation, submission, retained evidence, and completion-event meaning
- Ownership decision: [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- Executable learning schemas: [Assessment v1](../../../contracts/learning/assessment/v1/README.md)
- Executable event schema: [Assessment completion event v1](../../../contracts/events/assessment/v1/README.md)
- Compatibility evidence: [Assessment v1 corpus](../../../contracts/compatibility/assessment/v1/README.md)

## Boundary and Authority

Assessment is the sole runtime owner of item meaning, attempts, responses,
deterministic scores, reviewed feedback selection, and bounded knowledge-check
completion evidence. Content transports an opaque immutable definition file;
Curriculum may retain an exact Assessment reference; neither grades a response.
Learner model and Audit may later consume the public completion event without
reading Assessment persistence or replacing its evidence.

Version 1 supports one required `single_select` item with two to six ordered
options and exactly one selected option. The only supported policy is
`single-select-exact-match@1.0.0`: the declared correct option produces `1/1`
and reviewed correct feedback; every other declared option produces `0/1` and
reviewed corrective feedback. There is no partial credit, retake, mastery,
manual review, AI grading, randomization, or client-side scoring authority.

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

## Completion Event

`assessment.knowledge-check.completed@1.0.0` is owned by Assessment. Its event
ID is the delivery deduplication identity; its idempotency key and source
reference equal the durable evidence ID; its aggregate is the attempt. The
bounded payload contains exact learning context and score but excludes the
selected option, correct answer, feedback, and private definition. This
establishes event meaning and atomic-persistence input only. It does not select
a queue, broker, dispatcher, delivery guarantee, Learner-model consumer, or
Audit consumer.

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
confidentiality, and the unchanged lesson-read database path. HTTP
authorization/composition, OpenAPI/generated client, UI, outbox delivery and
consumption, Learner-model/Audit projection, recovery, managed cloud, and
end-to-end behavior remain gaps.
