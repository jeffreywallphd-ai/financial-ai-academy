---
id: WRK-0110
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: SLI-0030
capability: CAP-0007
depends_on: [WRK-0109]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/scripts/generate-api-client.mjs", "apps/web/src/generated/api-client", "apps/web/tests/contract/client-usage.ts", "backend/migrations/curriculum", "backend/migrations/project", "backend/migrations/README.md", "backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/hosts", "backend/src/financial_ai_academy/modules/content", "backend/src/financial_ai_academy/modules/curriculum", "backend/src/financial_ai_academy/modules/identity", "backend/src/financial_ai_academy/modules/project", "backend/tests/architecture", "backend/tests/contract/lesson_package", "backend/tests/integration/api", "backend/tests/integration/assessment", "backend/tests/integration/curriculum", "backend/tests/integration/project", "backend/tests/unit/content", "backend/tests/unit/curriculum", "backend/tests/unit/identity", "backend/tests/unit/project", "backend/tests/unit/test_bootstrap_settings.py", "contracts/api", "contracts/compatibility/lesson-package/v1", "contracts/learning/lesson-package/v1", "deployments/local", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/project-workspace-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0030-create-independent-or-learning-project.md", "docs/planning/work-packets/WRK-0110-deliver-project-persistence-public-api.md", "tests/architecture"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 908f15d5f7fe99181c3bdbd49c80077369b805ba
claim_id: WRK-0110:3404de80-d341-4b3a-ac21-75ed6c49c02d
claimed_by: codex-cap-0007
claimed_at: 2026-10-16T20:06:34Z
---

# Agent Work Packet: Deliver Project Persistence and Public API

## Objective and Deliverable

Compose the approved Project contracts into one server-authoritative backend
flow that admits exact learning-project briefs through Content, records their
exact placement through Curriculum, creates and reopens independent or
learning-started Project shells through Project-owned PostgreSQL storage, and
exposes protected create/list/read HTTP operations in reviewed OpenAPI and the
generated TypeScript client. Browser, command-line, service, and future
headless AI consumers use the same public operations and API. This packet does
not build the browser Project interface.

## Required Context

Before editing, read every applicable `AGENTS.md`, `docs/README.md`, the routed
baseline, architecture-contracts, security-risk, testing-quality, interface,
and delivery-planning context, the change-impact matrix, decision readiness,
CAP-0007, SLI-0030, WRK-0109, ADR-0011, ADR-0012, ADR-0006, ADR-0007, the
Project workspace contract, module map, dependency rules, public API and
compatibility standards, single-profile identity/security contract, Content
package admission, Curriculum exact-placement patterns, module-owned migration
streams, Project contract/domain code, generated-client workflow, affected
tests, and nearest READMEs. Revalidate that tenancy, cloud, execution,
Portfolio, Assessment submission, and AI authority remain outside this packet.

## Decisions and Assumptions

- Add a closed `project.brief.v1` opaque JSON declaration to lesson-package v1
  as an optional additive field/capability. Content validates it with the
  accepted Project brief parser and exposes exact published bytes and safe
  identifiers only through a public operation. Existing packages without a
  project brief remain byte-compatible and valid.
- Curriculum owns a separate exact Project-brief placement. It stores stable
  placement, Curriculum ID/version/digest, package ID/version/digest, brief
  schema/ID/version/digest, and creation time. It validates the exact brief
  through Content's public facade and creates no Project instance.
- Project owns create policy, learner ownership, idempotency, Project identity,
  immutable accepted origin, lifecycle, revision, and shell persistence. It
  reads Content and Curriculum only through Project-owned gateway ports and
  their public module operations; no cross-schema foreign keys or repository
  imports are allowed.
- Independent creation needs no learning lookup. Learning creation must resolve
  the exact Curriculum placement and Content brief and must match every
  retained reference and safe brief summary before a transaction starts.
- The protected API uses server-resolved learner context and server-issued
  `project.create` or `project.read` permission. `POST /api/v1/projects` accepts
  only the reviewed create-intent shape. `GET /api/v1/projects` and
  `GET /api/v1/projects/{project_id}` expose only the reviewed Project shell.
- Exact idempotent replay for one learner/key returns the original shell.
  Reusing the key with changed canonical intent fails as conflict. Generated
  Project ID, learner ID, revision, and UTC times are server-owned.
- This packet may extend a synthetic local fixture to qualify a learning
  origin, but it must not make fixture seeding a production requirement or add
  browser-only authority.

## In Scope

