---
id: WRK-0006
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-agent
updated: 2026-08-05
parent: SLI-0002
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: [contracts/learning/assessment/v1, contracts/events/assessment/v1, contracts/compatibility/assessment/v1, contracts/compatibility/lesson-package/v1/approved/intro-risk-return-knowledge-check, backend/pyproject.toml, backend/uv.lock, backend/tests/contract/assessment, contracts/README.md, contracts/learning/README.md, contracts/events/README.md, contracts/compatibility/README.md, docs/contracts/README.md, docs/architecture/contracts/assessment-contract.md, docs/architecture/contracts/content-package-contract.md, docs/domain/README.md, docs/architecture/assurance/architecture-verification.md, docs/assurance/known-verification-gaps.md]
generated_artifacts: [backend/uv.lock, contracts/compatibility/assessment/v1/vectors]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0006:e6b61dcb-036c-4d6f-a165-90a50b3529a5
claimed_by: codex-agent
claimed_at: 2026-08-05T13:07:02Z
---

# Agent Work Packet: Establish Deterministic Assessment Contracts

## Objective and Deliverable

Establish the executable, language-neutral contract family and conformance
corpus for SLI-0002's one-question deterministic knowledge check. The
observable technical result is a new immutable introductory-lesson fixture
version whose Assessment-owned definition, learner presentation, submission,
result/evidence, and completion-event records validate reproducibly while the
published `intro-risk-return@1.0.0` fixture remains byte-for-byte unchanged.

## Required Context

Before any file change, prominently read and follow every applicable
`AGENTS.md` and the repository-root `docs/README.md`. Route through the
baseline pack with `learning-adaptation` as primary and `security-risk` as
adjacent. Read SLI-0002, SLI-0001's contract handoff, ADR-0002, ADR-0005,
ADR-0007, ADR-0008, the contract architecture and compatibility rules, the
content-package contract, module ownership, learning-evidence vocabulary,
community evidence protection, education-versus-advice guidance, current
lesson-package schemas/fixtures, contract runners, dependency metadata, and
nearest contract/backend READMEs.

## Decisions and Assumptions

- Version 1 supports exactly one required single-select item, one selected
  option, integer score `0` or `1`, maximum score `1`, and bounded reviewed
  correct/incorrect feedback. No partial credit, ordering, randomization,
  free text, numeric tolerance, manual review, or AI behavior is permitted.
- The Assessment definition is private contract input. A separate learner
  presentation excludes the correct option and scoring internals. Feedback is
  bounded platform-authored plain text; it is not HTML or executable markup.
- Definition identity includes `assessment_id`, semantic
  `assessment_version`, definition digest, item ID/version, and exact scoring
  policy identifier. Package, definition, or scoring changes require a new
  immutable version; consumers never substitute `latest`.
- A submission carries an opaque submission ID, the exact public version
  references supplied with the presentation, and one option ID. Identity and
  server time are supplied by the application boundary, not selected by the
  browser.
- The completed evidence contract carries opaque attempt/evidence IDs, exact
  learner/content/assessment/item/scoring provenance, selected option ID,
  score/max score, correctness, bounded feedback reference/text, and server
  timestamp. It makes no mastery or lesson-completion projection claim.
- The initial event type is versioned as an Assessment-owned knowledge-check
  completion event. It is suitable for later idempotent Learner-model and
  Audit consumers but this packet creates no consumer, queue, broker, or
  delivery guarantee.
- Exact JSON Schema identifiers, canonical fixture bytes, negative cases, and
  digest vectors become compatibility-sensitive outputs. Contract test
  dependencies must be exact, reviewed, and locked.

## In Scope

- Draft 2020-12 schemas for the single-select definition, safe presentation,
  submission command, deterministic result/evidence, and Assessment-owned
  completion event.
- A documented event envelope with owner, event ID/type/version, occurrence
  time, aggregate/source references, idempotency identity, and bounded payload.
- Positive fixtures for correct and incorrect submissions plus independent
  expected scores, feedback, evidence, and event payloads.
- Negative fixtures for unsupported versions/policies/types, duplicate or
  missing IDs/options, invalid correct-option membership, multiple/no selected
  option, stale references, unsafe feedback, oversize values, unknown fields,
  malformed timestamps/digests, and evidence/event inconsistencies.
