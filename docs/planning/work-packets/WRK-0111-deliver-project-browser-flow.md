---
id: WRK-0111
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: SLI-0030
capability: CAP-0007
depends_on: [WRK-0110]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/dist", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/learning-catalog/LearningOpportunityDetailPage.tsx", "apps/web/src/features/learning-catalog/model.ts", "apps/web/src/features/project-workspace", "apps/web/src/generated/api-client", "apps/web/src/styles/app.css", "apps/web/src/styles/project-workspace.css", "apps/web/tests/browser/project-workspace", "apps/web/tests/component/learningOpportunityDetail.test.tsx", "apps/web/tests/component/projectWorkspace.test.tsx", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/unit/learningCatalogModel.test.ts", "apps/web/tests/unit/projectWorkspaceModel.test.ts", "backend/src/financial_ai_academy/hosts/api", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/curriculum/adapters/postgres_repository.py", "backend/src/financial_ai_academy/modules/curriculum/application/service.py", "backend/src/financial_ai_academy/modules/curriculum/ports/repositories.py", "backend/src/financial_ai_academy/modules/curriculum/public.py", "backend/src/financial_ai_academy/modules/project", "backend/tests/architecture", "backend/tests/integration/api/test_single_profile_project_api.py", "backend/tests/integration/curriculum/test_postgres_project_brief_placements.py", "backend/tests/unit/curriculum/test_project_brief_placements.py", "backend/tests/unit/project", "contracts/api/openapi.json", "deployments/local/README.md", "deployments/local/serve.py", "docs/architecture/contracts/project-workspace-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0030-create-independent-or-learning-project.md", "docs/planning/work-packets/WRK-0111-deliver-project-browser-flow.md", "tests/architecture"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/dist"]
base_revision: e8a85b83daf969da83abcf9dd7fcae99abeed494
claim_id: WRK-0111:5a6b8559-0855-4d16-8fe0-0147f4452c95
claimed_by: codex-cap-0007
claimed_at: 2026-10-16T20:45:01Z
---

# Agent Work Packet: Deliver the Project Browser Flow

## Objective and Deliverable

Deliver an accessible, plain-language browser flow that lets an authorized
learner view and reopen Project shells, create an independent Project, and
start a Project from an exact approved learning brief. The flow must consume
the generated public client and the same Project operations available to
headless clients. Add the smallest transport-neutral Project start-option read
needed to list available briefs and keep exact learning-origin fields out of
learner-authored form input.

## Required Context

Before editing, read every applicable `AGENTS.md`, repository-root
`docs/README.md`, the routed interface-design and testing-quality context,
change-impact matrix, decision readiness, planning guide/register/concurrency
protocol, CAP-0007, SLI-0030, WRK-0110, ADR-0012, Project workspace contract,
public API and compatibility standards, single-profile security contract,
learner-language and interface standards, design guide and semantic tokens,
generated-client workflow, affected Project/API/web code, consumers, tests,
and nearest READMEs. Revalidate that the accepted single-learner identity and
inert Project boundary remain current.

## Decisions and Assumptions

- Keep create/list/read and the new exact start-option read as public HTTP
  operations. Browser code imports only the generated client and has no private
  backend, database, Content, or Curriculum dependency.
- Expose protected Project start-option list and exact reads. Project resolves
  the exact Curriculum placement and Content brief through its existing owned
  gateways and returns a closed learner-safe presentation plus the complete
  immutable origin required by create. The client never assembles, edits, or
  guesses digests, versions, source IDs, or learner identity.
- The Projects page is the entry point for independent and learning-backed
  work. It lists zero, one, or many server-resolved start options and links by
  public placement ID. Unknown, stale, or unavailable options fail closed
  before a create request.
- Reuse one opaque idempotency key across retries of the same unchanged draft.
  Changing the material intent creates a new key; learner copy does not expose
  the key as a task field.
- Use existing semantic variables, reviewed icons, shared controls, and page
  patterns. No shared token, icon, theme, or visual-language decision is needed.

## In Scope

- Add transport-neutral Project operations and protected GET routes that list
  available learning start options and resolve one exact option without
  creating learner state.
