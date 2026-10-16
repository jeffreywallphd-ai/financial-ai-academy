---
id: WRK-0097
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0027
capability: CAP-0006
depends_on: ["WRK-0096"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/assessment/assessment_0002_practice_evidence.down.sql", "backend/migrations/assessment/assessment_0002_practice_evidence.up.sql", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/assessment/application/service.py", "backend/src/financial_ai_academy/modules/assessment/ports/repositories.py", "backend/src/financial_ai_academy/modules/assessment/public.py", "backend/tests/integration/assessment/test_postgres_assessment.py", "backend/tests/integration/assessment/test_postgres_practice_submission.py", "backend/tests/unit/assessment/test_practice_service.py", "docs/architecture/contracts/assessment-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0027-submit-and-score-practice-attempt.md", "docs/planning/work-packets/WRK-0097-compose-practice-submission-persistence.md"]
generated_artifacts: []
base_revision: 33d2e740f6e04fd7d1371642fa2bc1a543949b00
claim_id: WRK-0097:1eb4a6c5-42e1-4c43-b0b5-8259da535df3
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T15:56:57Z
---

# Agent Work Packet: Compose Practice Submission and Persistence

## Objective and Deliverable

Add one transport-neutral Assessment public operation that resolves an exact
placed practice, invokes the accepted WRK-0096 parser/scorer with server-owned
identity and time, and atomically retains an append-only practice attempt,
ordered responses, item scores, completion result, and outbox event in
PostgreSQL. Exact transport replays return the original result; conflicting
submission reuse and a second completed attempt fail closed. This packet makes
the application seam ready for a versioned public HTTP API without adding that
host, generated client, browser flow, or a separate AI mode.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository-
root `docs/README.md`; route through the baseline, learning-adaptation,
architecture-contract, security-risk, testing-quality, and delivery-planning
context. Read the change-impact matrix, decision readiness, CAP-0006,
SLI-0027, WRK-0096, ADR-0005, ADR-0007, the Assessment contract and module
README, PostgreSQL migration guidance, the accepted practice schemas/parser/
scorer, Content and Curriculum public gateways, existing knowledge-check
application/repository behavior, relevant unit/integration tests, and
concurrent-work rules.

## Decisions and Assumptions

- Assessment remains the sole owner of deterministic practice validation,
  scoring, attempt evidence, completion evidence, and its outbox record.
- The public application request contains server-supplied learner identity,
  the route-bound placement ID, and the exact submission document bytes. The
  placement ID is resolved before scoring and must correlate with the document.
- The server supplies attempt, evidence, and event UUIDs plus the canonical UTC
  timestamp. Clients supply only the stable submission UUID inside the accepted
  document and never select learner identity, score, completion, or time.
- Practice evidence uses additive Assessment-owned tables instead of widening
  or reinterpreting existing single-item knowledge-check tables.
- One accepted attempt is allowed per learner, placement, practice ID, and
  practice version until SLI-0028 introduces explicit retry policy. Exact
  canonical replay of the same learner/submission returns the first result;
  different input under that identity conflicts.
- The aggregate and outbox insert share one transaction. Ordinary update or
  delete of accepted evidence is rejected. Development/test rollback is allowed
  only while no retained evidence must be preserved.
- The application operation is transport-neutral and is the single seam later
  used by the protected HTTP endpoint, generated web client, command-line
  qualification, and future headless consumers.

## In Scope

- Add typed public application request/result behavior for whole-practice
  submission without introducing a transport framework dependency.
- Reuse exact Curriculum placement and Content private-definition gateways,
  the production practice definition parser, and the accepted WRK-0096
  submission parser/scorer.
- Map bounded parser, stale-reference, conflict, completion-limit, clock, ID,
  and storage failures to learner-safe Assessment errors without echoing
  responses, private answers, database details, or provider data.
- Extend the Assessment repository port and PostgreSQL adapter with one atomic
  practice-submission operation and exact-result replay.
