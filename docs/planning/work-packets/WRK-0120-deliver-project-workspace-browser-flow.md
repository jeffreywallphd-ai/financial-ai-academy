---
id: WRK-0120
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: SLI-0031
capability: CAP-0007
depends_on: [WRK-0119]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/router.tsx", "apps/web/src/features/project-workspace", "apps/web/src/styles/project-workspace.css", "apps/web/tests/browser/project-workspace", "apps/web/tests/component/projectWorkspace.test.tsx", "apps/web/tests/unit/projectWorkspaceModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0120-deliver-project-workspace-browser-flow.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Deliver the Project Workspace Browser Flow

## Objective and Deliverable

Deliver the accessible learner-facing consumer of the completed Project
workspace API. An authorized learner can reopen an exact workspace, add or
revise notes and source references, add one bounded inert file with honest
provenance, inspect safe metadata, download the original bytes, close an
immutable snapshot, download its evidence export, and continue editing the
live workspace without changing the closed snapshot.

The generated public client remains the only browser-to-backend seam. The
browser is a thin client: it does not duplicate server policy, infer authority,
execute or actively render artifacts, manufacture domain links, or make a
browser-only operation required by headless clients.

## Required Context

Before editing, read and follow every applicable `AGENTS.md`, `docs/README.md`,
the routed interface-design and Project context, the change-impact matrix,
decision-readiness register, planning guide/register, CAP-0007, SLI-0031,
WRK-0119, ADR-0011, ADR-0012, the Project workspace contract, API and
generated-client contracts, the user-facing language and interface standards,
the design style guide and semantic tokens, the current Project routes,
models, API adapters, styles, unit/component/browser tests, and
`apps/web/README.md`.

Revalidate the actual generated schemas before constructing any request. Keep
exact IDs, revisions, digests, versions, and classification codes available in
an accessible `Technical record`, while primary UI copy stays task-focused and
plain.

## Decisions and Assumptions

- WRK-0119's protected generated-client operations are the fixed input. The
  browser may make them usable but may not replace, reinterpret, or weaken
  their authorization, optimistic revision, idempotency, artifact, snapshot,
  export, or no-execution behavior.
- Opening a Project reads its shell, workspace, and snapshot list as one closed
  learner view. A malformed or failed member prevents partial workspace
  presentation.
- A form action carries one learner intent and the currently displayed server
  revision. An exact unchanged retry retains one request key; a changed intent
  uses a fresh key. Server conflicts reload current facts before another edit.
- Artifact input is restricted to the contract's supported media and ten-MiB
  bound. The browser calculates byte count and SHA-256 with Web Crypto and
  sends base64 through the generated request type. The server remains the
  authority and rechecks every fact.
- Files are never executed, expanded, linked to a runtime, or actively
  rendered in the browser. Inspection is metadata and plain text only where
  the accepted record says so; this packet does not need an inline preview.
- Downloaded artifact bytes and snapshot export JSON are derived from
  successful generated-client responses, given conservative local file names,
  and explicitly initiated by the learner. No hidden background export occurs.
- Typed domain links may be displayed when returned by the API, but there is
  no browser control to create a link while no owning-module gateway is
  admitted. No Portfolio state or owner facts are copied into the UI.
- Valid zero/many records, supported classifications, optional provenance,
  Unicode text, varied IDs/digests, and server order remain valid. Tests must
  not freeze incidental wording, timestamps, counts, or visual layout.

## In Scope

- Extend the exact Project detail loader to fetch and close the Project shell,
  workspace, and snapshot-list responses through the generated client after
  the existing private single-profile session is established.
- Add runtime validation for the complete returned workspace and snapshot
  shapes, including exact keys, bounds, timestamps, IDs, revisions, digests,
  classifications, and correlations to the selected Project.
- Add generated-client actions for add/replace note, add/replace reference,
  inert artifact upload, snapshot close, artifact download, and evidence
  export. Map bounded server failures into learner-actionable states without
  exposing private or technical details.
- Present ordered notes, source references, artifact metadata, returned typed
  links, and closed snapshots with accessible empty states and exact technical
  records. Provide clear edit, add, download, close-snapshot, export, and
  continue-working actions.
