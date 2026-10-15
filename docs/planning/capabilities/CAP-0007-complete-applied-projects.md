---
id: CAP-0007
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0005", "CAP-0006"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0030", "SLI-0031", "SLI-0032", "SLI-0033"]
---

# Capability: Complete Applied Projects

## Outcome

An individual learner can create an independent applied project or branch from
an approved learning project, maintain a bounded workspace of resources and
inert artifacts, associate the project with independently owned domain resources
such as one or more simulated portfolios when their public contracts are
available, close immutable workspace snapshots, and optionally submit an exact
snapshot as learning evidence without the platform implying live financial
execution or arbitrary notebook/code authority.

## Users and Value

Learners need to integrate concepts in work that can begin inside a curriculum
and continue beyond it, or start independently around a question, portfolio,
dataset, or analytical goal. Value is observable when a learner can preserve a
project's origin, charter, resources, intermediate work, linked domain context,
and result provenance; resume after interruption; and freeze an exact snapshot
without giving up the live workspace.

Learning submissions can consume a frozen snapshot without turning every
project into an assessment. Future instructors can review the resulting
versioned evidence through a separate capability, while community and cloud
operators retain one provider-neutral Project meaning and explicit execution
boundary.

## Scope

### In Scope

- A Project-owned shell with stable identity, learner ownership, user-authored
  title and charter, origin, lifecycle, and project-scoped authorization.
- Creation either from an approved Content brief and exact Curriculum placement
  or as an independent out-of-lesson project. Learning-initiated projects retain
  exact source provenance but can continue outside the lesson.
- A bounded mutable Project workspace containing notes, resource links, dataset
  manifests, notebook or code files, result files, assumptions, environment
  metadata, reflections, and versioned inert-artifact manifests. Learners
  execute tools outside the platform in environments they control.
- Typed, versioned, many-valued links from Project to independently owned domain
  resources. The design permits links to multiple Portfolio-owned resources,
  but a live Portfolio adapter is qualified only after Portfolio public
  contracts, calculations, provenance, and authorization are accepted.
- Immutable digest-bound Project snapshots that close one exact workspace state
  while allowing the live project to continue through later revisions.
- Provenance that distinguishes supplied data, learner-created artifacts,
  deterministic calculations, simulations, model predictions, and narrative
  interpretation.
- Optional immutable Assessment submission evidence bound to one exact Project
  snapshot, learning brief, curriculum placement, learner context, dataset and
  environment versions, and completion policy. Independent projects need no
  Assessment record and imply no learner progress.
- Deterministic validation of required milestones and artifact closure. Any
  qualitative instructor feedback or override remains a later capability.
- Interruption-safe resume, idempotent snapshot and submission behavior,
  learning-source and domain-link version handling, exportable project evidence,
  and accessible responsive learner behavior.
- Shared domain and contract semantics for local and cloud profiles; adapters
  may differ only after their execution, storage, identity, and data-use
  authority is accepted.

### Out of Scope

- Live brokerage, custody, trade execution, personalized portfolio suitability,
  guaranteed performance, or production financial decision automation.
- Instructor grading, feedback, revision requests, manual overrides, peer
  review, cohort management, certification, or accreditation.
- AI-authoritative grading, AI-selected completion, autonomous agents modifying
  submitted evidence, or generated claims without source and version evidence.
- General collaborative documents, broad personal workspace organization, or
  unrestricted file storage unrelated to the active project.
- Ownership or reimplementation of portfolio positions, transactions,
  valuation, rebalancing, performance, risk, or market-data provenance inside
  Project. Live portfolio linking remains outside delivery until the Portfolio
  public boundary is accepted.
- Licensed market-data providers, external model providers, organization
  tenancy, enterprise identity, billing, or managed-cloud operations unless
  separately decided and admitted.
- Public sharing, publishing, deployment, external notifications, or execution
  of a learner's work against real financial accounts or systems.
- Platform-managed or provider-managed notebook/code execution, active artifact
  rendering, network or secret access, package installation, runtime images,
  execution callbacks, or claims that the platform reproduced learner results.

## Canonical Context

- [Product Capability Catalog](../../product/capability-catalog.md)
- [Product Vision and Scope](../../product/product-vision-and-scope.md)
- [Product Non-Goals](../../product/non-goals.md)
- [Initial Glossary](../../domain/glossary.md)
- [Module Map](../../architecture/modules/module-map.md)
- [First Learning Loop Ownership](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
- [Reusable Project Workspace](../../adr/ADR-0012-reusable-project-workspace.md)
- [Inert Applied-Project Artifacts](../../adr/ADR-0011-inert-applied-project-artifacts.md)
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Security Architecture](../../security/README.md)
- [Community Evidence Protection](../../security/community-learner-evidence-protection.md)
- [Education Versus Financial Advice](../../risk-compliance/education-versus-financial-advice.md)
- [Interface Design System](../../design/README.md)
- [CAP-0005](CAP-0005-navigate-competency-based-curriculum.md)
- [CAP-0006](CAP-0006-practice-and-demonstrate-understanding.md)
- [DEC-0007](../decision-requests/DEC-0007-applied-project-lifecycle-ownership.md)
- [DEC-0008](../decision-requests/DEC-0008-project-artifact-execution-boundary.md)