- Regenerate OpenAPI and the TypeScript client; preserve direct non-browser use
  of every Project route.
- Add `/projects`, `/projects/new`, and `/projects/:projectId` browser routes
  with session establishment, list/detail loaders, independent and learning
  create behavior, safe retry, and bounded status/error states.
- Add a clear Projects navigation entry and show available learning-backed
  Project choices there without changing lesson discovery semantics.
- Present title, charter, active status, origin meaning, creation/update time,
  and the learning brief's title and purpose in primary or supporting content;
  put exact IDs, versions, revisions, and digests in an accessible `Technical
  record` disclosure.
- Extend the explicit local synthetic fixture with one exact Project package
  and Curriculum placement so development
  and later live qualification can exercise the ordinary flow without turning
  seeding into production bootstrap behavior.
- Add focused backend, API, web model/component, and mocked Chromium coverage
  for successful, empty, varied, retry, denial, stale, malformed, responsive,
  theme, keyboard, reduced-motion, and forced-color behavior.
- Synchronize Project/API/local-development/interface/planning documentation.

## Out of Scope

Project title or charter editing; notes; links; files; datasets; notebooks;
code; result artifacts; uploads; previews; snapshots; export; deletion;
restore; domain-resource or Portfolio links; Assessment submission or Project
completion; milestones; instructor review; collaboration; organizations;
provider execution; packages; network; secrets; cloud deployment; production
recovery; AI-authored content; AI authority; personalized advice; and styling-
only polish that does not affect operation, meaning, accessibility, responsive
use, or theme parity.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project/application | public types, service, existing gateways and contract adapter | exact start-option operation and focused tests/docs | let all clients resolve safe exact learning input without moving Content/Curriculum authority |
| API/client | protected Project routes/models, OpenAPI, generator and generated types | one GET route plus regenerated artifacts and client-usage evidence | preserve one API-first boundary for browser and headless clients |
| Browser | router, session, catalog link semantics, Project feature, shared shell | Projects list/create/detail pages and token-only feature CSS | deliver the approved learner-visible slice outcome |
| Local fixture | explicit synthetic seed and local run guide | one approved Project package/placement/opportunity under the existing opt-in flag | make development and qualification representative without production seeding |
| Verification/docs | focused API/web/browser/architecture tests and named docs | direct synchronization only | preserve ownership, plain language, accessibility, and anti-rigidity evidence |

## Contracts and Interfaces

Add public Project request/results equivalent to:

```text
resolve_learning_project_start_option(placement_id)
  -> { title, purpose, origin: LearningProjectOrigin }

list_learning_project_start_options()
  -> [{ title, purpose, origin: LearningProjectOrigin }, ...]
```

The result is derived from the exact validated Curriculum placement and Content
brief already consumed by Project creation. It contains no source bytes,
milestone definitions, storage locations, provider data, learner identity, or
authorization facts. The host exposes it as a protected GET route and maps
missing, stale, malformed, or unavailable sources to the existing bounded
public error envelope. `POST /api/v1/projects` remains authoritative for
creation and revalidates the returned origin; a start option is not a token,
reservation, approval, or durable learner record.

Browser routes consume only generated request and response types. Form fields
are limited to origin choice, title, and charter. Exact learning origin is
read-only presentation/input from the public API. Navigation and error copy use
learner terms; technical evidence remains complete in a native details element.

## Dependencies and Parallel Safety

