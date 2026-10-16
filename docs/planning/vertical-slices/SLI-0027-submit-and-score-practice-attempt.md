---
id: SLI-0027
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: CAP-0006
depends_on: ["SLI-0026"]
decision_gates: []
---

# Vertical Slice: Submit and Score a Practice Attempt

## Outcome and User Scenario

An authorized learner answers every item in one exact placed practice activity,
submits the attempt once, and receives deterministic item-level and activity-
level feedback. Assessment retains the exact responses, scores, completion
evidence, and provenance atomically. The browser and non-browser/headless
clients submit through the same versioned public API; no browser-only scoring,
AI-specific transport, or autonomous action authority is introduced.

## Scope Boundaries

### In Scope

- Define a closed versioned submission and result contract for the three
  SLI-0026 response types: single select, multiple select, and fixed-decimal
  numeric entry.
- Accept responses in any request order, correlate them by stable item ID, and
  return item results in definition order. Reject missing, duplicate, extra,
  unknown, or incompatible responses without retaining partial evidence.
- Canonicalize semantically unordered multiple-selection values for request
  identity and require canonical decimal strings at the definition's exact
  scale. Never use binary floating-point scoring.
- Keep authorization, response validation, scoring, feedback selection,
  timestamps, completion IDs, and durable state changes server-authoritative.
- Score each supported item deterministically against the exact private
  definition and return the applicable approved feedback and review references
  without exposing answer keys or evaluator declarations.
- Retain append-only attempt, item response, item score, completion, and
  transactional outbox evidence against exact learner, placement, package,
  definition, schema, item, and policy versions or digests.
- Make exact replays with the same learner, submission ID, and canonical input
  return the original result. Reject the same submission ID with different
  input and reject a second completed attempt until SLI-0028 owns retry policy.
- Expose one protected public POST operation through reviewed OpenAPI and the
  generated TypeScript client, then use that generated client in the accessible
  browser flow.
- Prove that command-line, service, browser, and future headless AI consumers
  can use the same public application API. Planning a separate AI mode, agent
  protocol, tool-calling surface, or autonomous authority remains out of scope.

### Out of Scope

- Partial-save, interruption resume, retries, attempt history, comparison,
  review navigation, projection rebuild, or replay consumers; these remain
  SLI-0028 and SLI-0029 work.
- Mastery inference, competency projection, adaptive ranking, recommendation,
  AI-authored questions, model/manual grading, generative feedback, or
  personalized financial advice.
- Free text, essays, code, files, notebooks, spreadsheets, executable
  expressions, randomized questions, new response types, partial credit, item
  weighting, negative scoring, or client-defined scoring rules.
- Instructor override, certification, proctoring, external item banks,
  organization tenancy, managed-cloud recovery, or a separate local/cloud core.
- Styling-only cleanup that does not impair meaning, operation, accessibility,
  or theme parity; optional polish may remain for CAP-0031.

## Canonical Context and Decisions

- [CAP-0006](../capabilities/CAP-0006-practice-and-demonstrate-understanding.md)
  defines this second observable increment and its deterministic evidence
  boundary.
- [SLI-0026](SLI-0026-open-versioned-practice-activity.md) supplies the exact
  closed definition, answer-safe presentation, placement, public opening API,
  and generated-client path that this slice extends.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  assigns practice attempts, response validation, scoring, and feedback to
  Assessment while Content and Curriculum retain their distinct authorities.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
  keeps the exact definition in immutable platform package bytes without
  making package transport a grader.
- [Assessment Contract](../../architecture/contracts/assessment-contract.md)
  establishes deterministic authority, idempotent append-only evidence,
  server-owned identity and time, and transaction boundaries.
- Existing knowledge-check submission is a behavioral precedent, not a table
  shape to overload: multi-item practice evidence receives an additive owned
  model and preserves existing knowledge-check semantics.
- Decision readiness is sufficient for deterministic closed-item scoring and
  append-only evidence. Model/manual grading, AI authority, tenancy, external
  providers, and managed-cloud recovery remain outside this selection.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver whole-attempt contracts, server scoring, atomic evidence, protected API, generated client, and browser result flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Deliver scoring and persistence through a backend/API operation while deferring the learner-visible result flow | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Score in the browser or retain responses in browser storage before server submission | no - it makes an untrusted client authoritative and cannot provide durable completion evidence | - | - | - | - | - | - | - |
