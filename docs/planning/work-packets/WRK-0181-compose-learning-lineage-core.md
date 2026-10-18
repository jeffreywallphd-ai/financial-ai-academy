---
id: WRK-0181
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0106
capability: CAP-0026
depends_on: [WRK-0180]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/adapters/__init__.py", "backend/src/financial_ai_academy/modules/audit/adapters/learning_lineage.py", "backend/src/financial_ai_academy/modules/audit/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/audit/application/__init__.py", "backend/src/financial_ai_academy/modules/audit/application/service.py", "backend/src/financial_ai_academy/modules/audit/domain/__init__.py", "backend/src/financial_ai_academy/modules/audit/domain/learning_lineage.py", "backend/src/financial_ai_academy/modules/audit/ports/__init__.py", "backend/src/financial_ai_academy/modules/audit/ports/gateways.py", "backend/src/financial_ai_academy/modules/audit/ports/repositories.py", "backend/src/financial_ai_academy/modules/audit/public.py", "backend/tests/integration/audit/test_postgres_learning_lineage.py", "backend/tests/unit/audit/test_learning_lineage.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0106-trace-learning-content-and-evidence-lineage.md", "docs/planning/work-packets/WRK-0181-compose-learning-lineage-core.md"]
generated_artifacts: []
base_revision: b48397334261a39ae57561d27c19f8d780c86bc8
claim_id: WRK-0181:a6fede7f-848e-4f10-97ca-3be71e3bbbe7
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T08:02:34Z
---

# Agent Work Packet: Compose the Learning-Lineage Core

## Objective and Deliverable

Compose the frozen provenance v1 values into an Audit-owned learning-lineage
application seam for exact published lessons and retained knowledge-check
completion evidence. Deliver a Content public-operation adapter, pure fragment
composition, an exact Audit-owned PostgreSQL read, idempotent completion
reconciliation, safe public requests, and focused unit/integration evidence.

This packet stops at the shared Python application boundary. Protected FastAPI,
OpenAPI, generated TypeScript, browser/headless transport parity, and live-host
qualification belong to WRK-0182 and WRK-0183.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered context routing,
change impact, decision readiness, delivery planning, the approved CAP-0026 and
refined SLI-0106 package, the completed WRK-0180 contracts, Content and
Assessment public operations, Audit reconciliation/domain/repository seams,
PostgreSQL migrations, affected consumers, tests, and nearest READMEs.

Before implementation, repeat and report the applicable startup gate and
revalidate the exact packet against current canonical sources and decision
readiness.

## Decisions and Assumptions

- CAP-0026 and SLI-0106 remain current; WRK-0180 is complete with a qualifying
  exact-candidate receipt and no open technical finding.
- Content remains authoritative for published lessons and educational sources.
  The adapter may read only `ContentOperations.get_published_lesson_version`
  and must discard body, asset, locator, and private authoring data.
- Assessment remains authoritative for completion events. Audit consumes only
  the existing `AssessmentAuditEventSourcePort` public projection and never
  reads Assessment persistence.
- Audit reads only its append-only `assessment_completion_records`. No new
  table, cross-module foreign key, or business-state copy is required.
- Source integrity is a deterministic adapter digest over the bounded public
  source metadata needed for provenance; locators are digest inputs only and
  never appear in an envelope or diagnostic.
- Completion occurrence is the stable one-based order of validated events by
  `(occurred_at, event_id)` within the server-bound learner and placement.

## In Scope

- Add pure Content-fragment and completion-fragment composition over WRK-0180
  `ProvenanceEnvelope`, `LineageNode`, `LineageEdge`, and `LineageView` values.
- Add a Content public-operation adapter that validates the exact requested
  package and maps lesson/source/publication facts without body, asset, locator,
  learner, provider, or storage payloads.
- Reuse Assessment's existing Audit event source; select one exact retained
  evidence occurrence and fail closed on missing or conflicting identity.
- Reconcile completion events idempotently before reading the exact retained
  Audit reference; compose Content, Assessment definition/event/evidence, and
  Audit reference nodes with deterministic IDs and relations.
- Add an Audit repository read by server-bound actor, placement, evidence, and
  exact source-event identity with bounded not-found/conflict behavior.
- Add stable public application requests for exact published-lesson and
  knowledge-check-completion lineage and return the frozen `LineageView`.
- Add unit tests for exact lesson/completion chains, variable source count/order,
  Unicode, idempotent replay, unavailable optional sources, conflicts, bounds,
  and confidential errors; add PostgreSQL tests for retained exact reads,
  restart-equivalent replay, isolation, and immutability.