- Add a checksum-protected forward/down migration for append-only practice
  attempts, ordered responses, item scores, completion evidence, and practice
  outbox rows with bounded checks and uniqueness constraints.
- Prove exact replay, conflicting replay, one-attempt limit, concurrency,
  rollback, restart visibility, append-only behavior, provenance, event
  confidentiality, all supported response variants, and unchanged knowledge-
  check storage.
- Update Assessment/persistence documentation and planning evidence.

## Out of Scope

FastAPI routes or models; OpenAPI; generated TypeScript clients; browser state
or rendering; command-line product UX; session/authorization host composition;
retry/resume/history/review navigation; Learner-model or Audit consumers;
outbox dispatch; background jobs; managed-cloud recovery; new response or
scoring types; mastery/adaptation; model/manual grading; separate AI mode,
agent protocol, tool calling, or autonomous action authority; dependencies and
lockfiles.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment public/application | existing knowledge-check and practice-open operations | public request/protocol plus practice-submit service composition | Establish one transport-neutral browser/headless application seam |
| Repository port/adapter | current atomic knowledge-check repository | additive practice append/replay operation and serialization | Persist accepted WRK-0096 result meaning without cross-module access |
| PostgreSQL | Assessment migration stream and rollback conventions | additive `assessment_0002` migration | Enforce atomicity, uniqueness, append-only evidence, and provenance |
| Tests | practice service and Assessment PostgreSQL suites | focused service and real-database practice evidence tests | Prove denial, idempotency, concurrency, rollback, restart, and regression behavior |
| Canonical guidance | Assessment contract/module and migration README | listed documentation | Record the public operation, table ownership, transaction, and deferred API boundary |
| Planning evidence | SLI-0027, WRK-0097, register | listed planning files | Keep just-in-time packet state synchronized |

No HTTP/OpenAPI/generated-client/web file, accepted schema or compatibility
fixture, Content/Curriculum persistence, knowledge-check result meaning,
dependency, or lockfile may change.

## Contracts and Interfaces

`SubmitPlacedPracticeRequest` carries a server-resolved learner UUID, one
route-bound placement ID, and the exact accepted `assessment-practice-
submission-v1` bytes. `AssessmentOperations.submit_placed_practice` returns the
accepted immutable `PracticeResult` or raises a bounded `AssessmentError`.
Callers do not supply attempt/evidence/event IDs or time.

The service resolves the exact `PlacedPracticeReference` and private Content
definition, parses it through the production definition port, builds the exact
presentation context, obtains server IDs/time, and passes the bytes to
`PracticeSubmissionPort.parse_and_score`. Only a complete candidate reaches
the repository.

The repository port accepts `PracticeSubmissionCandidate` and returns
`(PracticeResult, created)`. Durable request identity is
`(learner_id, submission_id)` plus the candidate's canonical fingerprint. A
matching replay returns the stored result; a different fingerprint raises a
practice conflict. A distinct submission for an already completed exact
practice raises the practice-completed condition. No partial record is visible.

The migration stores aggregate provenance in `practice_attempts`, one ordered
closed response and score row per item, one complete result document, and one
bounded completion event. Persistence JSON mirrors the accepted schemas but is
never exposed by direct table reads outside Assessment.

## Dependencies and Parallel Safety

