---
id: SLI-0071
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: CAP-0017
depends_on: ["CAP-0007", "SLI-0070"]
decision_gates: []
---

# Vertical Slice: Organize Project Workspaces, Snapshots, and Inert Resources

## Outcome and User Scenario

An authorized learner saves typed references to an existing Project workspace,
one of its immutable snapshots, or an inert Project resource manifest in the
Personal workspace, organizes those references with the existing learner-owned
notes, bookmarks, and collections, and safely resumes them after interruption.
Project remains authoritative for access and content, while the Personal
workspace retains only bounded safe reference facts and never renders,
downloads, expands, or executes the referenced resource.

The same protected public API supports the generated browser client and
non-browser callers. Saving a reference grants no Project permission and adds
no browser-only or AI-specific authority.

## Scope Boundaries

### In Scope

- Extend the closed Personal-workspace reference union additively for a Project
  workspace, immutable Project snapshot, and inert Project resource manifest.
- Resolve every Project reference through Project public operations and a
  Personal-workspace-owned adapter. No Personal-workspace code may import
  Project internals or read Project tables or object storage directly.
- Retain only safe organization facts: stable Project/reference identity,
  reference kind, learner-safe title and lifecycle, exact Project/workspace
  revision when applicable, immutable snapshot digest and close time when
  applicable, inert manifest kind/version/digest/byte count when applicable,
  bounded provenance, last validation time, route, and availability meaning.
- Reuse the existing learner-owned note, bookmark, collection, membership,
  ordering, archive, restore, remove, revision, idempotency, quota, and
  persistence behavior without transferring target ownership.
- Add contextual `Save to Saved learning` entry points on authorized Project
  workspace, snapshot, and resource surfaces while keeping exact identifiers
  out of ordinary learner input.
- Revalidate Project access on target resolution and ordinary reopen. Missing,
  stale, removed, or unauthorized targets fail closed without protected detail
  and without blocking unrelated saved records.
- Expose the additive reference kinds through the reviewed OpenAPI snapshot and
  generated TypeScript client for browser, command-line, service, and future
  headless-AI clients under the same protected API and deterministic policy.
- Prove restart durability, idempotency, concurrency, target isolation,
  authorization, inert handling, safe technical records, and exact cleanup.
- Include anti-rigidity coverage for multiple Projects, revisions, snapshots,
  manifest kinds and sizes, variable safe titles, optional safe metadata,
  absent optional adapters, unavailable individual targets, and additive
  compatible technical fields.

### Out of Scope

- Copying a Project shell, mutable workspace document, note or source content,
  snapshot material, artifact bytes, download URL, permission, or Project event
  into the Personal workspace.
- Opening artifact bytes through the Personal-workspace boundary, active
  previews, browser execution, code or notebook execution, archive expansion,
  provider callbacks, network retrieval, package installation, credentials,
  secrets, or external durable action.
- Creating, editing, snapshotting, submitting, archiving, deleting, exporting,
  or downloading Project-owned state from the Personal workspace. Existing
  Project public surfaces remain the owners of those operations.
- Portfolio links, charts, experiments, AI conversations, arbitrary URLs,
  external-drive resources, cross-domain search, or stale-reference maintenance
  beyond Project; those remain SLI-0072 or later owning capabilities.
- Collaboration, instructor or organization access, sharing, publication,
  managed-cloud retention, multi-tenant policy, or a separate autonomous AI
  mode.
- Treating a saved reference as learning evidence, completion, assessment,
  competency, mastery, enrollment, approval, financial advice, or investment
  suitability.
- Styling-only polish that does not impair meaning, accessibility, responsive
  use, or theme parity; optional polish remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0017](../capabilities/CAP-0017-maintain-personal-learning-workspace.md)
  defines Project references as the second manifest increment after the base
  Personal workspace.
- [CAP-0007](../capabilities/CAP-0007-complete-applied-projects.md) and
  [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) keep Project
  authoritative for the shell, mutable workspace, inert resources, immutable
  snapshots, and their public operations.
- [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md) allows
  the Personal workspace to own learner organization and typed references but
  not target state, permissions, or execution.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) requires
  Project resources to remain passive, untrusted data outside an execution
  environment.
