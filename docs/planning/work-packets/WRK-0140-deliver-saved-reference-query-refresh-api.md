---
id: WRK-0140
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0072
capability: CAP-0017
depends_on: [WRK-0139]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/public.py", "backend/src/financial_ai_academy/modules/personal_workspace/application/service.py", "backend/src/financial_ai_academy/modules/personal_workspace/adapters/postgres_repository.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/tests/unit/personal_workspace/test_personal_workspace_service.py", "backend/tests/integration/personal_workspace/test_postgres_personal_workspace.py", "backend/tests/integration/api/test_single_profile_personal_workspace_api.py", "contracts/api/openapi.json", "contracts/api/README.md", "apps/web/README.md", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/planning/vertical-slices/SLI-0072-search-and-refresh-saved-references.md", "docs/planning/work-packets/WRK-0140-deliver-saved-reference-query-refresh-api.md", "docs/planning/register.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 53ae2789993a6d1de89f9dc5b24ec4d7fec81a14
claim_id: WRK-0140:808c1345-90ff-4338-983f-5ae0d4bb26bd
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T15:09:20Z
---

# Agent Work Packet: Deliver Saved-Reference Query and Refresh API

## Objective and Deliverable

Deliver the API-first application, persistence, protected HTTP, reviewed
OpenAPI, and generated TypeScript-client seam for the query and explicit
per-record refresh contracts frozen by WRK-0139. Browser, command-line,
service, and future headless-AI consumers must share one learner-bound API and
deterministic authority model.

This packet stops before learner-facing search, filter, status, refresh, or
safe-resume controls. It leaves a stable generated client for WRK-0141 and a
complete persistence/API boundary for integrated qualification in WRK-0142.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed architecture-contract,
API/security, testing-quality, and delivery-planning context; change-impact
matrix; decision-readiness register; ADR-0012 and ADR-0021; CAP-0017; SLI-0072;
completed WRK-0139; Personal-workspace application, public, source-gateway,
contract, and PostgreSQL seams; protected host models/routes and identity
permissions; OpenAPI/client generators; affected tests; and nearest READMEs.

## Decisions and Assumptions

- Query is a read-only `POST /api/v1/personal-workspace/query` with one closed
  versioned JSON body. This preserves the frozen query contract without
  spreading repeated arbitrary URL parameters or inventing a browser-only
  projection.
- Query requires only `personal_workspace.read`, derives learner identity from
  the opaque server session, reads one Personal-workspace aggregate, performs
  no source-owner call, and writes nothing.
- `refresh_reference` is additive to the existing protected mutation union and
  requires `personal_workspace.write`. Its public mutation carries only record
  ID plus the existing schema/idempotency/revision envelope.
- The host converts current server-issued Curriculum and Project read
  permissions into a closed set of readable reference kinds. This keeps
  opportunity and lesson permissions distinct while grouping the three
  Project kinds behind `project.read`. The service derives the owner and
  selector only after loading the learner-owned record. A missing exact-kind
  permission skips the owner call and follows the same unavailable
  transition as missing, denied, removed, adapter-absent, or source-outage.
- Exact replay is checked before owner resolution. Changed-key reuse, stale
  workspace revision, and missing workspace-owned record keep their existing
  bounded meanings and never call an owner or write partial state.
- Existing PostgreSQL JSON aggregate and mutation replay tables are expected to
  persist status changes without a migration. Repository code changes only if
  direct focused evidence exposes a defect; destructive or cross-module schema
  work is outside this packet.
- Query results retain versioned historical destination data, but
  `target_status` is authoritative: only `available` is an actionable resume
  result. Browser suppression is WRK-0141 work and no API consumer may infer
  authority from the retained route alone.
- The reviewed OpenAPI snapshot remains the only source for generated
  TypeScript types. No separate AI endpoint, hand-maintained client, source
  table read, background refresh, or alternate authorization path is added.

## In Scope

- Add public query and refresh command/request operations while preserving the
  closed five-reference union, existing error envelope, and server-owned
  learner identity.
- Orchestrate pure query over the authorized current aggregate and return the
  exact normalized result from WRK-0139 without source resolution or mutation.
- Derive a refresh selector from the retained record, gate the owner call with
  server-derived readable-owner context, verify exact returned identity, and
  apply available/stale/unavailable through the trusted pure core.
- Preserve exact idempotency replay, changed-key conflict, optimistic revision,
  atomic save, workspace digest, order, collections, and learner isolation for
  refresh mutations.
- Prove PostgreSQL restart/round-trip and concurrent stale-write behavior for
  available, stale, and unavailable refresh results without a migration.
