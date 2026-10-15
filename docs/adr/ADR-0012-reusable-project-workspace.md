# ADR-0012: Reusable Project Workspace with Learning and Domain Links

- Status: accepted
- Date: 2026-10-15
- Decision request: [DEC-0007](../planning/decision-requests/DEC-0007-applied-project-lifecycle-ownership.md)
- Supersedes: [ADR-0010](ADR-0010-applied-project-lifecycle-ownership.md)

## Context

Applied projects need to participate in structured learning without being
confined to it. A learner may start from a published learning project, branch
into independent investigation, create a personal project outside a curriculum,
or organize work around one or more simulated portfolios and related resources.
The earlier ownership decision placed project instances and mutable artifacts in
Assessment. That is economical for a learning-only flow, but it makes Assessment
the workspace for unrelated personal and financial-domain activity.

The architecture needs a reusable project identity and mutable work boundary
while preserving the existing owners of learning definitions, curriculum rules,
assessment evidence, learner projections, portfolio calculations, and audit
records. It must also keep mutable work separate from immutable submissions and
must not create an unbounded general-purpose file or execution platform.

## Decision

Introduce a **Project** module inside the modular monolith.

Project owns:

- a stable project identifier, learner owner, user-authored title and charter,
  origin, lifecycle, and project-scoped authorization inputs;
- a mutable project workspace containing bounded notes, resource links, inert
  artifacts, and versioned artifact manifests;
- immutable, digest-bound workspace snapshots that close an exact set of
  project metadata, links, resources, and artifact versions without stopping
  later work in the live workspace; and
- typed, versioned links to learning sources and independently owned domain
  resources.

Project origin is a closed, versioned union. The initial semantic categories are
learning-initiated and independent. A learning-initiated project retains exact
Content and Curriculum references but remains a Project-owned workspace that can
continue outside a lesson. An independent project has a learner-authored charter
and no implied curriculum, Assessment, or progress meaning.

Ownership around Project remains explicit:

- **Content** owns immutable published learning-project briefs, instructions,
  supplied resources, educational sources, limitations, and publication state.
- **Curriculum** owns learning placement, prerequisites, milestone requirements,
  availability, and the rules for satisfying a curriculum activity.
- **Assessment** owns immutable learning submissions, deterministic validation,
  and bounded completion evidence. A submission references one closed Project
  snapshot and the exact Content and Curriculum requirements it is evaluated
  against. It never owns or mutates the live Project workspace.
- **Portfolio** owns simulated portfolio identities, positions, transactions,
  valuation, rebalancing, performance and risk calculations, and their market
  data provenance. A Project may link to zero or more Portfolio-owned resources
  through stable public identifiers and version or as-of evidence when the
  Portfolio contract is accepted. Project does not copy or reinterpret portfolio
  state or calculations.
- Other domain modules retain the same ownership rule. A Project link records a
  reference and provenance needed to interpret the association; it does not
  transfer domain authority to Project.
- **Learner model** consumes Assessment evidence for learning projections.
  Creating, editing, snapshotting, linking, or archiving an independent Project
  does not by itself produce completion, mastery, or competency evidence.
- **Audit** owns append-oriented transition, snapshot, submission, link, and
  integrity references without becoming a second project, assessment, or domain
  database.

Project-domain links are many-valued so one project may be associated with
multiple portfolios or other resources. Exact wire fields require executable
contracts, but every link identifies its owning module and resource, link type,
applicable version or as-of evidence when available, provenance, and lifecycle.
Removing a live association cannot alter an immutable Project snapshot or an
Assessment submission that already references it.

Modules collaborate through public application operations or registered
versioned events. Project may validate a learning or domain reference through an
owning module's public surface. Assessment may resolve an immutable Project
snapshot through Project's public surface. Content, Curriculum, Portfolio, and
other domain modules do not import Project internals, and Project does not import
Assessment to decide learning completion.

ADR-0011 remains authoritative for artifact effects. Project artifacts are
untrusted inert data; Project supplies no kernel, subprocess, network, secret,
package-installation, runtime-image, or provider-execution authority.

## Consequences

- Learners can retain and grow projects outside lessons while preserving exact
  learning provenance when a project originated from a curriculum activity.
- Mutable workspace evolution is separated cleanly from immutable snapshots and
  Assessment submissions.
- Projects can organize work around multiple portfolios without absorbing
  financial-domain invariants or forcing Portfolio to depend on learning.
- Project adds a real module, persistence boundary, public facade, events,
  authorization surface, retention rules, and export/deletion obligations.
- Workspace and submission lifecycles must be coordinated through immutable
  snapshot references rather than cross-module transactions or shared tables.
- Project must remain project-scoped. General bookmarks, conversations, global
  notes, and unrelated files remain part of a later personal-workspace
  capability rather than expanding Project into a universal container.
- Live Portfolio integration cannot be claimed until Portfolio ownership,
  calculations, public operations, version/as-of semantics, and authorization
  are accepted and delivered independently.

## Alternatives Rejected

- **Keep all project instances and mutable artifacts in Assessment.** Rejected
  because independent projects and portfolio-associated work have no necessary
  assessment lifecycle and would overload learning evidence ownership.
- **Let a dedicated Project module also own submissions and completion.**
  Rejected because it would duplicate Assessment authority and blur project
  progress with learning completion.
- **Create separate Project and general Workspace modules now.** Rejected because
  a second generic workspace boundary adds storage, authorization, retention,
  and snapshot orchestration before cross-activity workspace requirements are
  sufficiently shaped. Project owns only its bounded workspace initially.
- **Treat portfolios as projects.** Rejected because portfolio transactions,
  valuation, market-data provenance, and financial calculations have different
  invariants and must remain under Portfolio ownership.

## Boundaries

This decision accepts Project as a module and defines ownership and dependency
direction. It does not accept exact schemas, file limits, Portfolio semantics,
provider data use, live financial actions, collaborative editing, public
sharing, organization tenancy, instructor review, or broad personal-workspace
behavior.

Typed Portfolio associations are an accepted Project-side seam, not evidence
that the proposed Portfolio module or its calculations are ready. Implementing
the Portfolio side requires its own shaped capability and durable decisions.
Adding provider-backed resources requires separate license, privacy, security,
and egress authority.

## Verification Implications

- Enforce a Project public surface and reject cross-module internal imports or
  persistence access.
- Prove that learning-initiated and independent projects share Project semantics
  while only explicit Assessment evidence affects learner projections.
- Prove immutable, digest-bound snapshots, continued mutation of successor
  workspace state, idempotent snapshot creation, and interruption recovery.
- Prove Assessment submissions reference exact snapshots and requirements and
  cannot mutate, delete, or silently follow the live workspace.
- Prove Project links can reference multiple resources without copying their
  business state and that link removal does not rewrite historical snapshots.
- Prove Portfolio and other domain modules remain authoritative through public
  contract, architecture, and persistence-isolation checks.
- Exercise authorization, cross-learner denial, export, deletion, retention,
  stale reference, unavailable owner, replay, and partial-failure paths.
- Preserve ADR-0011 execution denial across every Project artifact path.

## Supersession

This ADR supersedes ADR-0010. A future split of Project's bounded workspace into
a general Workspace module, or a transfer of Project ownership, requires another
superseding ADR with contract, persistence, event, and migration analysis.
