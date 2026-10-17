---
id: WRK-0125
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: ["WRK-0124"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/migrations/README.md", "backend/migrations/assessment/assessment_0004_project_submission_evidence.down.sql", "backend/migrations/assessment/assessment_0004_project_submission_evidence.up.sql", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/assessment/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/assessment/adapters/project_submission_gateways.py", "backend/src/financial_ai_academy/modules/assessment/application/service.py", "backend/src/financial_ai_academy/modules/assessment/ports/project_submission_gateways.py", "backend/src/financial_ai_academy/modules/assessment/ports/repositories.py", "backend/src/financial_ai_academy/modules/assessment/public.py", "backend/src/financial_ai_academy/modules/project/README.md", "backend/src/financial_ai_academy/modules/project/application/service.py", "backend/src/financial_ai_academy/modules/project/public.py", "backend/tests/integration/assessment/test_postgres_project_submission.py", "backend/tests/unit/assessment/test_project_submission_service.py", "backend/tests/unit/project/test_project_learning_snapshot.py", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/project-submission-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0125-compose-project-submission-persistence.md"]
generated_artifacts: []
base_revision: 4810c3a83d65b564342c50dd840df244e374cc92
claim_id: WRK-0125:1d5e50e1-ab03-4e12-ae08-f4eda430527b
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T03:26:49Z
---

# Agent Work Packet: Compose Project Submission Persistence

## Objective and Deliverable

Add transport-neutral Assessment operations that assemble one learner-authorized
project-submission candidate from Project, Content, and Curriculum public
operations; validate an exact WRK-0124 submission; and atomically retain the
accepted immutable evidence and outbox event in PostgreSQL. The same operations
must return deterministic refusal issues without persistence, provide exact
evidence and ordered history reads, preserve exact replay, and append a later
snapshot as a superseding occurrence without rewriting prior evidence. This
packet stops before FastAPI, OpenAPI, generated clients, projection consumers,
Audit consumers, or browser behavior.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md`. Route through the baseline, architecture-contracts,
learning-adaptation, testing-quality, and delivery-planning context. Apply the
change-impact matrix and decision-readiness register. Read CAP-0007, SLI-0032,
WRK-0124, ADR-0005, ADR-0011, ADR-0012, the Assessment and Project submission
contracts, Assessment/Project/Content/Curriculum public operations and nearest
READMEs, the project snapshot and learning-brief executable schemas, existing
practice application/repository/migration patterns, affected tests, and
concurrent-work controls.

## Decisions and Assumptions

- ADR-0012 leaves Project authoritative for the shell, learning origin,
  workspace, and immutable snapshot; Content authoritative for the approved
  brief; Curriculum authoritative for placement; and Assessment authoritative
  only for submission validation, immutable evidence, event, and history.
- Assessment adapters may call only public operations. They may not read or
  join another module's tables or retain Project-owned bytes or workspace
  records.
- A milestone is revision-bound to its exact approved brief. The candidate's
  `milestone_version` is therefore the exact `brief_version`; no independent
  milestone lifecycle or fall-forward policy is invented.
- The service receives learner identity from its caller and obtains evidence
  and event IDs plus canonical UTC time from existing server ports. Submission
  documents cannot select identity, sequence, occurrence, supersession, or
  server metadata.
- Validation refusals are side-effect free. Accepted submission, evidence,
  ordered resource bindings, and outbox event commit in one Assessment-owned
  transaction.
- Exact replay identity is learner plus submission ID plus WRK-0124 canonical
  request fingerprint. Changed reuse conflicts. A distinct accepted snapshot
  appends the next locked Project occurrence and points to the immediately
  prior submission without updating it.
- Existing knowledge-check and practice data remain unchanged. The new
  migration is additive and ordinary mutation of accepted Project evidence is
  rejected.

## In Scope

- Define Assessment-local gateway ports and adapters over the existing Project,
  Content, and Curriculum public operations.
- Add one Project-owned public operation that returns only immutable snapshot,
  learning-origin, and exact safe resource-reference facts. Rehydrate domain-
  link target version/as-of from the workspace document retained atomically
  with that snapshot; never expose note bodies, URLs, artifact bytes, paths, or
  current mutable workspace state.
- Assemble the closed candidate from one authorized learning-origin Project,
  exact immutable snapshot, exact published brief, and exact placement without
  artifact bytes, private paths, or mutable workspace state.
- Add transport-neutral public requests and Assessment service operations for
  candidate reading, validation/submission, exact evidence reading, and ordered
  Project submission history.
- Reuse WRK-0124 parsing, validation, evidence, event, and history projection;
  do not duplicate or reinterpret deterministic policy.
- Extend the Assessment repository port and PostgreSQL adapter with atomic
  append, exact replay, conflict, locked occurrence/accepted-sequence ordering,
  supersession, exact evidence read, ordered history, and safe event replay
  storage.
- Add checksum-protected `assessment_0004` forward/down migrations with
  append-only guards and empty-development rollback limits.
- Prove public-operation isolation, independent-project denial, source drift,
  validation refusal, accepted persistence, replay, conflict, concurrency,
  supersession, rollback, restart, append-only behavior, confidentiality, and
  regression behavior.
- Update Assessment and project-submission architecture guidance plus planning
  state and evidence.

## Out of Scope

FastAPI models or routes; OpenAPI; generated TypeScript; browser UI; Learner-
model or Audit consumption; dispatch workers; retries outside transaction
replay; instructor or AI grading; mastery/competency; live Portfolio meaning;
artifact execution or active rendering; external providers; organization
tenancy; managed-cloud recovery; new dependencies or lockfiles; remote push or
deployment.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Assessment public/application | existing practice and knowledge-check operations | additive project candidate, submit, evidence, and history requests/operations | Establish the shared transport-neutral API core |
| Project public/application | retained snapshot and workspace record | additive learner-safe learning-snapshot-facts operation | Preserve exact domain-link version/as-of without exposing stored workspace or crossing persistence ownership |
| Cross-module collaboration | Project snapshot facts, Content brief, Curriculum placement public operations | Assessment-local gateway ports/adapters only | Assemble exact learner-safe facts without cross-module persistence access |
| Assessment persistence | repository port/adapter and migration stream | additive Project evidence aggregate, replay, history, and outbox storage | Preserve atomic immutable evidence and deterministic ordering |
| Verification | WRK-0124 contract tests and existing Assessment/PostgreSQL suites | focused unit and real-database tests | Prove refusal, replay, concurrency, supersession, restart, and isolation |
| Canonical guidance | Assessment and Project submission contracts | listed documentation | Record runtime ownership and remaining host/consumer seams |
| Planning | SLI-0032, WRK-0125, register | listed planning files | Keep JIT refinement and lifecycle synchronized |

No WRK-0124 schema or compatibility record, Project/Content/Curriculum
persistence schema or adapter, host, OpenAPI, generated client, web file,
dependency, or lockfile may change.

## Contracts and Interfaces

The candidate operation accepts server-resolved `learner_id`, `project_id`, and
`snapshot_id`. The Project adapter opens the exact learner-owned shell and
snapshot; an independent origin is denied. Content and Curriculum adapters
resolve the origin's exact brief and placement and reject any version/digest
drift. The adapter maps the closed snapshot references to WRK-0124 resource
values and the brief's ordered milestones to brief-version-bound candidate
milestones, then the accepted contract adapter parses the produced candidate.

The submit operation accepts the same route-bound selectors and exact closed
submission bytes. It validates against a freshly resolved candidate. Refusal
returns the WRK-0124 validation result and writes nothing. Acceptance supplies
server metadata, commits one immutable `ProjectCompletionEvidence` and safe
`ProjectCompletionEvent`, and returns the original stored evidence on exact
replay.

The repository's durable replay key is `(learner_id, submission_id)` plus the
canonical fingerprint. Project history is learner- and project-bound,
occurrence is contiguous per stream, accepted sequence is monotonically
increasing, and a later distinct accepted submission points to the immediate
prior submission. Exact evidence/history reads are revalidated through the
contract adapter before leaving Assessment.

The outbox stores only the WRK-0124 safe event document. It contains no learner
identity, artifact-level mapping, bytes, paths, secrets, database facts,
qualitative claims, or mutable Project state. JIT-B2 will publish these
operations through one protected API; JIT-C will consume only typed safe replay.

## Dependencies and Parallel Safety

WRK-0124 is complete and supplies the only accepted candidate, submission,
validation, evidence, event, history, canonical fingerprint, and safe issue
semantics. WRK-0125 owns shared Assessment application/repository files,
Assessment migrations, SLI/register state, and the gateway adapters, so it is
not parallel-safe with the dependent API/client, projection/Audit, browser, or
qualification packets. Complete this packet before authoring JIT-B2.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Eligible candidate | one learner-owned learning Project and exact closed snapshot whose origin matches the published brief and placement | candidate assembly runs | one closed WRK-0124 candidate contains exact origin, milestone, snapshot, and resource facts only | unit/public-gateway |
| Independent or stale source | the Project is independent or a brief, placement, origin, shell, or snapshot fact differs | candidate assembly runs | a bounded denial occurs before persistence without fall-forward or private detail | unit/integration |
| Deterministic refusal | a closed submission omits, duplicates, invents, or stales milestone/resource evidence | submit runs | ordered safe issues return and no evidence/outbox row exists | unit/PostgreSQL |
| Accepted submission | every exact milestone maps to closed snapshot resources | submit runs | one immutable evidence/event aggregate commits atomically and is reopenable after restart | unit/PostgreSQL |
| Exact replay and conflict | the same learner/submission repeats equivalent input or changed input | concurrent or later calls run | equivalent replay returns original IDs/time; changed reuse conflicts without another row | unit/PostgreSQL concurrency |
| Superseding snapshot | a later exact snapshot is submitted with a new submission ID | commit serializes | a new occurrence points to the prior submission and both evidence records remain unchanged and ordered | PostgreSQL/history |
| Atomic failure | any aggregate or outbox write fails | repository commit runs | no partial evidence, binding, or event remains | PostgreSQL fault injection |
| Append-only evidence | an ordinary update/delete targets accepted Project evidence | PostgreSQL executes it | mutation is rejected and retained history remains intact | PostgreSQL |
| Shape flexibility | valid briefs/snapshots vary milestones, resource kinds/counts/order, Unicode, optional exact-version forms, IDs, and times | assembly, persistence, and replay run | meaning is preserved without fixture-count or ASCII assumptions | parameterized unit/PostgreSQL |
| Existing behavior | knowledge-check, practice, Project snapshot, Content, and Curriculum regressions run | the additive migration/core is installed | existing public behavior and retained records are unchanged | regression/architecture |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/assessment/test_project_submission_service.py backend/tests/unit/assessment/test_project_submission_contract.py backend/tests/contract/assessment_project
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/assessment/test_postgres_project_submission.py backend/tests/integration/assessment/test_postgres_assessment.py backend/tests/integration/assessment/test_postgres_practice_submission.py backend/tests/integration/assessment/test_postgres_practice_progress.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/project backend/tests/unit/content backend/tests/unit/curriculum backend/tests/unit/assessment
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0125-compose-project-submission-persistence.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

PostgreSQL checks use the repository's isolated test DSN/container. Submit one
exact candidate, generate a fresh affected-verification receipt, and obtain one
independent technical review. Add no dependency or lockfile change.

## Documentation and Evidence Update

Document the public-operation-only gateway boundary, exact candidate assembly,
server-owned metadata, side-effect-free refusal, additive Assessment tables,
atomic aggregate/outbox commit, canonical replay/conflict identity, locked
occurrence/supersession/history rules, append-only protection, rollback limits,
and deferred host/generated-client/consumer/UI work. Record exact checks,
candidate/receipt, review disposition, assumptions, and residual gaps in this
packet and SLI-0032. Keep approval and reviewer records only in ignored local
storage.

## Stop Conditions

Stop for a breaking WRK-0124 or Project snapshot contract; ambiguous exact-
source or milestone-version meaning; cross-module table/object access; copying
Project-owned bytes or mutable workspace state; caller-selected learner/time/
sequence/supersession authority; mutable/deletable accepted evidence; private
data in an event; qualitative, mastery, instructor, or AI authority; execution,
provider, Portfolio, tenancy, managed-cloud, or legal/commercial expansion; new
dependency; active scope collision; conflicting canonical source; or material
CAP-0007/SLI-0032 drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
nonfunctional styling, generated ordering with unchanged meaning, or another
inconsequential in-scope correction. Fix it locally or defer optional cleanup
to CAP-0031.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0125`; the exact candidate and receipt; public
gateway/application seams; table/transaction/outbox boundaries; refusal,
replay, conflict, concurrency, supersession, rollback, restart, append-only,
confidentiality, anti-rigidity, and regression evidence; focused, architecture,
security, planning, documentation, aggregate, and independent-review results;
documentation impact; assumptions; and residual gaps. Confirm that host,
OpenAPI, generated client, browser, Learner-model/Audit consumers, dependencies,
AI authority, and external execution did not change, then leave JIT-B2 ready
for just-in-time refinement.

## Planning History

- 2026-10-17: Authored just in time after WRK-0124 completed. The former JIT-B
  seam was split into one independently reviewable application/persistence
  packet and a dependent protected API/generated-client packet. This refinement
  preserves the approved CAP/SLI outcome and adds no lower-level approval gate.
- 2026-10-17: Claimed from base revision `4810c3a` after the implementation
  gate confirmed current CAP authority, dependency completion, decision
  readiness, exact scope, and no active ownership collision.
- 2026-10-17: Returned to `ready` before implementation when revalidation found
  that the existing Project snapshot projection intentionally omits a domain
  link's exact target version/as-of. Refined the packet to add a Project-owned
  safe snapshot-facts operation backed by the workspace record already retained
  atomically with the snapshot. This prevents guessed values and cross-module
  table access without changing the approved CAP/SLI outcome or persistence
  schema.
