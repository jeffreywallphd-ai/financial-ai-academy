---
id: SLI-0033
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: CAP-0007
depends_on: ["SLI-0030", "SLI-0031", "SLI-0032"]
decision_gates: []
---

# Vertical Slice: Qualify the Complete Applied Project Capability

## Outcome and User Scenario

An authorized learner can create an independent Project or start from an exact
learning brief, save and resume mutable work, retain inert resources with clear
provenance, close immutable snapshots, continue the live workspace, and submit
an exact learning-bound snapshot without changing earlier evidence. Browser and
non-browser clients use the same protected public API and the same shared
domain/application core.

This final CAP-0007 increment produces cumulative evidence for the complete
Project journey and closes only material gaps found by that qualification. It
does not add a second Project workflow, duplicate every focused test, invent a
live Portfolio target, or turn harmless wording, styling, IDs, timestamps,
fixture counts, or response ordering into functional requirements.

## Scope Boundaries

### In Scope

- Map every CAP-0007 acceptance statement to current contract, domain,
  application, real-PostgreSQL, API, generated-client, browser, live,
  architecture, security, accessibility, or recovery evidence.
- Run a cumulative Project-focused matrix from independent or learning origin
  through mutable workspace, inert artifact handling, typed references,
  immutable snapshot/export, learning submission, derived completion, Audit
  reference, normal restart, and browser/headless parity.
- Verify that Project owns its shell, workspace, artifact manifest, typed-link
  references, and snapshots; Assessment owns immutable learning submissions;
  Learner model and Audit consume only public events and projections.
- Prove provenance categories remain distinguishable, snapshot and export
  records remain digest-bound, artifact handling remains inert, and no Project
  surface gains compute, package, network, secret, provider, callback, or host
  execution authority.
- Verify zero-or-many typed domain links preserve only owner-issued references,
  never copy domain state, and present unavailable, stale, removed, or
  unauthorized owner status explicitly. The synthetic contract owner used for
  qualification must not be described as a live Portfolio integration.
- Inspect malformed, unsafe, oversized, unsupported, stale, unauthorized,
  cross-learner, duplicate, interrupted, partially persisted, replay,
  conflict, and supersession behavior with bounded diagnostics and no false
  completion.
- Confirm private-host restart durability, cleanup containment, shared
  local/future-cloud semantics at the port and contract boundary, accessible
  responsive/theme behavior, and equivalent API meaning for generated browser
  and ordinary supported non-browser clients.
- Keep anti-rigidity evidence explicit: valid notes, references, artifacts,
  links, origins, snapshots, and submissions may vary in count, content, safe
  metadata, ordering where semantically unordered, IDs, and timestamps without
  invalidating the workflow.
- Reconcile only documentation, evidence maps, known gaps, planning state, and
  bounded qualification controls made stale by the cumulative result.
- Close SLI-0033 and CAP-0007 deterministically when the current evidence maps
  to every acceptance statement and no material defect remains.

### Out of Scope

- A live Portfolio adapter, copied Portfolio state, portfolio calculation,
  market data, real or simulated financial execution, or provider-backed
  domain-resource resolution.
- Platform-managed or provider-managed execution, active notebook/code
  rendering, kernels, subprocesses, package installation, runtime images,
  callbacks, outbound network, secrets, or claims that learner results were
  independently reproduced.
- Managed-cloud composition, organization tenancy, key management, cloud
  storage, cloud recovery, queue selection, quotas, or production operations.
- Instructor workflows, manual or AI grading, certification, collaboration,
  public sharing, publishing, external notifications, or organization roles.
- A separate AI endpoint, agent protocol, browser-only backend, autonomous
  authority, or duplicate headless application core. Future AI clients may use
  the public API qualified here.
- Styling-only polish that does not impair operation, meaning, accessibility,
  responsive behavior, or theme parity. Optional cleanup remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0007](../capabilities/CAP-0007-complete-applied-projects.md) defines the
  complete four-slice Project outcome and final qualification increment.
- [SLI-0030](SLI-0030-create-independent-or-learning-project.md),
  [SLI-0031](SLI-0031-save-project-work-and-close-a-snapshot.md), and
  [SLI-0032](SLI-0032-submit-a-project-snapshot-for-learning.md) supply the
  implemented Project behavior and focused evidence.
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) assigns Project,
  Assessment, Learner model, Content, Curriculum, and Audit ownership and
  requires exact immutable snapshot references across those boundaries.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) makes every
  dataset, notebook, code file, environment declaration, and result an inert,
  untrusted artifact with no platform execution authority.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md) requires one shared
  domain/application core across deployment profiles.
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
  bounds direct recovery evidence to private-host community operation.
