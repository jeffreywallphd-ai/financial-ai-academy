---
id: WRK-0144
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0073
capability: CAP-0017
depends_on: [WRK-0143]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/personal_workspace/public.py", "backend/src/financial_ai_academy/modules/personal_workspace/application/service.py", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/tests/unit/personal_workspace/test_personal_workspace_service.py", "backend/tests/integration/personal_workspace/test_postgres_personal_workspace.py", "backend/tests/integration/api/test_single_profile_personal_workspace_api.py", "backend/tests/architecture/test_module_boundaries.py", "contracts/api/openapi.json", "contracts/api/README.md", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "apps/web/README.md", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0073-qualify-personal-workspace-durability-boundaries.md", "docs/planning/work-packets/WRK-0144-deliver-personal-workspace-export-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts", "apps/web/src/generated/api-client/client.ts", "apps/web/src/generated/api-client/index.ts"]
base_revision: 282eb4d6e7065e4b8013cd07cec660752f3f2392
claim_id: WRK-0144:563c9dc9-b9e2-4ab1-ac50-8f31834bc6c2
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T16:58:50Z
---

# Agent Work Packet: Deliver Personal Workspace Export and Quota API

## Objective and Deliverable

Compose the completed WRK-0143 contract into one server-authoritative,
transport-neutral export operation and one protected JSON API route. Browser,
command-line, service, and future headless-AI consumers receive the same closed
owner export view through reviewed OpenAPI and generated TypeScript types.

