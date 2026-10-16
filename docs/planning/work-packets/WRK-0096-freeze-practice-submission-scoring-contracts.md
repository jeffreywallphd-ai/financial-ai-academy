---
id: WRK-0096
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0027
capability: CAP-0006
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/practice_submission_contract.py", "backend/src/financial_ai_academy/modules/assessment/domain/practice.py", "backend/src/financial_ai_academy/modules/assessment/ports/practice_submission.py", "backend/tests/contract/assessment_practice", "backend/tests/unit/assessment/test_practice_scoring.py", "contracts/compatibility/assessment-practice/v1", "contracts/learning/README.md", "contracts/learning/assessment/practice/v1", "docs/architecture/contracts/assessment-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0027-submit-and-score-practice-attempt.md", "docs/planning/work-packets/WRK-0096-freeze-practice-submission-scoring-contracts.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Freeze Practice Submission and Scoring Contracts

## Objective and Deliverable

Freeze additive Assessment-owned practice submission, result, and completion-
event contracts plus pure deterministic validation and scoring for all three
SLI-0026 item types. Deliver executable schemas, independently fixed approved
records, a bounded denial corpus, immutable domain values, canonical request
identity, and transport-neutral parser/scorer evidence. The result is the
stable input to the later application/persistence packet; it adds no database,
HTTP operation, generated client, browser behavior, or separate AI mode.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, security-risk, testing-quality, and delivery-planning
context. Read the change-impact matrix, decision readiness, CAP-0006,
SLI-0026, SLI-0027, ADR-0005, ADR-0007, the Assessment and content-package
contracts, contract/versioning standards, Assessment module README, existing
practice v1 schemas/corpus/parser/domain/tests, existing knowledge-check
submission/result/event semantics, nearest contract READMEs, and concurrent-
work rules.

## Decisions and Assumptions

- Extend the additive `assessment/practice/v1` family with separate submission,
  result, and completion-event schemas. Do not widen or reinterpret existing
  knowledge-check-v1 records.
- One submission covers the whole exact practice. It contains one response per
  definition item, keyed by stable item ID, plus the exact placement/package/
  practice/definition provenance visible in the presentation.
- Request response order is semantically irrelevant. Validation correlates by
  item ID, rejects missing, duplicate, extra, unknown, or wrong-type responses,
  and returns results in private definition order.
- Single select carries one `selected_option_id`. Multiple select carries a
  nonempty unique `selected_option_ids` array whose order is semantically
  irrelevant. Numeric entry carries one canonical fixed-decimal `entered_value`
  matching the definition's exact scale and sign rule.
- A canonical request fingerprint is lowercase SHA-256 over compact sorted-key
  UTF-8 JSON after responses are sorted by item ID and multiple selections are
  sorted by option ID. Equivalent request/selection ordering must yield the
  same fingerprint. Text is encoded with `ensure_ascii=false` and receives no
  implicit Unicode normalization.
- Each item has score zero or one and maximum one. Multiple select is exact-set
  scoring without partial credit. Numeric comparison uses `Decimal` and the
  private exact or inclusive-range rule. The applicable correct/incorrect
  feedback branch and its approved review references are returned.
- Activity score is the sum of ordered item scores. `all_correct` means total
  equals maximum; otherwise `review_needed`. Activity review references are
  the stable definition-order union of applicable item-feedback references,
  de-duplicated by ID.
- Result and event records retain exact versions/digests and opaque server-
  issued attempt/evidence/event IDs and timestamp, but this pure packet does
  not issue those values or persist anything.

## In Scope

- Add Draft 2020-12 submission, result, and completion-event schemas to the
  existing practice-v1 family with closed response/result unions and resource
  bounds inherited from the definition contract.
- Extend the compatibility corpus with one independently fixed approved
  submission/result/event chain, canonical request fingerprint vector, order-
  equivalent vector, and table-driven denials for malformed, unsupported,
  stale, incomplete, extra, duplicate, or answer-leaking meaning.
- Extend the dependency-light conformance runner to validate exact chain
  correlation, canonicalization, deterministic scores/feedback/summary,
  provenance, event/result equivalence, and closed private-data boundaries.