- Extend lesson-package v1 with one optional bounded Project-brief file
  declaration, capability value, file-closure/integrity validation, exact
  identity/digest validation, Content public query, and compatibility cases.
- Add Curriculum public request/result types, application behavior, repository
  port/adapter, additive up/down migration, and focused tests for one exact
  Project-brief placement.
- Add Project public types and stable bounded errors; learning gateway ports
  and public-only adapters; deterministic create/read/list application service;
  Project repository/system ports and PostgreSQL/UTC/UUID adapters; and
  Project-owned additive migration.
- Persist one closed Project shell aggregate per project with learner ownership,
  idempotency key, canonical request fingerprint, immutable JSON origin,
  lifecycle, positive revision, and UTC times. Reads revalidate the contract.
- Add Project composition, migration-stream ordering, single-profile
  permissions, safe API models/routes/error mapping, reviewed OpenAPI, generated
  TypeScript client, and client-usage contract evidence.
- Add unit, contract, architecture, API, and real-PostgreSQL coverage for exact
  resolution, idempotency, concurrency, restart-safe reads, authorization,
  cross-learner denial, malformed/stale/unavailable sources, privacy, no
  Assessment/Learner-model side effects, rollback boundaries, and varied valid
  inputs/count/order.
- Synchronize Content, Curriculum, Project, Identity, API, migration,
  architecture, and planning documentation.

## Out of Scope

Browser Project screens; editing title/charter; artifacts, notes, links,
datasets, notebooks, files, uploads, previews, snapshots, export, deletion,
restore, domain-resource or Portfolio links; Assessment submission/completion;
Learner-model progress/mastery; Audit events; collaboration or organizations;
jobs, providers, cloud, production recovery; arbitrary execution, packages,
network, secrets, rendering, or callbacks; AI-authored or AI-authoritative
creation; recommendations; personalized advice; and financial execution.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Content package/public seam | optional Project-brief declaration, admission, exact query, corpus/tests | Existing packages remain compatible; Content owns source bytes and exposes no object key/path |
| Curriculum | exact Project-brief placement public/application/repository/migration seam | No Project instance, learner state, Content table read, or cross-schema foreign key |
| Project | public/application/gateway/repository/system adapters and PostgreSQL migration | One domain core; Project owns shell and learner authorization inputs; origin is immutable |
| Identity/API | two permissions, closed models/routes/errors, OpenAPI and generated client | Session-derived learner only; CSRF/origin policy on POST; no alternate browser or AI authority |
| Composition/qualification | module migration/application composition and isolated tests | Module-owned streams, deterministic teardown, same public operation for browser/headless clients |
| Documentation/planning | named contract/module/API/migration and packet/slice/register artifacts | Exact delivered and omitted boundaries remain explicit |

## Contracts and Interfaces

Content adds `GetPublishedProjectBriefRequest` and
`PublishedProjectBrief`, returning exact package identity, declared brief
identity/schema/digest, file digest, and validated bytes. Curriculum adds
`CreateProjectBriefPlacementRequest`, `ResolveProjectBriefPlacementRequest`, and
`ProjectBriefPlacement`. Missing, conflicting, stale, or unavailable records
use existing bounded module-error conventions without storage details.

Project adds transport-neutral operations equivalent to:

```text
create_project(CreateProjectRequest[learner_id, intent]) -> ProjectShell
list_projects(ListProjectsRequest[learner_id]) -> tuple[ProjectShell, ...]
open_project(OpenProjectRequest[learner_id, project_id]) -> ProjectShell
```

The future host supplies learner identity and permission. The application
validates the intent through the WRK-0109 contract adapter, resolves learning
origin through exact public gateways, computes a canonical fingerprint, and
persists through a Project-owned repository port. List order is deterministic
by creation time then project ID but tests must not assume synthetic IDs or
fixed record counts beyond declared scenario meaning.

The API accepts no learner, project ID on create, revision, lifecycle, time,
permission, storage, provider, completion, score, Portfolio, execution, or
advice field. Error envelopes remain bounded and correlation-safe. OpenAPI is
the source for generated TypeScript; generated outputs are never hand-edited.

## Dependencies and Parallel Safety

