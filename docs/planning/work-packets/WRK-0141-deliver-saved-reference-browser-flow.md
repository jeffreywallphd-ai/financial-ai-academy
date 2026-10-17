---
id: WRK-0141
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0072
capability: CAP-0017
depends_on: [WRK-0140]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/features/personal-workspace/api.ts", "apps/web/src/features/personal-workspace/model.ts", "apps/web/src/features/personal-workspace/PersonalWorkspacePage.tsx", "apps/web/src/features/personal-workspace/PersonalWorkspaceRoutes.tsx", "apps/web/src/styles/personal-workspace.css", "apps/web/tests/unit/personalWorkspaceModel.test.ts", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/browser/personal-workspace/personal-workspace.spec.ts", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/planning/vertical-slices/SLI-0072-search-and-refresh-saved-references.md", "docs/planning/work-packets/WRK-0141-deliver-saved-reference-browser-flow.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 96e6f10376e7e1d3c22febac8184905e0f4d6784
claim_id: WRK-0141:f9f60968-15b4-4815-8b9c-0f23c0ae5c36
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T15:35:42Z
---

# Agent Work Packet: Deliver the Saved-Reference Browser Flow

## Objective and Deliverable

Deliver SLI-0072's learner-visible search, filter, reference-status, explicit
check, and safe-resume flow on `/saved-learning`. Consume only the reviewed
generated Personal-workspace query and mutation operations so the browser and
headless clients continue to share one API, authority model, and status truth.

The primary flow uses plain task language. Exact query, workspace, reference,
status, source, version, digest, and time facts remain available through
accessible technical records. The packet adds no browser-only policy, source
resolution, persistence, background refresh, or AI authority.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed delivery-planning,
interface-design, and testing-quality context; change-impact matrix;
decision-readiness register; ADR-0009, ADR-0012, and ADR-0021; CAP-0017;
SLI-0072; completed WRK-0139 and WRK-0140; Personal-workspace contract and
generated client; current Saved learning model, loader/action, component,
styles, tests, nearest README, semantic tokens, reviewed icons, content style,
and user-facing language standards. Canonical sources govern over this packet.

## Decisions and Assumptions

- WRK-0140 supplies the complete public query and record-only refresh seam.
  This packet is a generated-client consumer and does not change backend,
  OpenAPI, generated types, owner permissions, or status semantics.
- The route accepts one closed browser value for each optional filter. It maps
  those values to the API's array fields, preserves the opaque continuation,
  and rejects duplicate, unknown, malformed, or over-broad URL values before a
  workspace or query call.
- The loader reads the authorized workspace for collections and editing, and
  queries the same learner workspace for the visible record page. It closes
  both responses and verifies matching workspace revisions before rendering.
- Search-result order is not mutation authority. Record reordering is offered
  only when the complete unfiltered workspace-order page is visible; filtered,
  differently sorted, or paged views cannot submit a partial reorder.
- Only an `available` reference exposes its retained owner destination as an
  action. `stale` and `unavailable` retain learner-authored content and exact
  historical facts but show no source-resume link.
- `Check source` submits only the saved record ID in the existing mutation
  envelope. The server derives learner, selector, owner access, replacement
  facts, validation time, and final status.
- Existing semantic tokens, form/button/card patterns, and reviewed `search`,
  `filter`, and `refresh` icons are sufficient. No shared visual-system change
  is planned.

## In Scope

- Add generated-type aliases and fail-closed validation for query request and
  response shapes, all five three-state references, applied-query correlation,
  bounded records, continuation, query digest, and workspace revision.
- Parse a closed `/saved-learning` search state, establish the current learner
  session, read the workspace, call `queryPersonalWorkspace`, retry one 401,
  and return one closed route state without exposing learner selection.
- Add task-first search and filter controls for text, record kind, source,
  reference kind, status, archive state, collection, and sort; support clear
  filters and opaque forward paging without switching query meaning.
- Render learner-visible status as `Ready to open`, `Saved details changed`, or
  `Source unavailable`, with concise meaning and a safe next action. Keep raw
  status and validation time in the technical record.
