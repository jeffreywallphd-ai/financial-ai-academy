---
id: WRK-0145
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0073
capability: CAP-0017
depends_on: [WRK-0144]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/features/personal-workspace/api.ts", "apps/web/src/features/personal-workspace/model.ts", "apps/web/src/features/personal-workspace/PersonalWorkspacePage.tsx", "apps/web/src/features/personal-workspace/PersonalWorkspaceRoutes.tsx", "apps/web/src/styles/personal-workspace.css", "apps/web/tests/unit/personalWorkspaceModel.test.ts", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/browser/personal-workspace/personal-workspace.spec.ts", "apps/web/README.md", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "docs/architecture/contracts/personal-workspace-contract.md", "docs/architecture/assurance/architecture-verification.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0073-qualify-personal-workspace-durability-boundaries.md", "docs/planning/work-packets/WRK-0145-deliver-personal-workspace-export-browser-flow.md"]
generated_artifacts: []
base_revision: d55878142b3ac8e21bd84fe705542ffc104818eb
claim_id: WRK-0145:d39726bc-3261-4743-ac7e-b3921a334c88
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T17:26:24Z
---

# Agent Work Packet: Deliver the Personal Workspace Export Browser Flow

## Objective and Deliverable

Add one plain-language, accessible Saved learning export experience that uses
the protected `exportPersonalWorkspace` generated-client operation delivered by
WRK-0144. An authorized learner can download the exact closed JSON owner export
without selecting learner, time, digest, storage, or destination authority.

Map the three existing public capacity outcomes to distinct, useful learner
guidance while preserving removal and exact-retry controls. Keep exact export
schema, generation time, workspace revision, and digest available in an
accessible technical disclosure. This packet changes no backend, executable
contract, OpenAPI, generated client, persistence, recovery behavior, or design-
system primitive.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`.
Revalidate CAP-0017, SLI-0073, WRK-0143, WRK-0144, ADR-0021, ADR-0008, the
Personal-workspace and API contracts, generated TypeScript client, browser
response guards, session retry policy, existing Project download/export
pattern, plain-language/interface standards, design tokens/icons, component
and focused Chromium tests, and nearest READMEs.

Stop if canonical sources conflict or the work requires a new API, contract
shape, browser persistence, import, recovery policy, combined learner-record
manifest, or another module's data.

## Decisions and Assumptions

- The reviewed `GET /api/v1/personal-workspace/export` operation is the only
  export source. Browser code supplies no request body, query, learner, time,
  digest, file name, provider, or storage destination.
- The browser validates the complete closed export response and its binding to
  the currently displayed workspace before downloading. A changed revision or
  digest produces a refresh-first outcome, never a stale download.
- The downloaded content is a UTF-8 JSON serialization of the validated server
  response. The stable local filename contains no learner or workspace ID.
- Export is initiated only by an explicit learner action. It is not automatic,
  background, uploaded, synchronized, signed, imported, or treated as a
  recovery artifact.
- Public quota codes remain server-authoritative. The browser maps them to
  static plain guidance and must not echo unvalidated server detail.
- Existing remove-record, remove-collection, and exact uncertain-response retry
  behavior remains available at maximum capacity. UI counts may explain the
  accepted limits but do not become mutation authority.
- Existing semantic variables, reviewed SVG icons, and Saved learning layout
  are reused; no new color, spacing, radius, shadow, or theme map is introduced.

## In Scope

- Add closed generated-client export response and outcome types plus a deep
  browser guard for schema, timestamp, digest, and workspace correlation.
- Add a session-aware export reader with one bounded unauthorized renewal,
  closed response validation, current revision/digest matching, and safe
  unauthorized, forbidden, changed, invalid-response, unavailable, and
  unexpected outcomes.
- Inject that reader through the application router into the Saved learning
  route/page; do not make generated client or session global inside UI code.
- Add an explicit `Download saved learning` control, pending state, safe JSON
  download, accessible success/failure status, and technical record containing
  only reviewed export facts.
- Map `record_limit`, `collection_limit`, and `collection_member_limit` to
  distinct plain-language action states. Retain prepared requests only where
  exact retry is safe and keep removal/reorganization controls usable.
- Prove empty, sparse, full, reordered, Unicode, optional-label, mixed-reference,
  changed-workspace, malformed-response, denied-session, retry, and download
  behavior through unit, component, and focused Chromium tests.
- Synchronize web, module, architecture, assurance, slice, packet, and register
  documentation with the exact delivered browser behavior and remaining live-
  recovery gap.

## Out of Scope

- Backend, domain, application, repository, migration, JSON Schema, OpenAPI, or
  generated-client changes.
- Import, upload, cloud sync, object storage, background jobs, combined learner-
  record export, Portfolio/Project content, target content, artifact bytes,
  permission/session/replay fields, credentials, or provider payloads.
- Physical erasure, retention, backup creation, restore, recovery-copy deletion,
  RPO/RTO, managed-cloud policy, or the JIT-D recovery exercise.
- Browser local persistence, service workers, native file-system APIs, archive
  formats, signing, encryption, or download-history retention.
- New icons, tokens, feature-local theme values, unrelated styling, or optional
  visual polish that does not affect function or accessibility.
- AI authority, autonomous action, personalized financial advice, external
  action, collaboration, organizations, or tenancy.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Browser model/API | generated export types, response guards, session retry | Personal-workspace model and API adapter | Closed export and quota outcomes |
| Browser composition | router dependency injection and route state | Router and Personal-workspace route/page | Explicit accessible download flow |
| Presentation | existing Saved learning classes and semantic tokens | Personal-workspace stylesheet only if required | State/status layout without new primitives |
| Verification | model, component, mocked Chromium suites | Listed Personal-workspace tests | Denial, parity, download, accessibility, anti-rigidity |
| Documentation/planning | web/module/architecture/assurance/slice/packet/register | Listed Markdown artifacts | Exact behavior and remaining JIT-D gap |

No path outside `write_scope` may change. If delivery needs an API, generated
artifact, executable contract, persistence, live-runner, design-system, or
another feature boundary, stop and reassess the packet.

## Contracts and Interfaces

Define a browser adapter equivalent to:

```text
exportPersonalWorkspace(expectedRevision, expectedDigest)
  -> ready(validated JSON, safe filename, export facts)
   | unauthorized | forbidden | changed | invalid-response
   | unavailable | unexpected
