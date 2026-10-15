---
id: WRK-0037
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: ["WRK-0035", "WRK-0036"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit", "backend/migrations/audit", "backend/migrations/README.md", "backend/src/financial_ai_academy/modules/README.md", "backend/tests/unit/audit", "backend/tests/integration/audit", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/modules/module-map.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/assurance/known-architecture-gaps.md", "docs/security/community-learner-evidence-protection.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0037-deliver-assessment-audit-references.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0037:e1f3e32f-6189-4138-b652-4b57ef4aab6b
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:50:47Z
---

# Agent Work Packet: Deliver Assessment Audit References

## Objective and Deliverable

Implement Audit-owned, append-oriented integrity/provenance references for the
validated Assessment completion events, with idempotent replay and tamper
conflict handling that never turns Audit into a second completion source.

## Required Context

Before changing files, read and follow `AGENTS.md`, `docs/README.md`, routed
architecture/data/testing/security context, CAP-0001, SLI-0016, WRK-0035 and
WRK-0036, ADR-0005, the Assessment public event source, community evidence
protection, module/dependency rules, migration patterns, and nearest READMEs.

## Decisions and Assumptions

Audit records event identity, source evidence, actor/action, exact provenance,
canonical integrity digest, and record time. Assessment remains authoritative
for business evidence and Learner model remains authoritative for completion
projection. Explicit synchronous reconciliation is not event delivery.

## In Scope

Create Audit domain/application/port/adapter/public seams, an Assessment-public
adapter, canonical digest and deterministic record identity, append-only
PostgreSQL migration/repository, idempotent replay, conflicting same-event
tamper denial, transactional interruption behavior, and focused unit/
architecture/real-PostgreSQL verification.

## Out of Scope

Completion-state queries, HTTP/UI exposure, administrative actor workflows,
export products, queue/worker/checkpoint semantics, retention automation,
security-event families, recovery tooling, and managed-cloud qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Audit | Accepted ownership and module patterns | New module-first boundary | Own source-event integrity/provenance references |
| Assessment adapter | WRK-0035 public operation only | Audit adapter | Map public events without importing Assessment internals |
| PostgreSQL | Module migration patterns | New `audit` stream/repository | Append and protect idempotent records in the owning schema |
| Architecture/security | Module map, gaps, evidence protection | Listed docs/tests | Enforce boundary and confidential metadata handling |
| Planning/docs | Slice/register/packet and READMEs | Listed files | Synchronize lifecycle and operational meaning |

## Contracts and Interfaces

The public reconcile request contains server-supplied learner and exact
placement IDs. The receipt returns only reconciled event count and source-set
digest. Stored records retain audit/event/evidence/attempt IDs, actor, action,
exact package/Assessment versions and digests, occurrence/record time, and a
canonical event digest. They omit answer, feedback, provider, and storage data.

## Dependencies and Parallel Safety

WRK-0035 and WRK-0036 are complete. This serial packet consumes only the
Assessment public event contract and establishes the Audit operation required
by the later API workflow.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty source | No completion events | Reconcile | Return zero and append nothing | unit/integration |
| Exact event | One valid event | Reconcile | Append one complete integrity reference | unit/integration |
| Duplicate replay | Same event is reconciled again | Reconcile | Return the same logical receipt and keep one row | integration |
| Conflicting identity | Same event ID has different content | Reconcile | Reject as tamper conflict and preserve original | unit/integration |
| Interrupted append | Failure occurs before commit | Reconcile | Append no partial Audit records | integration |
| Source/storage unavailable | Assessment or PostgreSQL fails | Reconcile | Return bounded unavailable error without leakage | unit |

## Verification Commands

Run Audit unit and real PostgreSQL integration suites, Assessment/Learner-model
regressions, backend architecture/full tests, security/docs/planning checks,
`git diff --check`, and narrower integrity/tamper tests.

## Documentation and Evidence Update

Record ownership, exact retained metadata, digest/idempotency/tamper semantics,
migration and rollback limits, counts/environment, append-only evidence,
non-claims, remaining API/UI work, and CAP conformance.

## Stop Conditions

Stop if Audit becomes business-state authority, reads Assessment SQL, mutates
records, stores private responses, requires a queue/delivery guarantee, exposes
cross-learner data, or makes retention/recovery/cloud claims outside authority.

## Required Handoff

Report public receipt, canonical integrity inputs, append/replay/conflict
behavior, tests, migration impact, known gaps, and readiness of WRK-0038.

## Verification Progress

- Added the Audit module, a bounded reconciliation receipt, and an
  Assessment-public-only adapter. Audit IDs are deterministic from event IDs;
  integrity digests cover the complete canonical public event, while receipts
  disclose only count and source-set digest.
- Added the isolated append-only `audit` migration stream. Exact replay retains
  one record, the same event ID with different content is rejected without
  overwrite, update/delete triggers protect accepted rows, and injected
  pre-commit failure leaves no partial records.
- The first PostgreSQL replay run exposed a UUID/string adapter-normalization
  defect that misclassified exact replay as conflict. The adapter now
  normalizes UUID columns at its boundary; the fresh-container rerun passed all
  three integration scenarios.
- Sixteen focused Audit/architecture tests and three real PostgreSQL 18.4
  integration tests passed. The complete backend suite passed 166 tests with 25
  environment-gated skips; aggregate architecture passed eight fitness
  functions, security passed ten control groups, documentation verified 191
  Markdown files and catalogs, planning verified 67 artifacts, and the diff
  check passed with line-ending warnings only.
- Audit remains integrity/provenance evidence, not completion authority. API,
  browser, background delivery, export/retention/recovery, and managed-cloud
  behavior remain outside this packet.

## Planning History

- 2026-10-15: Authored after the Assessment replay source and Learner-model
  projection completed; no unresolved decision or material CAP drift was found.
- 2026-10-15: Delivered append-only Audit references and qualified exact replay,
  tamper conflict, mutation denial, and transactional interruption.