| D. Persist each answer independently and add resume/retry/history in this increment | no - it materially overlaps the separately approved SLI-0028 increment and expands recovery policy | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it delivers the complete approved user
scenario across contracts, core, persistence, API, generated client, browser,
and headless qualification without opening a new decision gate. Its public API
remains the stable product boundary and its additive evidence model is
reversible before accepted attempts exist. Candidate B is decision-ready but
withholds the observable learner result, reducing value and end-to-end
completeness. Candidate C violates deterministic server authority. Candidate D
absorbs retry and recovery behavior reserved for SLI-0028. Candidate A wins
without a tie-break and conforms to the CAP-0006 manifest.

## Boundary Path

1. A client opens the exact answer-safe presentation created by SLI-0026 and
   holds only its public placement, definition, item, version, and digest
   selectors.
2. The client creates one stable submission UUID, sends one response per item
   through the public practice-submission operation, and reuses that UUID only
   for transport retries of the same canonical request.
3. The protected host resolves server-issued learner context and authorization,
   rejects caller-selected identity and malformed transport, and invokes only
   the Assessment public application operation.
4. Assessment resolves exact Curriculum placement and private Content package
   data through public facades, revalidates the closed definition, correlates
   responses by item ID, and scores each response with deterministic domain
   rules.
5. Assessment selects the exact correct or incorrect feedback branch, derives a
   versioned activity summary, and asks its repository port to append the
   attempt, ordered responses, scores, completion evidence, and outbox event in
   one transaction.
6. The repository returns the previously committed result for an exact replay,
   rejects conflicting reuse or a disallowed second completion, and rolls back
   every row on any pre-commit failure.
7. The public response exposes learner-safe ordered results and technical
   provenance. The generated browser client renders it accessibly; a headless
   client receives the same contract without UI state or backend internals.

## Contracts, Data, and Provenance

Add one versioned practice-submission request family and one learner-safe result
family. A request carries a stable submission UUID, exact placement/package/
definition selectors, and a closed response union keyed by item ID. Multiple-
select option order is semantically irrelevant and canonicalized before request
fingerprinting. Numeric input remains a canonical fixed-decimal string at the
declared scale; NaN, infinity, exponents, locale separators, scale coercion,
implicit units, and binary floats are invalid.

The result contains the original submission ID, server-issued attempt and
completion IDs and timestamp, exact provenance, total score and maximum, an
ordered result for every definition item, the applicable learner-safe feedback
branch, and approved review references. It does not expose correct answer
values, private evaluator declarations, mastery, suitability, or advice. The
activity summary is a closed deterministic value such as `all_correct` or
`review_needed`, not an AI judgment.

Use additive Assessment-owned tables for immutable practice attempts, item
responses, item scores, completion evidence, and a versioned practice-
completion outbox event. Do not overload the existing single knowledge-check
tables, add cross-module foreign keys, or let Curriculum/Content read Assessment
persistence. The entire aggregate and outbox append share one transaction.
Every accepted row retains exact learner, placement, package, definition,
schema, policy, item, response, scoring-rule, and request-fingerprint
provenance needed for later replay and comparison.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Correct and mixed attempt | The authorized learner receives ordered item feedback, a deterministic total, an activity summary, review references, and exact evidence IDs | domain/application/API/browser/live |
| Headless submission | A non-browser client submits through the same protected POST and receives the same contract and retained evidence as the browser | API/live qualification |
| Request-order flexibility | Valid responses may arrive in any order and valid multiple selections in any option order; canonical scoring and replay are unchanged | contract/domain/idempotency |
| Exact replay | The same learner, submission ID, and canonical request returns the original result with no duplicate rows or events | application/PostgreSQL/concurrency |
| Conflicting replay | Reusing a submission ID with different canonical input fails closed and preserves the original evidence | application/PostgreSQL/API |
| Attempt limit | A new submission after the first completed attempt is refused until SLI-0028 supplies retry policy | application/API/browser |
| Closed input | Missing, duplicate, extra, unknown, wrong-type, unknown-option, or noncanonical-decimal responses fail before any evidence append | schema/domain/application |
| Stale or unauthorized | Stale exact selectors, unavailable definitions, missing permission/session, or caller-selected learner identity fail without private answers or activity facts | API/security/browser |
| Atomic failure | A scoring, serialization, repository, or outbox failure leaves no partial attempt, response, score, completion, or event rows | adapter/PostgreSQL/fault injection |
| Concurrent duplicate | Concurrent identical submissions converge on one durable result; conflicting contenders cannot create mixed evidence | PostgreSQL/integration |
| Answer confidentiality | Results reveal only the applicable approved feedback and references, never answer keys or evaluator declarations | contract/API/security |
| Accessible result | Submit, pending, denial, retry-safe transport error, and result states preserve labels, focus, live-region meaning, keyboard operation, reflow, and theme parity | component/Chromium/design |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0096 | Freeze submission/result/completion-event contracts, canonical request identity, pure response validation, deterministic scoring, and compatibility corpus | SLI-0026 | none | verifying |
| JIT-B | Compose Assessment submission, atomic append-only persistence, migration, idempotency, concurrency, rollback, and outbox evidence | JIT-A | none | candidate |
| JIT-C | Add the protected public POST, reviewed OpenAPI/generated client, and accessible browser submit/result flow with headless parity | JIT-B | none | candidate |
| JIT-D | Qualify contracts, real PostgreSQL transactions, API/headless and browser behavior, restart/replay, denials, confidentiality, accessibility, and live local composition | JIT-C | none | candidate |

