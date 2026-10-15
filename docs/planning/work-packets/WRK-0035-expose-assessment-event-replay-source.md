---
id: WRK-0035
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/tests/unit/assessment", "backend/tests/integration/assessment", "docs/architecture/contracts/assessment-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0035-expose-assessment-event-replay-source.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0035:cb3b2d98-eb01-42fd-97dc-fe179ff50296
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:42:16Z
---

# Agent Work Packet: Expose the Assessment Event Replay Source

## Objective and Deliverable

Add a typed, validated, read-only Assessment public operation that returns the
retained completion events for one learner and exact placement in deterministic
order, giving later Learner-model and Audit consumers a replay source without
cross-schema access or queue semantics.

## Required Context

Before changing files, read and follow `AGENTS.md`, `docs/README.md`, routed
architecture/testing/security context, CAP-0001, SLI-0016, ADR-0005,
decision-readiness, the Assessment contract/schema/module/repository/tests, and
the nearest README files.

## Decisions and Assumptions

The existing append-only outbox remains Assessment-owned source evidence.
This operation is an explicit synchronous query, not acknowledgement,
dispatch, queue, or delivery-guarantee state. Learner identity is supplied by a
trusted server-side caller and is never inferred from event payload alone.

## In Scope

Define typed public request/event results, validate persisted event envelopes
against the executable v1 contract, filter by learner and placement, guarantee
stable occurrence/event ordering, and fail closed on malformed, unsupported,
or internally inconsistent evidence. Add focused unit and real-PostgreSQL tests
for empty, exact, duplicate-query, tampered, filtered, and unavailable cases.

## Out of Scope

Consumer checkpoints, delivery status, event mutation, queue/broker/worker
selection, Learner-model or Audit persistence, HTTP exposure, UI, and recovery
claims.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment public/application | Existing submit/open operations and event builder | `modules/assessment/public.py`, application and owned ports | Publish a typed replay query without exposing persistence |
| Assessment adapter | Append-only outbox and repository tests | Assessment PostgreSQL adapter and focused tests | Read filtered event documents without cross-module access |
| Contract validation | Completion-event schema/parser patterns | Assessment-owned contract adapter if needed | Reject malformed or unsupported stored envelopes |
| Composition | Existing derived schema paths and Assessment construction | Bootstrap settings/composition only | Inject the executable event-contract parser without hard-coded repository paths |
| Architecture docs | Accepted Assessment contract | Assessment contract and module README when materially affected | Record replay-source semantics and explicit non-guarantees |
| Planning | Current slice/packet/register | This packet, SLI-0016, register | Keep lifecycle synchronized |

## Contracts and Interfaces

The request contains `learner_id` and `placement_id`; the result is an immutable
sequence of typed `assessment.knowledge-check.completed@1.0.0` events retaining
event/attempt/evidence identities and exact version/digest/score/time fields.
The existing executable event JSON Schema remains authoritative. No selected
option, answer, feedback, provider binding, path, SQL shape, or delivery flag is
published.

## Dependencies and Parallel Safety

SLI-0015 is complete and owns the stable source event. This is the first serial
packet in SLI-0016. Its Assessment public contract must be accepted by the next
consumer packet before other slice work begins; no parallel packet is declared.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty source | No matching completion event | Query exact learner/placement | Return an empty immutable result | unit/integration |
| Exact source | One retained completion | Query matching context | Return all exact provenance in stable order | contract/integration |
| Isolation | Events for another learner or placement exist | Query one context | Disclose only exact matching events | integration |
| Repeat query | Source is unchanged | Query repeatedly | Return identical events without mutation | integration |
| Invalid source | Stored envelope is malformed, unsupported, or inconsistent | Query replay source | Fail closed with bounded diagnostics | unit/integration |
| Storage unavailable | PostgreSQL read fails | Query replay source | Return bounded Assessment unavailable error | unit |

## Verification Commands

Run Assessment contract/unit/integration tests on PostgreSQL 18.4, backend
architecture tests, documentation/planning checks, `git diff --check`, and any
new narrower parser/adapter tests.

## Documentation and Evidence Update

Record the public query, event filtering/ordering, executable contract reuse,
failure behavior, environment and exact test counts, queue/delivery non-claim,
documentation impact, and readiness of WRK-0036.

## Stop Conditions

Stop if the operation requires a queue or delivery guarantee, exposes raw SQL
or provider/storage details, weakens append-only evidence, changes event v1
meaning, permits cross-learner reads, or needs cross-module persistence access.

## Required Handoff

Report exact public types and filters, validation and ordering behavior, tests,
documentation changes, residual gaps, and the next packet boundary.

## Verification Progress

- Added a typed public replay request/event and a schema-backed parser for
  `assessment.knowledge-check.completed@1.0.0`. The application query checks
  server-supplied learner/placement context, rejects duplicate or inconsistent
  envelopes, and returns stable occurrence/event-ID ordering.
- The PostgreSQL adapter reads only Assessment-owned outbox/evidence/attempt
  tables, filters at the source, and never changes acknowledgement or delivery
  state. Repeated reads preserve all five evidence-table row counts.
- Forty-six focused Assessment contract/unit/architecture tests and eight real
  PostgreSQL 18.4 integration tests passed. The complete backend suite passed
  150 tests with 19 environment-gated tests skipped; architecture passed eight
  fitness functions, documentation verified 189 Markdown files and catalogs,
  planning verified 65 artifacts, and the diff check passed with line-ending
  warnings only.
- No dispatcher, queue, worker, checkpoint, or delivery guarantee was chosen.
  Learner-model and Audit consumption remain the next packet boundaries.

## Planning History

- 2026-10-15: Authored immediately before implementation from ready SLI-0016;
  no unresolved decision or material CAP change was found.
- 2026-10-15: Refined before code changes to include the composition-owned
  event-schema path and parser injection; scope and CAP behavior are unchanged.
- 2026-10-15: Delivered and qualified the exact replay source, including real
  PostgreSQL filtering and non-mutation evidence, without crossing the queue
  decision boundary.
