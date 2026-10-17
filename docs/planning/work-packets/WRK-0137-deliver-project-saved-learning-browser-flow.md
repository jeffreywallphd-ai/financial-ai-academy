---
id: WRK-0137
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0071
capability: CAP-0017
depends_on: [WRK-0136]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/features/personal-workspace/PersonalWorkspacePage.tsx", "apps/web/src/features/personal-workspace/api.ts", "apps/web/src/features/personal-workspace/model.ts", "apps/web/src/features/project-workspace/ProjectDetailPage.tsx", "apps/web/tests/browser/project-workspace/project-workspace.spec.ts", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/component/projectWorkspace.test.tsx", "apps/web/tests/unit/personalWorkspaceModel.test.ts", "docs/architecture/contracts/personal-workspace-contract.md", "docs/planning/vertical-slices/SLI-0071-organize-project-workspaces-snapshots-resources.md", "docs/planning/work-packets/WRK-0137-deliver-project-saved-learning-browser-flow.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 2c408443c8adf95d8cb803d96d8b47a707d948dd
claim_id: WRK-0137:cafa3d30-634c-464d-969a-a501cc8b5fae
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T13:41:53Z
---

# Agent Work Packet: Deliver the Project Saved-Learning Browser Flow

## Objective and Deliverable

Deliver contextual `Save to Saved learning` entry points for an authorized
Project workspace, immutable checkpoint, and inert file record. Reuse the
existing protected Personal-workspace API and generated TypeScript contract so
the browser can create a note or bookmark for an exact Project selector, return
to the exact Project context, and organize the resulting mixed records without
copying or executing Project-owned content.

This is a consumer packet. It does not add a backend route, change OpenAPI,
grant Project access, or introduce separate browser, headless, or AI authority.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed planning, design, language,
architecture, contract, security, testing, and delivery context; change-impact
matrix; decision-readiness register; ADR-0009, ADR-0011, ADR-0012, and ADR-0021;
CAP-0017; SLI-0071; completed WRK-0136; the Personal-workspace and Project
contracts; reviewed generated client; current Project detail and Saved Learning
routes; affected styles and design tokens; focused browser, component, and unit
tests; and the nearest README before editing.

## Decisions and Assumptions

- The Project detail loader is already the authorization boundary for rendering
  contextual controls. Links carry only the exact safe selector fields already
  visible on that authorized surface; the Personal-workspace server revalidates
  Project access when a create mutation is submitted.
- The existing `/saved-learning/new` loader and action remain the one browser
  flow. Its selection parser is widened by a closed discriminator for
  `project_workspace`, `project_snapshot`, and `project_artifact`; no new route
  or client is added.
- Project return locations are derived from the validated selector instead of
  accepting arbitrary learner-controlled paths. Exact workspace, checkpoint,
  and file anchors are added only where needed for deterministic return focus.
- A guessed or malformed Project selection may show only a generic invalid or
  unavailable state. It must not confirm Project existence, ownership, title,
  content, or authorization.
- Saved records continue to use the current note, bookmark, collection,
  membership, order, archive, restore, and remove operations. Project mutation,
  download, export, preview, execution, and submission remain owned by Project.
- Existing semantic tokens and button/layout patterns are sufficient. No new
  feature-local visual scale, icon, color, radius, shadow, or theme map is
  expected.

## In Scope

- Extend the closed browser `SaveSelection`, query parser, return-path
  derivation, hidden selector fields, form-to-generated-mutation mapping, retry
  correlation, and learner-facing object labels for all three Project variants.
- Add contextual links on the authorized Project workspace header/source area,
  each immutable checkpoint, and each inert file card. Keep exact IDs in the
  generated link, never in ordinary learner input.
- Add stable safe anchors for exact return to the Project workspace, checkpoint,
  or file record without exposing a storage path or enabling active content.
- Prove valid selector variety and exact form mapping, duplicate/missing/unsafe
  query rejection, positive artifact-version bounds, safe return derivation,
  generic failure behavior, immutable retry payloads, and no learner/owner facts
  in browser requests.
- Prove contextual entry, note/bookmark creation, redirect, mixed Curriculum and
  Project reference display, collection organization, archive/restore/remove,
  exact Project return, accessibility, reflow, theme parity, and inert file
  behavior in focused component and mocked-browser checks.
- Update direct browser and Personal-workspace contract guidance plus SLI-0071,
  this packet, and the planning register.

## Out of Scope

Backend/domain/persistence/migration/API/OpenAPI/generated-client changes;
Project or Personal-workspace authorization changes; Project mutation from
Saved Learning; artifact content, download, export, preview, archive expansion,
rendering, network retrieval, package installation, subprocess, or execution;
learner-entered target IDs; arbitrary URLs; Portfolio or other domain adapters;
cross-domain search or stale-reference maintenance; managed cloud; tenancy;
collaboration; provider/model/AI authority; financial advice or action; new
dependency or lockfile; styling-only polish; isolated live PostgreSQL/backend
topology qualification, which remains in WRK-0138.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project context | Current authorized detail, checkpoint, and file surfaces | `ProjectDetailPage.tsx` and focused Project component/browser checks | Add exact safe links and return anchors without changing Project actions |
| Saved Learning selection | Current Curriculum-only query parser, hidden fields, action mapping, retry payload | Personal-workspace model, API, page, and focused unit/component checks | Reuse the generated union for exact Project selectors |
| Mocked browser behavior | Current Project public API mock and workspace flow | Focused Project Playwright specification | Prove contextual entry and mixed saved-record organization without a live topology |
| Guidance | Current browser and contract documentation | Listed README and contract Markdown | Record closed Project selection and unchanged server authority |
| Planning evidence | SLI-0071, WRK-0137, register | Listed planning files | Keep JIT-C lifecycle and JIT-D dependency synchronized |

