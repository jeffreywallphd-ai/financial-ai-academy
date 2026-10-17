---
id: CAP-0017
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0001", "CAP-0007"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0070", "SLI-0071", "SLI-0072", "SLI-0073"]
---

# Capability: Maintain a Personal Learning Workspace

## Outcome

An individual learner can save, organize, resume, link, and export personal
notes, bookmarks, charts, datasets, simulations, notebooks, projects, and AI
conversation references without transferring ownership from their source
domains or executing untrusted artifacts.

## Users and Value

Learners need continuity across lessons and applied work. Value is observable
when saved items survive interruption, remain traceable to exact sources, and
can be organized or removed without corrupting the underlying learning,
project, financial, or AI record.

## Scope

### In Scope

- A learner-owned workspace index for notes, bookmarks, collections, and typed
  references to independently owned resources.
- Project workspaces and immutable snapshots under ADR-0012; inert notebooks,
  datasets, code, and results under ADR-0011.
- Resume, search, organize, link/unlink, archive, delete/export request, stale
  reference, quota, and recovery-safe behavior.
- Progressive adapters for later charts, portfolios, experiments, and AI
  conversations without requiring them to start the base capability.

### Out of Scope

- Copying domain aggregates into the workspace, executing artifacts, shared
  collaboration, instructor access, public publishing, or cloud drive sync.
- Treating a bookmark or link as enrollment, evidence, permission, or ownership.
- Managed-cloud retention or organization policy before those decisions exist.

## Canonical Context

- [Reusable Project Workspace](../../adr/ADR-0012-reusable-project-workspace.md)
- [Inert Applied-Project Artifacts](../../adr/ADR-0011-inert-applied-project-artifacts.md)
- [Data Architecture](../../architecture/data/data-architecture.md)
- [Community Evidence Protection](../../security/community-learner-evidence-protection.md)
- [CAP-0007](CAP-0007-complete-applied-projects.md)

## Decision Gates and Constraints

- Project owns mutable project workspaces and immutable snapshots; other domain
  resources remain independently authoritative.
- Workspace links carry stable references and provenance only and never grant
  cross-module persistence access or provider credentials.
- Initial artifacts are passive and untrusted. Later resource adapters must
  preserve their owning CAP contracts and authorization.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0070 | A learner saves and resumes notes, bookmarks, and collections tied to exact approved learning resources. | First after CAP-0001; establishes workspace identity, ownership, and reference contracts. | Collaboration, publication, or copied source authority changes the CAP package. | captured |
| SLI-0071 | The learner sees and organizes reusable Project workspaces, snapshots, and inert resource manifests without executing their contents. | After CAP-0007 and SLI-0070. | Platform execution or Project ownership of other domains changes the CAP package. | captured |
| SLI-0072 | The learner links supported domain resources, searches and filters the workspace, and handles stale, unavailable, removed, or unauthorized references safely. | After SLI-0071; adapters may arrive as their owning capabilities complete. | A link granting authority, hidden copying, or repository-wide lockstep changes the CAP package. | captured |
| SLI-0073 | Workspace behavior is qualified for interruption, idempotency, quotas, reference integrity, deletion/export boundaries, accessibility, recovery, and local/cloud semantics. | Last; depends on SLI-0070 through SLI-0072. | Shared tenancy, hosted sync, or artifact execution changes the CAP package. | captured |

## Capability Acceptance

- Saved items and references resume deterministically with owner, type, source,
  version, timestamps, and provenance intact.
- Link, unlink, archive, and deletion behavior never mutates another module's
  aggregate or silently removes immutable evidence.
- Untrusted artifacts stay inert; stale and unauthorized targets disclose no
  protected content and do not block unrelated workspace use.
- Accessibility, portability, backup-set inclusion, quotas, and failure recovery
  are directly verified.

- Every slice includes focused failure and anti-rigidity tests; missing or stale
  optional resource adapters isolate only those references and never lock the
  base workspace.

## Risks and Non-Goals

A general workspace can become a god module. This CAP owns organization and
references, not portfolio calculations, learning evidence, provider behavior,
or arbitrary file execution.

## Documentation Impact

Delivery will refine workspace/reference vocabulary, storage and retention,
project/resource adapters, deletion/export semantics, security, operations,
accessibility, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 14 with manifest SLI-0070 through
  SLI-0073. The package has no unresolved durable decision and awaits one CAP
  planning approval; later adapters remain independently gated.
- 2026-10-16: Reconciled the complete four-slice package with current project,
  identity, and optional-adapter boundaries. Managed organization policy stays
  out of scope; the manifest remains unchanged.