```

The adapter calls the bodyless, queryless generated GET. A successful response
must close exactly over `schema_version`, `workspace_digest`, `generated_at`,
and `workspace`; pass the existing workspace response guard; use the accepted
export schema and canonical timestamp profiles; bind inner and outer digest;
and match the displayed workspace revision and digest. Browser code may
serialize the accepted response but may not recompute or replace server facts.

Extend the existing mutation action vocabulary with exact browser meanings for
the three capacity codes. Copy explains the accepted 200-item, 50-collection,
and 100-items-per-collection limits and recommends removal or reorganization
without exposing learner content, hidden counts, storage facts, or internals.

## Dependencies and Parallel Safety

WRK-0144 is complete and fixes the only public export/quota API consumed here.
This packet owns shared Personal-workspace browser, test, and documentation
surfaces and is not parallel-safe with another SLI-0073 packet. It must complete
before JIT-D changes the live cumulative qualification and closes the slice.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact download | Current displayed workspace and matching export | Learner chooses Download saved learning | One UTF-8 JSON file contains the exact validated response; filename leaks no learner/workspace ID | unit/component/browser |
| Server authority | Any browser caller | Export runs | Generated GET has no body/query and browser supplies no learner/time/digest/storage authority | API/browser contract |
| Changed workspace | Export revision or digest differs from displayed workspace | Response arrives | No file is created; learner is told to refresh first | unit/component/browser |
| Closed response | Missing, extra, malformed, noncanonical, mismatched, or private-shaped export | Response arrives | No partial data/download is exposed; bounded invalid-response guidance appears | parameterized unit/component |
| Session/permission | Missing, expired, malformed, or denied session | Export is requested | One bounded renewal is attempted only for 401; otherwise no download and plain private-access guidance | unit/browser |
| Empty and varied | Empty, sparse, reordered, Unicode, optional-label, and mixed-reference workspaces | Export is requested | The same invariants accept the complete server view without fixture-specific branches | parameterized unit/browser |
| Record capacity | API returns `record_limit` | A mutation is refused | Guidance says 200 items and offers removal; existing saved work and controls remain | component/browser |
| Collection capacity | API returns `collection_limit` | A mutation is refused | Guidance says 50 collections and offers collection removal; records remain usable | component/browser |
| Member capacity | API returns `collection_member_limit` | Membership is refused | Guidance says 100 items and recommends removal/reorganization without replacing membership | component/browser |
| Retry and removal | An uncertain mutation or any quota refusal is visible | Learner reviews the page | Exact retry remains available only for unchanged prepared requests; removal controls are not blocked | component/browser |
| Accessible status | Export is pending, ready, changed, denied, or invalid | State changes | Control has an accessible name/state; status is announced and exact facts remain in Technical record | component/Chromium |
| Target isolation | Mixed Curriculum/Project references are exported | Download completes | No owner call, target mutation, artifact download, or executable action is added | architecture/browser |

## Verification Commands

Run focused Personal-workspace model and component tests; focused Chromium
Saved learning tests including download assertions; TypeScript typecheck;
zero-warning web lint and static build; generated-client currency; learner-
language, design-system, security, documentation, planning, and whitespace
checks; controller-selected exact-candidate affected verification; independent
technical review; and `python dev-tools/agent/check_ready.py`. No disposable
database or full live browser journey is required here because JIT-D owns the
cumulative community-profile and recovery qualification.

## Documentation and Evidence Update

Record the explicit learner action, bodyless generated-client call, response
closure and current-workspace binding, safe filename/content, exact capacity
guidance, retry/removal continuity, authorization/privacy/target isolation,
accessibility, responsive light/dark behavior, focused checks, assumptions,
and remaining JIT-D live-recovery work. Keep approval and review evidence only
in ignored local control-plane storage.

## Stop Conditions

Stop for a new or changed API/contract; download of target content or artifact
bytes; import/upload/cloud sync; caller-owned learner/time/digest/storage facts;
browser persistence; automatic/background export; another module's data or
mutation; recovery/retention/erasure policy; managed-cloud claim; new design
primitive; inaccessible control; active write collision; stale CAP package;
conflicting canonical authority; or material CAP-0017/SLI-0073 drift.

Do not stop for harmless whitespace, optional wording, incidental fixture
order/count, or nonfunctional styling. Fix bounded in-scope issues locally or
defer optional polish without a new approval or review loop.

## Required Handoff

Report `CAP-0017.SLI-0073.WRK-0145`; exact candidate and qualifying receipt;
generated-client operation and response guard; server-authority/current-state
binding; downloaded content and safe filename; exact capacity guidance;
removal/retry continuity; authorization/privacy/target-isolation evidence;
accessibility and anti-rigidity results; focused, affected, web, and aggregate
checks; documentation impact; assumptions; and the remaining JIT-D live-
recovery and slice-closure work.

## Planning History

- 2026-10-17: Authored just in time after WRK-0144 completed. The packet reuses
  the reviewed generated export operation and established Project download
  composition while retaining Personal-workspace server authority. It adds no
  API, generated artifact, persistence, browser storage, import, or recovery
  policy and requires no lower-level approval within approved CAP-0017.
- 2026-10-17: Validated the bounded browser-only packet with resolved decisions,
  a completed WRK-0144 dependency, executable checks, and no active scope
  collision; advanced it to ready without changing the approved CAP package.
- 2026-10-17: Activated from the recorded base after confirming the current CAP
  binding, completed dependency, exact bounded scope, resolved decisions, and
  no active coordination collision.
- 2026-10-17: Implemented the explicit generated-client export flow with deep
  closed-response and displayed-workspace binding, a stable ID-free JSON
  download, accessible technical facts and recovery states, and distinct
  capacity guidance that leaves removal controls available. Focused model and
  component tests passed 102 checks, focused Chromium passed 19 journeys, and
  type, lint, build, learner-language, design, documentation, planning, and
  whitespace checks passed before exact-candidate verification.