No backend, OpenAPI, generated-client, design-token, icon, shared style,
dependency, lockfile, build-tool, or control-plane file may change.

## Contracts and Interfaces

The existing `/saved-learning/new` query admits exactly these additional
selection forms, with each parameter present exactly once:

- `kind=project_workspace`, `project=<project_id>`;
- `kind=project_snapshot`, `project=<project_id>`,
  `snapshot=<snapshot_id>`;
- `kind=project_artifact`, `project=<project_id>`,
  `artifact=<artifact_id>`, `version=<positive integer>`.

The parser derives the exact safe return target from the selector:

- `/projects/<project_id>#workspace`;
- `/projects/<project_id>#snapshot-<snapshot_id>`;
- `/projects/<project_id>#artifact-<artifact_id>-v<version>`.

The submitted generated mutation contains only the existing schema version,
idempotency key, expected Personal-workspace revision, note/bookmark fields,
and exact typed Project selector. It contains no learner ID, workspace ID,
Project title/charter, owner claim, permission, snapshot material, artifact
content, storage path, URL, provenance payload, or execution instruction.

## Dependencies and Parallel Safety

WRK-0136 is complete and supplies the stable protected API, generated union,
runtime response guard, and safe Saved Learning rendering. WRK-0137 owns both
Project contextual controls and the Personal-workspace browser selector/action
path, so it is not parallel-safe with another packet touching those files or
tests. WRK-0138 cannot start until this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Contextual workspace save | An authorized learner opens a Project | They choose `Save Project to Saved learning` | The existing save flow receives the exact Project-workspace selector and offers a note or bookmark without learner-entered IDs | component/browser |
| Checkpoint save | An immutable checkpoint is visible | The learner chooses its save control | The selector binds exact Project and checkpoint IDs and returns to that checkpoint | unit/component/browser |
| Inert file save | An inert file record is visible | The learner chooses its save control | Only safe manifest identity/version enters the selector; no bytes, storage locator, preview, or execution action crosses the boundary | unit/security/browser |
| Mixed organization | Curriculum and Project records coexist | The learner adds them to a collection, reorders, archives, restores, or removes them | Existing organization behavior applies without mutating either source | component/browser |
| Safe guessed link | A selection is missing, duplicated, malformed, or manually guessed | The loader or action evaluates it | It fails generically without protected target detail or partial mutation | unit/browser |
| Exact retry | A Project note/bookmark response is uncertain | The learner retries without editing | The complete validated selector and idempotency key remain fixed; an edit creates a fresh request | unit/component |
| Return and resume | A Project record is saved and the learner returns later | They use the saved destination or return control | The exact Project context is restored through the Project-owned route and authorization | component/browser |
| Flexible safe data | Multiple valid IDs, artifact versions/kinds, titles, checkpoints, and mixed collection order are used | Focused checks run | Invariants hold without fixed fixture count, wording, Project origin, or incidental order | parameterized unit/browser |

## Verification Commands

Run:

```text
npm --prefix apps/web run test -- apps/web/tests/unit/personalWorkspaceModel.test.ts apps/web/tests/component/personalWorkspace.test.tsx apps/web/tests/component/projectWorkspace.test.tsx
npm --prefix apps/web run test:browser -- apps/web/tests/browser/project-workspace
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run build
python dev-tools/language/check_user_facing_language.py --changed
python dev-tools/design/check_design_system.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0137-deliver-project-saved-learning-browser-flow.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Run the exact affected-check plan on one clean submitted candidate and obtain a
fresh qualifying receipt and independent technical disposition. Use the
repository-pinned Node 24/npm 10.8.2 runtime. Do not use a running developer
server as browser evidence; the focused Playwright wrapper owns an isolated
loopback server and cleanup.

## Documentation and Evidence Update

Document the three contextual controls, closed query/selector forms, derived
return locations, generated-client reuse, server-side revalidation, inert file
boundary, unchanged Project ownership, headless/API parity, and remaining live
qualification seam. Completion evidence records exact unit/component/browser
counts, accessibility/reflow/theme results, malformed-selection and private-
field denials, request-shape containment, affected/aggregate results, changed
files, assumptions, unqualified live checks, and residual gaps. Receipts and
technical-review records remain only in ignored local control-plane storage.

## Stop Conditions

Stop for a backend, API, OpenAPI, generated-client, authorization, or migration
change; Project state mutation from Saved Learning; learner-entered target IDs;
arbitrary return URLs; target existence disclosure; copied Project content,
snapshot material, artifact bytes, storage location, permission, provider data,
or source URL; preview/download/export/execution through Personal workspace;
new dependency; style-system divergence; active scope collision; unresolved
decision; conflicting canonical sources; or material CAP-0017/SLI-0071 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report the exact candidate; all three contextual link and selector shapes;
derived return paths; generated mutation containment; mixed-reference
organization/resume behavior; mocked browser accessibility/reflow/theme and
inert-resource evidence; focused, language, design, security, affected,
aggregate, and independent-review results; changed files; documentation impact;
assumptions; unqualified live checks; and residual gaps. Confirm no backend,
API/OpenAPI/generated-client, migration, Project mutation, artifact content or
execution, provider, separate AI authority, or financial action changed, then
leave WRK-0138 dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0136 completed. The packet reuses
  the stable protected API and generated Project-reference union for contextual
  browser entry, exact closed selector mapping, mixed organization, and mocked
  browser behavior. Isolated live PostgreSQL/backend qualification remains in
  JIT-D. No lower-level approval is required.
- 2026-10-17: Activated from recorded base `2c40844` after validating the
  completed dependency, exact write scope, design and language constraints,
  current CAP authority, and absence of active coordination overlap.
