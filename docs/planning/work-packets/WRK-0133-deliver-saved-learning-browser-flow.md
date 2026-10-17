---
id: WRK-0133
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0070
capability: CAP-0017
depends_on: ["WRK-0132"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/personal-workspace", "apps/web/src/styles/personal-workspace.css", "apps/web/tests/browser/personal-workspace", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/unit/personalWorkspaceModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0070-save-learning-notes-bookmarks-collections.md", "docs/planning/work-packets/WRK-0133-deliver-saved-learning-browser-flow.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Saved Learning Browser Flow

## Objective and Deliverable

Deliver the learner-visible SLI-0070 browser seam on top of the accepted
WRK-0132 public API. An authorized learner can open `Saved learning`, see a
clear empty or populated workspace, save an exact learning opportunity or
placed lesson as a note or bookmark, edit learner-authored text, organize
records into ordered collections, reorder, archive, restore, remove, and reopen
the same accepted state after normal route navigation or reload.

The browser consumes only the generated public API client and adds no policy,
identity, persistence, source-resolution, or AI authority. Exact identifiers,
versions, digests, validation times, and publication provenance remain
available under accessible `Technical record` disclosures while the primary
flow uses plain learner language.

## Required Context

Before any repository file change, read and follow every applicable
`AGENTS.md`, repository-root `docs/README.md`, the routed interface-design,
architecture-contract, testing-quality, and delivery-planning context, the
change-impact matrix, decision readiness, CAP-0017, SLI-0070, WRK-0131,
WRK-0132, ADR-0021, the Personal-workspace contract and generated API types,
the web application README and nearest feature patterns, design-system rules,
content style guide, user-facing language standard, implementation, consumers,
and focused tests. Canonical sources govern over this packet.

## Decisions and Assumptions

- CAP-0017 has a current approved four-slice package, SLI-0070 is active, and
  WRK-0132 is complete. This JIT-C refinement changes no CAP outcome, slice
  membership, order, decision posture, or non-goal.
- ADR-0021 and the implemented public API are sufficient. No identity,
  tenancy, provider, licensing, model-authority, execution, recovery,
  commercial, or external-action decision is introduced.
- The canonical learner route is `/saved-learning`; creation may begin from a
  bounded same-origin `/saved-learning/new` route carrying one validated
  opportunity or placed-lesson selector already known to a learning page.
  Directly guessed or stale selectors remain harmless because the server
  resolves and authorizes every source-bearing mutation.
- The flow adds `Saved learning` to primary navigation and may link to the new
  save route from current opportunity-detail and lesson-reading pages only if
  those pages already possess the complete accepted selector. It never asks a
  learner to type internal resource identifiers.
- The generated OpenAPI client and WRK-0132 schemas remain unchanged. Browser
  validation closes the response shapes and cross-record relationships before
  rendering; compatible extra response fields may be ignored.
- React Router loaders and actions own session retry, status mapping, and
  mutation dispatch. Components receive closed route state and do not call the
  backend, inspect cookies, or generate an alternate domain model.
- Each mutation uses the displayed workspace revision and a stable UUID
  idempotency key retained across a bounded retry. A stale revision prompts a
  refresh instead of silently replaying against newer state.
- Existing semantic tokens, shared controls, `StatusPanel`, and reviewed SVG
  icons are sufficient. No shared token, icon, or design-language change is
  planned.

## In Scope

- Add generated-client-backed Personal-workspace model, response validators,
  loader, mutation action, and route state for empty, ready, unauthorized,
  forbidden, stale, not-found, unavailable, invalid-response, and unexpected
  outcomes.
- Add `/saved-learning` and bounded `/saved-learning/new` routes plus a primary
  `Saved learning` navigation destination with accurate skip-link behavior.
- Present notes and bookmarks in accepted record order; distinguish archived
  records in text; expose safe same-origin source destinations; and retain note
  body whitespace without active or unsafe rendering.
- Present collections in accepted order with current membership. Support
  create, rename, remove, and replace-membership operations without copying
  records or targets.
- Support create note/bookmark from one validated learning opportunity or
  placed-lesson selector; update note or bookmark; reorder records; archive,
  restore, and remove a record.
- Keep exact workspace, record, collection, target, package, publication,
  validation, revision, time, schema, and digest facts available through
  labeled accessible `Technical record` disclosures.
- Provide task-first loading, empty, success, stale, denial, source-not-found,
  invalid-response, and unavailable messages with a real safe next action and
  no private implementation detail.
- Add focused model, component, and mocked Chromium coverage for valid varied
  workspaces, every UI mutation family, retry identity, denial/failure,
  keyboard/focus, accessibility scan, responsive reflow, 200-percent zoom,
  light/dark/system meaning, reduced motion, and forced colors.
- Update the web README, SLI-0070 packet table/history, packet evidence, and
  planning register together.

## Out of Scope

- Backend, domain, application, persistence, migration, Identity, Curriculum,
  OpenAPI, generated-client, public-contract, or deployment changes.
- Real PostgreSQL, application restart, non-browser HTTP, or complete live
  cross-system qualification; JIT-D owns those cumulative checks.
- Project workspaces, snapshots, artifacts, domain-resource adapters, search,
  filters, export/deletion requests, quotas beyond existing API errors,
  recovery-set behavior, and local/cloud parity claims; later SLI-0071 through
  SLI-0073 own those outcomes.
- Arbitrary URLs, imported browser bookmarks, uploads, rich text, Markdown or
  HTML rendering, semantic search, embeddings, generated notes, execution,
  active artifact preview, provider calls, network-selected resources, secrets,
  or external notifications.
- Enrollment, eligibility, recommendation, completion, Assessment, competency,
  mastery, grade, learner-projection, financial, Project, or target mutation.
- Collaboration, sharing, publishing, instructor access, organization tenancy,
  managed-cloud sync/retention/recovery, a separate AI mode, or autonomous
  durable mutation.
- Shared token/icon/component changes and nonfunctional styling polish. Optional
  polish that does not affect meaning, accessibility, responsiveness, or theme
  parity remains CAP-0031 work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated contract | Reviewed OpenAPI and generated `schema.d.ts` Personal-workspace types | none | Consume the accepted headless/public seam without contract drift |
| Browser model/API | Current feature API/model patterns, session helper, generated client | new `apps/web/src/features/personal-workspace/` files | Close response meaning and map protected reads/mutations through loaders/actions |
| Browser composition | App router, shell, root style imports, current learning routes | listed app files and new feature route/components | Add the saved-learning destination and bounded selector handoff |
| Presentation | Design tokens, content-language guides, existing project/learning styles | new `personal-workspace.css` only | Deliver accessible responsive layout without a parallel design system |
| Verification | Current unit/component/Playwright conventions | listed focused test paths | Prove safe shape, mutations, errors, accessibility, themes, and anti-rigidity |
| Documentation/planning | Web README, SLI-0070, packet, register | listed documentation files | Keep delivered route, boundaries, evidence, and lifecycle synchronized |

## Contracts and Interfaces

Consume only generated types for `PersonalWorkspaceResponseModel` and
`PersonalWorkspaceMutationRequestModel` through:

```text
GET  /api/v1/personal-workspace
POST /api/v1/personal-workspace/mutations
```

The loader establishes the accepted single-profile session, performs the
queryless workspace read, retries one 401 only after session invalidation, and
returns a closed route state. The mutation action accepts only recognized
form intents, validates identifiers/text/bounds needed before constructing the
generated request, posts one schema-version `1.0.0` mutation with the current
revision and stable idempotency key, closes the complete returned workspace,
and redirects or revalidates only after success.

The browser must never accept or send learner identity, workspace identity,
server time, record identity, source facts, package/publication provenance,
target status, digest, permission, provider, database, or policy authority.
Create-note and create-bookmark actions carry only the closed opportunity or
placed-lesson selector plus learner-authored title/body/label. Record and
collection mutations carry only existing workspace-owned IDs and accepted
ordered ID lists.

The response validator requires schema, learner/workspace identity, positive
revision, canonical UTC times, lowercase digest, unique record and collection
IDs, closed note/bookmark and opportunity/placed-lesson unions, same-origin
learning destinations, required-but-nullable bookmark labels, complete
publication provenance, and collection membership that references existing
unique records. It may ignore compatible additional fields but never render a
partial invalid result.

## Dependencies and Parallel Safety

WRK-0132 is the sole direct dependency and is complete. This packet owns app
composition, the new Personal-workspace browser feature, its stylesheet,
focused tests, and planning evidence. It overlaps central router/shell files
and therefore is not parallel-safe with another web-shell or SLI-0070 writer.
It must complete before JIT-D is authored and claimed.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty workspace | Valid revision-one response with no records or collections | Learner opens `Saved learning` | Page explains what is absent and links to a real learning action without inventing records | component/browser |
| Save exact note | Opportunity or lesson page has a complete accepted selector | Learner opens `Save to Saved learning`, enters valid note text, and saves | One generated-client mutation contains only selector and learner text; accepted note appears with exact target facts | unit/component/browser |
| Save bookmark | Complete accepted selector and nullable personal label | Learner saves with or without a label | Bookmark renders in record order and preserves required-nullable label meaning | unit/component/browser |
| Edit and organize | Populated workspace has notes, bookmarks, and several collections | Learner edits text, creates/renames/removes collections, changes membership, and reopens | Each accepted mutation uses current revision; order and membership match the returned workspace | component/browser |
| Reorder and lifecycle | Multiple active/archived records exist | Learner moves a record, archives/restores it, or removes it | Visible order/status changes only after accepted response; removal does not imply target deletion | component/browser |
| Stable retry | A mutation response is uncertain or temporarily unavailable | Learner retries the same prepared action | The same idempotency key and payload are reused; changed form state is not silently substituted | unit/browser |
| Stale revision | Another accepted write advances revision | Learner submits an older form | Page reports saved work changed, writes nothing locally, and offers refresh rather than auto-overwrite | unit/component/browser |
| Source/owned record absent | Server returns bounded 404 | Learner saves a stale source or changes a missing owned item | Page reports the item is unavailable, discloses no hidden source or learner detail, and offers a safe return | component/browser |
| Session/permission denial | Session cannot be established or permission is missing | Page loads or action runs | No workspace content is shown; task-focused recovery is available where safe | unit/browser |
| Invalid/partial response | Payload has an unknown union, unsafe route, duplicate IDs, dangling membership, bad time/digest, or missing required-nullable label | Browser receives it | Whole view fails closed; no partial private workspace is rendered | unit/component/browser |
| Flexible valid shapes | Valid Unicode, long-within-limit text, zero/many records and collections, different orders, both reference kinds, nullable labels, and compatible extra fields | Browser validates and renders | Meaning remains usable without fixture-count, exact-copy, or incidental-order assumptions | parameterized unit/component |
| Technical record | Valid record and workspace provenance exists | Learner opens disclosures by keyboard | Exact IDs, versions, digests, publication and validation facts remain labeled, selectable, and complete | component/browser |
| Accessible/theme parity | Empty, ready, error, and mutation states | Keyboard, narrow viewport, 200% zoom, forced colors, reduced motion, light/dark/system, and axe checks run | Equivalent content, actions, hierarchy, focus, and status meaning remain available | Chromium/design |

## Verification Commands

Run generated-client currency check; focused Personal-workspace model and
component tests; focused mocked Chromium; TypeScript typecheck; zero-warning
lint; web build; complete web unit/component regression; learner-language and
design-system checks; planning and packet validation; documentation,
whitespace, affected-path verification, one independent technical review, and
`python dev-tools/agent/check_ready.py`. Use the repository-local ignored
temporary root when the Windows sandbox cannot create test fixtures in its
packaged-system temp directory. Do not add PostgreSQL or full live-system runs
to this UI packet unless an observed failure crosses that boundary.

## Documentation and Evidence Update

Document the learner route, contextual save entry, generated-client boundary,
mutation/retry behavior, fail-closed response validation, plain-language and
technical-record hierarchy, accessibility/theme evidence, exact checks,
assumptions, unqualified live environments, and residual JIT-D work. Keep
receipts and reviewer records only in ignored local control-plane storage; do
not copy approval or reviewer metadata into tracked artifacts.

## Stop Conditions

Stop for a required API/schema/backend change; unknown selector or mutation
meaning; browser-selected learner/source/provenance/permission authority; local
persistence as source of truth; hidden overwrite after stale revision; unsafe
HTML or active target rendering; transfer or mutation of Curriculum, Content,
Project, Assessment, Learner model, or financial state; arbitrary URL/file,
execution, provider, network, credential, collaboration, sharing, tenancy,
managed-cloud, external action, autonomous AI authority, financial advice or
action; new dependency; shared design-system change; active write collision;
or material CAP-0017/SLI-0070 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it inside scope or defer optional polish to
CAP-0031.

## Required Handoff

Report exact candidate; `/saved-learning` routes and entry points; generated
client operations; response-validation and selector boundaries; supported
mutations and stable retry behavior; accessible technical evidence; task-first
errors; focused model/component/Chromium, typecheck, lint, build, design,
language, affected, and aggregate results; changed files; documentation impact;
assumptions; unqualified live/PostgreSQL/headless checks; and residual JIT-D
work. Confirm no backend, contract, generated-client, persistence, target-
domain, execution, provider, managed-cloud, separate-AI, or financial behavior
changed.

## Planning History

- 2026-10-17: Authored JIT-C immediately after WRK-0132 completed. The packet
  delivers the approved learner-visible save/resume outcome exclusively through
  the existing generated public client, with bounded plain-language,
  accessibility, technical-record, and anti-rigidity evidence. No lower-level
  approval is required.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  generated-client, interface-authority, write-scope, and planning validation
  passed without material CAP drift.