WRK-0109 is complete and fixes every contract/domain invariant consumed here.
This packet owns shared Content/Curriculum/Project composition, migrations,
Identity permissions, API/OpenAPI/client outputs, architecture catalogs, the
parent slice, and planning register. It is not parallel-safe with another
packet changing those surfaces. It must complete before the learner-facing UI
packet is authored.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Package compatibility | Existing packages and one package with an exact approved Project brief admit deterministically | lesson-package contract/unit |
| Independent create | Server-resolved learner creates and reopens one active independent Project | application/PostgreSQL/API |
| Learning create | Exact placement and brief resolve through public facades and the immutable accepted origin is retained | gateway/application/PostgreSQL/API |
| Headless parity | Ordinary authenticated non-browser HTTP creates, lists, and reads the same records as the generated client contract | API/generated-client test |
| Idempotent retry | Exact learner/key replay returns the original shell; changed reuse conflicts; concurrent exact calls create one row | unit/PostgreSQL/API |
| Source denial | Missing, stale, mismatched, unavailable, or malformed brief/placement fails before Project insert | contract/application/PostgreSQL/API |
| Authorization/privacy | Caller-selected learner, missing session/permission, cross-learner ID, guessed ID, private fields, and storage details fail closed | API/security/architecture |
| Restart/read integrity | Persisted shells survive a normal composition restart and invalid stored meaning fails unavailable without partial output | PostgreSQL/API |
| No learning-evidence effect | Creation changes no Assessment, Learner-model, Audit, Portfolio, or provider state | application/PostgreSQL/architecture |
| Anti-rigidity | Valid title/charter boundaries, Unicode, multiple projects, harmless metadata variation, generated IDs/times, and list order ties preserve meaning | parameterized unit/contract/PostgreSQL/API |
| Migration bounds | Fresh up and controlled empty development down succeed; retained Project rows prevent claims of harmless destructive rollback | migration integration/docs |

## Verification Commands

Run focused lesson-package, Content, Curriculum, Project domain/application,
real-PostgreSQL, and protected API suites; migration up/down and restart tests;
OpenAPI generation check; generated-client reproduction and client-usage
typecheck; architecture/import/schema-ownership tests; security; work-packet,
planning, documentation, and whitespace checks; `python
dev-tools/agent/check_ready.py`; exact-candidate affected verification; and one
independent technical disposition. Use the repository-local temp root on
Windows when sandbox-owned temporary directories deny cleanup. Run no browser
suite unless the generated-client or API contract check requires it; browser
behavior belongs to the next packet.

## Documentation and Evidence Update

Record package compatibility, Content/Curriculum/Project ownership, migration
IDs and rollback limits, Project operations and permissions, public API paths,
OpenAPI/client reproduction, idempotency/concurrency/restart behavior,
authorization/privacy, headless parity, no evidence side effects, exact checks,
environment qualifications not performed, and residual risks. Keep exact
receipts and technical dispositions only in ignored control-plane storage.

## Stop Conditions

Stop for lesson-package breaking change; ambiguous source or Project ownership;
mutable accepted origin; cross-module repository/table access; client-selected
learner/permission/time/revision; unsafe idempotency; artifact/snapshot/domain-
link/Portfolio/Assessment semantics; execution/network/secrets/packages;
organization tenancy; providers/jobs/cloud/recovery; AI authority; personalized
financial advice; destructive retained-data migration; private-data leakage;
new dependency; generated output that cannot reproduce; canonical conflict;
active scope collision; or material CAP-0007/SLI-0030 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
nonfunctional style, incidental fixture counts/order, or other inconsequential
cleanup. Fix it within scope or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; package and placement contract changes;
Project persistence/migration/API/client behavior; independent and learning
origin results; idempotency/concurrency/restart/authorization/privacy/no-side-
effect evidence; focused, PostgreSQL, API, generated, architecture, security,
affected, and aggregate checks; changed files; documentation impact;
assumptions; environment checks not performed; and residual gaps. Confirm no
browser Project interface, artifact, snapshot, submission, domain link,
Portfolio behavior, provider, external execution, separate AI mode, or
autonomous authority was added, then leave the UI packet dependency-ready.

## Planning History

- 2026-10-16: Authored just in time after WRK-0109 completed. The packet
  composes the accepted contract into the smallest durable protected backend
  and public API seam, keeping the browser interface, workspace resources,
  snapshots, submissions, domain links, and execution separate. No lower-level
  approval is required.
- 2026-10-16: Incrementally included directly affected legacy migration,
  Identity-permission, schema-inventory, settings, and OpenAPI-isolation tests
  discovered by the complete backend suite. This is compatibility maintenance
  for the same approved boundary, not a new feature or authority surface.
- 2026-10-16: Incrementally included the top-level architecture harness after
  the architecture gate showed its minimal composition fixture must supply the
  newly required Project service. This is direct compatibility maintenance for
  the same composition boundary and does not expand product scope.