- Add immutable practice response, item outcome, aggregate result, and
  submission-candidate domain values plus pure scoring functions.
- Add a narrow Assessment-owned submission contract port/adapter that parses
  the transport-neutral request, validates it against one exact private
  definition/context, computes the canonical fingerprint, scores it, and maps
  supplied server metadata to a safe result/event document.
- Add contract and unit tests for accepted and denied meaning, every supported
  scoring branch, order independence, fixed-decimal boundaries, safe feedback,
  anti-rigidity, and unchanged knowledge-check/practice-opening behavior.
- Update the Assessment contract, module README, and learning-contract catalog
  with exact ownership, versioning, scoring semantics, and deferred boundaries.

## Out of Scope

Assessment application service/public operation changes; repository ports or
adapters; SQLite/PostgreSQL tables or migrations; transactions, uniqueness,
concurrency, idempotent retrieval, outbox storage, restart behavior; HTTP,
OpenAPI, generated client, browser UI, session/authorization composition, live
qualification; retry/resume/history/projections/replay consumers; new response
types or scoring policies; AI/model/manual grading; adaptive selection;
arbitrary execution; external providers; and separate headless AI-mode
planning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Executable contracts | existing practice definition/presentation and knowledge-check submission/result/event families | additive practice submission/result/event schemas and practice catalog | Freeze whole-attempt transport and evidence meaning without changing existing records |
| Compatibility evidence | current practice and Assessment corpus conventions | practice-v1 approved records, vectors, denials, runner, and tests | Fix correlation, canonicalization, scoring, feedback, confidentiality, and event meaning |
| Assessment domain | current practice values and knowledge-check scorer | practice response/result values and pure scoring helpers | Keep deterministic policy transport- and storage-neutral |
| Contract adapter | practice definition adapter and its port | new practice-submission port/adapter and focused unit tests | Parse and score exact input without application, persistence, clock, or identity side effects |
| Canonical guidance | Assessment contract, module README, learning contract catalog | listed documentation | Record owned semantics and remaining boundaries |
| Planning evidence | SLI-0027, WRK-0096, register | listed planning files | Keep JIT lifecycle synchronized |

No existing schema identifier, approved knowledge-check fixture, digest,
database, migration, public service method, repository port, API route,
OpenAPI snapshot, generated client, web file, dependency, or lockfile may
change.

## Contracts and Interfaces

`assessment-practice-submission-v1` carries `schema_version`, a UUID
`submission_id`, exact placement/package/definition/practice selectors, and a
bounded array of closed responses. Each response repeats item ID/version,
item type, scoring-policy ID/version, and exactly the value allowed by its
type. It never carries learner identity, score, feedback, correct answers,
timestamps, or server evidence IDs.

`assessment-practice-result-v1` carries server-issued attempt/evidence IDs,
learner and original submission IDs, exact activity provenance, aggregate
score/max/summary, ordered item results, applicable feedback and approved
review-reference IDs, and one UTC `submitted_at`. Item results echo only the
learner's submitted value and the applicable safe feedback. They do not carry
correct answer values or private evaluator objects.

`assessment.practice.completed@1.0.0` wraps the exact safe result payload plus
a server-issued event ID and occurred time. The event result and top-level
correlation must agree exactly. This packet validates and maps documents but
does not write or publish the event.

The submission adapter accepts bytes, one exact `PracticeDefinition`, its
`PracticePresentationContext`, and supplied server metadata. It returns an
immutable submission candidate containing the canonical request fingerprint,
safe aggregate result, and completion-event document, or one bounded
`assessment.practice.*` failure with a safe reference. It performs no
persistence, clock, network, identity lookup, authorization, provider, model,
API, or UI action.

## Dependencies and Parallel Safety

