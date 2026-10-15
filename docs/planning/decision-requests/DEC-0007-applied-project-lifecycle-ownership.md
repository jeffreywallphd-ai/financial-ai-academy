---
id: DEC-0007
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0012-reusable-project-workspace.md
---

# Decision Request: Choose Applied-Project Lifecycle Ownership

## Decision Needed

Choose which module boundaries own applied-project definitions, active learner
project instances, mutable milestone work, artifact manifests, immutable
submissions, deterministic completion evidence, learner projections, and audit
references for CAP-0007.

Use one option label exactly as written below:

- **Option A — Extend the accepted learning-loop owners**
- **Option B — Introduce a dedicated Project module**
- **Option C — Split Workspace artifacts from Assessment submissions**
- **Option D — Add a reusable Project workspace with learning and domain links**

## Why Now

CAP-0007 cannot define public operations, persistence, events, artifact
ownership, submission evidence, projection consumers, write scopes, or slice
acceptance until each project fact has one semantic owner. ADR-0005 accepts the
Content, Curriculum, Assessment, Learner model, and Audit boundaries for the
first lesson loop, but explicitly does not accept every future module or
automatically extend that decision to applied projects.

Deferring the choice is safe and keeps CAP-0007 `decision-blocked`. Implementing
before the choice would let an early repository or API shape establish accidental
architecture authority and could duplicate learner evidence.

## Current Authority and Constraints

- The product catalog requires guided and open-ended applied projects with
  milestones, datasets, notebooks, saved results, reflections, and submissions.
- ADR-0005 assigns versioned resources to Content, curriculum structure and
  prerequisites to Curriculum, assessment definitions/submissions/evidence to
  Assessment, derived progress to Learner model, and trace/integrity references
  to Audit for the first learning loop.
- ADR-0012 accepts Project as the reusable workspace and snapshot owner while
  leaving broad personal-workspace behavior and independently owned domain
  aggregates outside Project.
- The product catalog treats applied learning projects, personal workspaces, and
  simulated portfolios as distinct candidate capabilities. A reusable project
  may reference a Portfolio-owned aggregate, but it cannot become the owner of
  positions, transactions, valuation, market-data provenance, or other
  financial invariants.
- Modules may retain stable external identifiers but cannot import another
  module's internals or persistence. Synchronous collaboration uses public
  application operations; asynchronous collaboration uses versioned events.
- Learner work and submission evidence must be append-oriented or versioned;
  derived completion cannot replace source evidence.
- CAP-0007 must not introduce live financial execution, AI-authoritative
  completion, organization tenancy, instructor review, or credentialing.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| Option A — Extend the accepted learning-loop owners | Reuses validated boundaries: Content owns immutable project instructions and supplied resources; Curriculum owns placement, prerequisites, and milestones; Assessment owns learner project instances, artifact manifests, submissions, deterministic validation, and completion evidence; Learner model owns projections; Audit owns trace references. Minimizes new modules and lets CAP-0007 build directly on CAP-0005 and CAP-0006. | Assessment becomes responsible for a broader and longer-lived evidence workflow; mutable in-progress work must be modeled carefully so it does not blur with immutable submissions; cross-module orchestration is explicit. | Versioned project-definition and placement contracts; Assessment instance/artifact/submission operations and events; Learner-model projection; Audit references; persistence and export ownership; API/generated client. | Moderate. A later dedicated module requires event/contract migration but stable public IDs and evidence boundaries can support extraction if kept explicit. |