WRK-0110 is complete and supplies Project persistence, create/list/read HTTP,
OpenAPI, generated client, and exact source gateways. This packet owns shared
Project/API/generated-client/browser-router/local-fixture surfaces and is not
parallel-safe with another packet changing them. It must complete before the
final SLI-0030 qualification packet is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Project list and reopen | zero, one, or several learner-owned shells | learner opens Projects or selects one | the page shows the current records in server order and reopens only the selected owned shell | web model/component/API |
| Independent create | ordinary valid title and charter | learner chooses independent work and creates | one active shell is created and its detail page opens | component/API/browser |
| Learning start | one or several exact available project briefs | learner chooses `Start project`, reviews one brief, and creates | the shell retains the exact server-resolved origin while remaining usable outside the lesson | application/API/component/browser |
| Headless parity | the start-option and Project endpoints are called without browser state | authenticated non-browser client resolves and creates | the same public shapes and policies apply | API/client-usage |
| Idempotent retry | response is delayed, unavailable, or retried with unchanged intent | learner retries | the same key is reused and no duplicate is presented or created | unit/component/API |
| Changed draft | learner materially changes title, charter, or origin after a failed attempt | create is retried | a new key is used and stale intent is not replayed | unit/component |
| Safe denial | session, permission, source, Project ID, or response is invalid/stale/unavailable | page loads or form submits | no private/partial facts appear; the learner sees result, protection fact, and next safe action | unit/component/browser/security |
| Plain-language evidence | a learning or independent shell is shown | learner reads primary content or opens Technical record | primary copy avoids computing/storage vocabulary while exact provenance remains keyboard reachable | component/language/browser |
| Anti-rigidity | valid Unicode, boundary-length copy, empty/multiple lists, varied times/IDs, and reordered records | pages render and forms validate | semantic behavior does not depend on one fixture, count, ID, order, or prose string | parameterized unit/component |
| Accessible parity | narrow viewport, zoom, keyboard, light/dark/system, reduced motion, and forced colors | learner uses list/create/detail | equivalent content, actions, focus, errors, and hierarchy remain available | Chromium/design checks |

## Verification Commands

Run focused Project application and protected API tests for start-option
resolution and revalidation; OpenAPI currency; generated-client reproduction;
client-usage typecheck; Project web unit/component suites; affected learning-
catalog tests; focused mocked Chromium Project flow; TypeScript typecheck,
lint, complete web unit/component suite, and build; learner-language and design-
system checks; architecture/security checks for generated-client-only browser
access and bounded responses; local fixture start smoke where practical;
planning, documentation, whitespace, affected exact-candidate verification;
`python dev-tools/agent/check_ready.py`; and one independent technical
disposition. Use a repository-local temp root on Windows when required.

## Documentation and Evidence Update

Record the start-option contract, browser/headless parity, routes and learner
copy, idempotency-key lifecycle, exact learning provenance, local opt-in fixture,
authorization/privacy behavior, accessibility and anti-rigidity evidence,
checks performed, environment qualifications not performed, and residual gaps.
Keep exact receipts and technical dispositions only in ignored control-plane
storage.

## Stop Conditions

Stop for a new ownership model; client-authored or mutable exact origin;
Content/Curriculum table or repository access; browser-only authority;
client-selected learner/permission/time/revision; destructive migration;
artifact/snapshot/submission/domain-link/Portfolio behavior; external execution,
network, secrets, provider, tenancy, recovery, AI authority, personalized
financial advice, breaking contract, shared visual-system change, inaccessible
meaning, canonical conflict, active scope collision, or material CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture counts/order, or similarly
inconsequential cleanup. Fix it locally or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; start-option and existing Project API
behavior; generated-client-only browser composition; independent and learning
create/reopen outcomes; idempotent retry; authorization/privacy; plain-language,
accessibility, responsive, theme, anti-rigidity, focused, web, architecture,
security, affected, and aggregate checks; changed files; documentation impact;
assumptions; checks not performed; and residual gaps. Confirm no artifact,
snapshot, submission, domain link, Portfolio behavior, external execution,
separate AI mode, or autonomous authority was added.

## Planning History

- 2026-10-16: Authored just in time after WRK-0110 completed. The packet keeps
  the learner flow API-first, adds only the exact read projection needed to
  prevent client-authored learning provenance, and remains inside the approved
  CAP-0007/SLI-0030 browser outcome. No lower-level approval is required.
- 2026-10-16: Refined the read projection during implementation to include a
  bounded list operation. This lets ordinary and headless clients discover
  zero, one, or many learning starts without hard-coded placement IDs or
  expanding Curriculum discovery semantics. The change remains inside the
  approved slice and does not add a decision gate.
- 2026-10-16: Added the repository-tracked static browser build directory to
  generated scope after the build produced the expected hashed artifacts. No
  authored behavior or acceptance scope changed.
