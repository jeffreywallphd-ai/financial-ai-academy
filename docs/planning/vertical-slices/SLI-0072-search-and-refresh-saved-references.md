---
id: SLI-0072
kind: vertical-slice
planning_status: complete
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: CAP-0017
depends_on: ["SLI-0071"]
decision_gates: []
---

# Vertical Slice: Search and Refresh Saved References

## Outcome and User Scenario

A learner can search and filter Saved learning through the protected public API,
see whether each retained Curriculum or Project reference is current, stale, or
unavailable, and explicitly check one reference without losing notes,
collections, order, provenance, or access to unrelated saved work.

Search reads the learner-owned index and never depends on a source adapter.
Checking a link calls only its owning module's learner-bound public operation.
Removed, inaccessible, unavailable, and unsupported targets collapse to one
confidential unavailable state, while an unavailable optional adapter affects
only the selected reference. Browser and headless clients use the same contract
and deterministic policy.

## Scope Boundaries

### In Scope

- Add a bounded, deterministic Personal-workspace record query over learner
  title/body/label and retained safe target facts, with closed filters for
  record kind, owner module, reference kind, target status, archive state, and
  collection membership.
- Provide stable sorts, record-ID tie-breaking, a bounded page size, and an
  opaque cursor or equivalent continuation that cannot escape the current
  learner workspace or silently switch query meaning.
- Add an explicit, idempotent `refresh_reference` mutation that accepts only a
  workspace-owned record ID. The server derives the exact retained selector,
  learner identity, owner adapter, validation time, and status transition.
- Extend the closed reference status with `stale` and `unavailable`. Retain the
  previously accepted safe facts and provenance, but disable the source-resume
  action unless a fresh public-owner result proves the exact reference current.
- Treat mutable Project-workspace metadata as refreshable safe facts. Treat a
  changed Curriculum publication/package identity or changed immutable Project
  snapshot/artifact identity or digest as stale without silently advancing the
  saved reference.
- Collapse missing, removed, denied, adapter-absent, and source-unavailable
  outcomes to the same public unavailable meaning. Do not expose which private
  condition occurred.
- Allow a later successful check to restore `available` only when the exact
  retained immutable identity still matches. Preserve ordinary revision,
  idempotency, replay, optimistic-concurrency, quota, and atomic persistence
  behavior.
- Expose query and refresh through reviewed OpenAPI and the generated
  TypeScript client so browser, command-line, service, and future headless-AI
  consumers share one API and authority model.
- Add learner-facing search, filters, status and refresh controls in plain
  language with keyboard, focus, reflow, forced-color, reduced-motion, and
  light/dark/system parity.
- Include failure and anti-rigidity coverage for empty and full workspaces,
  mixed source and record kinds, Unicode learner text, varied ordering, absent
  adapters, one broken source among healthy sources, stale cursors, stale
  workspace revisions, exact replay, recovery, and harmless additive fields.

### Out of Scope

- A live Portfolio, Market data, Experiment, Assessment, Learner-model, AI
  conversation, chart, or other new domain adapter before its owning public
  contract and capability are accepted.
- Background polling, repository-wide lockstep events, a cross-domain database
  join, direct reads of another module's tables or object storage, or a search
  service dependency.
- Copying target content, silently advancing an immutable source version,
  deleting historical learner notes because a target disappears, or revealing
  whether a target exists for another learner.
- Browser-only search or status truth, caller-supplied learner identity,
  caller-supplied target status, arbitrary query fields, or a separate AI API.
- Artifact preview, download, archive expansion, network retrieval, package
  installation, subprocess execution, collaboration, publication, cloud sync,
  organization policy, portfolio calculation, financial advice, or external
  action.
- Workspace export/delete-request, backup/recovery qualification, and complete
  interruption/quota qualification, which remain in SLI-0073.
- Styling-only polish beyond functional, accessible use; optional visual polish
  remains CAP-0031 work unless the user requests it earlier.

## Canonical Context and Decisions

- [CAP-0017](../capabilities/CAP-0017-maintain-personal-learning-workspace.md)
- [SLI-0071](SLI-0071-organize-project-workspaces-snapshots-resources.md)
- [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md)
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md)
- [Personal Workspace Contract](../../architecture/contracts/personal-workspace-contract.md)
- [Personal Workspace Module](../../../backend/src/financial_ai_academy/modules/personal_workspace/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)

ADR-0021 keeps learner-authored organization in Personal workspace and target
meaning and permission in each owning module. Existing Curriculum and Project
public operations are sufficient for this increment. No provider, tenancy,
model-authority, execution, managed-cloud, or external-action decision is open.
Later source adapters remain optional and separately gated by their owning
capabilities.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. API query plus explicit per-record public-owner refresh for current Curriculum and Project references | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add Portfolio and other future domain adapters while delivering search and stale handling | no | 2 | 1 | 0 | 0 | 0 | 1 | 1 | 5 |
| C. Subscribe Personal workspace to repository-wide target lifecycle events and refresh every reference automatically | yes | 2 | 2 | 2 | 1 | 0 | 1 | 1 | 9 |
| D. Implement browser-only local search and infer status when a learner follows a link | yes | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 10 |

