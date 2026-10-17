---
id: WRK-0136
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0071
capability: CAP-0017
depends_on: [WRK-0135]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/application/service.py", "backend/src/financial_ai_academy/modules/personal_workspace/ports/learning_reference.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/learning_reference.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/project_reference.py", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/unit/personal_workspace/test_learning_reference_gateway.py", "backend/tests/unit/personal_workspace/test_project_reference_gateway.py", "backend/tests/unit/personal_workspace/test_personal_workspace_service.py", "backend/tests/integration/personal_workspace/test_postgres_personal_workspace.py", "backend/tests/integration/api/test_single_profile_personal_workspace_api.py", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/openapi.json", "contracts/api/README.md", "apps/web/README.md", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/features/personal-workspace/model.ts", "apps/web/src/features/personal-workspace/PersonalWorkspacePage.tsx", "apps/web/tests/unit/personalWorkspaceModel.test.ts", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/modules/module-map.md", "docs/planning/vertical-slices/SLI-0071-organize-project-workspaces-snapshots-resources.md", "docs/planning/work-packets/WRK-0136-compose-personal-workspace-project-api.md", "docs/planning/register.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: d408affe1d01910c1ba8cd1b1c9554a11ec5393d
claim_id: WRK-0136:427699ce-df74-4b69-bad6-b03efc4b68fb
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T13:10:53Z
---

# Agent Work Packet: Compose Personal-Workspace Project API

## Objective and Deliverable

Deliver the API-first application, persistence-compatibility, protected HTTP,
reviewed OpenAPI, and generated TypeScript-client seam for all three accepted
Project reference variants. Server-owned learner context must flow through one
closed reusable source dispatcher to learner-bound Project public reads, while
browser, command-line, service, and future headless consumers receive the same
Personal-workspace contract and authority.

This packet does not add Project save controls. It does keep the existing Saved
Learning read surface compatible with the widened public response union by
displaying closed Project-reference facts already created by an API client.
Project entry actions and the isolated live journey remain in dependent JIT-C
and JIT-D packets.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed architecture/contracts,
security, testing, and delivery-planning context; change-impact matrix;
decision-readiness register; ADR-0007, ADR-0009, ADR-0011, ADR-0012, and
ADR-0021; CAP-0017; SLI-0071; completed WRK-0135; affected module/API/web
READMEs; Personal-workspace application, persistence and API seams; Project
public operations; reviewed OpenAPI generator; generated-client tooling; and
the nearest focused tests.

## Decisions and Assumptions

- Project remains authoritative for access, lifecycle, shell, workspace,
  snapshot, and artifact manifests. Personal workspace stores only the closed
  inert values accepted by WRK-0135.
- Learner identity becomes an explicit required input to the source-gateway
  port and is supplied only from the application request created by the
  authenticated server session. Curriculum resolution may ignore that value,
  but callers and implementations share one transport-neutral signature.
- One Personal-workspace-owned dispatcher selects Curriculum or Project
  adapters by the closed selector union. Optional adapter absence, unsupported
  selector meaning, missing/denied targets, and mismatched return values fail
  through the existing bounded source-unavailable result.
- Project source-bearing creates require `project.read` in addition to the
  existing Personal-workspace write permission. Curriculum variants retain
  their current owner permissions. Non-source mutations need no owner read.
- Existing PostgreSQL storage is a versioned JSON aggregate already governed
  by the expanded Personal-workspace contract. No migration is added unless a
  focused persistence test proves the existing representation cannot round-
  trip all three variants, exact replay, restart, and learner isolation.
- The reviewed OpenAPI snapshot remains the sole source of generated TypeScript
  types. No hand-maintained browser model, alternate AI endpoint, or UI-only
  authority is introduced.

## In Scope

- Extend the source-gateway port and Personal-workspace service so server-owned
  learner identity reaches source resolution, and validate exact Project
  workspace, snapshot, and artifact selector/result correlation before any
  write.
