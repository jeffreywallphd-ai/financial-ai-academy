---
id: SLI-0030
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-16
parent: CAP-0007
depends_on: []
decision_gates: []
---

# Vertical Slice: Create an Independent or Learning Project

## Outcome and User Scenario

An authorized learner creates one Project from a personal charter or starts one
from an exact approved learning-project brief, then reopens the Project shell
with its stable identity, title, charter, active lifecycle, and immutable origin
provenance intact. A learning-started Project can continue independently of the
lesson without losing its exact Content and Curriculum source. The same
protected public API serves the generated browser client and supported non-
browser clients; no browser-only authority or AI-specific transport is added.

## Scope Boundaries

### In Scope

- Introduce the Project module as owner of project identity, learner ownership,
  user-authored title and charter, origin, active lifecycle, revision, creation
  metadata, and project-scoped authorization.
- Define a closed origin union for an independent project or a learning-started
  project. Independent origin carries no implied curriculum or completion;
  learning origin retains exact approved project-brief, Content package, and
  Curriculum placement identities, versions, and digests.
- Admit one bounded immutable learning-project brief through Content and one
  exact Curriculum placement through their public operations without giving
  Project access to either module's persistence.
- Provide deterministic create and read/list application operations with
  server-owned learner context, idempotent creation, optimistic revision
  semantics where applicable, and bounded learner-safe failures.
- Persist Project-owned shell records in PostgreSQL without cross-module foreign
  keys, provider payloads, copied learning content, or copied domain state.
- Expose protected public API operations, reviewed OpenAPI, and the generated
  TypeScript client for independent creation, learning-origin creation, and
  reopening the learner's Project shells.
- Deliver an accessible responsive browser flow that uses the generated client,
  distinguishes independent from learning-started work in plain language, and
  shows exact origin details without technical infrastructure vocabulary.
- Keep the public operations directly usable by command-line, service, and
  future headless AI clients. A separate AI mode, agent protocol, autonomous
  authority, or model-selected project is not part of this slice.
- Prove malformed, duplicate, stale-source, unavailable-source, unauthorized,
  cross-learner, interrupted, and partial-write behavior fails closed without
  creating Assessment evidence or Learner-model progress.

### Out of Scope

- Project notes, resource links, datasets, notebooks, code, result files,
  environment declarations, artifact upload/download/preview, snapshots,
  export, typed domain-resource links, deletion, or restore; those belong to
  SLI-0031.
- Assessment submission, milestone validation, completion evidence, retry,
  supersession, project history projection, instructor review, or feedback;
  those belong to SLI-0032 or later capabilities.
- Portfolio positions, transactions, calculations, valuation, market data,
  live Portfolio linking, or any copied domain aggregate state.
- Platform/provider execution, active rendering, subprocesses, kernels,
  packages, network, secrets, callbacks, runtime images, arbitrary file
  storage, or claims that learner results were reproduced.
- Collaboration, shared ownership, organizations, roles beyond the accepted
  local learner context, public sharing, publishing, external notifications,
  managed-cloud qualification, or production recovery.
- AI-authored charters, AI-authoritative creation, recommendations, mastery,
  grading, personalized investment advice, or financial execution.
- Styling-only polish that does not impair operation, meaning, accessibility,
  responsive use, or theme parity; optional cleanup remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0007](../capabilities/CAP-0007-complete-applied-projects.md)
  defines the complete four-slice Project outcome and this first shell/origin
  increment.
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) assigns both
  learning-started and independent project identity, charter, origin,
  lifecycle, mutable workspace, snapshots, and typed links to Project while
  Content/Curriculum retain learning authority and Assessment owns only exact
  submitted evidence.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) prohibits
  platform or provider execution. This slice creates no artifact or execution
  surface and must not establish one accidentally.