- Add closed API request/response models and routes for query plus the refresh
  mutation; reject caller learner, owner, selector, replacement facts, status,
  timestamp, provenance, destination, provider, storage, or permission data.
- Regenerate and verify the reviewed OpenAPI snapshot and generated client;
  compile direct browser/headless client usage for query, continuation, and
  refresh without adding interface behavior.
- Update direct module/API/contract/assurance guidance, SLI-0072, this packet,
  and the planning register.

## Out of Scope

Browser search/filter/status/refresh/resume controls; styling; component or
Chromium journeys; isolated live Docker/PostgreSQL/browser/headless topology;
background polling or owner events; a cross-domain search service; new owner
adapter; Portfolio, Market data, Assessment, Learner-model, AI-conversation, or
other future source; source content copying; target mutation; artifact content,
preview, download, export, archive expansion, or execution; import/export or
delete request; migration unless the current JSON representation fails direct
qualification; identity/tenancy/cloud/provider/model/legal/commercial change;
new dependency or lockfile change; financial advice or action.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public/application seam | Current public requests, service, frozen contract core and source gateway | listed public/service files | Add query and record-only refresh orchestration with server-derived owner access |
| Persistence | Existing aggregate/replay repository and focused PostgreSQL suite | focused repository and PostgreSQL test files | Prove refresh atomicity, replay, isolation, concurrency, and no-migration compatibility |
| Protected API | Current Personal-workspace host models, routes, permissions, and error mapping | listed host files and API integration test | Expose closed query and refresh through the same authenticated boundary |
| Generated consumer contract | Current OpenAPI snapshot, generator outputs, and client usage checks | snapshot, generated files, README, and contract tests | Preserve reproducible browser/headless parity |
| Guidance | Current module, API, architecture contract, and assurance docs | listed Markdown | Record authority, confidentiality, non-actionable history, and remaining browser/live gap |
| Planning | SLI-0072, WRK-0140, register | listed planning files | Keep JIT lifecycle and next dependency synchronized |

No Curriculum/Project implementation, owner persistence, executable learning
contract, migration, identity policy, browser feature, design-system,
deployment, provider, dependency, or lockfile file may change.

## Contracts and Interfaces

`QueryPersonalWorkspaceRequest` contains only server-owned learner identity and
the frozen `WorkspaceQuery`. The protected request body contains the same
closed query fields but never learner, workspace identity, permission, owner,
provider, or storage data. The result is the frozen `WorkspaceQueryResult` with
normalized applied query, complete matching records, workspace revision,
query digest, and optional authenticated continuation.

`RefreshReferenceCommand` contains only `record_id`. The existing mutation
envelope supplies schema version, idempotency key, and expected revision. The
application request additionally receives a server-derived immutable set of
readable reference kinds. This set is not an HTTP request field and is not part of
the idempotency fingerprint. The service derives one typed selector from the
retained reference and calls the existing closed source gateway only when its
owner is readable. Exact selector/result correlation uses the same checks as
source-bearing creation before `apply_reference_refresh` can persist a result.

Missing permission, missing/denied/removed source, absent optional adapter,
source outage, or safe public-owner failure all become the same unavailable
status and public response. They expose no owner-specific cause. A trusted
current result becomes available only when immutable meaning matches; drift
retains historical facts and becomes stale. An available response route remains
actionable only when status is available.

The query endpoint returns 200 or the existing bounded error envelope. Refresh
reuses `POST /api/v1/personal-workspace/mutations`. Invalid shapes map to 400;
changed key or stale revision to 409; missing workspace-owned record to 404;
integrity or repository availability failures remain bounded without source or
storage detail.

## Dependencies and Parallel Safety