- Compose a closed Curriculum/Project dispatcher from the existing public-only
  adapters and wire it into local application composition without importing
  either owner module's internals or persistence.
- Prove the existing PostgreSQL JSON aggregate and replay store round-trip all
  three Project reference variants across restart with unchanged revision,
  digest, idempotency, stale-write, learner-isolation, and atomicity behavior.
- Extend request selectors and response reference unions in validated API
  models, owner-permission selection, selector mapping, API success/denial/
  guessed-target/confidentiality tests, and query-selected-learner refusal.
- Regenerate and verify the reviewed OpenAPI snapshot and TypeScript client;
  add headless/client compile evidence for each Project selector and safe
  response union, and keep the existing Saved Learning read surface exhaustive
  over that widened union without adding Project save controls.
- Update direct Personal-workspace API, contract, module, and architecture
  guidance plus SLI-0071, this packet, and the planning register.

## Out of Scope

New database tables or columns unless existing JSON persistence fails direct
qualification; destructive migration; Project mutation; artifact upload,
download, content, preview, export, archive expansion, or execution; browser
Project save entry points or new Project interactions;
live Docker/PostgreSQL/browser topology qualification; full accessibility or
restart journey; Portfolio/domain resources; collaboration; search/filter;
target refresh events; import/export; managed cloud; identity-mode or tenancy
change; provider/model/AI authority; external action; financial advice; new
dependency or lockfile change.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Application source seam | Existing port, Curriculum adapter, Project adapter, service and composition | Listed Personal-workspace application/port/adapter files and bootstrap composition | Carry server learner context and dispatch only the closed selector union |
| Persistence compatibility | Existing JSON repository and PostgreSQL integration suite | Focused Personal-workspace PostgreSQL tests; repository code only if direct evidence proves a defect and scope is refined first | Prove additive variants need no migration and preserve replay/restart behavior |
| Protected API | Current Personal-workspace models, permission helper and route contract | API models and focused API tests | Add closed Project selectors/references and require Project read authority |
| Generated consumer contract | Current OpenAPI snapshot, generator, Saved Learning reference display, and client checks | Snapshot, generated client files, exhaustive read-only reference display, and listed client/component tests | Preserve one browser/headless public seam without adding Project create controls |
| Architecture guidance | Current API, Personal-workspace and module assurance | Listed README and architecture Markdown | Record public-only ownership, API parity and remaining UI/live gap |
| Planning evidence | SLI-0071, WRK-0136, register | Listed planning files | Keep packet lifecycle and next seam synchronized |

No Project implementation, Project schema, Identity policy, browser feature,
design-system, migration, provider, deployment, dependency, or lockfile file
may change.

## Contracts and Interfaces

`LearningReferenceGatewayPort.resolve` receives one closed selector plus the
server-owned learner ID and canonical validation time. The dispatcher sends
Curriculum selectors only to `PublicCurriculumLearningReferenceGateway` and
Project selectors only to `PublicProjectLearningReferenceGateway`. The service
then checks returned type and exact selector identity before constructing the
existing revision-bound mutation intent.

The protected mutation body adds exactly these selector shapes:

- `project_workspace`: `project_id`;
- `project_snapshot`: `project_id`, `snapshot_id`;
- `project_artifact`: `project_id`, `artifact_id`, `artifact_version`.

The response union exposes exactly the WRK-0135 safe fields. It contains no
learner-selected owner, Project charter/origin, workspace/snapshot material,
artifact content, provenance URL, object/storage locator, permission claim,
download/export/preview/execution action, provider payload, or arbitrary URL.
All operations keep the current Personal-workspace paths, error envelope,
same-origin policy, revision and idempotency semantics. Project variants require
`project.read`; Personal-workspace reads/writes retain their existing required
permissions.

## Dependencies and Parallel Safety