Map the three accepted workspace limits to distinct safe public outcomes and
prove that a refused over-limit mutation does not write aggregate or replay
state, while reads, export, removal, exact retry, restart, and unrelated valid
work continue. This packet changes no browser feature, database schema,
recovery tool, cross-module portable-record workflow, or managed-cloud policy.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`.
Revalidate CAP-0017, SLI-0073, WRK-0143, ADR-0021, ADR-0008, the executable
Personal-workspace and API contracts, module/application/repository boundaries,
single-profile Identity permissions, FastAPI/Pydantic conventions, OpenAPI and
generated-client tooling, PostgreSQL tests, and nearest READMEs.

Stop if canonical sources conflict or the work requires import, combined
learner-record export, whole-account erasure, retention, destructive migration,
managed-cloud recovery, another module's persistence, or new identity policy.

## Decisions and Assumptions

- WRK-0143's `WorkspaceExportView`, canonical digest, generation chronology,
  quota codes, and privacy closure are fixed inputs and are not redefined here.
- The public operation accepts only server-derived learner identity. It reads
  the current Personal-workspace aggregate, revalidates it, and supplies the
  existing server clock to the pure export contract.
- The protected route is `GET /api/v1/personal-workspace/export`; it requires
  the existing `personal_workspace.read` permission and accepts no learner,
  query selector, generation time, digest, or storage destination.
- The response is JSON with `schema_version`, `workspace_digest`,
  `generated_at`, and `workspace`. It is not a file download, signature,
  permission grant, import, background job, or recovery artifact.
- Public failures distinguish `record_limit`, `collection_limit`, and
  `collection_member_limit`. Each message states the limit and a safe action
  without echoing learner content, IDs, database facts, or contract internals.
- Existing aggregate and replay tables are sufficient. A rejected capacity
  mutation reaches no repository save, creates no replay row, and requires no
  migration. Existing repository behavior is qualified, not redesigned.
- OpenAPI remains the sole source for the generated TypeScript client. No
  browser-only API or separate AI authority is introduced.

## In Scope

- Add transport-neutral export request/result behavior to Personal-workspace
  public operations and the application service.
- Generate the export from the current revalidated aggregate with a server
  time; keep virtual-empty reads side-effect free.
- Map the three WRK-0143 capacity failures to stable public error codes and
  plain safe messages while retaining existing invalid, stale, conflict,
  not-found, integrity, source, and unavailable meanings.
- Add the protected export route and closed response models; reject query
  selectors and caller-supplied identity or server-owned export facts.
- Regenerate and review OpenAPI and the TypeScript client, including direct
  generated-client usage evidence for a non-browser caller.
- Prove with unit, API, and real-PostgreSQL tests that export is exact after
  accepted mutation/removal/retry/restart and that capacity denial leaves
  aggregate and replay state unchanged while unrelated reads and work remain.
- Add authorization, privacy, target-isolation, malformed-response,
  compatibility, and anti-rigidity evidence for empty, varied, maximum,
  reordered, Unicode, optional-label, and mixed-reference workspaces.
- Synchronize API, module, architecture, generated-consumer, slice, packet,
  and register documentation with exact delivered behavior.

## Out of Scope

- Browser controls, download UX, styling, browser storage, accessibility UI,
  or Chromium flow; those belong to the dependent browser packet.
- New tables, columns, migration, aggregate shape, replay format, repository
  method, retention, physical purge, account erasure, recovery-copy deletion,
  or database restore implementation.
- Combined learner-record manifest, import, populated-target merge, archive,
  object storage, background export, resumable transfer, or CAP-0019 behavior.
- Target content, permission state, Project workspace material, artifact bytes,
  sessions, credentials, storage keys, provider payloads, or replay rows in an
  export response.
- Target-domain mutation, cross-module repository/table access, collaboration,
  organizations, tenancy, managed cloud, provider selection, execution,
  autonomous AI authority, financial advice/action, or external action.
- Styling-only or unrelated documentation cleanup.

## Expected File and Boundary Impact

| Area | Allowed change | Required invariant |
| --- | --- | --- |
| Public/application | Export request/operation and capacity error mapping | Framework-free shared core; server-owned learner and time |
| Persistence evidence | Existing repository integration tests only | No schema/repository change; denial writes nothing |
| API | Closed export model/route and bounded errors | Existing read permission; no query or caller-owned server facts |
| OpenAPI/client | Reproduced snapshot and generated TypeScript files | One browser/headless contract; no handwritten generated edits |
| Tests | Service, PostgreSQL, API, client, and architecture evidence | Exact export/replay/restart/capacity/privacy behavior |
| Documentation/planning | Exact public seam, limits, omissions, evidence | No managed-cloud, import, deletion, or portability overclaim |

No path outside `write_scope` may change. If implementation needs a migration,
repository change, Identity permission change, browser product file, recovery
tool, deployment composition, or another module, stop and reassess the packet.

## Contracts and Interfaces

Expose a transport-neutral operation equivalent to:

```text
export_personal_workspace(learner_id) -> WorkspaceExportView
```

The service validates learner identity, opens the current workspace through
the existing owned repository boundary, revalidates the aggregate, and calls
the WRK-0143 export operation with the server clock. The response retains the
accepted v1 envelope exactly. A virtual empty workspace may be exported without
creating a database row.

The public mutation error vocabulary adds exact capacity meanings for records,
collections, and unique collection members. All three are safe application
outcomes, not storage errors. They report no learner content or hidden count
beyond the public limit and recommended removal/reorganization action.

## Dependencies and Parallel Safety

WRK-0143 is complete and fixes the exact export/quota contract consumed here.
This packet owns shared application, host API, OpenAPI, generated-client, test,
documentation, slice, and register surfaces. It is not parallel-safe with
another SLI-0073 packet and must complete before the browser packet starts.

## Acceptance Scenarios

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Empty export | Authorized read of an absent workspace returns a closed revision-one export without a database write | unit/PostgreSQL/API |
| Populated export | Accepted notes, bookmarks, collections, order, Unicode, optional labels, and mixed references appear exactly with the canonical workspace digest | unit/API/PostgreSQL |
| Server authority | Learner identity and generation time come only from session and server clock; query or body attempts to select them fail | unit/API/security |
| Authorization | Missing, expired, malformed, or read-without-permission session cannot export; write permission is not substituted for read | API |
| Record capacity | The 200th record is accepted; the next returns `record_limit`, stores no aggregate/replay change, and export/removal still work | unit/PostgreSQL/API |
| Collection capacity | The 50th collection is accepted; the next returns `collection_limit` without blocking reads or unrelated valid mutations | unit/PostgreSQL/API |
| Member capacity | 100 unique canonical members are accepted; the next returns `collection_member_limit` without replacing membership | unit/PostgreSQL/API |
| Retry and restart | Exact accepted retries remain stable and exports before/after ordinary service restart preserve workspace meaning and digest | PostgreSQL/API |
| Closed privacy | Export omits credentials, sessions, permissions, replay rows, storage facts, target payloads, artifact bytes, and provider data | API/schema/security |
| Target isolation | Export and capacity denial do not mutate Curriculum, Project, Assessment, Learner-model, Audit, or provider state | architecture/API |
| Headless parity | Reviewed OpenAPI and generated client expose the same export and error vocabulary to direct non-browser consumers | snapshot/client contract |
| Anti-rigidity | Empty, sparse, full, reordered, Unicode, optional-field, and mixed-reference workspaces share the same invariants | parameterized tests |

## Verification Commands

Run focused Personal-workspace service, real-PostgreSQL, protected API, and
module-boundary tests; OpenAPI currency; generated-client reproduction and
usage typecheck; security and private-field checks; planning, documentation,
Python compilation, and whitespace checks; controller-selected exact-candidate
affected verification; independent technical review; and `python
dev-tools/agent/check_ready.py`. No browser qualification is required here.

## Documentation and Evidence Update

Record the public operation/path, permission, response fields, digest/time
authority, exact quota outcomes, zero-write denials, retry/restart behavior,
OpenAPI/client parity, persistence compatibility, target isolation, qualified
checks, assumptions, and remaining browser/recovery gaps. Keep approvals,
review records, and receipts only in ignored local control-plane storage.

## Stop Conditions

Stop for a need to change the WRK-0143 envelope or limits; a migration or
repository redesign; new Identity permission; caller-selected learner/time/
digest; target content or permission export; replay/session/credential/storage/
artifact/provider data; import or cross-module manifest; whole-account erasure,
retention, purge, recovery-copy deletion, managed-cloud policy, destructive
operation, cross-module persistence, external action, active write collision,
conflicting canonical authority, or material CAP-0017/SLI-0073 drift.

Do not stop for harmless whitespace, incidental fixture order/count, optional
wording, or nonfunctional styling. Fix in-scope inconsequential issues locally
or defer optional cleanup without a new approval or review loop.

## Required Handoff

Report `CAP-0017.SLI-0073.WRK-0144`; exact candidate and qualifying receipt;
public operation and API route; response fields and authority; exact quota
codes/messages and zero-write evidence; PostgreSQL retry/restart behavior;
authorization/privacy/target-isolation evidence; OpenAPI/client headless parity;
focused, affected, security, and aggregate results; documentation impact;
compatibility assumptions; and the remaining browser/live-recovery packets.

## Planning History

- 2026-10-17: Authored just in time after WRK-0143 completed. The packet uses
  the fixed export/quota contract, existing repository and read permission,
  adds no migration or new identity policy, and requires no lower-level
  approval within the current approved CAP-0017 package.
- 2026-10-17: Activated from recorded base `282eb4d` after confirming the
  current CAP binding, completed WRK-0143 dependency, exact bounded scope,
  resolved decisions, and no active coordination collision.
- 2026-10-17: Verified the export request boundary rejects query and body input
  before workspace access while retaining server-owned learner, generation
  time, digest, and storage authority.