- Preserve retry intent and learner-entered drafts after an unavailable
  response. Handle stale revisions and changed-key conflicts without silently
  overwriting work.
- Use existing semantic design variables and reviewed icons only. Preserve
  light/dark meaning, keyboard order, visible focus, error association,
  narrow-width reflow, zoom, reduced motion, and forced-color behavior.
- Add unit, component, and mocked Chromium evidence for safe response closure,
  flexible record shapes, retry/stale behavior, artifact safety language,
  snapshots, continued work, download/export intent, accessibility, and theme
  parity. Keep API/headless availability as the primary boundary.

## Out of Scope

- Any backend, schema, OpenAPI, generated-client, database, object-adapter,
  migration, identity, permission, or Project domain-policy change.
- Artifact execution, notebooks or kernels, package installation, runtime
  environments, provider calls, archive expansion, active HTML/SVG/PDF/code
  rendering, network access, secrets, callbacks, or automated analysis.
- Live Portfolio or other owning-module integration, browser-invented domain
  links, copied financial state, market data, calculations, personalized
  recommendations, transactions, advice, or real financial actions.
- Assessment submission, completion, grading, mastery, competency projection,
  instructor review, Learner-model mutation, AI autonomy, or browser-only
  authority.
- Import/restore, collaboration, sharing, publication, tenancy, managed-cloud
  storage/recovery, broad workspace navigation, and optional styling-only
  polish unrelated to function, accessibility, or meaning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated API/client | `contracts/api/openapi.json`, `apps/web/src/generated/api-client/` | no | Fixed public source for every browser request and response |
| Browser model/API | `apps/web/src/features/project-workspace/model.ts`, `api.ts` | yes | Close returned shapes and translate bounded learner intent to generated calls |
| Browser route/view | Project route, detail page, app router | yes | Compose the complete learner workspace without moving authority into React |
| Design system | style guide, tokens, reviewed icons | no shared asset change; Project stylesheet only | Reuse semantic variables for accessible responsive behavior |
| Browser verification | Project unit, component, and focused Chromium tests | yes | Prove flexible shapes, failures, artifact/snapshot flows, accessibility, and no execution |
| Documentation/planning | web README, this packet, SLI-0031, register | yes | Keep delivered route and lifecycle evidence current |
| Backend/persistence | Project domain/application/adapters/hosts and migrations | no | Completed in WRK-0119 and remains the API authority |

## Contracts and Interfaces

Consume only the generated operations `getProject`, `getProjectWorkspace`,
`listProjectSnapshots`, `mutateProjectWorkspace`, `uploadProjectArtifact`,
`downloadProjectArtifact`, `closeProjectSnapshot`, and
`exportProjectSnapshot`. Requests may contain only the schema-defined Project
identifier path plus intent, expected revision, request key, bounded metadata,
and artifact bytes. They may not contain learner identity, permission, storage,
provider, execution, or policy selectors.

The loader returns one discriminated route state containing a correlated
`ProjectShellResponseModel`, `ProjectWorkspaceResponseModel`, and ordered
`ProjectSnapshotResponseModel` set. Mutations return bounded success/error
states that allow route revalidation; no response is cached as independent
authority. WRK-0121 receives this complete browser seam plus focused tests as
an input to full-slice qualification.

## Dependencies and Parallel Safety

