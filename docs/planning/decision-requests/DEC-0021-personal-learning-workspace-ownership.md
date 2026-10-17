---
id: DEC-0021
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-17
parent: null
depends_on: ["DEC-0007"]
decision_gates: []
decision_record: null
---

# Decision Request: Choose Personal Learning Workspace Ownership

## Decision Needed

Choose the module ownership and public boundary for a learner-owned personal
workspace that organizes notes, bookmarks, collections, and typed references
to resources owned by learning, Project, and later domain modules.

## Why Now

CAP-0017 is ready to begin with a saved learning-resource workspace. Its first
slice requires durable learner-owned state, authorization, persistence, public
contracts, and deletion/export behavior. ADR-0012 deliberately limited Project
to project-scoped work and says that introducing or splitting out a general
Workspace module requires a superseding decision. Implementation cannot safely
select that owner from the CAP package alone.

## Current Authority and Constraints

- Project remains authoritative for project shells, mutable project workspaces,
  inert artifacts, immutable snapshots, and Project-owned typed links under
  ADR-0012.
- Content and Curriculum remain authoritative for immutable learning resources
  and their exact placements. A bookmark, note, or collection cannot transfer
  that authority or become learning evidence.
- Assessment and Learner model remain authoritative for completion evidence and
  learning projections. Organizing a resource cannot change either.
- Workspace references must carry stable identity, version, provenance, and
  availability state without copying another module's aggregate.
- The initial boundary is private-host and learner-scoped. This decision grants
  no organization tenancy, collaboration, publication, cloud sync, provider
  credentials, active rendering, or artifact execution.
- Project artifacts and any referenced notebooks, datasets, code, and results
  remain inert under ADR-0011.

## Options

| Option | Benefits | Costs and risks | Affected contracts and operations | Reversibility |
| --- | --- | --- | --- | --- |
| A. Introduce a focused Personal workspace module | Gives learner organization one explicit owner while preserving Content, Curriculum, Project, Assessment, and later domain authority. Supports one provider-neutral public API for browser, service, command-line, and future headless clients. Keeps the reference index separate from Project's richer artifact and snapshot lifecycle. | Adds a new modular-monolith boundary, persistence schema, authorization surface, reference adapters, quotas, retention, export/deletion, recovery, and stale-reference behavior. It could become a god module unless its contract is limited to owned notes, bookmarks, collections, and references. | Module map and architecture tests; personal-workspace contracts; PostgreSQL schema/migrations; application ports and owner adapters; protected API/OpenAPI/generated client; export/deletion/recovery and security documentation. | Medium before broad adoption if contracts remain closed and provider-neutral; lower after other capabilities depend on workspace identifiers and exports. |
| B. Expand Project into the general personal workspace owner | Reuses delivered Project identity, persistence, links, API patterns, and snapshot experience. Avoids another module at first. | Violates Project's current project-scoped boundary unless ADR-0012 is superseded. Notes and bookmarks unrelated to projects would force artificial Projects, blur Project snapshots with general organization, and increase god-module and migration risk. | Superseding Project decision; Project contracts, persistence, APIs, UI, exports, retention, and architecture tests; migration rules distinguishing existing project work from general workspace records. | Low-medium; separating general records later would require identity, reference, export, and retention migration. |
| C. Keep records with each owning domain and compose a federated workspace view | Avoids one general workspace aggregate and lets each module control lifecycle details for its own learner annotations and saved state. | Duplicates note/bookmark/collection semantics and authorization across modules, makes cross-domain collections and ordering transactional only by coordination, and couples resume/search/export to every participating owner. Missing adapters can degrade the whole view unless a separate projection is introduced, which recreates much of Option A. | Additive learner-state contracts and storage in Content/Curriculum/Project and later modules; cross-module query/projection contracts; coordinated export, deletion, indexing, recovery, and compatibility behavior. | Low after multiple owners persist incompatible saved-item semantics; early reversal is possible before public identifiers spread. |

## Recommendation

Recommend **Option A — Introduce a focused Personal workspace module**.

Verified facts: ADR-0012 keeps Project project-scoped, rejects a general
Workspace module at that time, and requires a superseding decision before one
is introduced. CAP-0017 now supplies the concrete cross-activity requirements
that were previously premature. Content, Curriculum, Assessment, Project, and
Learner model already have distinct accepted authority.

Inference: a narrow Personal workspace module is the cleanest boundary because
the new durable state is learner organization rather than source content,
project work, assessment evidence, or learner projection. It is viable only if
its contract owns no target-domain state and optional adapters fail
independently.

Assumption requiring confirmation: the product intends saved notes, bookmarks,
and collections to persist independently of a Project rather than requiring all
personal organization to occur inside an explicit Project.

## Evidence Required

- A bounded ownership matrix for note, bookmark, collection, typed reference,
  source resource, immutable Project snapshot, and export/deletion authority.
- Closed versioned contract sketches for saved items, collection membership,
  exact target identity/version/provenance, stale/unauthorized states, and
  optimistic/idempotent mutation.
- Dependency and persistence analysis proving no cross-module internal imports,
  tables, transactions, or copied aggregates.
- Threat and failure analysis for cross-learner denial, inaccessible targets,
  deletion, quota, export, recovery, and diagnostics.
- Confirmation that headless and browser clients share the same protected API
  and that missing optional adapters isolate only their references.

## Required Authority

Product and architecture authority with domain ownership, identity/security,
data, contracts, recovery, export/deletion, accessibility, and operations
review.

## Decision Record and Promotion

Promote the selected boundary to a superseding ADR for the relevant ADR-0012
personal-workspace restriction, then update the module map, contract
architecture, decision readiness, and affected context packs before delivery.

## Dependent Planning Updates

Revalidate CAP-0017 and its SLI-0070 through SLI-0073 manifest. Revalidate
CAP-0019 where portable learning-record export depends on workspace ownership.
If the chosen option changes the approved CAP-0017 boundary or slice manifest,
return that CAP package for renewed CAP-level approval.

## Planning History

- 2026-10-17: Captured when incremental delivery found that CAP-0017's general
  learner workspace crosses the explicit ADR-0012 Project-scope boundary.