WRK-0135 and SLI-0070 are complete. WRK-0136 owns shared Personal-workspace
application/API/OpenAPI/generated-client meaning and therefore is not parallel-
safe with another packet touching those files or contracts. JIT-C cannot start
until this packet is complete and the generated client is stable.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Closed dispatch | Each Curriculum and Project selector reaches the source port with a server learner and validation time | The dispatcher resolves it | Exactly the owning public adapter runs; unsupported or absent adapters fail without affecting unrelated selector kinds | unit anti-rigidity |
| Exact Project correlation | A Project adapter returns a workspace, snapshot, or artifact reference | The service prepares a create note/bookmark intent | Exact selector identities and artifact version match before persistence; mismatches fail with no write | application/unit |
| Protected Project create | An authenticated learner has Personal-workspace write and Project read | Each Project selector is posted | The same Personal-workspace operation returns the closed safe response with server-owned learner context | API/headless |
| Permission denial | Project read is missing, or a guessed/cross-learner target is unavailable | A Project selector is posted | The request fails before or within public Project resolution without confirming protected existence or writing replay/workspace state | API/application/security |
| Existing persistence | Project references coexist with Curriculum references in one aggregate | Writes, exact replay, reopen, and process-level repository recreation run | Exact variants, order, revision, digest, replay and learner isolation survive with no schema migration | PostgreSQL integration |
| Retry and stale write | One Project reference mutation is repeated or conflicts | Persistence runs | Exact replay skips source resolution; changed-key reuse and stale revision fail without target mutation or overwrite | application/PostgreSQL |
| Generated headless parity | The OpenAPI snapshot and TypeScript client regenerate | Typed direct clients construct all selectors and inspect all response kinds | Generated types compile and no browser-only or separate AI authority appears | OpenAPI/client contract |
| Closed public shape | Extra Project content, storage, permission, provider or execution fields are supplied or returned | API validation runs | The request/response fails closed and private values do not enter the error envelope | API/contract |
| Flexible valid data | IDs, titles, revisions, snapshot/artifact facts, times, collection order and optional labels vary within accepted bounds | Complete focused suites run | Invariants hold without exact wording, fixture count/order or UI assumptions | parameterized unit/integration |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace backend/tests/integration/api/test_single_profile_personal_workspace_api.py backend/tests/architecture/test_module_boundaries.py
backend/.venv/Scripts/python.exe -m pytest backend/tests/integration/personal_workspace
backend/.venv/Scripts/python.exe -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
node apps/web/tests/contract/generated-client.test.mjs
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0136-compose-personal-workspace-project-api.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use the repository's isolated PostgreSQL runner or exact test DSN for database
evidence; never target a shared database. Regenerate OpenAPI and the client only
through their committed generators, then run both in `--check` mode. Run the
affected-check plan against one exact clean candidate and obtain one fresh
qualifying receipt and independent technical disposition.

## Documentation and Evidence Update

Document server-owned learner propagation, closed owner dispatch, the three API
selector/response variants, `project.read`, JSON persistence compatibility,
same browser/headless contract, and remaining browser/live seams. Completion
evidence records exact focused/PostgreSQL/API/client counts, generated-artifact
currency, authorization and containment results, assumptions, unqualified live
checks, changed files, receipt, and residual gaps. Receipts and reviewer records
remain only in ignored local control-plane storage.

## Stop Conditions

Stop for direct Project/Curriculum internal or persistence import; learner ID
accepted from the caller; reference granting permission; copied Project content
or storage location; Project mutation/download/export/preview/execution;
destructive or unplanned migration; new API route or identity model beyond the
existing Personal-workspace operation; Project browser entry/action or styling
work beyond exhaustive read compatibility; active
scope collision; dependency/lockfile change; private-data leak; unresolved
decision; conflicting canonical sources; or material CAP-0017/SLI-0071 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report the exact candidate; source-port/dispatcher signature; Project identity
correlations; permissions; PostgreSQL no-migration evidence; API selector and
response unions; OpenAPI/client reproduction and headless compile evidence;
focused, architecture, security, affected, aggregate and independent-review
results; changed files; documentation impact; assumptions; unqualified live/UI
checks; and residual gaps. Confirm no browser interface, Project mutation,
artifact content/download/execution, migration, provider, managed-cloud,
separate AI authority, or financial action changed, then leave JIT-C dependency-
ready.