WRK-0119 is complete and supplies all server and generated-client operations.
This packet owns the Project browser route, model, API wrapper, styles, and
focused tests, so it is not parallel-safe with another writer in those areas.
It must complete before the SLI-0031 qualification packet begins.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Open and resume | A valid owned Project has zero or many workspace records | The learner opens its exact route | The complete correlated workspace and snapshots appear in server order, with useful empty states and no partial unsafe response | unit/component/browser |
| Save note/reference | The displayed workspace revision is current | The learner submits one bounded add or edit | One generated-client mutation is sent, current facts reload, and entered Unicode text remains exact | unit/component/browser |
| Stale edit or retry | A write conflicts or is temporarily unavailable | The learner retries or reloads | Unchanged intent keeps its key; stale facts do not overwrite work; current workspace can be reopened before a new intent | unit/component/browser |
| Inert file admission | A supported bounded file and complete source facts are selected | The learner explicitly adds it | The browser sends computed count/digest/base64 through the generated type; metadata appears only after server acceptance | unit/component/browser |
| Unsafe/unsupported file | A file exceeds bounds or lacks an admitted media/classification combination | The learner attempts to add it | The browser explains the usable next action and sends no request; the server remains authoritative for accepted attempts | unit/component/browser |
| Safe artifact handling | An accepted artifact exists | The learner inspects or downloads it | Only plain metadata/technical facts are rendered; download is explicit; nothing executes, expands, or actively previews | component/browser |
| Snapshot and continue | Current shell/workspace revisions are valid | The learner closes a snapshot and then adds more work | The closed snapshot remains listed unchanged while the live revision advances | component/browser |
| Evidence export | A closed snapshot is available | The learner asks for its evidence record | The generated export response downloads as deterministic JSON with no hidden automatic action | unit/component/browser |
| Authorization/privacy | Session, permission, record, or response validation fails | The route or action completes | Bounded task-focused recovery appears without partial private workspace data | unit/component/browser |
| Flexible valid shape | Counts, ordering, Unicode, classifications, optional source facts, IDs, and digests vary | Models and views consume them | Valid records work without fixture, exact-copy, or visual-layout dependence | unit/component |
| Accessible parity | The flow is used in light/dark, keyboard, narrow, reduced-motion, and forced-color contexts | The learner navigates and acts | Equivalent content/actions, labels, focus, error relationships, and reflow remain available | component/browser/design check |
| API-first/no side effect | Browser support is removed or bypassed | A headless client uses WRK-0119 | Every supported operation remains available without UI state, and browser work creates no learning or financial authority | architecture/client evidence |

## Verification Commands

Run the focused Project model and component tests; Project browser Chromium
qualification with accessibility analysis; `npm --prefix apps/web run lint`;
`npm --prefix apps/web run typecheck`; `npm --prefix apps/web test`;
`npm --prefix apps/web run build`; generated-client currency; design-system,
learner-language, documentation, planning, and whitespace checks; affected
exact-candidate verification with one independent technical review; and
`python dev-tools/agent/check_ready.py`. Reuse the existing browser server
isolation rather than assuming a fixed free port.

## Documentation and Evidence Update

Update `apps/web/README.md` with the delivered route behavior, generated-client
boundary, inert file handling, snapshot/export meaning, plain-language
presentation, and explicit omissions. Reconcile this packet, SLI-0031, and the
planning register at activation and completion. Do not claim full-slice live
PostgreSQL/restart qualification here; WRK-0121 owns that integrated evidence.
Approval and reviewer records remain only in ignored local control-plane
storage.

## Stop Conditions

Stop for a required backend or generated-contract change; conflicting
canonical meaning; client-owned identity, authorization, revision, digest, or
policy; an execution, active-rendering, archive, network, secret, provider,
Portfolio, financial-action/advice, Assessment, mastery, Learner-model,
tenancy, managed-cloud, or autonomous-AI requirement; cross-module internals;
unbounded bytes; inaccessible required interaction; active write-scope
overlap; or material CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, fixture order/count, or another inconsequential issue.
Fix it within scope or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; generated operations consumed; runtime
response closure; mutation/retry/stale behavior; artifact digest, source,
download, and no-execution behavior; snapshot continuation and export;
authorization/privacy; accessibility and responsive evidence; focused, web,
design, documentation, affected, and aggregate checks; changed files;
documentation impact; assumptions; residual gaps; and the next qualification
packet. Confirm that no backend authority, execution surface, active preview,
live Portfolio behavior, financial action/advice, Assessment or learner-state
effect, managed-cloud profile, or separate AI mode was added.

## Planning History

- 2026-10-16: Authored just in time after WRK-0119 completed. The packet is the
  smallest complete generated-client learner flow for the accepted workspace,
  inert artifact, immutable snapshot, evidence-export, and continue-working
  contracts. It keeps the public API independently usable by headless clients
  and exposes no new decision gate.