- [Module Map](../../architecture/modules/module-map.md),
  [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  and [Community Evidence Protection](../../security/community-learner-evidence-protection.md)
  govern ownership, public boundaries, and private-host evidence handling.
- Decision readiness is sufficient for provider-neutral cumulative
  qualification of the implemented private-host workflow. Tenancy, managed
  cloud, live domain providers, external execution, and broader authority remain
  outside this slice.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Reuse the three focused slice evidence sets, run one cumulative API-first Project matrix, close only concrete gaps, and record a CAP acceptance map | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add a broad meta-runner that reruns every repository check without mapping evidence to Project acceptance | yes | 1 | 1 | 2 | 2 | 1 | 1 | 2 | 10 |
| C. Add a live Portfolio provider or domain-resource implementation to make typed-link evidence less synthetic | no - Portfolio contracts and provider authority belong to later capabilities | - | - | - | - | - | - | - |
| D. Qualify a managed-cloud deployment, external execution provider, or independent result reproduction | no - it crosses unresolved tenancy, provider, execution, protection, and recovery boundaries | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 and is the only complete conforming refinement. It
produces the approved observable outcome with current public contracts and
focused evidence, then adds only the cross-flow proof needed to close CAP-0007.
It is independently verifiable, decision-ready, additive, and reversible.

Candidate B is eligible but creates a slower and more rigid gate without
showing which Project claim each check supports. Candidate C would invent live
Portfolio semantics that CAP-0007 explicitly excludes. Candidate D crosses
durable decision gates and would misstate the available evidence. Candidate A
wins without a tie-break.

## Boundary Path

1. Reuse SLI-0030 evidence for exact independent and learning origin, Project
   identity, immutable provenance, authorization, PostgreSQL durability, and
   generated-browser/headless API parity.
2. Reuse SLI-0031 evidence for mutable notes and references, inert artifact
   bytes, typed domain-reference isolation, snapshot closure, continued work,
   exact export, restart, and execution denial.
3. Reuse SLI-0032 evidence for exact learning-bound snapshot submission,
   deterministic validation, immutable Assessment evidence, supersession,
   bounded Learner-model projection, and append-only Audit references.
4. Run a focused cumulative matrix that crosses the three seams without
   duplicating their full internal suites and verifies that independent work
   never creates learning completion while learning submissions never mutate
   the live Project or earlier snapshot evidence.
5. Reproduce the reviewed OpenAPI and generated TypeScript client, then prove
   that generated browser traffic and an ordinary authenticated HTTP client
   traverse the same protected Project operations.
6. Verify module ownership, inertness, privacy, private-host durability,
   accessibility, containment, and shared-core semantics with exact checks and
   an acceptance-to-evidence map.
7. Route any material product defect to a separately bounded corrective packet;
   fix inconsequential issues in scope or defer optional polish to CAP-0031.
8. Close the slice and CAP only after every acceptance claim is direct,
   explicitly representative, or truthfully recorded as unqualified.

## Contracts, Data, and Provenance

No new product contract, table, route, event, provider port, migration, or
generated-client shape is planned. Qualification consumes the accepted Project
shell, origin, workspace, resource, inert-artifact, typed-link, snapshot,
export, learning-submission, completion-projection, and Audit-reference
contracts.

Evidence must retain exact Project, learner scope, origin, Content package,
Curriculum placement, workspace revision, record version/digest, artifact
classification/content digest, environment declaration, typed owner reference,
snapshot, submission occurrence/supersession, validation policy, Assessment
event, Learner-model source, Audit reference, schema, and tool versions or
digests. Reports remain categorical and privacy-minimized; they do not retain
learner identity, cookies, credentials, artifact bytes, host paths, private
provider data, or raw diagnostics.

The accepted provenance categories for observed data, deterministic
calculation, simulation, model prediction, AI-generated interpretation, and
learner-authored reflection remain labels and evidence claims, not a grant of
truth, safety, reproducibility, advice, or execution authority.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Complete independent journey | The learner creates, reopens, edits, resumes, snapshots, exports, and continues an independent Project without any Assessment or Learner-model completion state | live API/Chromium/PostgreSQL |
| Complete learning-bound journey | The learner starts from exact learning sources, snapshots work, submits that exact snapshot, and reopens immutable evidence while later live work and snapshots remain separate | live API/Chromium/PostgreSQL |
| Canonical ownership | Project, Content, Curriculum, Assessment, Learner model, and Audit interact only through their owned public operations/events with no cross-schema reads or copied authority | architecture/application/PostgreSQL |
| Provenance and immutable history | Origins, resources, artifacts, links, snapshots, exports, submissions, projections, and Audit references retain exact versions/digests and earlier evidence cannot be rewritten | contract/domain/PostgreSQL/restart |
| Typed-link isolation | Zero or multiple owner-issued references remain references only; changed, stale, removed, unauthorized, and unavailable targets are explicit without copied domain state or a live Portfolio claim | contract/application/API/browser |
| Inert artifact confinement | Upload, passive inspection, download, snapshot, export, and submission never activate code, network, packages, secrets, providers, callbacks, host paths, or hidden rendering | contract/architecture/security/live |
| Replay, conflict, and interruption | Exact retries are stable; changed reuse conflicts; interrupted writes/rebuilds preserve the prior complete state; restart retains accepted meaning | application/PostgreSQL/API/live |
| Confidential authorization | Missing permission, caller-selected identity, guessed IDs, and cross-learner access fail closed with bounded learner-safe errors and no private existence leak | API/security/live |
| API/headless parity | Generated browser and supported non-browser clients use the same protected Project operations and shared core with no UI-only authority | OpenAPI/client/architecture/live |
| Accessible equivalent views | Origin, workspace, artifacts, links, snapshots, submission, history, errors, and status retain keyboard/focus/reflow/theme/forced-color/reduced-motion meaning | component/Chromium/design |
| Shared-core and recovery bounds | Deployment-neutral ports and contracts are direct evidence; private-host restart is direct while managed-cloud composition and recovery stay explicitly unqualified | architecture/live/documentation |
| Anti-rigidity | Compatible counts, safe metadata, semantically unordered input, generated IDs/times, plain wording, and nonfunctional styles do not become accidental acceptance constraints | focused mutation tests/review |
| Containment and cleanup | Qualification uses isolated state, terminates its owned processes/containers, and emits no secret, personal identifier, or unbounded artifact | runner/security/live |

## Agent Work Packets

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| JIT-A | Run the cumulative Project capability matrix, close only directly observed acceptance gaps, reconcile the evidence and known-gap maps, and deterministically close SLI-0033 and CAP-0007 | SLI-0030, SLI-0031, SLI-0032 | none | captured |

The packet identifier is reserved and the bounded packet is authored immediately
before activation. If qualification finds a material product defect, JIT-A
stops and a new corrective packet is reserved inside this slice rather than
hiding product changes in an evidence-only packet.

## Verification and Qualification

Run the Project contract/domain/application/API and real-PostgreSQL suites;
module-boundary, migration, concurrency, rollback, replay/rebuild, authorization,
and inertness checks; OpenAPI and generated-client reproduction; relevant web
unit/component tests; TypeScript typecheck, lint, and build; focused Project
Chromium flows; and the isolated approved-lesson PostgreSQL/Python/headless/
Chromium workflow.

Run focused harness anti-rigidity and containment tests, security, learner-
language, design-system, documentation, planning, whitespace, exact-candidate
affected verification, technical review, completion structure, and the fixed
aggregate readiness gate. Reuse current exact evidence when its candidate and
affected boundary are unchanged. Rerun a check only when the packet changes
that boundary or freshness is necessary to close a claim; do not require an
unrelated full rerun merely to obtain a newer timestamp.

## Rollback and Migration

The selected work is qualification and documentation unless it finds a bounded
defect. It adds no planned migration or public contract. Rollback removes only
new qualification assertions and evidence documentation; delivered Project
behavior remains intact. A persistence correction must preserve accepted
Project, snapshot, submission, projection, and Audit evidence through a
separately bounded forward-compatible packet rather than destructive rollback.
Ephemeral test state may be deleted only inside the isolated qualifier.

## Stop Conditions

Stop for changed CAP outcome or slice manifest; Project ownership drift; a live
Portfolio or other provider integration; copied domain state; external or
arbitrary execution; active rendering; organization tenancy; collaboration;
managed-cloud, encryption, key, queue, quota, or recovery choices; instructor
or AI authority; breaking public contracts; destructive evidence handling;
cross-module persistence access; duplicate browser/headless cores; private
learner or artifact leakage; stale CAP binding; active write collision; or
inability to prove qualification containment.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential correction. Fix it locally within scope or defer optional
polish to CAP-0031.

## Documentation Impact and Completion Evidence

Reconcile CAP-0007, the architecture-verification map, known verification gaps,
affected module/security/deployment guidance, SLI-0033, its bounded work packet,
and the planning register. Completion evidence must map every CAP acceptance
statement to an owning exact check; identify changed boundaries; record
contract and migration compatibility; distinguish direct private-host/shared-
core evidence from unqualified managed-cloud/provider behavior; state checks
not performed; and identify assumptions, residual risks, and follow-up work.

The final evidence must state that Portfolio integration, external providers,
managed cloud, production recovery, independent result reproduction, arbitrary
execution, collaboration, instructor workflows, public publishing, a separate
AI mode, and autonomous authority were not planned or added.

## Planning History

- 2026-10-17: Refined the final CAP-0007 manifest increment after SLI-0030
  through SLI-0032 completed. Candidate A scores 14/14 and uses an evidence-
  first cumulative matrix with one bounded packet. It preserves the API-first
  browser/headless shared core, reuses current focused evidence, and avoids a
  duplicate meta-runner or inconsequential acceptance gates.