- Reconcile Audit/module/contract/verification documentation and planning state.

## Out of Scope

- HTTP routes/models, sessions/permissions, OpenAPI, generated clients,
  JavaScript/TypeScript, browser UI, browser tests, or hosted runtime behavior.
- New migrations, owner-table reads, Content/Assessment writes, copied lesson
  bodies, responses, feedback, learner payloads, locators, or provider data.
- Cross-domain Project/practice/financial/market/AI lineage, export, retention,
  recovery, organization tenancy, signing, notification, or external action.
- General graph query languages, arbitrary root kinds, background jobs, queues,
  caches, or speculative performance indexes.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Audit domain/application | listed lineage module, service/public/ports exports | compose one bounded shared-core read |
| Audit adapters/persistence | listed Content adapter and exact Audit read query | translate owner public facts and retained Audit references |
| Tests | two focused learning-lineage files | prove semantics and PostgreSQL containment |
| Architecture/docs/planning | exact listed rows/sections | record implemented ownership and evidence honestly |

No Content, Assessment, API host, migration, Web, generated-client, deployment,
or unrelated documentation path is writable.

## Contracts and Interfaces

1. `ReadPublishedLessonLineageRequest` carries exact package ID, version, and
   digest; `ReadKnowledgeCheckCompletionLineageRequest` carries server-bound
   learner, placement, evidence, and occurrence selectors.
2. The Content adapter returns one lesson envelope plus zero-to-many educational
   source envelopes. It preserves exact package digest and publication time,
   canonicalizes source order, and exposes no source locator.
3. Completion composition correlates one exact validated Assessment event to
   one retained Audit record, exact Assessment definition, published lesson,
   and educational sources. The evidence root contains no score, answer,
   feedback, learner identifier, or Assessment payload.
4. PostgreSQL reads are Audit-schema-only, deterministic, and exact. Missing,
   duplicated, or changed correlation fails with bounded `AuditError` meaning.
5. All resulting views pass the frozen WRK-0180 graph, identity, timestamp,
   bound, source-accounting, ordering, and digest validation unchanged.
6. No lineage request grants authorization; WRK-0182 binds protected transport
   context. This packet accepts the learner only as existing server-side
   application context used for Assessment reconciliation and Audit lookup.

## Acceptance Scenarios

| Scenario | Expected evidence |
| --- | --- |
| Exact lesson | lesson plus all bounded source nodes, stable digest, no body/locator |
| Exact completion | evidence root correlates event, Audit, definition, lesson, and sources |
| Idempotent replay | repeated reconcile/read returns the same view and one Audit row |
| Variable valid sources | zero-to-many reordered Unicode sources canonicalize without fixture-count assumptions |
| Missing or changed owner fact | bounded unavailable/inconsistent error; no partial view or new owner write |
| Retained conflict | same event identity with changed meaning remains denied and original row survives |
| PostgreSQL containment | read query touches Audit-owned table only and update/delete remain denied |
| Layer isolation | no API/Web/provider/model/identity implementation dependency enters the core |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit/test_learning_lineage.py backend/tests/unit/audit/test_provenance_contract.py -q`
- `backend\.venv\Scripts\python.exe -m pytest backend/tests/integration/audit/test_postgres_learning_lineage.py -q` with the repository PostgreSQL test DSN
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Freeze an exact candidate, run the tracked affected-check plan and qualifying
verification, then obtain one independent technical disposition. Do not add
unrelated API, Web, or full-suite work to compensate for absent impact.

## Stop Conditions

Stop for conflicting owner facts; a required Content/Assessment table read;
copied owner payloads; a new migration or public breaking contract; stale CAP
authority; unresolved identity, tenancy, retention/recovery, provider, legal,
encryption, queue, model, or external-execution choice; an active scope
collision; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
valid source count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0106.WRK-0181`; exact candidate and qualifying receipt;
public requests and owner adapter; lineage/digest invariants; idempotent
reconciliation and exact Audit read evidence; PostgreSQL containment;
architecture/security/documentation impact; migration/rollback status;
assumptions; residual gaps; CAP conformance; and unresolved decisions. Confirm
that HTTP/client/UI/live qualification remains WRK-0182/WRK-0183 scope.

## Planning History

- 2026-10-18: Authored just in time after WRK-0180 completion. The packet
  consumes the frozen provenance contract through existing owner public seams,
  adds no lower-level approval, and leaves protected transport to WRK-0182.
- 2026-10-18: Activated from clean base `b483973` after dependency, CAP
  authority, decision readiness, write scope, and ownership revalidation.