- A new immutable successor lesson fixture containing the complete definition
  and preserving the existing package schema, path, integrity, source, and
  education-only rules.
- A dependency-light Python conformance runner and focused tests that do not
  depend on application services, PostgreSQL, API models, or browser code.
- Contract catalog, semantic ownership, compatibility, direct-evidence, and
  remaining-gap documentation made necessary by these exact shapes.

## Out of Scope

- Assessment application behavior, domain scoring implementation, attempts,
  PostgreSQL tables, migrations, outbox persistence, module gateways, API
  operations, generated TypeScript, UI, or local composition.
- Learner-model projection, Audit consumption, event delivery infrastructure,
  retakes, attempt limits, history, recovery tooling, managed cloud, authoring,
  external standards, imports, or additional item/scoring types.
- Mutation or replacement of any accepted SLI-0001 package bytes, schema IDs,
  digest vectors, API behavior, or evidence claims.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment contracts | Contract architecture, ownership, compatibility policy | `contracts/learning/assessment/v1/` | Exact portable definition, presentation, submission, and evidence shapes |
| Event contract | Event governance and future consumers | `contracts/events/assessment/v1/` | Versioned owner and idempotency semantics without selecting delivery infrastructure |
| Conformance corpus | Lesson-package corpus and security denials | `contracts/compatibility/assessment/v1/` | Independent expected results and malformed/version fixtures |
| Successor package | Existing immutable approved fixture | New `intro-risk-return-knowledge-check/` fixture only | Add the complete Assessment definition without mutating `1.0.0` |
| Contract runner | Existing Python contract-test pattern | `backend/tests/contract/assessment/` and exact dependency metadata | Executable cross-record invariants and deterministic vectors |
| Canonical docs | Contract/domain/assurance sources | Exact named documentation in `write_scope` | Record semantic ownership and direct contract evidence only |

## Contracts and Interfaces

The packet must define one closed contract chain:

1. a private immutable definition with prompt, ordered option IDs/labels,
   exact correct option, scoring policy, and two bounded feedback messages;
2. a learner presentation with the same public identity/version/digest and
   options but no correct option or scoring internals;
3. a submission containing an opaque submission ID, exact version tokens, and
   one selected option ID;
4. deterministic evidence/result values for score `0|1`, maximum `1`,
   correctness, safe feedback, attempt/evidence IDs, and full provenance; and
5. one Assessment-owned completion event that refers to the durable evidence
   rather than duplicating an unbounded response or becoming projection state.

Stable contract codes must distinguish malformed, unsupported, stale/mismatch,
unknown option, conflicting submission, and unsafe definition conditions. Raw
correct-answer material, learner responses, fixture bytes, filesystem paths,
stack traces, and provider data never enter diagnostics.

## Dependencies and Parallel Safety

SLI-0001 is complete and supplies the immutable package, contract-runner, and
compatibility baseline. This is the first SLI-0002 packet and has no packet
dependency. Its schemas and vectors are accepted inputs for every later
packet, so it has no parallel-safe peer. WRK-0007 may start only after the
contract family, event shape, successor fixture digest, and denial corpus are
stable and this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Valid definition | One bounded item with unique options and one matching correct option | Definition validation runs | The private definition and safe learner presentation validate with identical public version tokens | Schema and semantic tests |
| Correct response | The selected option matches the fixed correct option | Expected-result evaluation runs | Score is exactly `1/1`, correctness is true, and reviewed correct feedback is selected | Independent fixture vector |
| Incorrect response | A declared non-correct option is selected | Expected-result evaluation runs | Score is exactly `0/1`, correctness is false, and reviewed corrective feedback is selected | Independent fixture vector |
| Presentation secrecy | A learner presentation is inspected | It is validated and serialized | Correct option and private scoring fields are absent | Negative structural assertion |
| Malformed definition or response | IDs, versions, options, membership, policy, shape, size, or feedback violates the profile | Conformance runs | Validation fails with a stable bounded code and emits no result/evidence/event | Negative corpus |
| Stale or mismatched provenance | Package, definition, item, policy, or digest tokens disagree | Cross-record validation runs | The chain fails closed and never normalizes to a newer version | Compatibility tests |
| Evidence/event consistency | Valid result, evidence, and event fixtures are compared | Cross-record validation runs | IDs, versions, score, time, and source references match exactly | Cross-schema invariant tests |
| Immutable successor | Existing and successor package fixtures are indexed | Digests are calculated repeatedly | `1.0.0` is unchanged; the new version has stable distinct bytes and digest | Package and assessment vector tests |
| Unsafe or excessive content | Feedback, labels, IDs, counts, or nesting exceed the bounded plain-text profile | Validation runs | Input is rejected without execution, fetch, HTML interpretation, or raw diagnostic echo | Security/resource tests |