- Add a per-record `Check source` mutation through the existing generated
  mutation client. Preserve exact uncertain retry behavior and ordinary
  optimistic revision checks.
- Suppress source links for non-available references. Preserve note/bookmark
  editing, archive/restore/remove, collections, membership, and complete-view
  record reordering without widening any authority.
- Add flexible unit, component, and isolated Chromium evidence for empty and
  varied results, Unicode search, every filter family, stable query mapping,
  continuation, mixed statuses and owners, stale/unavailable safe display,
  refresh success/failure/retry, closed malformed responses, keyboard/focus,
  reflow, 200-percent text, light/dark/system parity, forced colors, reduced
  motion, and accessibility.
- Update direct web and architecture guidance, SLI-0072, this packet, and the
  planning register.

## Out of Scope

Backend/domain/application/repository/migration/API/OpenAPI/generated-client
changes; new owner adapters; live PostgreSQL or restart qualification;
background polling or events; semantic/vector search; target mutation;
artifact content, preview, download, expansion, or execution; arbitrary URL;
local browser persistence as truth; export/delete-request; backup/recovery;
managed cloud; tenancy; provider/model authority; collaboration; external
action; financial advice or action; dependency or lockfile change; shared
design-token/icon change; styling-only polish. WRK-0142 owns the cumulative
live browser/headless and slice-closure evidence.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Browser model and API | Generated query/mutation types, current validators and loader/action | listed Personal-workspace model and API files | Close and map the accepted public operations without a second contract |
| Learner interface | Existing page, route states, semantic tokens and icons | listed page, route, and feature stylesheet | Add plain-language search, status, check, paging, and safe resume |
| Focused verification | Current unit/component/isolated Chromium fixtures | listed three test files | Prove mapping, containment, accessibility, anti-rigidity, and regression |
| Guidance | Current web and Personal-workspace assurance text | listed README and architecture Markdown | Record delivered browser consumer and remaining live seam |
| Planning | SLI-0072, WRK-0141, register | listed planning files | Keep JIT-C lifecycle and JIT-D dependency synchronized |

No backend, executable contract, generated client, router, shell, shared design
asset, deployment, dependency, lockfile, or control-plane file may change.

## Contracts and Interfaces

The loader uses exactly:

```text
GET  /api/v1/personal-workspace
POST /api/v1/personal-workspace/query
```

The page maps optional, single-valued browser parameters to the closed query
request: text, record kind, owner module, reference kind, target status,
archive state, collection, sort, limit, and opaque cursor. Unknown or repeated
fields and invalid values fail before API access. Cursor links preserve every
normalized non-cursor value. The returned query revision must match the opened
workspace revision; mismatch fails closed rather than combining two states.

`Check source` uses the existing mutation operation:

```text
POST /api/v1/personal-workspace/mutations
mutation = { operation: "refresh_reference", record_id: <workspace-owned ID> }
```

The browser sends no learner ID, source owner, selector, target status,
replacement fact, destination, validation time, permission, provenance,
provider material, or target content. Only available records produce an owner
route. Stale and unavailable records retain history and learner organization
but cannot navigate to the retained destination from the primary interface.

## Dependencies and Parallel Safety

