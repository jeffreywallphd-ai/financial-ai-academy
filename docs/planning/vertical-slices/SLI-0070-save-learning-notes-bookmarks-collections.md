---
id: SLI-0070
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: CAP-0017
depends_on: []
decision_gates: []
---

# Vertical Slice: Save Learning Notes, Bookmarks, and Collections

## Outcome and User Scenario

An authorized learner saves a note or bookmark for an exact approved learning
resource, groups saved records into personal collections, and reopens the same
workspace after interruption with learner ownership, order, exact source
identity, version, provenance, and last validated availability intact. The
same protected public API serves the generated browser client and supported
non-browser clients; no browser-only or AI-specific authority is added.

## Scope Boundaries

### In Scope

- Introduce the focused Personal workspace module accepted by ADR-0021 as the
  owner of learner-authored notes, bookmarks, collections, membership/order,
  record lifecycle, and workspace revision.
- Define closed versioned Personal-workspace contracts for notes, bookmarks,
  collections, exact approved-learning references, mutation intents, and the
  learner's current workspace view.
- Resolve initial references only through Curriculum's public learning-
  opportunity and exact lesson-placement operations. Retain exact resource,
  placement, package, version, digest, title, route, provenance, validation
  time, and bounded availability meaning without copying lesson bodies or
  Curriculum aggregates.
- Provide deterministic open, create/update, collect/reorder, archive/restore,
  and remove operations with server-owned learner context, expected-revision
  concurrency, idempotent mutation, bounded quotas, and learner-safe errors.
- Persist one learner-owned Personal-workspace aggregate and accepted mutation
  replays in module-owned PostgreSQL tables without cross-module foreign keys
  or direct access to Content/Curriculum persistence.
- Expose protected API operations, reviewed OpenAPI, and generated TypeScript
  client behavior for browser, command-line, service, and future headless AI
  callers through the same authorization and mutation policy.
- Deliver an accessible responsive `Saved learning` browser flow that uses the
  generated client, leads with notes/bookmarks/collections, and keeps exact
  identifiers, versions, digests, and provenance under an accessible
  `Technical record` disclosure.
- Prove interruption, exact retry, changed-key conflict, stale revision,
  unavailable source, missing session/permission, cross-learner denial,
  persistence restart, quota, and partial-write behavior.
- Include anti-rigidity coverage for variable valid titles and note text,
  multiple collections and memberships, empty and non-empty workspaces,
  reordered records, additional compatible technical fields, generated IDs
  and timestamps, and nonfunctional presentation changes.

### Out of Scope

- Project workspaces, snapshots, artifact manifests, notebooks, datasets,
  files, results, Project-reference adapters, or Portfolio/domain resources;
  those begin in SLI-0071 and SLI-0072.
- A general arbitrary URL manager, browser-history capture, external-drive
  synchronization, imported bookmarks, semantic search, embeddings, or AI-
  generated notes.
- Enrollment, eligibility, recommendations, completion, assessment evidence,
  competency/mastery state, grades, instructor access, or curriculum mutation.
- Collaboration, sharing, public publishing, organizations, multi-tenant
  authorization, managed-cloud retention/recovery, or cross-device sync claims.
- Active rendering, file upload, archive expansion, code/notebook execution,
  provider callbacks, network fetches selected by learners, packages, secrets,
  credentials, or external notifications.
- A separate AI mode, agent protocol, autonomous durable mutation, model-
  selected resources, personalized financial advice, or live financial action.
- Styling-only polish that does not impair meaning, accessibility, responsive
  use, or theme parity; optional polish remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0017](../capabilities/CAP-0017-maintain-personal-learning-workspace.md)
  defines the four-slice outcome and this first learning-resource increment.
- [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md) assigns
  learner-authored notes, bookmarks, collections, and typed references to a
  focused Personal workspace module while target owners retain authority.
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) keeps Project
  project-scoped. This slice neither copies nor changes Project state.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) continues to
  deny execution. This slice introduces no artifact surface.