## Verification Commands

```powershell
py -m uv sync --project backend --frozen
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/lesson_package backend/tests/contract/assessment
python dev-tools/documentation/check_docs.py
python dev-tools/planning/check_planning.py
python dev-tools/agent/check_ready.py
git diff --check
```

Inspect the exact dependency licenses and advisories if dependency metadata
changes. Report any external registry/advisory lookup not performed rather
than implying it ran.

## Documentation and Evidence Update

Document the Assessment contract family, scoring authority, safe-presentation
split, evidence/event semantics, exact fixture version/digest, conformance
commands, compatibility commitments, and direct versus gap evidence. Do not
claim application scoring, persistence, delivery, API, UI, recovery, cloud, or
end-to-end coverage. Update derived context only after its canonical source is
changed and only if the existing summary becomes stale.

## Stop Conditions

- Exact shapes would require a second item/scoring type, retake policy,
  completion/mastery projection, manual/AI grading, authoring, or external
  learning-standard decision.
- The safe presentation cannot exclude correct-answer/scoring internals.
- Independent expected vectors cannot reproduce score, feedback, evidence, or
  event bytes deterministically.
- A contract change would mutate SLI-0001 fixture bytes or silently reinterpret
  an accepted package, assessment, or evidence version.
- Event design requires selecting a queue, broker, delivery guarantee, or
  consumer policy that remains decision-required.
- Sensitive or untrusted values cannot be bounded and redacted, a dependency
  has incompatible provenance/license/security posture, canonical authority
  conflicts, or another active packet overlaps scope.

## Required Handoff

Implementation evidence recorded 2026-08-05:

- Added Draft 2020-12 schema IDs for `definition`, `presentation`,
  `submission`, `result`, and
  `assessment.knowledge-check.completed@1.0.0`. The only item/policy profile is
  `single_select` plus `single-select-exact-match@1.0.0`, with independent
  expected `1/1` correct and `0/1` incorrect vectors.
- The presentation excludes correct-answer, feedback, and private scoring
  fields. Evidence retains the bounded selected option and exact provenance;
  the event refers to evidence and excludes the response, answer, and
  feedback.
- The definition meaning digest is
  `98e941f9b53ef429cb6d359246ddb9812e354db2a9381a2ee180ed5758343d2b`.
  The immutable `intro-risk-return@1.1.0` package digest is
  `7cf84bc2f7483d9131db315260b3812f3ea29821bf296571c0c7e38f05b536bc`;
  its lesson bytes exactly match the accepted 1.0.0 fixture.
- The compatibility corpus covers 20 malformed, unsupported, stale, unknown,
  unsafe, inconsistent-evidence, and inconsistent-event denials with stable
  bounded codes. No raw response, correct option, fixture bytes, path, or
  stack trace is emitted by its CLI diagnostics.
- `backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/lesson_package backend/tests/contract/assessment -q`
  passed `56` tests. Documentation, planning, whitespace, planning-skill
  behavior/discovery, and aggregate agent-readiness checks passed.
- No dependency metadata changed; the runner reuses locked `jsonschema==4.26.0`
  and the standard library. No external registry, license service, or advisory
  lookup was performed in this packet.
- Canonical Assessment/content/domain semantics, contract catalogs, and
  direct-versus-gap assurance were reconciled. Application scoring,
  PostgreSQL evidence/outbox, API/client, UI, event delivery/consumers,
  recovery, cloud, additional item types, retakes, mastery, and AI remain
  unsupported and pass to later packets or slices.

Report every schema ID/version, the exact item/scoring profile, safe/private
field split, event type and idempotency semantics, successor package identity
and digest, fixture/vector inventory, denial codes, dependency review, exact
commands/results, documentation changes, compatibility commitments, residual
contract risks, and unsupported capabilities handed to WRK-0007.

## Planning History

- 2026-08-05: Shaped from SLI-0002 boundary seam 1; planning approval and implementation activation remain separate local-only stages.