WRK-0140 is complete and supplies the protected query/refresh API, persistence,
generated-client union, confidentiality policy, and replay behavior. WRK-0141
owns the existing Saved learning browser model, API mapping, page, style, and
focused tests, so it is not parallel-safe with another writer in those files.
WRK-0142 cannot start until this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty query | An empty workspace or no matching records | Learner opens or filters Saved learning | Clear learner text explains what is absent and how to broaden or add saved learning | component/browser |
| Text and filters | Mixed notes/bookmarks, Curriculum/Project sources, statuses, archives, and collections | Learner searches and combines filters | One closed generated query is sent and only complete returned records render | unit/browser |
| Stable page | More records exist than one page | Learner follows `Show more results` | Opaque continuation preserves the same query and appends no invented authority | unit/component/browser |
| Current source | A record is available | It renders | Status meaning and an owner-route action are visible; exact source facts remain in the technical record | component/browser |
| Stale or unavailable source | An explicit check recorded non-current status | It renders | Learner text and organization remain, no source link appears, and `Check source` remains available | component/browser |
| Explicit check | Any saved reference is visible | Learner chooses `Check source` | Mutation contains only record ID plus existing revision/idempotency envelope and accepted status replaces no learner text | unit/browser |
| Uncertain retry | Refresh response is unavailable or invalid | Learner retries unchanged | Exact prepared request identity is reused; editing or another action creates a fresh request | unit/component |
| Revision mismatch | Workspace read and query result disagree | Loader closes the pair | Whole page fails safely without mixing old and new private state | unit/browser |
| Partial reorder defense | A filtered, sorted, or paged result is visible | Learner reviews record actions | No incomplete record-order mutation can be submitted | component/browser |
| Flexible safe shapes | Valid Unicode, variable counts/order, all five kinds, three statuses, and additional collections are returned | Focused suites run | Invariants hold without a fixed fixture count, exact prose, or incidental order | parameterized unit/component |
| Accessible themes | Ready, empty, error, stale, and unavailable views | Keyboard, axe, narrow width, 200-percent text, forced colors, reduced motion, and three themes run | Equivalent meaning, actions, hierarchy, focus, and reflow remain available | Chromium/design |

## Verification Commands

Run:

```text
npm --prefix apps/web run test -- apps/web/tests/unit/personalWorkspaceModel.test.ts apps/web/tests/component/personalWorkspace.test.tsx
npm --prefix apps/web run test:browser -- apps/web/tests/browser/personal-workspace
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run build
python dev-tools/learner-language/check_learner_language.py
python dev-tools/design/check_design_system.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0141-deliver-saved-reference-browser-flow.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use the repository-pinned Node 24/npm 10.8.2 runtime. Run an exact clean-
candidate affected-check plan, obtain a fresh qualifying receipt, and complete
proportionate independent technical review. The isolated Playwright wrapper
owns its loopback server and cleanup; do not rely on a developer server.

## Documentation and Evidence Update

Document query mapping and response closure; status and safe-resume meaning;
record-only explicit check; server-derived authority; partial-reorder defense;
confidential error handling; generated-client/headless parity; accessibility,
language, and anti-rigidity results; changed files; assumptions; unqualified
live profiles; and residual WRK-0142 work. Approval and reviewer records remain
only in ignored local state.

## Stop Conditions

Stop for a required backend, contract, OpenAPI, generated-client, permission,
identity, persistence, or migration change; query across learners; caller-
controlled owner, selector, status, replacement fact, timestamp, provenance,
destination, or permission; differentiated missing/denied/removed disclosure;
source content or target mutation; arbitrary URL; active artifact behavior;
browser-only status truth; background coupling; new dependency; shared design-
system change; unresolved decision; active scope collision; canonical conflict;
stale CAP package; or material SLI/CAP drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report `CAP-0017.SLI-0072.WRK-0141`; exact candidate and receipt; closed query
mapping; status and safe-resume behavior; explicit record-only checks; partial-
reorder defense; generated-client/headless parity; focused unit/component/
Chromium, language, design, security, affected, aggregate, and independent
technical results; changed files; documentation impact; assumptions;
unqualified live checks; and residual gaps. Confirm no backend, contract,
generated-client, migration, target mutation, artifact execution, provider,
managed-cloud, separate AI authority, or financial action changed, then leave
WRK-0142 dependency-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0140 completed. The packet
  consumes the accepted protected query and refresh API to add the approved
  plain-language browser flow, while cumulative live browser/headless and
  restart qualification remain in JIT-D. No lower-level approval is required.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  generated-client, interface-authority, exact write-scope, documentation, and
  planning validation passed without material CAP or slice drift.
- 2026-10-17: Activated from recorded base `96e6f10` after validating the
  completed dependency, current CAP authority, closed browser/API boundary,
  exact write scope, and absence of an active file collision.
- 2026-10-17: Independent review of the first implementation candidate found
  that the browser had not bound the returned applied query and digest to the
  requested query, and that a complete but permuted result could expose record
  reordering. The in-scope correction reproduces canonical Unicode query
  meaning and digest, rejects mismatch, and requires exact canonical workspace
  order before reordering controls appear.
