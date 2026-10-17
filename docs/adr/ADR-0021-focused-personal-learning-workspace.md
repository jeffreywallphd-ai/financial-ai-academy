# ADR-0021: Focused Personal Learning Workspace Module

- Status: accepted
- Date: 2026-10-17
- Decision request: [DEC-0021](../planning/decision-requests/DEC-0021-personal-learning-workspace-ownership.md)
- Amends: [ADR-0012](ADR-0012-reusable-project-workspace.md)

## Context

Learners need notes, bookmarks, collections, and a resumable index of work that
crosses lessons, Projects, and later domain resources. These records are not
source content, curriculum placement, assessment evidence, learner
projections, Project artifacts, or the business state of a referenced domain.

ADR-0012 deliberately kept Project project-scoped and deferred a separate
general Workspace module until cross-activity requirements were concrete.
CAP-0017 now defines those requirements. Putting unrelated notes and bookmarks
in Project would force artificial Projects and blur Project snapshots with
personal organization. Distributing the same saved-item behavior across every
resource-owning module would duplicate lifecycle and authorization policy and
make cross-domain collections, search, export, and deletion depend on all
owners at once.

## Decision

Introduce a focused **Personal workspace** module inside the modular monolith.
It owns only learner organization and learner-authored workspace content:

- stable learner-scoped note, bookmark, collection, and saved-reference
  identities;
- note content and the ordering, membership, archive, and deletion state of
  workspace-owned records;
- typed references to exact public resources, including owning module,
  resource type and identity, applicable version or as-of evidence, purpose,
  source provenance, validation time, and bounded availability state; and
- workspace-owned mutation revisions, idempotency evidence, quota accounting,
  export views, and audit/provenance references.

Personal workspace does not own or copy the referenced aggregate. Content owns
published learning resources, Curriculum owns placement and eligibility,
Assessment owns evidence, Learner model owns projections, Project owns Project
workspaces and snapshots, and later domain modules retain their accepted
authority. Creating, organizing, archiving, or deleting a workspace record
does not enroll a learner, satisfy a requirement, change evidence, mutate a
Project, grant permission, or change a referenced resource.

Every supported reference kind is resolved through an owning module's public
application operation behind a Personal-workspace port. An adapter may return
available, stale, unavailable, removed, or unauthorized without exposing
protected target content. Missing or failing optional adapters isolate only
their references and never prevent unrelated notes, bookmarks, collections,
or supported references from being used.

The module exposes one versioned protected public API for browser,
command-line, service, and future headless AI clients. Identity and durable
mutation authority remain server-owned. A headless client receives no special
authority over authorization, learning state, Project state, financial state,
or another module's data.

The initial persistence boundary is module-owned PostgreSQL transactional
state in the accepted private-host learner context. Workspace exports and
recovery participation use explicit versioned views and the accepted community
recovery boundary. Object or analytical stores cannot become the workspace
source of truth. Managed-cloud tenancy, retention, encryption, sync, and
recovery remain separately gated.

Project notebooks, datasets, code, environments, and results remain untrusted
inert evidence under ADR-0011 even when the Personal workspace references
them. This decision authorizes no upload execution, active preview, provider
callback, credential transfer, package installation, or remote synchronization.

## Consequences

- Learners can organize cross-activity work without turning Project, Content,
  Curriculum, Assessment, or Identity into a general container.
- The platform gains a new module, persistence schema, public facade,
  authorization surface, reference-adapter seam, quota policy, export/deletion
  obligations, and recovery participation.
- Project remains project-scoped. Personal workspace may reference a Project or
  immutable snapshot but cannot copy its workspace, artifacts, snapshot
  material, or lifecycle.
- Target deletion or lost authorization can make a reference stale or
  inaccessible without corrupting unrelated workspace records. Removing a
  workspace reference cannot delete or rewrite its target.
- The module risks becoming a god module. Closed record/reference unions,
  owner-specific public adapters, no target payload copying, and architecture
  tests are required controls.

## Alternatives Rejected

- **Expand Project into the general workspace owner.** Rejected because it
  would reverse ADR-0012's project-scoped boundary, force unrelated work into
  artificial Projects, and couple simple organization to artifact/snapshot
  lifecycle.
- **Store saved records with every target-owning module and compose a federated
  view.** Rejected because it duplicates note, bookmark, collection,
  authorization, export, and deletion semantics while making cross-domain
  organization depend on all owners simultaneously.
- **Use browser-local storage as the authoritative workspace.** Rejected
  because it cannot satisfy protected cross-device/session resume, shared API,
  recovery, export, provenance, or server-owned authorization semantics.

## Boundaries

This decision does not authorize collaboration, instructor access, public
sharing, organization tenancy, cloud synchronization, provider-backed storage,
active artifact rendering or execution, arbitrary files, external-drive sync,
semantic search, AI-authored durable mutation, or live financial actions.

Exact schemas, quotas, retention intervals, export containers, search
implementation, and adapter inventory belong to CAP-0017 contracts and
qualification. Adding a reference kind is conforming only when its owner and
public contract are accepted and the adapter preserves this authority model.
A reference that grants permissions, copies target business state, or requires
a new provider, tenancy, execution, or licensing posture needs further
decision review.

## Verification Implications

- Enforce a Personal-workspace public surface and reject cross-module internal
  imports, repository access, foreign keys, and target-table transactions.
- Prove learner ownership, cross-learner denial, optimistic/idempotent
  mutation, bounded quotas, interruption recovery, and deterministic resume.
- Prove exact resource identity/version/provenance and typed stale,
  unavailable, removed, and unauthorized behavior without protected-content
  disclosure.
- Prove that link, unlink, archive, and workspace deletion never mutate target
  aggregates or immutable Project snapshots.
- Prove optional-adapter absence isolates only affected references and that
  base notes, bookmarks, and collections remain usable.
- Exercise versioned export, deletion boundaries, recovery-set inclusion,
  accessibility, local/cloud semantic parity, and API use by browser and
  non-browser clients.
- Preserve ADR-0011 execution denial for every referenced inert artifact.

## Supersession

This ADR amends only ADR-0012's prior deferral of a separate general workspace
boundary. ADR-0012 remains authoritative for Project ownership, Project
workspaces, artifacts, snapshots, learning origins, and domain links. Transfer
of either module's ownership or merging the two modules requires another
superseding decision.