## Completion Evidence

- Exact reviewed implementation candidate:
  `8570856d04da5085ba777233d5252ce84928f876`, a strict descendant of the
  original submitted candidate after two bounded functional corrections.
- The application now carries server-owned learner identity through one closed
  Curriculum/Project dispatcher. Each Project workspace, snapshot, and artifact
  result must match its selector identity before persistence, and an unavailable
  owner adapter fails only its own selector through the bounded source-
  unavailable result.
- The protected Personal-workspace API and reviewed OpenAPI/generated client
  expose the three closed Project selector/reference variants through the same
  browser and headless contract. Project source-bearing creates require
  `project.read`; no learner-supplied owner, alternate AI endpoint, or UI-only
  authority was added.
- Focused backend contract, application, API, and architecture qualification
  passed 215 tests on the corrected candidate. The focused browser model and
  component qualification passed 55 tests, including real loader/action
  acceptance for every Project variant and rejection of malformed paths,
  chronology, bounds, destinations, enums, and private fields.
- Existing PostgreSQL JSON aggregate compatibility passed 10 isolated tests on
  the original implementation candidate before the correction. The correction
  changed only dispatcher absence handling and browser response validation; it
  did not change persistence, migration, request/response schemas, OpenAPI, or
  generated client output. No migration was required.
- The corrected exact-candidate affected plan passed all 10 selected checks.
  OpenAPI and generated-client currency, TypeScript typecheck, zero-warning web
  lint, production build, 17 architecture checks, 10 security control groups,
  225 planning artifacts, 373 Markdown files, 125 design tokens, 56 icons,
  whitespace integrity, and the fixed 29-check aggregate readiness gate passed.
- Ignored local control-plane storage retains the qualifying exact-candidate
  receipt and closed technical findings. Tracked artifacts contain no approval
  or reviewer metadata.
- No Project mutation, artifact content/download/preview/export/execution,
  destructive migration, provider, managed-cloud, separate AI authority, or
  financial action changed. Contextual Project save controls and isolated live
  browser/headless qualification remain in JIT-C and JIT-D.

## Planning History

- 2026-10-17: Authored just in time after WRK-0135 completed. The packet
  composes its closed Project references into the existing JSON persistence and
  protected Personal-workspace API, preserves one generated browser/headless
  contract, and leaves browser entry points and live journey qualification to
  JIT-C/JIT-D. No lower-level approval is required.
- 2026-10-17: Refined after client generation exposed a pre-existing Curriculum-
  only read assumption. Added the existing Saved Learning reference display and
  focused component test to scope solely for exhaustive safe rendering of API-
  created Project references; Project save controls remain JIT-C work.
- 2026-10-17: Candidate verification exposed two closed-contract gaps: the
  browser response guard still accepted only Curriculum references, and the
  dispatcher did not model an unavailable owner adapter explicitly. Added the
  existing response guard and focused browser model/action tests to scope so
  valid Project references survive the real loader/action boundary while
  malformed or private fields still fail closed. The dispatcher correction
  remains inside its original backend scope.
- 2026-10-17: Returned the corrected packet to verification after all Project
  reference variants passed the real browser loader/action response guard,
  malformed and private values failed closed, unavailable owner adapters stayed
  isolated, and the focused backend, web, contract, architecture, security,
  planning, documentation, design, lint, type, and whitespace checks passed.
- 2026-10-17: Finalized the Project persistence/API/OpenAPI/generated-client
  seam after exact-candidate affected verification, aggregate readiness, and
  independent technical verification completed with no open functional gap.
  JIT-C is dependency-ready without changing CAP-0017 or SLI-0071 meaning.