- [Module Map](../../architecture/modules/module-map.md),
  [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  and [Decision Readiness](../../adr/decision-readiness.md) require public
  operations, module-owned persistence, generated clients, and server-owned
  authorization.
- [Interface Design System](../../design/README.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern the learner-facing flow without freezing incidental prose or styling.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver closed learning-reference and workspace contracts through Personal-workspace core, PostgreSQL, protected API, generated client, and accessible save/resume browser flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Deliver contracts, core, persistence, and API but defer the learner-visible save/resume flow | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Store notes and bookmarks inside Project or Curriculum | no - it contradicts ADR-0021 and transfers learner organization to a target owner | - | - | - | - | - | - | - |
| D. Store the workspace only in browser local storage | no - it cannot provide protected API/headless parity, server-owned authorization, restart recovery, or durable export provenance | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it is the smallest complete SLI-0070 path:
the learner can save, organize, interrupt, and resume through the accepted new
module and the common protected API. The initial reference union is limited to
already implemented public learning-resource operations, so the slice has no
provider, tenancy, execution, licensing, or Project-adapter decision.

Candidate B is bounded but does not produce the approved learner-visible
increment. Candidate C violates accepted ownership. Candidate D creates a
browser-only authority and cannot satisfy durability, recovery, provenance, or
headless access. Candidate A wins without a tie-break and does not redefine any
later CAP-0017 slice.

## Boundary Path

1. Curriculum exposes or reuses public exact-resolution operations for an
   approved learning opportunity and placed lesson. The Personal workspace
   adapter maps only safe exact identity, version, digest, title, route,
   provenance, and availability facts.
2. Personal workspace validates a closed learning-reference union and accepts
   learner-authored note, bookmark, collection, membership, ordering, archive,
   and remove intents under one expected workspace revision and idempotency key.
3. Pure domain/application behavior assigns server-owned IDs and canonical UTC
   times, enforces bounds and reference closure, and produces one next workspace
   aggregate without mutating Curriculum, Content, Assessment, Learner model,
   or Project.
4. A Personal-workspace PostgreSQL adapter atomically persists the next
   aggregate and exact accepted replay evidence under learner ownership. It
   never queries another module's schema or creates cross-module foreign keys.
5. Protected API operations derive learner identity and permission only from
   the server session, map bounded errors, publish reviewed OpenAPI, and
   regenerate the shared TypeScript client.
6. The generated client powers an accessible `Saved learning` route for
   creating, editing, organizing, archiving, restoring, removing, and reopening
   records. A supported non-browser caller observes the same state and policy.
7. Focused and isolated live qualification proves restart durability,
   idempotency, concurrency, source resolution, learner isolation, quota and
   denial paths, accessibility, and exact cleanup.

## Contracts, Data, and Provenance

Create an additive `personal-workspace/v1` contract family with a closed
learning-reference union and closed workspace-record union. Initial reference
kinds are an exact learning opportunity and an exact placed lesson. Both retain
the Curriculum owner, stable resource and placement identities, package
identity/version/digest, safe title and route, source/publication provenance,
validation time, and one bounded availability value. Opportunity references
also retain their exact source fingerprint when supplied by Curriculum.

The workspace document has a schema version, server-owned learner-bound
workspace identity, positive revision, ordered records, ordered collections,
canonical creation/update times, and a deterministic document digest. Notes
own bounded learner text and one target reference. Bookmarks own one target
reference and optional learner label. Collections own a bounded title and an
ordered set of existing note/bookmark IDs; collection membership never copies
the member or target record.

A mutation intent supplies one idempotency key, exact expected revision, and a
closed operation. Server-owned IDs, learner identity, accepted reference facts,
canonical time, next revision, and persistence state are never client
authority. Exact replay returns the accepted workspace; changed reuse and stale
revision fail without overwrite. Removal affects only workspace-owned records
and collection membership; it never mutates the target learning resource.

The Personal-workspace repository owns its schema and migration. It stores no
lesson body, assessment definition, learner projection, Project artifact,
provider payload, credential, host path, or raw session value. Diagnostics and
API errors disclose no learner identifier, private note content, database
detail, or hidden target content.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Empty open | An authorized learner opens a deterministic empty workspace without a write side effect and sees a clear next action | domain/application/API/browser |
| Save exact note | The learner saves and reopens bounded note text tied to the same exact approved lesson/opportunity identity, version, digest, and provenance | contract/application/PostgreSQL/API/browser/live |
| Save bookmark | The learner saves and reopens an exact approved learning reference with an optional personal label and no copied source body | contract/application/API/browser |
| Organize collections | The learner creates multiple collections, changes ordered membership, reorders records, and resumes the exact accepted organization | domain/PostgreSQL/API/browser |
| Archive and remove | Archive/restore changes only workspace visibility; removal updates workspace-owned membership and never mutates the target learning resource | domain/application/API/live |
| Headless parity | A supported non-browser HTTP client creates and reads the same workspace through the same server-owned identity, contract, and policy | API/live qualification |
| Exact retry and stale write | Repeating one exact mutation returns its accepted result; changed key reuse or an old expected revision fails without duplicate or lost update | domain/PostgreSQL/API/live |
| Source denial | Unknown, malformed, changed, unavailable, or non-approved learning references fail before mutation without alternate-version substitution or protected-content disclosure | gateway/application/API/security |
| Authorization | Caller-selected learner identity, missing session/permission, cross-learner reads, and guessed workspace/record IDs fail closed with bounded public errors | application/API/security/live |
| Quota and interruption | Bounded record/text/collection/member limits and simulated interruption fail atomically while unrelated valid records remain usable | domain/PostgreSQL/anti-rigidity |
| Flexible valid shapes | Empty and populated workspaces, varied valid text, multiple record/collection counts, reordered members, optional labels, and generated IDs/times remain valid within the closed versioned contract | contract/domain/UI anti-rigidity |
| Accessible parity | Labels, forms, collections, status, errors, keyboard/focus order, reflow, reduced motion, forced colors, and light/dark/system themes preserve equivalent content and actions | component/Chromium/design |
| Restart and cleanup | Saved records survive normal application restart and qualification removes only its isolated topology and ignored artifacts | PostgreSQL/live runner |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0131 | Freeze Personal-workspace v1 learning-reference, record, mutation, compatibility, pure domain, public-operation, and anti-rigidity contracts | none | none | complete |
| WRK-0132 | Compose Curriculum public resolution, Personal-workspace application/persistence/migrations, protected API, reviewed OpenAPI, and generated client | WRK-0131 | none | complete |
| WRK-0133 | Deliver the plain-language accessible `Saved learning` browser flow exclusively through the generated client | WRK-0132 | none | complete |
| WRK-0134 | Qualify contracts, PostgreSQL, API/headless access, browser behavior, restart, accessibility, provenance, containment, and capability boundaries | WRK-0133 | none | active |

Exact `WRK-*` identifiers replace these seam labels as each bounded packet is
authored. Dependent packets are not claimed until their predecessor is complete.

## Verification and Qualification

Run JSON-schema and compatibility fixtures; Personal-workspace domain,
application, gateway, and repository tests; real-PostgreSQL migration,
atomicity, replay, conflict, restart, and isolation tests; protected API success
and denial tests; reviewed OpenAPI and generated-client reproduction; web
model/component tests; focused mocked and isolated live Chromium; and one
non-browser public-API observation.

Run architecture/import and persistence-ownership checks, security checks,
learner-language and design-system checks, documentation and planning checks,
whitespace, typecheck, zero-warning lint, build, affected verification,
independent technical review, completion structure, and
`python dev-tools/agent/check_ready.py`. Every packet includes focused
anti-rigidity evidence appropriate to its layer; incidental whitespace,
wording, style, fixture count, or ordering must not create a re-review loop.

## Rollback and Migration

Contracts and database changes are additive and versioned. New Personal-
workspace migrations require forward and development-down evidence against
real PostgreSQL. Empty-workspace reads remain side-effect free; the first
accepted mutation may create the learner's aggregate atomically.

A code rollback may remove an unreferenced route and UI, but it cannot silently
reinterpret, copy, or transfer saved records. Public contract removal or
semantic change follows compatibility governance. Isolated qualification data
may be deleted only inside its exact disposable topology.

## Stop Conditions

Stop for transfer of learning or Project authority, cross-module persistence
access, a reference that grants permission or copies source state, organization
or collaborative ownership, public sharing, provider/network/credential use,
artifact upload or execution, semantic search/embeddings, Assessment or
Learner-model mutation, AI-authoritative durable writes, managed-cloud policy,
breaking contract change, destructive migration, private-data leakage, stale
CAP approval, active write collision, or material CAP-0017 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will update Personal-workspace module, contract, migration, API,
generated-client, web, architecture verification, security/recovery, local
development, and known-gap documentation together with slice and packet
evidence. Completion must record exact contract/migration compatibility,
idempotency and revision behavior, authorization and privacy, source
provenance, API/browser/headless parity, accessibility, restart/containment,
exact checks, assumptions, unqualified environments, and residual risks.

Evidence must state that Project resources, broader domain adapters, arbitrary
files, execution, collaboration, sharing, organizations, managed cloud,
provider synchronization, semantic search, separate AI mode, and autonomous
authority were not delivered or qualified.

## Planning History

- 2026-10-17: Refined the first approved CAP-0017 manifest increment after
  ADR-0021 accepted the focused Personal workspace owner. Candidate A scores
  14/14 and establishes the smallest complete API-first learning-resource
  save/resume flow. The outcome, four-slice manifest, order, decision posture,
  and non-goals remain unchanged, so the refinement conforms to the current
  CAP package and needs no slice-level approval.
- 2026-10-17: Refined JIT-A as WRK-0131 around the additive Personal-workspace
  contract family and pure core. Persistence, API, client, UI, Project/domain
  adapters, and execution remain outside the packet.
- 2026-10-17: Completed WRK-0131 at exact candidate
  `79ba235c8efd8ca621508f031897cdb000cf75a7`. The contract and pure-core suite
  passed 81 tests; architecture, security, documentation, planning, whitespace,
  and aggregate readiness checks passed. JIT-B is now dependency-ready.
- 2026-10-17: Refined JIT-B as WRK-0132 around a selector-based public command,
  server-resolved Curriculum provenance, side-effect-free empty reads, atomic
  first materialization, Personal-workspace-owned PostgreSQL persistence, and
  protected generated-client access for browser and headless consumers.
- 2026-10-17: Activated WRK-0132 after confirming its completed WRK-0131
  dependency, current CAP package, resolved decision posture, exact bounded
  write scope, and API-first headless parity. No lower-level approval is
  required.
- 2026-10-17: Returned WRK-0132 to ready after implementation proved local-host
  composition belongs in the same API seam. The scope refinement remains
  inside SLI-0070 and requires one new claim manifest, not another approval.
- 2026-10-17: Re-activated WRK-0132 with the refined local-host path included
  in its exact scope and a fresh base revision. All product meaning, dependency,
  and CAP-package assumptions remain unchanged.
- 2026-10-17: Completed WRK-0132 at exact candidate
  `c8c7e9cc3be5784e71cbe918c1242847f4f1802a`. Focused application and contract,
  real-PostgreSQL, protected API, generated-client, architecture, security,
  affected-path, documentation, planning, whitespace, and aggregate readiness
  checks passed. JIT-C is now dependency-ready; browser and cumulative live
  qualification remain pending.
- 2026-10-17: Refined JIT-C as WRK-0133 around the generated-client-only
  `Saved learning` route, contextual exact-resource save entry, complete
  learner-owned mutation set, fail-closed browser validation, accessible
  technical records, and plain-language/theme/anti-rigidity evidence.
- 2026-10-17: Activated WRK-0133 after confirming its completed WRK-0132
  dependency, current CAP package, resolved decision posture, exact bounded
  browser write scope, generated-client boundary, and interface standards.
- 2026-10-17: Returned WRK-0133 to ready before implementation so its exact
  scope can include contextual save links and tests on the current opportunity
  and lesson pages. This prevents learner-entered internal IDs without changing
  the approved slice or public contract.
- 2026-10-17: Re-activated WRK-0133 with contextual opportunity/lesson entry
  files and focused regressions included in the fresh exact scope.
- 2026-10-17: Moved WRK-0133 to verification at exact candidate `55911c5` after
  focused and complete web checks, 11 Chromium scenarios, affected-path and
  aggregate qualification, and closure of every blocking technical finding.
- 2026-10-17: Completed WRK-0133 at exact candidate `55911c5` with the public
  browser flow, generated-client boundary, uncertain-retry identity, and all
  required accessibility and failure evidence accepted.
- 2026-10-17: Refined JIT-D as WRK-0134 around one isolated live Saved Learning
  browser journey, the same state through public headless HTTP, PostgreSQL
  correlation, normal restart, exact cleanup, cumulative evidence, and slice
  closure. No product behavior or lower-level approval is added.
- 2026-10-17: Activated WRK-0134 from base `bc388b2` after validating the
  completed dependency, current CAP package, resolved decision posture, exact
  evidence-only scope, API/headless parity, and exclusive edit ownership.
