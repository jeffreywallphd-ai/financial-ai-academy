---
id: WRK-0103
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: ["WRK-0102"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/assessment/assessment_0003_practice_progress.down.sql", "backend/migrations/assessment/assessment_0003_practice_progress.up.sql", "backend/src/financial_ai_academy/modules/assessment/", "backend/tests/integration/assessment/", "backend/tests/unit/assessment/", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0103-implement-practice-draft-retry-persistence.md"]
generated_artifacts: []
base_revision: c2524c9dd2e639661d3b2500a7fd4fd1652a97b8
claim_id: WRK-0103:e958ad7a-e94f-443b-9423-623912757eee
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T17:27:54Z
---

# Agent Work Packet: Implement Practice Draft and Retry Persistence

## Objective and Deliverable

Implement the Assessment-owned persistence and application seam for resumable
practice drafts, exact formative retry enforcement, stable attempt ordering,
and typed completion-event replay. Preserve the accepted practice result and
event documents byte-for-byte while making the shared public application core
usable by future HTTP, generated-client, browser, and headless consumers.

## Required Context

Follow every applicable `AGENTS.md`, `docs/README.md`, routed context pack, the
change-impact matrix, decision-readiness register, CAP-0006, SLI-0028,
WRK-0102, ADR-0005, ADR-0007, ADR-0008, the Assessment contract, compatibility
rules, module dependency rules, migration guidance, and concurrent-work
protocol. Inspect the current Assessment domain, application service, public
facade, repository ports, PostgreSQL adapter, migration, unit tests, integration
tests, and nearest README before editing.

## Decisions and Assumptions

- Assessment remains the sole owner of drafts, attempts, retry enforcement,
  result evidence, and practice completion events. No other module reads its
  tables.
- One mutable draft is keyed by learner plus the complete exact practice scope.
  Save revision, learner identity, and save time are server authoritative.
- Conditional saves use revision zero for create. An exact same-content replay
  returns the current draft; a different stale snapshot conflicts without
  changing it. A current-revision content replacement increments revision.
- Exact submission replay is resolved before the attempt limit. A distinct
  accepted submission receives the next stable order only when it is at or
  below the immutable definition's `max_attempts`, from 1 through 10.
- The submission transaction clears only the matching draft after the entire
  attempt, response, score, completion-evidence, and outbox aggregate succeeds.
  Any denial or rollback leaves the draft intact.
- Existing retained attempts become attempt order 1 without changing result or
  event JSON. New ordering is persistence metadata and public application
  meaning for later history composition, not a breaking result-v1 change.
- Event replay validates retained outbox bytes through the existing Assessment
  contract adapter before returning typed records; callers never receive raw
  database rows as authority.

## In Scope

- Add production domain and public application representations for exact draft
  scope, saved drafts, retry state, and ordered completion replay.
- Add a contract adapter that validates and canonicalizes accepted draft-save
  bytes against the frozen v1 schema and exact private definition without
  scoring or exposing private answer/evaluator data.
- Extend Assessment repository ports and application service for exact draft
  read, conditional full-snapshot save, deterministic retry-state read, and
  learner/placement-bounded completion-event replay.
- Add `assessment_0003_practice_progress` migration for one mutable draft per
  exact scope, lockable retry scope, and stable attempt order. Preserve all
  earlier evidence and make reapply/teardown deterministic in development.
- Extend PostgreSQL submission persistence so exact replay precedes the limit,
  concurrent final-slot submissions cannot overrun `max_attempts`, attempt
  order has no gaps or duplicates, and matching-draft deletion is atomic.
- Add pure application and real-PostgreSQL evidence for save/replay/conflict,
  isolation, restart durability, submit clearing/failure preservation, limits
  1 through 10, replay at the limit, concurrency, rollback, migration, and
  confidential typed event replay.
- Reconcile Assessment, migration, architecture-verification, module-map, slice,
  packet, and register documentation made stale by this implementation.

## Out of Scope