## Decision Gates and Constraints

- ADR-0012 assigns learning-initiated and independent identity, charter,
  lifecycle, mutable workspace, artifact manifests, immutable snapshots, and
  typed learning/domain links to Project. Content and Curriculum retain learning
  definition and placement authority. Assessment owns only immutable learning
  submissions, deterministic validation, and completion evidence by exact
  snapshot reference. Learner model and Audit retain projection and trace roles.
- ADR-0011 makes every dataset, notebook, code file, environment declaration,
  and result an untrusted inert artifact. The platform provides no kernel,
  subprocess, package installation, network, secret, runtime image, provider
  callback, or execution job. Learners run tools externally and return bounded
  evidence whose validation does not prove code safety or result truth.
- CAP-0005 is required for the learning-initiated origin, versioned objectives,
  prerequisites, milestones, and curriculum placement. CAP-0006 is required for
  optional Assessment submission evidence, deterministic completion policy,
  retry/version behavior, and learner history. Independent Project behavior
  creates no substitute learning evidence.
- Every dataset, notebook, code artifact, environment, model result, simulation,
  and narrative output remains explicitly typed, digest-bound, resource-bounded,
  and provenance-bearing. A file upload never becomes trusted merely because it
  belongs to a project, and previews remain passive and allowlisted.
- Authorization, milestone requirements, artifact closure, submission,
  completion, and durable state changes remain deterministic. AI/ML output is
  versioned input and cannot approve its own evidence.
- Project may retain typed references to zero or more domain resources, but
  owning modules remain authoritative. A link never grants persistence access,
  provider authority, or permission to copy or recalculate domain state. The
  first live Portfolio adapter requires accepted Portfolio contracts and is not
  implied by this CAP package.
- Community operation must stay inside ADR-0008's private-host and recovery
  limits. Managed-cloud protection, key, sandbox, tenancy, quota, and recovery
  choices remain unavailable without separate decisions.
- Platform-managed or provider-managed execution, a general Workspace module,
  active rendering, organization tenancy, external data/model providers, or
  broader cloud protection requires a new durable decision and material CAP
  reshaping before implementation.
- The decision gates are resolved and the reconciled package has its one
  CAP-level planning approval. Delivery remains ordered behind CAP-0005 and
  CAP-0006 and still uses just-in-time slice and work-packet refinement.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0030 | A learner creates one authorized independent Project with a personal charter or branches from one approved learning brief into a Project that preserves exact Content and Curriculum provenance and can continue outside the lesson. | First after CAP-0005 and CAP-0006 for the learning-origin path; establishes the ADR-0012 Project shell, closed origin union, lifecycle, authorization, public operations, and persistence boundary. | Moving Project ownership, adding organization or collaborative ownership, making source provenance mutable, or turning Project into a general workspace changes the CAP package. | captured |
| SLI-0031 | The learner safely saves, versions, inspects through passive allowlisted behavior, downloads, links, and resumes bounded Project resources and inert artifacts, then closes an immutable snapshot while continuing the live workspace. | After SLI-0030; establishes ADR-0011 confinement and execution denial plus ADR-0012 artifact manifests, snapshots, many-valued typed domain links, stale/unavailable-owner behavior, and export semantics. A live Portfolio adapter remains gated on accepted Portfolio contracts. | Adding execution, active rendering, network/secret access, unrestricted storage, copied domain state, real financial actions, or an unaccepted provider changes the CAP package. | captured |
| SLI-0032 | For a learning-bound project, the learner submits one exact Project snapshot, receives deterministic missing/invalid requirement feedback, and can reopen immutable Assessment evidence and derived completion while the live Project workspace remains independent and later snapshots do not overwrite history. | After SLI-0031; introduces idempotent Assessment submission by snapshot reference, exact learning versions, Learner-model projection, Audit references, and supersession rules. Independent projects remain valid without this path. | Making every project an assessment, instructor grading/override, AI-authoritative completion, collaborative submission, certification, or mutable submitted evidence changes the CAP package. | captured |
| SLI-0033 | Independent and learning-bound Project flows are qualified for provenance, snapshot integrity, typed-link isolation, declared reproducibility, artifact confinement, execution denial, interruption/resume, version drift, authorization, community protection, accessibility, responsive/theme parity, and shared local/cloud semantics. | Last; depends on SLI-0030 through SLI-0032 and closes ADR-0012 ownership/snapshot obligations and ADR-0011 inert-artifact obligations without claiming live Portfolio integration or independent result reproduction. | Qualifying live Portfolio behavior, managed-cloud tenancy/recovery, execution, external providers, instructor workflows, public publishing, or live financial execution changes the CAP package. | captured |