WRK-0139 is complete and freezes the schemas, pure query, authenticated cursor,
and trusted refresh transition. WRK-0140 owns shared application, persistence,
host API, OpenAPI, and generated-client files, so it is not parallel-safe with
another Personal-workspace API packet. WRK-0141 cannot start until the generated
client and public status semantics are complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Headless query | A session has Personal-workspace read and sends a closed query | The protected query operation runs | Server learner context selects one aggregate, no owner is called or written, and normalized bounded records are returned | application/API/client |
| Stable continuation | A valid next cursor is reused with identical query meaning | A later page runs | The same workspace/revision/query scope advances without duplicate or omission; tampered, cross-workspace, stale, or changed-query cursors fail generically | application/API |
| Exact refresh | A readable retained Curriculum or Project reference still matches | Record-only refresh runs | The service derives the selector, validates the owner result, and atomically stores current safe facts with available status | application/PostgreSQL/API |
| Immutable drift | A readable package, snapshot, or artifact immutable fact changes | Refresh runs | Historical facts remain, status becomes stale, and no owner state changes | application/PostgreSQL |
| Confidential unavailable | Owner permission, adapter, target, or source is unavailable | Refresh runs | The owner call is skipped or collapses to the same unavailable status and no private cause appears | application/API/security |
| Recovery | A prior stale or unavailable record resolves to the exact retained meaning | Refresh runs later | Available status returns while learner text, order, memberships, provenance, and replay safety remain intact | application/PostgreSQL |
| Exact replay | An accepted refresh request is repeated | Mutation runs | The accepted workspace returns before any owner call or write; changed-key reuse fails without overwrite | application/PostgreSQL/API |
| Revision race | Two refreshes use one expected revision | Persistence serializes them | Exactly one wins; the other receives stale revision and cannot overwrite newer status | PostgreSQL integration |
| Permission boundary | Read or write permission is absent, or caller adds learner/owner/status/replacement fields | API validation and authorization run | The request fails or follows confidential unavailable policy without target confirmation or partial write | API/security |
| Generated parity | OpenAPI and generated client reproduce | Browser and ordinary non-browser TypeScript callers compile | Both use the same query and refresh types with no separate AI authority | OpenAPI/client |
| Anti-rigidity | Empty/full workspaces, mixed reference/status kinds, valid Unicode, varied page sizes/order, and one absent optional owner are exercised | Focused suites run | Unrelated query, mutation, owner, and startup paths remain usable without count/order/copy assumptions | parameterized/integration |

## Verification Commands

Run:

```text
uv run --project backend pytest backend/tests/contract/personal_workspace backend/tests/unit/personal_workspace backend/tests/integration/api/test_single_profile_personal_workspace_api.py -q
uv run --project backend pytest backend/tests/integration/personal_workspace -q
uv run --project backend python -m financial_ai_academy.hosts.api.generate_openapi --check
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
node apps/web/tests/contract/generated-client.test.mjs
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0140-deliver-saved-reference-query-refresh-api.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
python -m compileall -q backend/src backend/tests
git diff --check
python dev-tools/agent/check_ready.py
```

Use a disposable repository-owned PostgreSQL topology or exact isolated test
DSN; never target shared data. Regenerate OpenAPI and the client only through
their committed generators, then run both check modes. Use a repository-local
writable temp root when the Windows sandbox temp path rejects fixture creation.
Run an exact clean-candidate affected-check plan, obtain a fresh qualifying
receipt, and complete proportionate independent technical review.

## Documentation and Evidence Update

Document the query route and authority, record-only refresh, server-derived
owner access, exact selector correlation, status/destination meaning,
confidential unavailable collapse, optional-adapter isolation, PostgreSQL
no-migration evidence, OpenAPI/client parity, and remaining browser/live seams.

Completion evidence records exact candidate/receipt; route and generated types;
scenario-to-test results; focused/PostgreSQL/API/client counts; idempotency,
concurrency, restart, authorization, confidentiality, target non-mutation,
anti-rigidity, architecture, security, and aggregate evidence; changed files;
documentation and migration impact; assumptions; unqualified live/UI profiles;
and residual gaps. Approval and reviewer records remain ignored local state.

## Stop Conditions

Stop for caller-controlled learner, owner, selector, permission, status,
timestamp, provenance, destination, or replacement facts; query outside the
current learner workspace; differentiated missing/denied/removed disclosure;
direct owner persistence or source-content access; source or artifact mutation;
cross-module transaction; destructive migration; background polling/event
coupling; browser interface work; new owner adapter; dependency/lockfile
change; managed-cloud/tenancy/provider/model/legal/external-action decision;
active scope collision; canonical conflict; stale CAP package; or material
SLI/CAP drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential in-scope correction. Fix it locally or defer optional polish.

## Required Handoff

Report `CAP-0017.SLI-0072.WRK-0140`; exact candidate and receipt; query and
refresh public operations; server-derived owner access and confidentiality;
PostgreSQL replay/restart/concurrency/no-migration evidence; API authorization;
OpenAPI/client/browser-headless parity; focused, architecture, security,
affected, aggregate, and independent technical results; changed files;
documentation impact; assumptions; unqualified live/browser checks; and
residual gaps. Confirm no browser feature, target mutation, artifact execution,
new adapter, provider, managed-cloud, separate AI authority, or financial
action changed, then leave WRK-0141 dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0139 completed. The packet
  composes its frozen query and refresh core through application, PostgreSQL,
  protected API, reviewed OpenAPI, and generated client while leaving browser
  controls and integrated live qualification to dependent packets. No lower-
  level approval is required.