- [Module Map](../../architecture/modules/module-map.md) and
  [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  require public operations and versioned contracts across module boundaries.
- CAP-0005 supplies exact Curriculum versions and placement meaning. CAP-0006
  supplies the later Assessment/evidence seam, but Project creation itself
  creates no completion or mastery evidence.
- Decision readiness is sufficient for a single authorized learner, Project-
  owned shell, exact learning-origin references, PostgreSQL persistence, public
  APIs, and a static browser client. Tenancy, managed cloud, execution,
  providers, live Portfolio behavior, and instructor authority remain outside
  this selection.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver the closed Project origin contract, Project core/persistence, protected API, generated client, and accessible create/reopen flow for both accepted origin types | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Define contracts and backend creation only, deferring the learner-visible create/reopen flow | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Keep learning-started projects inside Content or Curriculum and add independent Project later | no - it contradicts ADR-0012 ownership and would split one project lifecycle across authorities | - | - | - | - | - | - | - |
| D. Add artifacts, execution, snapshots, Portfolio links, and Assessment submission in the first slice | no - it collapses later manifest slices and crosses accepted execution and provider boundaries | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it delivers the complete approved SLI-0030
scenario across canonical learning sources, the new Project core, persistence,
public API, generated client, and accessible UI. Its closed two-origin contract
is independently verifiable, has no unresolved decision, and remains additive
and reversible before later workspace or snapshot state exists.

Candidate B is decision-ready and useful but produces no learner-visible
outcome, so value and end-to-end completeness score one. Candidate C violates
accepted ownership. Candidate D materially changes the CAP package and the
inert-artifact boundary. Candidate A wins without a tie-break and preserves the
enumerated SLI-0030 outcome.

## Boundary Path

1. Content admits one immutable learning-project brief as exact versioned
   package content with stable ID, purpose, learner-visible summary, source
   references, and digest; it does not own a learner's Project instance.
2. Curriculum records an exact project-brief placement under a versioned
   curriculum/activity relationship and exposes it through a public operation;
   it does not create or persist Project state.
3. Project accepts either an independent-origin command with a learner-authored
   charter or a learning-origin command resolved through Content and Curriculum
   public facades. It validates the closed origin union and creates one stable
   learner-owned active Project shell idempotently.
4. A Project-owned PostgreSQL adapter atomically stores the shell and immutable
   origin references without cross-module foreign keys or copied source bytes.
5. Protected host operations resolve server-issued learner context, enforce
   project-scoped authorization, map bounded errors, and expose create and
   reopen/list shapes in reviewed OpenAPI.
6. The generated TypeScript client powers an accessible browser flow for both
   origin types. A supported non-browser client calls the same API without
   importing backend internals or relying on UI state.
7. Focused and isolated live qualification proves idempotency, origin
   immutability, restart persistence, authorization, source-version behavior,
   absence of Assessment/Learner-model side effects, and exact cleanup.

## Contracts, Data, and Provenance

Introduce additive versioned contract families for the private approved
learning-project brief and the public Project shell. The Project origin is a
closed discriminated union:

- `independent` retains an explicit learner-created origin classification and
  no learning-source fields; and
- `learning` retains exact Content package, project-brief, Curriculum,
  placement, schema, version, and digest references plus the approved brief
  purpose needed to explain where the Project began.

The public create request supplies an idempotency key, origin selector, title,
and bounded charter. The server supplies learner identity, project identity,
revision, timestamps, and authorization. The response and read/list records
never expose storage keys, host paths, provider payloads, hidden curriculum
facts, or another learner's Project.

Project persistence is module-owned and migration-backed. Origin classification
and exact references are immutable after creation; title and charter mutability
are not introduced unless required for this slice's observable scenario and
covered by explicit conditional-update semantics. No Assessment, Learner-model,
Audit, artifact, snapshot, outbox, Portfolio, or provider row is created by the
creation path.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Independent creation | An authorized learner creates and reopens one active Project with a stable ID, bounded title/charter, independent origin, and no learning-progress implication | domain/application/API/browser/live |
| Learning-origin creation | The learner starts from one exact approved brief and reopens a Project whose immutable origin retains exact Content and Curriculum provenance while the Project can continue outside the lesson | contract/application/PostgreSQL/API/browser/live |
| Headless creation and read | A supported non-browser HTTP client creates and reads the same public Project shell through the same server-owned identity and policy | API/live qualification |
| Idempotent retry | Repeating one exact create command returns the same Project; conflicting reuse fails without a duplicate or partial shell | domain/PostgreSQL/API/live |
| Origin immutability | Later source versions or repeated reads do not rewrite the Project's accepted origin classification or exact references | domain/PostgreSQL/restart |
| Source denial | Unknown, stale, mismatched, unauthorized, or unavailable learning brief/placement fails before Project creation without exposing hidden source facts | contract/application/API/security |
| Authorization | Caller-selected learner identity, missing session/permission, cross-learner reads, and guessed Project IDs fail closed with a bounded public error | application/API/security/browser |
| No evidence side effect | Independent and learning-origin creation creates no Assessment attempt/submission/completion or Learner-model progress/mastery state | application/PostgreSQL/live |
| Flexible valid input | Compatible title/charter lengths, harmless wording, stable optional metadata, and multiple learner-owned Project records do not trigger one-fixture/count/order assumptions | domain/contract/UI anti-rigidity tests |
| Accessible parity | Origin choices, labels, descriptions, validation, status, focus, keyboard order, reflow, reduced motion, forced colors, and light/dark/system themes preserve equivalent meaning | component/Chromium/design |
| Restart and cleanup | Project shells survive a normal seed-free application restart and qualification removes only its isolated topology and ignored artifacts | PostgreSQL/live runner |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts.

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0109 | Freeze learning-project-brief and Project-shell contracts, origin semantics, compatibility fixtures, and pure Project domain values | none | none | complete |
| WRK-0110 | Compose Content/Curriculum learning-origin resolution, Project application/persistence, migrations, protected API, reviewed OpenAPI, and generated client | WRK-0109 | none | complete |
| JIT-C | Deliver the plain-language accessible independent and learning-origin create/reopen browser flow from the generated client | JIT-B | none | pending just-in-time refinement |
| JIT-D | Qualify contracts, PostgreSQL, API/headless access, browser behavior, origin immutability, idempotency, authorization, evidence non-effects, restart, accessibility, and containment | JIT-C | none | pending just-in-time refinement |

## Verification and Qualification

Run schema and semantic conformance for approved and malicious brief/origin/
Project records; Project domain and application tests for both origin types,
idempotency, immutability, authorization, stale/unavailable sources, and
evidence non-effects; real-PostgreSQL migration, atomicity, conflict, restart,
and isolation tests; protected API success and denial tests; reviewed OpenAPI
and generated-client reproduction; web model/component tests; focused mocked
and isolated live Chromium; and a non-browser public-API observation.

Run architecture/import and schema-ownership checks, security, learner-
language, design-system, documentation, planning, whitespace, typecheck, lint,
build, affected verification, independent technical review, completion
structure, and aggregate readiness. Anti-rigidity tests vary valid title and
charter content, safe optional metadata, record counts and ordering, generated
IDs/timestamps, and nonfunctional presentation without weakening identity,
origin, authorization, or provenance invariants.

## Rollback and Migration

Contracts and database changes are additive and versioned. New Project,
Content-brief, or Curriculum-placement migrations require forward and
development-down evidence against real PostgreSQL. A code rollback may remove
an unreferenced route and UI, but it must not rewrite or silently reclassify an
accepted Project origin. Public contract removal or semantic change follows
compatibility governance rather than an in-place rollback.

Because this slice creates no artifact bytes, snapshot, Assessment submission,
provider call, or external effect, rollback has no execution cleanup or domain-
resource compensation. Isolated qualification data may be deleted only inside
the bounded test topology.

## Stop Conditions

Stop for organization/collaborative ownership, mutable source provenance,
Content/Curriculum ownership of learner Project instances, general Workspace
scope, cross-module persistence access, artifacts or unrestricted storage,
active rendering or execution, network/secrets/packages, Portfolio semantics,
Assessment submission/completion, instructor authority, AI-authoritative
creation, personalized financial advice, external providers, managed-cloud
tenancy/recovery, a separate local/cloud core, breaking contracts, destructive
migration, private-data leakage, stale CAP binding, active write collision, or
material CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, one incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery is expected to update Project, Content, Curriculum, API, web, local
deployment, contract, migration, architecture-verification, security, and
known-gap documentation together with the slice and packet evidence. Completion
must record exact contract and migration compatibility; independent and
learning-origin behavior; idempotency and immutable provenance; API/browser/
headless parity; authorization and privacy; explicit absence of Assessment and
Learner-model side effects; accessibility; restart/containment; exact checks;
assumptions; environment qualifications not performed; and residual risks.

Evidence must state that artifacts, snapshots, Portfolio integration,
Assessment submission, execution, external providers, organizations, managed
cloud, production recovery, a separate AI mode, and autonomous authority were
not delivered or qualified.

## Planning History

- 2026-10-16: Activated the slice with WRK-0109 as its first bounded packet;
  implementation remains inside the approved CAP-0007 manifest and the
  resolved ADR-0011/ADR-0012 boundaries.
- 2026-10-16: Refined the first approved CAP-0007 manifest increment after
  CAP-0005 and CAP-0006 completed and portfolio allocation selected CAP-0007 as
  the only dependency-ready capability lane. Candidate A scores 14/14 and
  establishes the smallest API-first Project shell/origin flow without
  artifacts, snapshots, submissions, live domain links, execution, or another
  decision gate. The refinement conforms to the current CAP package.
- 2026-10-16: Completed WRK-0110 with the exact Project source-resolution,
  persistence, migration, protected API, reviewed OpenAPI, generated-client,
  and non-browser access seam passing its required verification. SLI-0030
  remains active for the learner-facing browser flow and final qualification.