## Capability Acceptance

The capability is complete only when evidence demonstrates that:

- project identity, charter, mutable workspace, artifact manifests, immutable
  snapshots, learning submissions, domain resources, completion evidence, and
  projections each have one canonical owner under ADR-0012 and cross only public
  operations or versioned events;
- ADR-0011 is enforced so no notebook, code, dataset, artifact, or external tool
  can obtain platform compute, network, secrets, provider execution, or host
  resources; learners execute tools only in environments they control;
- a learner can create an independent project or branch from exact learning
  sources, save and resume mutable work, close an immutable snapshot, continue
  the live workspace, and optionally submit the exact snapshot without duplicate
  projects, lost work, mutable submitted evidence, or silent source migration;
- a Project can retain multiple typed links without copying referenced domain
  state; stale, removed, unauthorized, or unavailable targets fail explicitly,
  and Project makes no live Portfolio claim before that public contract exists;
- workspace snapshots and evidence manifests are closed, versioned,
  digest-bound, size/resource bounded, and traceable to learning sources, domain
  links, datasets, environments, artifacts, results, assumptions, and reflection;
- independent Project activity creates no learner completion or mastery state,
  while an authorized Assessment submission retains the exact snapshot and
  learning requirements used for deterministic completion evidence;
- observed data, deterministic calculations, simulations, model predictions,
  and AI-generated interpretation are distinguishable in contracts and UI;
- malformed, unsafe, oversized, unsupported, stale, unauthorized,
  cross-learner, duplicate, interrupted, and partially persisted work fails with
  bounded diagnostics and no false completion;
- export and replay preserve evidence meaning without including secrets,
  provider credentials, host paths, or unauthorized source data;
- local and cloud adapters conform to the same project semantics while inert
  handling, unavailable execution, and unsupported recovery profiles remain
  explicit; and
- milestone, artifact, provenance, validation, submission, and history views
  meet keyboard, focus, error association, non-color state, zoom/reflow,
  reduced-motion, forced-color, both-theme, and assistive-technology expectations.

## Risks and Non-Goals

- Project scope can become a general IDE, notebook platform, data warehouse, or
  file-sharing product unless artifact and execution authority stays explicit.
- Dataset and model artifacts can introduce license, privacy, leakage, malware,
  secret, and resource-exhaustion risks even when no code is executed.
- Results can be mistaken for observed performance or investment advice unless
  provenance and simulation/prediction labels remain prominent.
- Project can become a god module if it absorbs portfolio calculations, global
  notes, conversations, provider behavior, or unrelated files. The accepted
  boundary is project-scoped workspace, snapshots, and references only.
- Snapshot closure, live-workspace continuation, submission retention, link
  removal, and project deletion have different lifecycles and can create
  dangling or misleading evidence unless exact historical references are
  preserved.
- Portfolio linking is architecturally accepted but not operationally ready;
  prematurely implementing it would invent Portfolio semantics and financial
  calculation authority.
- Managed execution and external connectors have materially different security,
  cost, reproducibility, and support obligations and remain explicit future
  decision boundaries.

## Documentation Impact

Delivery is expected to refine Project origin, lifecycle, workspace, snapshot,
resource-link, domain-link, export/deletion, and Assessment-submission
vocabulary; exact contract families and resource limits; the inert-artifact
threat model; data provenance and license guidance; community protection;
interface patterns; operations; module READMEs; architecture verification; and
known gaps while preserving ADR-0011 and ADR-0012.

## Planning History

- 2026-10-15: Shaped from the catalog candidate “Complete applied projects” as
  a complete provisional `cap-package-v1` manifest. CAP-0005 and CAP-0006 are
  the hard delivery foundations. DEC-0007 and DEC-0008 were created as one
  related decision set; the CAP cannot be approved or delivered until both are
  promoted canonically and the package is reconciled to their selected options.
- 2026-10-15: Reconciled the package to ADR-0010's learning-loop ownership and
  ADR-0011's inert-artifact boundary. The complete slice manifest remains
  SLI-0030 through SLI-0033 and is ready for one CAP-level planning review.
- 2026-10-15: Reshaped the package around ADR-0012. Project now owns reusable
  learning-initiated and independent workspaces and immutable snapshots;
  Assessment consumes snapshots only for learning submissions; and typed links
  may reference multiple independently owned domain resources. The slice
  manifest remains SLI-0030 through SLI-0033 and requires a fresh CAP-level
  planning review before delivery.