## Verification and Qualification

Run request/result/event schema and semantic compatibility over approved and
malicious examples; pure domain scoring tests for every correct, incorrect,
boundary, order, and malformed response; application tests for exact resolution,
authorization inputs, idempotency, conflict, attempt limits, server-owned time
and IDs, and failure mapping; SQLite and real-PostgreSQL adapter tests for
atomicity, uniqueness, concurrency, rollback, restart, and outbox correlation;
protected API success and denial tests; reviewed OpenAPI/generated-client
reproduction; web model, component, and browser tests; and isolated live API,
headless, browser, and restart qualification.

Anti-rigidity tests vary valid item counts and ordering, response ordering,
option counts and selection ordering, valid decimal sign/range/scale cases,
feedback/reference counts, compatible optional metadata, and all supported
response types. They must not make a fixture's incidental order, count,
timestamps, generated IDs, or visual styling a functional requirement. Also run
architecture import/schema-ownership checks, security, learner-language,
accessibility, design, documentation, planning, whitespace, build, and aggregate
readiness gates applicable to changed boundaries.

## Rollback and Migration

Contracts, tables, indexes, and event types are additive and versioned. Test
forward migration and a development rollback while no accepted practice
evidence exists. After evidence is accepted, preserve it and remove exposure by
route/feature rollback; use backup/restore or a later governed migration rather
than destructive down-migration. Existing knowledge-check evidence and meaning
must remain unchanged. A breaking public contract or event change requires a
new version and compatibility handling, not in-place reinterpretation.

## Stop Conditions

Stop for model/manual grading, AI-authored content, adaptive/mastery authority,
arbitrary or external execution, new response types, partial credit or scoring
policy not already frozen in SLI-0026, client-owned identity/time/scoring,
mutable/deletable evidence, cross-module persistence access, private answer
leakage, conflicting canonical sources, a breaking existing Assessment
contract, tenancy, managed-cloud recovery, a separate local/cloud core, active
write-scope overlap, or material CAP-0006 package drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional copy polish, or another inconsequential issue. Fix it locally
or defer optional cleanup to CAP-0031.

## Documentation Impact and Completion Evidence

Update the Assessment, API, web, local deployment, contract, event, persistence,
architecture-verification, and known-gap documentation affected by delivered
behavior. Completion evidence must identify the exact candidate and retained
versions, focused and aggregate checks, real-database and live qualification,
headless/browser parity, idempotency/concurrency/rollback proof, migration and
restore boundary, contract/client reproduction, accessibility/security results,
assumptions, residual gaps, and CAP-conformance assessment. It must state that a
future headless AI consumer can reuse the public API while no separate AI mode
or autonomous authority was planned or implemented.

## Planning History

- 2026-10-16: Refined the second approved CAP-0006 manifest increment after
  SLI-0026 completed. Candidate A scores 14/14 and delivers deterministic
  whole-attempt submission and evidence through one API-first browser/headless
  boundary without activating retry/history, mastery, model authority, or a new
  durable decision. The refinement conforms to the current CAP package.
- 2026-10-16: Recorded the public API as the continuing product boundary for
  browser and future headless AI consumers. A separate AI mode, protocol, and
  autonomous action plan remain explicitly deferred.
- 2026-10-16: Refined JIT-A as WRK-0096 around additive submission, result, and
  completion-event contracts plus pure deterministic scoring and canonical
  request identity. Persistence and the public API remain the next packet's
  boundary.
- 2026-10-16: Activated WRK-0096 after the implementation gate confirmed
  current CAP authority, completed SLI-0026 dependency, decision readiness,
  exact write scope, and collision-free ownership. No lower-level approval was
  requested.
- 2026-10-16: WRK-0096 implemented the additive whole-attempt contracts, pure
  deterministic three-type scorer, canonical order-independent request
  identity, learner-safe result, and bounded confidential completion event.
  Persistence, the public POST, generated client, and browser result flow remain
  the next packet boundaries.