## Selection Rationale

Candidate A wins without a tie-break. It provides the complete learner outcome
through one browser/headless API, uses current accepted owner contracts, keeps
source failures isolated to one explicit action, and is independently
verifiable and reversible. Candidate B is ineligible because unimplemented
owners do not yet provide accepted public contracts and a live adapter would
cross their capability gates. Candidate C couples Personal workspace to every
producer and makes an optional source outage a background coordination problem.
Candidate D is easy to reverse but would create browser-only behavior and no
durable, queryable reference status for headless clients.

The refinement preserves CAP-0017's SLI-0072 outcome, dependency, and material-
change boundary. It neither adds a slice nor requires renewed CAP approval.

## Boundary Path

1. A caller with Personal-workspace read authority submits one closed query.
   The host derives learner identity and rejects unknown, duplicated, malformed,
   or over-broad fields before workspace access.
2. Personal workspace reads only its own bounded aggregate and applies pure
   normalized search, filter, stable sort, and continuation policy. Querying
   never calls Curriculum, Project, a provider, or a search service.
3. The API returns bounded record projections plus the workspace revision,
   applied query meaning, and optional continuation. Every result remains part
   of the current learner's workspace and retains source/provenance facts.
4. An explicit refresh request carries only record ID, expected workspace
   revision, idempotency key, and schema version. The application derives the
   existing typed selector from the retained reference.
5. The closed owner gateway calls Curriculum or Project through learner-bound
   public operations. No owner persistence, object storage, artifact bytes,
   private authorization fact, or provider payload crosses the boundary.
6. Exact current meaning refreshes safe mutable facts and status. Changed
   immutable meaning records `stale`; denied, missing, removed, unavailable, or
   absent-adapter outcomes record `unavailable`. The mutation never changes or
   deletes another module's aggregate.
7. PostgreSQL atomically persists the updated learner aggregate and replay
   evidence. The reviewed OpenAPI/generated client exposes the same operation
   to the browser and headless clients.
8. Saved learning renders query results and status in plain language. Only an
   `available` result exposes the owner route; stale or unavailable records
   retain learner notes and organization plus safe recovery actions.

## Contracts, Data, and Provenance

Add a versioned query request/result contract rather than overloading arbitrary
URL parameters. The request is closed over normalized text, zero or more closed
enum filters, stable sort, bounded page size, and an opaque continuation bound
to learner, workspace revision, and normalized query digest. Invalid, changed,
expired, cross-learner, or stale continuations fail generically without partial
or old results. An empty query remains a valid bounded listing.

Extend each accepted reference with exactly three public status meanings:
`available`, `stale`, and `unavailable`. `validated_at` records the last explicit
owner check. The workspace retains the last accepted safe source facts and
provenance for history; a non-available status suppresses the actionable source
destination in projections and UI without erasing the historical destination
from the versioned stored record. This is learner-owned reference history, not
new permission or copied target content.

`refresh_reference` is a server-enriched mutation. The caller cannot select an
owner, selector, status, timestamp, replacement identity, title, digest,
destination, provenance, or learner. Exact replay returns the accepted result;
changed-key reuse, stale revision, removed record, malformed retained selector,
integrity failure, or unavailable Personal-workspace storage fails with the
existing bounded error contract.

The current owner gateway remains a closed platform-owned dispatcher with
optional adapters. Each later domain must add a typed selector/reference pair
and one owner adapter under its own accepted contract; absence never prevents
queries, mutations on unrelated records, or Personal-workspace startup.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Search learner-owned text | Normalized text matches note titles/bodies, bookmark labels, and retained safe target labels without searching private source content | contract/domain/API/browser |
| Filter mixed records | Closed record/source/reference/status/archive/collection filters compose predictably across Curriculum and Project records | domain/API/browser |
| Stable pages | Sort and record-ID tie-breakers produce deterministic pages; a cursor cannot change learner, revision, or query meaning | contract/application/API |
| Headless parity | A non-browser client performs the same query and refresh through the reviewed protected API as the browser | API/live |
| Current mutable workspace | Refreshing an accessible Project workspace updates bounded safe mutable facts and remains available without changing Project | application/PostgreSQL/API |
| Changed immutable source | A changed package, snapshot, artifact identity, version, or digest marks the retained reference stale and does not silently advance it | contract/application/security |
| Confidential source failure | Missing, removed, denied, unavailable, and absent-adapter cases produce the same unavailable meaning and disclose no target existence or permission facts | gateway/API/security |
| Recovery after outage | A later exact owner result returns an unavailable reference to available while preserving learner note, membership, order, and provenance | domain/PostgreSQL/API |
| Isolated failure | One unavailable source or adapter does not block search, unrelated records, collections, ordinary mutations, or another owner | application/API/browser |
| Exact retry and conflict | Exact refresh replay is stable; changed-key reuse and stale workspace revision do not duplicate or overwrite state | domain/PostgreSQL/API |
| Safe resume | Only available results expose their canonical owner action; stale/unavailable records retain plain-language context and learner-owned organization | component/browser/accessibility |
| Anti-rigidity | Empty/full workspaces, varied Unicode text, mixed kinds, optional fields, counts, order, and additive safe result fields preserve invariants | property/parameterized/browser |