HTTP routes or API models; OpenAPI or generated clients; browser work; public
history composition; Curriculum review-target resolution; Learner-model
history projection; adaptive ranking; mastery or competency inference;
cross-version draft migration; draft expiry or retention; explicit draft reset;
queues, workers, or dispatch; tenancy; provider selection; managed-cloud
recovery; external execution; or a separate browser, headless, or AI core.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Assessment domain/public application | exact draft, retry, ordered replay representations and operations | Keep one reusable core for later API and headless consumers |
| Assessment ports/adapters | contract validation and owned PostgreSQL persistence | Enforce server authority and module isolation |
| Assessment migration | additive draft, retry-scope, and attempt-order structures | Preserve accepted evidence while enabling concurrency-safe retries |
| Assessment tests | unit and real-PostgreSQL evidence | Prove conditional, atomic, restart, rollback, and concurrency behavior |
| Architecture and module docs | only listed Assessment persistence/replay guidance | Reconcile delivered ownership and known behavior |
| Planning | packet, slice, and register | Record bounded lifecycle and evidence |

No Content, Curriculum, Learner-model, API host, OpenAPI snapshot, generated
client, web application, design-system, dependency, or lockfile may change.

## Contracts and Interfaces

The application accepts draft-save bytes only through the frozen
`assessment/practice/v1/draft-save` contract and returns the frozen server
draft and retry-state meanings through typed public dataclasses. Exact selector
correlation is checked against the resolved placement and private definition.
Responses may be empty or partial but must be unique, known, and type/policy
compatible. Canonical response fingerprints make ordering-insensitive exact
replay deterministic.

The repository accepts a validated, complete practice submission candidate
plus the exact definition's maximum. It returns the original result for exact
submission replay or persists a stable one-based attempt order. The unchanged
result/event JSON stays authoritative; ordering is stored separately. Typed
replay is bounded by learner and placement and ordered by attempt order.

## Dependencies and Parallel Safety

WRK-0102 is complete and supplies the accepted draft/retry/history contract
semantics. This packet owns the shared Assessment module and its migration and
is not parallel-safe with another Assessment implementation packet. WRK-0103
must complete before the composed API/history packet begins.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Create and resume | Revision-zero save creates one draft; a fresh repository/service instance reads the same exact canonical snapshot | unit/PostgreSQL/restart |
| Exact save replay | Reordered equivalent content with the original expectation returns the current draft and does not advance revision | unit/PostgreSQL |
| Conditional replace | Current revision plus changed valid content replaces the snapshot and increments revision once | unit/PostgreSQL |
| Stale conflict | Different content with a stale revision is refused and the newer draft remains unchanged | unit/PostgreSQL/concurrency |
| Isolation | Another learner or exact practice/version scope cannot read, replace, or clear the draft | unit/PostgreSQL |
| Successful submit | The complete aggregate and stable attempt order commit, then only the matching draft is removed in the same transaction | PostgreSQL |
| Failed submit | Validation, limit, injected outbox failure, or transaction rollback preserves the draft and all prior evidence | unit/PostgreSQL/fault injection |
| Variable retry policy | Distinct attempts are accepted exactly through every valid maximum from 1 to 10; the next is confidentially refused | unit/PostgreSQL |
| Replay at limit | Any exact accepted submission still returns its original result after the limit and consumes no order | unit/PostgreSQL |
| Concurrent final slot | Two contenders for the last slot yield at most one new attempt with no duplicate or skipped order | PostgreSQL/concurrency |
| Compatible migration | Existing attempt/result/event bytes remain unchanged and migrate to order 1; apply, reapply, and development teardown are deterministic | PostgreSQL/migration |
| Typed replay | Bounded learner/placement replay returns validated ordered events after restart and excludes raw persistence/private answer data | unit/PostgreSQL/security |
| Anti-rigidity | Variable item counts, partial response counts, identifiers, timestamps, and maxima work without fixture-specific assumptions | unit/PostgreSQL |

## Verification Commands