| Option B — Introduce a dedicated Project module | Gives project instances, milestones, artifacts, submissions, and project completion one cohesive owner; keeps Assessment focused on bounded assessments; creates a clear extraction candidate if projects become operationally distinct. | Adds a new domain boundary, persistence, public facade, events, tests, and support surface before usage evidence; risks duplicating Assessment completion evidence and Curriculum milestone meaning; requires a new ADR and more composition. | New Project contracts, database schema, events, module checks, exports, API/client, and adapters; revised Assessment/Learner-model/Audit consumption. | Low to moderate after data exists because splitting or folding the module would require durable evidence migration and event compatibility. |
| Option C — Split Workspace artifacts from Assessment submissions | Creates a reusable mutable workspace for notes/files/notebooks while preserving Assessment as the owner of immutable submissions and completion evidence; aligns with the separate personal-workspace product capability. | Pulls a future capability and module forward; introduces the widest orchestration surface and identity/storage lifecycle; creates difficult transactional boundaries between mutable workspace snapshots and immutable submission manifests. | New Workspace contracts and storage; Assessment snapshot/submission contracts; Curriculum project placement; Learner-model/Audit events; export, deletion, quota, and recovery operations. | Low after persisted workspace data and submission references exist; boundary changes require coordinated storage and contract migration. |
| Option D — Add a reusable Project workspace with learning and domain links | Introduces one focused Project module that owns a user project shell, origin, lifecycle, mutable workspace, versioned artifact manifests, and immutable workspace snapshots. Learning-bound projects reference Content-owned briefs and Curriculum-owned placement, prerequisites, and milestone requirements; Assessment owns immutable submissions and completion evidence that reference a closed Project snapshot. Personal or domain-linked projects can exist without Assessment. A Project may reference a Portfolio-owned portfolio or other domain aggregate without taking ownership of its invariants. This combines Option A's learning integration, Option B's independent project identity, and Option C's mutable-work versus immutable-submission separation without adding a separate general Workspace module immediately. | Adds a real domain boundary, public facade, persistence, events, authorization, retention, export, and snapshot-consistency obligations before the first learning project. It creates two related lifecycles—Project workspace state and Assessment submission state—and risks becoming a generic container or god module. Domain links, deletion, portability, quotas, and interrupted snapshot creation need explicit policy. It is unjustified complexity if independent personal or domain-linked projects are only speculative. | New Project shell/workspace/snapshot contracts and persistence; Content/Curriculum origin references; Assessment submission-by-snapshot contracts; optional stable references to Portfolio and later domain owners; Learner-model consumption only for learning evidence; Audit trace references; API/generated client; export, deletion, retention, and authorization policy. | Moderate before broad adoption if public IDs and snapshots are closed and versioned; low after personal projects, learning submissions, and domain links depend on the boundary. Removing or repartitioning it would require coordinated project, artifact, submission, and reference migration. |

## Option D Boundary Sketch

Option D is viable only if the Project boundary stays narrow:

- **Project** owns the reusable project identifier, owner, origin, user-authored
  charter, project lifecycle, mutable workspace, versioned artifact manifests,
  and immutable digest-bound workspace snapshots.
- **Content** owns immutable learning project briefs, instructions, supplied
  resources, sources, and publication state. Project stores only an exact
  reference when its origin is learning-bound.
- **Curriculum** owns learning placement, prerequisites, milestone requirements,
  and availability. Project may track work against exact milestone identifiers
  but does not redefine their learning meaning.
- **Assessment** owns immutable learning submissions, deterministic validation,
  and completion evidence. A submission references one closed Project snapshot;
  it never copies or mutates the live workspace.
- **Portfolio** and other domain modules own their aggregates and calculations.
  A personal or domain-linked Project stores a stable public reference or closed
  evidence snapshot, not portfolio positions, transactions, valuation rules, or
  market-data truth.
- **Learner model** consumes only Assessment evidence for learning projections.
  Merely creating or advancing an independent Project has no learning-progress
  meaning.
- **Audit** retains transition, snapshot, submission, and integrity references
  without becoming a second project or domain database.

The dependency direction remains one-way. Project may resolve learning or domain
references through public operations or platform-owned gateways. Assessment may
read an immutable Project snapshot through the Project public surface. Content,
Curriculum, Portfolio, and other domain owners do not import Project internals,
and Project never imports Assessment to decide completion.

The project origin should be a closed, versioned union such as `learning`,
`personal`, or `domain-linked`. Adding a new origin requires an explicit adapter
contract and cannot silently grant learning, financial, execution, or provider
authority.

## Recommendation