## Agent Work Packets

Packet IDs are reserved and authored one at a time immediately before each
packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0139 | Freeze query, continuation, status-transition, and refresh contracts plus pure search/status behavior and anti-rigidity evidence | SLI-0071 | none | complete |
| WRK-0140 | Deliver owner refresh orchestration, PostgreSQL/API/OpenAPI/generated-client support, replay/concurrency, and confidential optional-adapter isolation | WRK-0139 | none | complete |
| WRK-0141 | Deliver plain-language browser search, filters, status, per-record refresh, and accessible safe resume through the generated client | WRK-0140 | none | complete |
| WRK-0142 | Qualify browser/headless parity, deterministic pages, live refresh/recovery, PostgreSQL restart, containment, cleanup, and slice closure | WRK-0141 | none | complete |

Dependent packets are not claimed until their predecessor is complete. The
sequential default avoids shared contract/client/API/UI collisions; a later
packet may declare independent test or documentation work parallel-safe only
after exact scopes prove no overlap.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; pure query normalization/filter/
sort/cursor/status tests; Curriculum and Project gateway success, changed-
meaning, denial, missing, adapter-absent, and recovery tests; Personal-workspace
domain/application/PostgreSQL replay, stale-revision, isolation, restart, and
integrity tests; protected API and authorization tests; reviewed OpenAPI and
generated-client reproduction; TypeScript query/response boundary tests; web
unit/component and focused Chromium tests; and one isolated live browser plus
ordinary headless HTTP journey.

Run architecture/import and persistence-ownership checks, private-field and
inert-resource containment checks, learner-language and design-system checks,
documentation and planning checks, whitespace, typecheck, zero-warning lint,
build, exact-candidate affected verification, independent technical review,
completion structure, and `python dev-tools/agent/check_ready.py`. Failure and
anti-rigidity evidence must prove that incidental count/order/copy/style and an
absent optional adapter do not create a full-workspace or re-review barrier.

## Rollback and Migration

Contract changes are additive within the versioned family. Existing
`available` documents remain valid without eager rewrite. If persisted status
or query support requires a migration, prove forward, reapply, development-
down, retained-data refusal, and real-PostgreSQL behavior; prefer the existing
JSON aggregate so no table-level source coupling is introduced.

A code rollback may remove query and refresh entry points only while preserving
accepted workspace documents and replay safety. It must not reinterpret stale
or unavailable records as current or erase learner notes. Unknown later source
types and statuses continue to fail closed.

## Stop Conditions

Stop for a new live domain adapter without an accepted owner contract; source
permission or ownership transfer; direct cross-module persistence or object-
storage access; query across other learners; caller-controlled status, owner,
selector, timestamp, provenance, or destination; silent immutable-version
advance; source content copying; target mutation; differentiated missing versus
unauthorized disclosure; background repository-wide coupling; a search-service
dependency; artifact content/download/preview/execution; destructive migration;
managed-cloud/tenancy/provider/model/legal decision; active scope collision;
stale CAP approval; conflicting canonical authority; or material CAP drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery updated the Personal-workspace contract and module guidance, protected
API and generated-client documentation, Saved Learning UI guidance, local
operations, security and architecture assurance, known gaps, packet artifacts,
this slice, and the planning register.

### Completion Evidence

- WRK-0139 through WRK-0142 are complete in dependency order. Together they
  deliver a closed query and result contract, signed continuation, exact
  three-state reference meaning, record-only source checks, public application
  and API orchestration, generated-client browser behavior, and cumulative
  local live qualification.
- The same protected public API serves browser and headless callers. Canonical
  query normalization and digests bind continuations to learner, workspace,
  revision, and query meaning; source checks derive owner authority on the
  server and cannot widen into target mutation or private-content access.