SLI-0026 is complete; SLI-0027 is selected and ready inside the current
approved CAP-0006 package. This first packet has no WRK dependency. It owns the
shared practice schemas, corpus, Assessment contract documentation, and
planning register, so it is not parallel-safe with another packet changing
those files. WRK-0096 must complete before the application/persistence packet
is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete attempt | One valid response exists for every item in an exact definition | Submission validation and scoring run | Ordered item outcomes, aggregate total, summary, safe feedback, references, result, and event match fixed evidence | schema/runner/unit |
| All scoring branches | Correct and incorrect single, exact/non-exact multiple, and exact/range numeric values are supplied | Pure scoring runs | Every item returns only zero or one and its matching reviewed feedback branch | parameterized unit/contract |
| Order independence | Response objects and selected-option arrays are reordered without changing meaning | Canonical request identity and scoring run | Fingerprint, ordered results, total, summary, and event meaning remain equivalent | vector/unit |
| Exact decimal | Scale 0 and 6, negative permission, exact bounds, and inclusive range endpoints are used | Decimal validation/scoring run | Valid canonical values compare exactly; floats, exponents, locale separators, negative zero, leading zeroes, sign or scale mismatches fail | vector/unit |
| Shape flexibility | Valid practice item counts, type combinations, option/reference counts, and response order vary | Contracts and scoring run | Meaning is accepted without fixture-specific count or sibling-order assumptions | generated contract/unit cases |
| Closed attempt | Missing, duplicate, extra, unknown, wrong-type, stale-version, unknown-option, empty multiple, or private-field input is supplied | Validation runs | One bounded failure occurs before any candidate is returned | denial corpus/unit |
| Safe result | Private answers, ranges, evaluator objects, and unused feedback branches exist in the definition | Result/event documents are serialized | Only submitted values and applicable safe feedback/references appear; private meaning is absent recursively | secrecy tests |
| Event correlation | Result or event identity, timestamp, version, score, or item provenance is mutated | Chain validation runs | Stale or malformed evidence fails with a bounded diagnostic | denial corpus |
| Existing behavior unchanged | Existing knowledge-check and practice-opening suites run | New files are present | Accepted contracts, digests, presentation, and service behavior remain unchanged | regression suites |
| Side-effect freedom | Parser/scorer are invoked repeatedly | Outputs and repository state are inspected | Results are deterministic and no persistence, clock, network, event publication, learner state, or completion row is created | unit/architecture |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_practice backend/tests/unit/assessment/test_practice_contract.py backend/tests/unit/assessment/test_practice_scoring.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment backend/tests/unit/assessment/test_assessment_service.py backend/tests/unit/assessment/test_practice_service.py
python dev-tools/architecture/check_architecture.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0096-freeze-practice-submission-scoring-contracts.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Submit one exact candidate, generate a fresh affected-verification receipt, and
obtain one independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document request/result/event shape, canonical response identity, closed
response and scoring semantics, decimal and exact-set rules, feedback/reference
selection, answer confidentiality, server-metadata boundary, unchanged
knowledge-check/practice-opening behavior, and deferred persistence/API/UI
work. Record exact commands and results, candidate and receipt, review
disposition, assumptions, and residual gaps in this packet and SLI-0027. Keep
approval and reviewer records only in the ignored local ledger.

## Stop Conditions

Stop for a breaking existing Assessment or practice-opening contract; ambiguous
request identity, scoring, decimal, feedback, or event meaning; private-answer
leakage; a requirement for partial credit, weights, free text, files, code,
notebooks, randomized items, arbitrary execution, AI/model/manual authority,
external provider semantics, client-side scoring, persistence/API/client/UI
change, new dependency, active scope collision, conflicting canonical source,
or material CAP-0006/SLI-0027 drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional prose polish, or another inconsequential in-scope correction.
Fix it locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; frozen request/result/event versions; canonical
fingerprint and response-order rules; scores, feedback, confidentiality and
denial evidence; legacy regressions; focused, architecture, affected,
aggregate, receipt, and review results; changed files; documentation impact;
assumptions; and residual gaps. Confirm that no persistence, migration,
transaction, API, generated client, browser UI, learner projection, replay
consumer, retry/history, AI mode, model authority, dependency, or external
execution changed, then leave JIT-B dependency-ready.

## Implementation Evidence

Not started.

## Planning History

- 2026-10-16: Authored just in time after SLI-0027 selection. The packet
  freezes whole-practice submission, result, completion-event, canonical
  identity, and pure deterministic scoring meaning without adding persistence,
  HTTP/UI behavior, a lower-level approval, or a separate AI mode.