- [Project Workspace Contract](../../architecture/contracts/project-workspace-contract.md),
  [Personal Workspace Contract](../../architecture/contracts/personal-workspace-contract.md),
  [Module Map](../../architecture/modules/module-map.md), and
  [Decision Readiness](../../adr/decision-readiness.md) require public-only
  resolution, module-owned persistence, generated clients, and server-owned
  authorization.
- [Interface Design System](../../design/README.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern the learner-facing flow without freezing incidental prose or styling.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Add the complete Project-reference union, public Project resolver, persistence/API/client support, contextual save and organization flow, and live inert-resource qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add only Project workspace and snapshot references and defer inert resource manifests | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Copy Project workspace, snapshot, or artifact state into Personal-workspace storage | no - it transfers target authority and violates ADR-0012 and ADR-0021 | - | - | - | - | - | - | - |
| D. Let the Personal workspace preview, download, or execute Project artifacts | no - it violates the accepted inert boundary and requires new execution authority | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it is the smallest complete implementation of
the enumerated SLI-0071 outcome. It adds all three already accepted Project
reference families through one reusable target-adapter boundary, preserves the
existing Personal-workspace organization model, and produces observable value
through browser and headless callers without inventing a second authority.

Candidate B is independently deliverable but leaves the approved inert-resource
manifest outcome incomplete. Candidate C creates duplicate mutable and immutable
truth. Candidate D turns organization into execution and crosses an unresolved
platform boundary. Candidate A wins without a tie-break and conforms to the
current CAP-0017 manifest.

## Boundary Path

1. Project exposes or reuses one public safe-reference operation that accepts a
   typed Project target selector and derives learner identity and permission
   only from server-owned context.
2. A Personal-workspace Project adapter maps the public result into the closed
   Project-reference union. It passes no target content, bytes, raw storage
   locator, private source, hidden authorization fact, or provider payload.
3. Personal workspace validates the resolved reference and applies the existing
   note, bookmark, collection, ordering, archive, restore, remove, revision,
   idempotency, and quota policies without mutating Project.
4. Personal-workspace-owned PostgreSQL stores the bounded reference document
   atomically with its learner-owned record. No cross-module foreign key or
   direct Project persistence access is introduced.
5. Protected API models publish the additive variants through the reviewed
   OpenAPI snapshot and generated TypeScript client. Revalidation and reopen
   preserve safe unavailable/denied meaning without leaking target existence.
6. Authorized Project surfaces create exact typed save intents, and the
   generated client powers their organization in `Saved learning`. Technical
   facts stay under an accessible disclosure; Project owns any later open,
   download, export, mutation, or submission action.
7. Focused and isolated live qualification proves browser/headless parity,
   exact Project correlation, persistence restart, denial, missing-target
   isolation, inert behavior, unrelated-domain non-mutation, and cleanup.

## Contracts, Data, and Provenance

Extend `personal-workspace/v1` additively with closed discriminated Project
reference variants. A Project-workspace reference retains a stable Project and
workspace identity, safe title and lifecycle, current Project/workspace
revision, route, bounded origin/provenance, validation time, and one bounded
availability. A snapshot reference additionally binds the immutable snapshot
identity, exact workspace revision, digest, and close time. An inert resource
reference binds the Project, resource/artifact identity, manifest version,
bounded kind and media classification, logical safe label, digest, byte count,
and immutable snapshot identity when the Project manifest is snapshot-bound.

The exact schema is closed and versioned. It excludes artifact bytes, note or
source bodies, archive contents, object-store keys, local paths, pre-signed
URLs, credentials, secrets, private provider metadata, raw authorization
claims, and learner-selected owner identity. Public Project operations remain
the only source of target meaning.

Existing Personal-workspace mutation and document semantics continue unchanged:
one server-owned learner workspace, positive revision, idempotent accepted
mutations, canonical times, deterministic digest, ordered records and
collections, and no target mutation on archive/remove. A target becoming
unavailable changes only validated reference meaning; it does not delete the
learner's note, collection membership, or immutable saved technical facts.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Save Project workspace | An authorized learner saves and reopens a note or bookmark tied to the exact Project/workspace identity and revision through public Project resolution | contract/application/API/browser/live |
| Save immutable snapshot | The learner saves and reopens the exact snapshot identity, workspace revision, digest, and close time without copying snapshot material | contract/application/PostgreSQL/API/browser |
| Save inert resource | The learner organizes safe manifest facts for an inert resource without receiving bytes, a storage locator, an active preview, or an execution action | contract/security/API/browser/live |
| Organize mixed references | Learning-resource and Project-reference records coexist in multiple ordered collections and survive reorder, archive, restore, remove, and restart | domain/PostgreSQL/API/browser/live |
| Headless parity | A supported non-browser HTTP caller reads and writes the same Project references through the same protected policy and contract as the browser | API/live qualification |
| Authorization revalidation | A guessed, cross-learner, removed, or newly unauthorized Project target fails closed without confirming protected existence or granting access | Project public operation/gateway/API/security |
| Missing optional target | One unavailable Project, snapshot, resource, or adapter affects only its typed reference; unrelated saved records and operations remain usable | application/API/browser anti-rigidity |
| No target mutation | Saving, organizing, archiving, or removing a reference leaves Project shell, workspace, snapshot, artifact, Assessment, and Learner-model state unchanged | application/PostgreSQL/live containment |
| No execution | Artifact bytes are never fetched through Personal workspace and no render, archive, network, package, subprocess, or execution seam is reachable | architecture/security/live containment |
| Exact retry and stale write | Exact replay returns the accepted workspace; changed-key reuse and stale revisions fail without duplicate reference or target mutation | domain/PostgreSQL/API/live |
| Flexible valid shapes | Multiple Project origins, lifecycle values, revisions, snapshots, manifest kinds/sizes, optional safe fields, and generated IDs/times remain valid without fixture-count or presentation lock-in | contract/domain/UI anti-rigidity |
| Accessible resume | Contextual save controls, status, errors, technical records, keyboard/focus order, reflow, forced colors, reduced motion, and light/dark/system themes preserve equivalent meaning and actions | component/Chromium/design |
| Restart and cleanup | Saved Project references survive normal application restart and qualification removes only its isolated topology and ignored artifacts | PostgreSQL/live runner |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0135 | Freeze additive Project-reference contracts, reuse Project public reads through a Personal-workspace Project adapter, and prove pure core and anti-rigidity behavior | SLI-0070, CAP-0007 | none | complete |
| WRK-0136 | Deliver Personal-workspace persistence/API/OpenAPI/generated-client support and authorization revalidation for all Project reference variants | WRK-0135 | none | complete |
| WRK-0137 | Deliver contextual Project save entry points and mixed-reference organization/resume behavior through the generated client | WRK-0136 | none | ready |
| JIT-D | Qualify browser/headless parity, exact Project/PostgreSQL correlation, restart, denial, containment, inert behavior, cleanup, and slice closure | JIT-C | none | captured |

Exact `WRK-*` identifiers replace these seam labels as each bounded packet is
authored. Dependent packets are not claimed until their predecessor is complete.

## Verification and Qualification

Run JSON-schema and compatibility fixtures; Project public-operation and
Personal-workspace domain/application/gateway tests; real-PostgreSQL migration,
atomicity, replay, conflict, restart, and isolation tests; protected API success
and denial tests; reviewed OpenAPI and generated-client reproduction; web
model/component tests; focused mocked and isolated live Chromium; and one
non-browser public-API observation.

Run architecture/import and persistence-ownership checks, inert-artifact and
security checks, learner-language and design-system checks, documentation and
planning checks, whitespace, typecheck, zero-warning lint, build, affected
verification, independent technical review, completion structure, and
`python dev-tools/agent/check_ready.py`. Every packet includes focused
anti-rigidity evidence appropriate to its layer; incidental whitespace,
wording, style, fixture count, ordering, or optional adapter absence must not
create a re-review loop.

## Rollback and Migration

Contract additions and any data changes are additive and versioned. Existing
learning-reference documents remain byte-compatible, and existing workspaces
need no eager rewrite. If a new persistence representation is required, its
migration must have forward, reapply, development-down, retained-data refusal,
and real-PostgreSQL evidence.

A code rollback may remove unreferenced Project save entry points and their
adapter, but it cannot silently reinterpret or delete accepted saved records.
Unknown later reference variants continue to fail closed under versioned
contract governance. Isolated qualification data may be deleted only from its
exact disposable topology.

## Stop Conditions

Stop for Project or Personal-workspace ownership transfer; direct cross-module
persistence access; a reference granting permission; copied workspace,
snapshot, resource, or artifact content; active rendering, download, archive
expansion, network, package, secret, provider, or execution behavior; live
Portfolio integration before its public contract is accepted; Assessment or
Learner-model mutation; AI-authoritative durable writes; managed-cloud or
multi-tenant policy; breaking contract change; destructive migration; private
data leakage; stale CAP package; active write collision; or material CAP-0017
drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery updates the Personal-workspace and Project public contract guidance,
module map, protected API/OpenAPI and generated-client documentation, browser
Saved Learning/Project behavior, local operation, architecture assurance,
security/containment evidence, known gaps, planning artifacts, and the register.

Completion must identify exact packet candidates and receipts, focused and
cumulative check results, independent review outcome, browser/headless/restart
evidence, unchanged unrelated-domain observations, anti-rigidity coverage,
migration/rollback evidence where applicable, assumptions, known gaps, and any
decision still requiring approval. No lower-level completion approval exists.

## Planning History

- 2026-10-17: Refined the second CAP-0017 manifest increment after completion
  of SLI-0070 and CAP-0007. Candidate A scores 14/14 and adds all accepted
  Project reference kinds through public operations and a reusable adapter
  while preserving target ownership and inert behavior. The refinement
  conforms to the current CAP package and needs no slice-level approval.
- 2026-10-17: Refined JIT-A as WRK-0135 around the additive Project-reference
  union, reuse of existing learner-bound Project public reads, one reusable
  Personal-workspace adapter, pure contract behavior, and anti-rigidity
  evidence. Persistence, API, generated-client, browser, and live behavior
  remain outside the packet.
- 2026-10-17: Activated WRK-0135 from the recorded base revision after
  validating current CAP authority, completed dependencies, resolved decision
  posture, the exact public-only write scope, and no active collision.
- 2026-10-17: Returned WRK-0135 to ready before product edits so its exact scope
  also includes the workspace and mutation-intent schemas that embed the
  reference union. The bounded correction does not change slice meaning.
- 2026-10-17: Re-activated WRK-0135 from the fresh recorded base with all three
  reference-bearing schemas inside the exact scope and no active collision.
- 2026-10-17: Completed WRK-0135 at exact candidate `d97d405` after the closed
  Project reference union, public-only adapter, path and chronology boundaries,
  confidentiality, anti-rigidity, and required repository checks all passed.
  The persistence/API packet may now start without changing slice meaning.
- 2026-10-17: Refined JIT-B as WRK-0136 around server-owned learner propagation,
  closed Curriculum/Project dispatch, existing JSON persistence compatibility,
  Project read authorization, and one reviewed OpenAPI/generated-client seam.
  Browser behavior and live qualification remain in JIT-C and JIT-D.
- 2026-10-17: Activated WRK-0136 from the recorded base after confirming the
  completed WRK-0135 dependency, exact API/generated-artifact scope, current CAP
  authority, resolved decision posture, and no active write collision.
- 2026-10-17: Moved WRK-0136 to verification after the closed Project dispatcher,
  API/generated client, PostgreSQL compatibility, and exhaustive safe-reference
  display passed focused checks. Independent disposition remains required.
- 2026-10-17: Returned WRK-0136 to active delivery for bounded corrections to
  the browser's closed Project-reference response guard and optional owner-
  adapter behavior. The correction preserves the approved slice outcome,
  public API, authority model, and packet boundaries.
- 2026-10-17: Returned WRK-0136 to verification after its real browser
  response boundary accepted each closed Project variant, rejected malformed
  or private facts, and optional owner adapters failed in isolation.
- 2026-10-17: Completed WRK-0136 at exact reviewed implementation candidate
  `8570856` after focused backend, API, browser, contract, architecture,
  security, affected, aggregate, and independent technical verification passed.
  The contextual Project save-control packet may now start.
- 2026-10-17: Refined JIT-C as WRK-0137 around exact contextual Project links,
  a closed extension of the existing Saved Learning selection/action flow,
  mixed-reference organization, and focused mocked-browser evidence. The
  protected API and generated client remain unchanged; live topology evidence
  remains in JIT-D.
- 2026-10-17: Activated WRK-0137 from the recorded base after confirming the
  completed WRK-0136 dependency, current CAP authority, closed browser-consumer
  scope, required design/language context, and no active file collision.
- 2026-10-17: Returned WRK-0137 to ready before product edits so its start
  manifest can bind the added shared failure-route scope. Product meaning and
  the approved slice outcome are unchanged.