- WRK-0142's exact candidate
  `68b41ac08b7576f57d6cd3b2dfd73cabda2ab4a7` produced the qualifying local
  receipt at
  `.local-codex/control-plane/receipts/WRK-0142/68b41ac08b7576f57d6cd3b2dfd73cabda2ab4a7/20261017T163415Z-b3af415b-3fd1-4f37-8ef6-02ad7d038720.json`
  with digest
  `sha256:7b302fdd04c3dfd9b3f653b318f7718e512990ab7dcd2b92ee7db72e4fbe1775`.
- Focused replay qualification passed 52 tests. Architecture passed 17 tests,
  security passed 10 control groups, and the fixed aggregate readiness gate
  passed all 29 checks. The live topology passed ten core Chromium journeys
  plus Project workspace, Personal workspace, and Project-learning submission
  journeys against disposable PostgreSQL 18.4, then proved retained state
  after a normal application restart.
- Failure and anti-rigidity evidence covers changed query meaning or digest,
  malformed evidence, unowned results, widened refresh authority, stale
  revisions, changed-key replay, confidential unavailable sources, equivalent
  UTC precision, Unicode text, optional fields, and smaller, larger, or
  reordered canonical workspaces with real signed multi-page continuations.
- Privacy-safe schema-wide exact-row fingerprints prove that query and refresh
  do not change Assessment, Audit, Content, Curriculum, Learner-model, or
  Project facts. Exact Personal-workspace aggregate and mutation rows remain
  stable through headless replay and restart.
- Contract additions remain compatible, existing saved references need no
  eager rewrite, and no migration was required. Rollback may remove unused
  query or refresh entry points only while preserving accepted records,
  learner notes, and fail-closed stale or unavailable meaning.
- Managed cloud, backup and restore, production load, background refresh,
  later domain adapters, artifact activity, separate AI authority, provider
  integration, and financial action remain outside this slice. No unresolved
  durable decision is introduced by those explicit later boundaries.
- The completed packet set conforms to the approved CAP-0017 package without
  material drift. Approval records remain only in ignored local storage, and
  no slice, packet, implementation, or completion approval is required.

## Planning History

- 2026-10-17: Refined the third approved CAP-0017 manifest increment after
  SLI-0071 completed. Candidate A scores 14/14 and adds API-first deterministic
  search plus explicit per-record public-owner refresh for the currently
  accepted Curriculum and Project reference kinds. Future adapters remain
  optional and separately gated; the refinement conforms to the approved CAP
  package and requires no lower-level approval.
- 2026-10-17: Refined JIT-A as WRK-0139 around additive query/result,
  continuation, three-state reference, and server-enriched refresh contracts,
  pure deterministic search/status behavior, compatibility, confidentiality,
  and anti-rigidity evidence. Application, persistence, API/client, browser,
  and live behavior remain later packet seams.
- 2026-10-17: Activated WRK-0139 from the recorded base after confirming the
  current CAP approval, completed SLI-0071 dependency, exact pure-contract
  scope, resolved decision posture, and absence of a known write collision.
- 2026-10-17: Completed WRK-0139 with authenticated learner/workspace-bound
  continuations, deterministic query, exact stale/unavailable transitions, and
  field-by-field immutable-reference drift evidence; refined JIT-B as WRK-0140
  for application, persistence, protected API, OpenAPI, and generated-client
  delivery without expanding into browser or live-qualification work.
- 2026-10-17: Completed WRK-0140 with protected deterministic query and
  record-only refresh, server-derived owner authority, confidential optional-
  adapter isolation, PostgreSQL restart and exact-replay evidence, and one
  reviewed OpenAPI/generated-client contract shared by browser and headless
  consumers. JIT-C is dependency-ready for just-in-time refinement.
- 2026-10-17: Refined JIT-C as WRK-0141 after WRK-0140 completed. The packet
  consumes the reviewed query and record-only refresh operations for closed
  browser search/filter/paging, three-state meaning, explicit checks, safe
  resume, partial-reorder defense, accessibility, and anti-rigidity evidence.
  It changes no API or CAP boundary and requires no lower-level approval.
- 2026-10-17: Refined JIT-D as WRK-0142 after WRK-0141 completed. The packet
  adds cumulative live generated-browser/headless query and record-only refresh
  parity, PostgreSQL replay/restart, target isolation, containment, cleanup, and
  slice-closure evidence without changing delivered product behavior.
- 2026-10-17: WRK-0142 entered evidence verification after its cumulative live
  browser/headless qualification and focused checks passed. SLI-0072 then
  entered closure verification against the exact candidate and evidence.
- 2026-10-17: All four dependency-ordered packets completed and SLI-0072
  entered deterministic closure verification with cumulative contract,
  browser/headless, replay, restart, containment, and anti-rigidity evidence.
- 2026-10-17: Completed SLI-0072 after its packet set, cumulative evidence,
  documentation impact, compatibility posture, known boundaries, and approved
  CAP-package conformance passed the deterministic completion gate.
