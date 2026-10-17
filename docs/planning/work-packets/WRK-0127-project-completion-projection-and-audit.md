---
id: WRK-0127
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: ["WRK-0126"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/assessment/public.py", "backend/src/financial_ai_academy/modules/assessment/application/service.py", "backend/src/financial_ai_academy/modules/assessment/ports/project_submission.py", "backend/src/financial_ai_academy/modules/assessment/adapters/project_submission_contract.py", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/learner_model", "backend/src/financial_ai_academy/modules/audit", "backend/migrations/learner_model", "backend/migrations/audit", "backend/migrations/README.md", "backend/src/financial_ai_academy/modules/README.md", "backend/tests/unit/assessment/test_project_submission_contract.py", "backend/tests/unit/assessment/test_project_submission_service.py", "backend/tests/integration/assessment/test_postgres_project_submission.py", "backend/tests/unit/learner_model", "backend/tests/integration/learner_model", "backend/tests/unit/audit", "backend/tests/integration/audit", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/project-submission-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0127-project-completion-projection-and-audit.md"]
generated_artifacts: []
base_revision: ec73bd62a4c56a5a8fac5cd66ab4a60b4d58a8fa
claim_id: WRK-0127:f5c83376-c5b5-43b4-8824-3c1eb0737487
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T04:20:09Z
---

# Agent Work Packet: Deliver Project Completion Projection and Audit References

## Objective and Deliverable

Complete the non-UI consumer seam for accepted Project submissions. Assessment
will expose its retained `assessment.project.completed@1.0.0` events through a
typed, validated, read-only replay operation. Learner model will rebuild one
bounded project-completion view from that public source, and Audit will append
idempotent integrity/provenance references to the same events. Assessment
remains the source of submission evidence; neither consumer may read or mutate
Assessment persistence.

## Required Context

Follow the repository-root `AGENTS.md` and `docs/README.md` startup and route
through the baseline, architecture-contracts, learning-adaptation,
testing-quality, and delivery-planning packs. Read CAP-0007, SLI-0032,
WRK-0124 through WRK-0126, ADR-0005, ADR-0011, ADR-0012, the Assessment and
Project-submission contracts, executable Assessment Project schemas, current
Assessment replay patterns, Learner-model and Audit public/domain/application/
repository seams, migration guidance, nearest READMEs, affected tests,
change-impact guidance, decision readiness, and concurrent-work rules.

## Decisions and Assumptions

- Completion means only that Assessment accepted structurally complete
  milestone-to-snapshot evidence for the exact learning-started Project. It is
  not mastery, competency, certification, qualitative grading, suitability, or
  advice.
- Assessment's existing Project outbox is immutable source evidence. Its new
  replay operation is a synchronous query, not dispatch, acknowledgement,
  checkpoint, delivery guarantee, worker, or queue selection.
- Learner-model state is disposable and rebuildable from the complete typed
  replay. Audit state is append-only integrity/provenance evidence and is not a
  second submission or completion database.
- Event documents continue to use the already reviewed executable
  `completion-event` schema. No Project submission wire meaning changes.

## In Scope

- Add a typed Assessment request/replay operation for one learner and Project,
  validating retained event envelopes and their correlated immutable evidence
  against the existing contract before returning stable occurrence order.
- Fail closed on malformed, unsupported, duplicate, cross-learner,
  cross-Project, or event/evidence-inconsistent retained source data.
- Add Learner-model Project source values, deterministic derivation, public
  request/view/history types, public-Assessment adapter, application operation,
  stable source digest, and atomic replace-from-complete-source persistence.
- Preserve exact event, evidence, submission, Project, snapshot, brief,
  placement, policy, milestone, occurrence, supersession, digest, and time
  references needed to explain and rebuild completion, without copying Project
  artifact bytes or Assessment validation internals.
- Add Audit Project source values, canonical integrity derivation,
  public-Assessment adapter, application reconciliation operation, deterministic
  Audit identity, append-only persistence, exact replay idempotency, and changed
  same-event conflict handling.
- Add additive Learner-model and Audit migrations with safe development down
  paths, focused unit/architecture/real-PostgreSQL tests, and synchronized
  module, contract, slice, packet, and register guidance.

## Out of Scope

HTTP/OpenAPI/generated-client changes; browser pages or components; Project or
Assessment schema meaning changes; edits to accepted Assessment evidence;
background delivery, queue, worker, checkpoint, or notification choices;
mastery, competency, ranking, recommendation, grading, instructor/peer/AI
review, overrides, or certification; artifact execution or active rendering;
Portfolio/provider behavior; organization tenancy; managed-cloud recovery;
new dependencies or lockfiles; remote push or deployment.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Assessment public/application | typed Project-event replay over the existing owned outbox and contract | Supply one validated consumer seam without exposing persistence |
| Learner model | additive Project projection types, policy, operation, adapter, repository, and migration | Own rebuildable project-activity completion and its source references |
| Audit | additive Project event mapping, reconciliation, records, repository, and migration | Own append-only integrity/provenance references only |
| Verification | focused Assessment, Learner-model, Audit, PostgreSQL, and architecture tests | Prove replay, isolation, rebuild, idempotency, tamper denial, and interruption |
| Guidance/planning | listed module, contract, architecture, slice, packet, and register files | Record the delivered boundary and remaining browser/qualification work |

No API route, generated artifact, browser code, Project persistence, Content or
Curriculum contract, dependency, or lockfile may change.

## Contracts and Interfaces

Assessment adds a public request containing server-supplied `learner_id` and
`project_id`, returning an immutable tuple of typed
`assessment.project.completed@1.0.0` events in occurrence order. Every event
retains its event identity/time and correlated immutable Project completion
evidence. Persisted envelopes are revalidated against the existing executable
schema and retained evidence before release.

Learner model adds an `open_project_completion` operation for the same trusted
context. Its result identifies the Project, reports `completed` only when at
least one valid event exists, labels the meaning as bounded Project activity
completion, supplies a stable source digest and rebuild time, and returns
ordered immutable source references. Audit adds a
`reconcile_project_completion` operation whose receipt discloses only Project,
count, and source digest; stored records contain public event/source identity,
actor/action, exact source provenance, canonical integrity digest, and record
time, but no workspace data or projection authority.

## Dependencies and Parallel Safety

WRK-0126 is complete and the existing protected API can create and reopen the
Assessment evidence consumed here. This packet owns the shared Assessment,
Learner-model, Audit, migration, architecture, and planning seams, so no
dependent SLI-0032 work is parallel-safe with it.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Empty replay | Assessment returns no events; Learner model is incomplete; Audit appends nothing | unit/PostgreSQL |
| Exact completion | One accepted submission replays with exact event/evidence provenance and produces one completed projection and one Audit reference | unit/PostgreSQL |
| Superseding history | Multiple accepted snapshots remain ordered, retain prior links, and rebuild the current complete view without rewriting history | unit/PostgreSQL |
| Exact repeat | Replaying/rebuilding/reconciling unchanged source produces the same source digest, one derived history set, and one Audit row per event | unit/PostgreSQL |
| Isolation | Other-learner or other-Project data is not disclosed or projected | Assessment/Learner-model/Audit |
| Invalid source | Malformed, duplicate, mismatched, unsupported, or changed same-event source fails closed before projection replacement or Audit overwrite | unit/PostgreSQL |
| Interrupted write | Injected Learner-model replacement or Audit append failure preserves the prior complete projection and appends no partial Audit batch | PostgreSQL |
| Shape flexibility | One through several occurrences, varied milestone/resource counts, Unicode learner content upstream, optional supersession, and generated IDs/times do not depend on one fixture | anti-rigidity unit/integration |
| Boundary preservation | Consumers import only Assessment public types and never read Assessment/Project tables or claim mastery, grading, advice, queue, or execution authority | architecture/security/docs |

## Verification Commands

Run focused Assessment Project, Learner-model, and Audit unit and real
PostgreSQL suites, then:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment/test_project_submission_service.py backend/tests/unit/learner_model backend/tests/unit/audit
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment/test_postgres_project_submission.py backend/tests/integration/learner_model backend/tests/integration/audit
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0127-project-completion-projection-and-audit.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use the isolated PostgreSQL qualification environment already allocated for
CAP-0007. Submit one exact affected candidate, produce a fresh verification
receipt, and obtain one independent technical review. Add no dependency or
lockfile change.

## Documentation and Evidence Update

Document the Assessment replay operation, validation and ordering; Learner-
model completion meaning, rebuild and persistence; Audit digest, append,
replay, and conflict behavior; migrations and safe down paths; focused and
aggregate checks; exact candidate/receipt; independent-review disposition;
assumptions; and remaining JIT-D/JIT-E work. Keep approval and reviewer records
only in ignored local storage.

## Stop Conditions

Stop for a breaking Assessment Project contract, cross-module persistence
access, mutation or duplication of source business evidence, ambiguous
completion ownership, mastery/competency/qualitative grading, executable
artifact behavior, provider/financial action, external delivery semantics,
tenancy/recovery expansion, new dependency, active file-scope collision,
conflicting canonical source, or material CAP-0007/SLI-0032 drift.

Do not stop or reopen review for harmless whitespace, optional prose,
nonfunctional styling, or generated ordering with unchanged meaning. Correct
such items locally or defer optional cleanup to CAP-0031.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0127`; exact candidate and receipt; typed replay,
projection, and Audit contracts; source validation, isolation, supersession,
rebuild, replay, tamper, interruption, and anti-rigidity evidence; migrations;
focused, architecture, security, planning, documentation, aggregate, and
independent-review results; documentation impact; assumptions; and residual
gaps. Confirm that API/browser behavior, Project and Assessment schema meaning,
mastery/AI authority, dependencies, queues, providers, and external execution
did not change, then leave JIT-D ready for refinement.

## Planning History

- 2026-10-17: Authored and validated immediately after WRK-0126 completed.
  The existing Project event schema and public Assessment evidence make both
  consumers implementable inside the approved CAP-0007/SLI-0032 package with no
  new durable decision or human approval gate.
- 2026-10-17: Before implementation, narrowed the replay validation seam to an
  additive parser on the existing Assessment Project contract adapter and added
  its focused contract test to declared scope. Contract meaning and CAP scope
  are unchanged.