**Recommend Option D — Add a reusable Project workspace with learning and
domain links.**

Verified facts: CAP-0005 and CAP-0006 require Curriculum, Assessment,
Learner-model, and Audit seams that Project must reuse for learning-bound work.
The product catalog also treats applied projects, personal workspaces, and
simulated portfolios as distinct capabilities. Projects are expected to
continue outside lessons and associate with independently owned resources, so
placing every mutable project instance in Assessment would mix unrelated
lifecycles.

Assumption: the initial Project workspace remains bounded to one learner and one
project, does not introduce real-time collaboration, and can close an immutable
snapshot without locking later workspace revisions. Portfolio and other domain
links use public identifiers and provenance; their owning modules remain
authoritative.

Inference: Option D is the smallest boundary that supports both learning-bound
and independent projects without making Assessment a general workspace. It is
more coherent than adding separate Project and Workspace modules now, and safer
than treating a portfolio as a project. The complexity is justified by the
cross-capability requirement, but delivery must establish the Project shell and
snapshot boundary before learning submission or live domain adapters.

## Evidence Required

- A boundary walkthrough assigning each CAP-0007 fact and invariant to exactly
  one owner under all four options.
- Public operation and event sketches for start, save, resume, validate, submit,
  supersede, project-completion projection, and audit referencing.
- A data-ownership and transaction analysis covering mutable work, immutable
  submission manifests, idempotency, interruption, export, deletion, and replay.
- A module-dependency review proving there is no cross-module persistence access
  or reverse dependency.
- A scale/reversibility assessment for expected artifact count/size and likely
  extraction triggers. No implementation prototype is required to choose
  Option A, but selecting B, C, or D should include a bounded seam prototype.
- For Option D, a lifecycle matrix proving that Project workspace state,
  Assessment submission state, learning completion, and referenced Portfolio or
  domain state cannot overwrite or imply one another.
- For Option D, a public-contract sketch for closing a workspace snapshot,
  submitting it for learning evidence, retaining a live successor workspace,
  and deleting or exporting the project without corrupting immutable evidence.
- Product sequencing evidence that at least one independent personal or
  domain-linked project flow is near enough to justify establishing the shared
  boundary before CAP-0007 delivery.

## Required Authority

The product and architecture owner must choose the domain boundary. Security and
data owners must confirm that the selected owner can satisfy learner evidence,
artifact protection, export, and deletion obligations. This tracked request
does not record any person's identity or decision.

## Decision Record and Promotion

ADR-0012 is the current accepted record for Option D and supersedes ADR-0010.
It fixes the ownership table, public dependency direction, snapshot boundary,
domain-reference posture, and future expansion gates. Exact contracts remain
subject to CAP-0007 slice planning and executable review.
Update the module map, decision-readiness register, relevant architecture and
domain documents, and planning context before marking DEC-0007 complete.

## Dependent Planning Updates

- Reconcile CAP-0007 scope, slice contracts, acceptance, risks, and documentation
  impact to the selected option before seeking CAP approval.
- Keep DEC-0008 coupled as the artifact/execution boundary; neither decision
  resolves the other.
- Later `select-vertical-slice` and `author-agent-work-packet` work must name the
  accepted owners and refuse cross-module persistence access.
- Revisit the future personal-workspace and instructor-review capabilities so
  they consume rather than duplicate CAP-0007 evidence.
- Keep Portfolio and other domain aggregates independently authoritative; shape
  their public contracts before activating a live Project adapter.

## Planning History

- 2026-10-15: Created from CAP-0007 decision-gate review as one member of the
  related applied-project decision set with DEC-0008.
- 2026-10-15: Added Option D as a non-authoritative reconsideration preview that
  combines a reusable Project workspace, existing learning owners, immutable
  Assessment submissions, and references to independently owned domain
  aggregates. At that point ADR-0010 remained current pending a later explicit
  decision and superseding ADR.
- 2026-10-15: ADR-0012 superseded ADR-0010 and established Option D's Project
  workspace, snapshot, learning-submission, and domain-link ownership boundary.