WRK-0096 is complete and supplies frozen submission/result/event semantics,
canonical request identity, pure scoring, and the production parser/scorer.
WRK-0097 owns the shared Assessment service, repository, migration stream, and
SLI/register files, so it is not parallel-safe with the later HTTP/client or
qualification packet. It must complete before JIT-C is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete attempt | One authorized learner submits every response for the exact placed definition | The public application operation runs | The returned ordered result matches WRK-0096 and one complete evidence aggregate plus event commits | unit/PostgreSQL |
| Headless-ready seam | A non-browser caller invokes the application operation with the same exact document a future HTTP host will accept | Submission succeeds | No browser, FastAPI, or client dependency participates and the same result contract is returned | unit/architecture |
| Exact replay | The same learner and submission ID repeat semantically equivalent reordered input | Concurrent or later calls execute | One aggregate exists and every caller receives the original IDs/time/result | unit/PostgreSQL concurrency/restart |
| Conflicting replay | The same learner/submission ID carries changed canonical input | Repository resolution runs | A bounded conflict is returned and original evidence remains unchanged | unit/PostgreSQL |
| Attempt limit | The learner uses a new submission ID after completing the same placed practice version | Submission runs before SLI-0028 | A bounded already-completed error occurs with no new rows | unit/PostgreSQL |
| Closed/stale input | The document is malformed, incomplete, wrong-type, stale, or mismatched to route placement/private definition | Resolution and scoring run | It fails before persistence with no private-answer disclosure | unit/PostgreSQL |
| Atomic failure | Any insert or the outbox hook fails before commit | Repository records the candidate | No attempt, response, score, completion, or event row remains | PostgreSQL fault injection |
| Append-only evidence | An ordinary update/delete targets accepted practice evidence | PostgreSQL executes it | The database rejects mutation and the aggregate remains intact | PostgreSQL |
| Existing behavior | Knowledge-check application and real-database tests run with both migrations | Practice support is installed | Existing knowledge-check replay, completion, and outbox behavior is unchanged | regression |
| Shape flexibility | Valid definitions vary item count/type/order, option/reference count, and response order | Application and repository serialize/replay them | Exact meaning persists without fixture-count or sibling-order assumptions | parameterized unit/PostgreSQL |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment/test_practice_service.py backend/tests/unit/assessment/test_practice_scoring.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/assessment_practice backend/tests/unit/assessment/test_practice_contract.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment/test_postgres_practice_submission.py backend/tests/integration/assessment/test_postgres_assessment.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment/test_assessment_service.py backend/tests/contract/assessment
python dev-tools/architecture/check_architecture.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0097-compose-practice-submission-persistence.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

The PostgreSQL commands require the repository's isolated test DSN/container.
Submit one exact candidate, generate a fresh affected-verification receipt, and
obtain one independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document the transport-neutral public operation, server-owned identity/time,
exact definition resolution, additive table ownership, uniqueness and replay
rules, atomic transaction/outbox boundary, append-only enforcement, rollback
limits, unchanged knowledge-check semantics, and deferred HTTP/client/UI work.
Record exact checks, candidate/receipt, review disposition, assumptions, and
residual gaps in this packet and SLI-0027. Keep approval and reviewer records
only in the ignored local ledger.

## Stop Conditions

Stop for a breaking accepted schema or knowledge-check contract; ambiguity in
canonical replay identity, attempt uniqueness, or retained response meaning;
cross-module persistence access; client-owned learner/time/scoring authority;
private-answer leakage; mutable/deletable accepted evidence; retry/history or
projection work reserved for SLI-0028; HTTP/generated-client/browser change;
model/manual/AI authority; a new provider/dependency; active scope collision;
conflicting canonical source; or material CAP-0006/SLI-0027 drift.

Do not stop or reopen review solely for harmless whitespace, nonfunctional
styling, optional prose polish, or another inconsequential in-scope correction.
Fix it locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report the exact candidate; public application request/result seam; table and
transaction boundaries; replay/conflict/completion-limit/concurrency/rollback/
restart evidence; confidentiality and append-only proof; knowledge-check
regressions; focused, architecture, affected, aggregate, receipt, and review
results; documentation impact; assumptions; and residual gaps. Confirm that no
HTTP/OpenAPI/generated client, browser UI, retry/history, projection/replay
consumer, separate AI mode, model authority, dependency, or external execution
changed, then leave JIT-C dependency-ready.

## Planning History

- 2026-10-16: Authored just in time after WRK-0096 completed. The packet adds
  the shared transport-neutral application/persistence core required by both
  browser and future headless clients while deferring HTTP and interface work.
- 2026-10-16: Claimed from base revision `33d2e74` after the implementation
  gate confirmed current CAP authority, dependency completion, decision
  readiness, bounded scope, and no active ownership collision.