Run the focused Assessment contract/domain/application suites; Assessment real-
PostgreSQL migration, draft, retry, concurrency, rollback, restart, and replay
tests; existing practice submission and knowledge-check regressions; module
boundary architecture checks; planning validation; documentation validation;
whitespace integrity; the selected affected verification route; one independent
technical review; and the fixed aggregate readiness gate when packet-start
selects shared/control impact. Use exact candidate receipts required by the
control plane.

## Documentation and Evidence Update

Record the migration and public application operations; draft/retry/replay
invariants; existing-byte preservation; variable-limit and concurrency results;
restart, rollback, confidentiality, focused, affected, aggregate, documentation,
planning, and architecture evidence; exact candidate and receipt; assumptions;
and remaining SLI-0028 gaps. State plainly that HTTP, clients, browser, review
routing, and Learner-model history remain later packet seams.

## Stop Conditions

Stop for a breaking accepted contract change; reinterpretation or mutation of
retained result/event bytes; cross-version draft migration; deletion or hiding
of accepted attempts; client-owned learner, revision, time, attempt order,
maximum, score, or authorization; cross-module persistence access; adaptive or
mastery authority; API/UI expansion; provider, queue, tenancy, cloud recovery,
or external execution choice; conflicting canonical sources; stale CAP binding;
or active write-scope collision.

Do not stop or reopen review for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or leave optional polish for CAP-0031.

## Required Handoff

Report the exact candidate and receipt; migration and interface inventory;
draft/retry/replay invariants; compatibility and confidential-data evidence;
focused, PostgreSQL, concurrency, rollback, restart, affected, architecture,
documentation, planning, aggregate, and independent-review results; changed
paths; assumptions and gaps. Confirm that the shared application surface stays
usable by non-browser/headless consumers and that no HTTP, client, browser,
mastery, adaptive, separate AI mode, provider, cloud, or external execution
work was added.

## Completion Evidence

- Exact candidate `0745422d1e742937a0c97fde817bf1d0e2d62235` implements the
  Assessment-owned draft, retry, attempt-order, and validated completion-replay
  seam. The qualifying affected-check receipt has logical digest
  `sha256:4a83facda10de6e7853e683a998901a01a492979c0d6fe0a28c4cb0c4b4c279f`.
- The additive migration preserves retained result and event documents while
  adding exact-scope draft, retry-lock, and stable attempt-order state. Draft
  clearing remains atomic with the complete evidence/outbox transaction.
- Replay now correlates validated event-envelope identities with authoritative
  event, attempt, evidence, and submission columns, rejects item-type/policy
  mismatches, and returns no raw response, answer, feedback, or evaluator data.
- Focused Assessment unit, contract, and real-PostgreSQL verification passed
  208 tests. The progress suite passed 17 real-database scenarios, including
  each supported maximum from 1 through 10, exact replay at the limit, stable
  ordering, concurrent final-slot protection, denied-submission draft
  preservation, restart, rollback, and migration byte preservation.
- Backend architecture passed 15 tests, aggregate readiness passed all 29
  checks, whitespace integrity passed, and the independent technical-review
  requirement is satisfied in the ignored local control-plane ledger.
- This packet changed no HTTP route, OpenAPI document, generated client,
  browser surface, mastery/adaptive authority, provider, cloud-recovery, or
  external-execution boundary. The public application operations remain
  transport-neutral for browser and non-browser/headless composition.

## Planning History

- 2026-10-16: Authored just in time as the second SLI-0028 seam after WRK-0102
  froze additive draft, retry, review-target, and history contract meanings.
  No durable decision gate is open; implementation stays inside the approved
  CAP-0006 package and preserves the reusable public application boundary.
- 2026-10-16: Completed at exact candidate
  `0745422d1e742937a0c97fde817bf1d0e2d62235`. Bounded correction closed replay
  provenance, item-policy correlation, and real-PostgreSQL variable-limit
  evidence without changing the accepted contract or CAP scope.
