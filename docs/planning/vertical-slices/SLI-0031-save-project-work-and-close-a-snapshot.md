---
id: SLI-0031
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: CAP-0007
depends_on: [SLI-0030]
decision_gates: []
---

# Vertical Slice: Save Project Work and Close a Snapshot

## Outcome and User Scenario

An authorized learner reopens a Project, saves bounded notes and references,
adds versioned inert files with clear source and result meaning, safely inspects
their metadata, downloads the original bytes, and closes an immutable snapshot
of one exact workspace revision. The live Project remains available for later
work after the snapshot closes. The same public operations support generated
browser and non-browser/headless clients without adding execution authority.

The slice also establishes a provider-neutral, many-valued domain-resource
link contract. A link can be accepted only through an available owning-module
public operation; no live Portfolio adapter or copied Portfolio state is
claimed in this increment.

## Scope Boundaries

### In Scope

- Define a Project-owned, revisioned workspace containing bounded learner
  notes, safe external reference metadata, inert artifact manifests, and typed
  domain-resource references.
- Define a closed inert-artifact classification for dataset, notebook, code,
  environment, result, reflection, and supporting-file evidence. Preserve an
  explicit result classification such as observed, calculated, simulated,
  predicted, or generated where applicable.
- Admit artifact bytes through strict type, size, count, normalized-path,
  digest, and provenance validation. Store and return bytes without executing,
  expanding archives, following links, or actively rendering content.
- Support learner-authorized metadata inspection and safe download with
  content-disposition and content-type behavior that never treats an artifact
  as trusted merely because it belongs to a Project.
- Use optimistic workspace revision checks plus idempotency so exact retries do
  not duplicate resources or artifacts and stale concurrent edits fail without
  overwriting accepted work.
- Define many-valued typed domain links by owning module, resource type, stable
  identifier, exact version or as-of evidence when available, link meaning,
  and provenance. Validate links only through an owning public operation and
  preserve explicit stale, removed, unauthorized, and unavailable-owner
  outcomes.
- Close an immutable, digest-bound snapshot over one exact Project shell,
  workspace revision, notes, references, artifact versions, and accepted
  domain links while allowing subsequent live-workspace revisions.
- Provide a deterministic evidence export whose manifest preserves snapshot,
  artifact, link, source, environment, assumption, and classification meaning
  without secrets, host paths, provider credentials, or unauthorized source
  data.
- Expose Project workspace, artifact, link, snapshot, download, and export
  behavior through Project application operations and the protected public API
  used by generated browser, service, command-line, and future headless AI
  clients.
- Deliver a plain-language, keyboard-accessible, responsive Project workspace
  and snapshot flow. Exact versions, digests, and IDs remain available in an
  accessible Technical record.

### Out of Scope

- Platform-managed or provider-managed notebook, code, model, calculation, or
  artifact execution; kernels, subprocesses, package installation, runtime
  images, network, secret access, callbacks, or active rendering.
- Claims that artifact code is safe, a result is true, an environment is
  reproducible, or the platform independently reproduced learner work.
- A live Portfolio adapter, Portfolio calculations or state, market-data
  providers, copied positions or transactions, financial actions, or
  personalized investment advice.
- Assessment submission, deterministic completion, Learner-model projection,
  instructor feedback, review, grading, override, certification, or any
  mutation of learning progress; those remain SLI-0032 and later capabilities.
- General-purpose file storage, global bookmarks or notes, conversations,
  collaboration, public sharing, publishing, deployment, or a broad Workspace
  module.
- Organization tenancy, managed-cloud storage/recovery, external providers,
  malware-service selection, or a separate local/cloud domain core.
- Styling-only cleanup that does not affect meaning, function, accessibility,
  or theme parity; optional polish may remain for CAP-0031.

## Canonical Context and Decisions

- [CAP-0007](../capabilities/CAP-0007-complete-applied-projects.md) defines
  this second observable increment and keeps submission in SLI-0032.
- [SLI-0030](SLI-0030-create-independent-or-learning-project.md) supplies the
  completed Project shell, learner ownership, immutable origin, public API, and
  generated-client foundation.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) requires
  inert, bounded, content-addressed handling and prohibits every execution,
  active-rendering, network, and secret effect.
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) assigns the
  mutable workspace, artifact manifests, immutable snapshots, and typed links
  to Project while retaining learning, domain-resource, and Assessment owners.
- [Project Workspace Contract](../../architecture/contracts/project-workspace-contract.md)
  governs the existing Project shell seam and requires additive versioning for
  workspace behavior.
- [Module Map](../../architecture/modules/module-map.md), [Module Dependency
  Rules](../../architecture/modules/module-dependency-rules.md), and [Security
  Architecture](../../security/README.md) keep cross-module access on public
  operations and untrusted bytes confined.
- [Interface Design Standards](../../standards/interface-design-standards.md)
  and [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern accessible, plain learner presentation without hiding provenance or
  safety limitations.
- Decision readiness is sufficient inside the accepted inert-artifact and
  reusable-Project boundaries. A live Portfolio integration, external
  provider, artifact execution surface, organization tenancy, or managed-cloud
  protection remains constrained or decision-required and is not activated.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver the complete bounded workspace, inert artifact, public link seam, immutable snapshot, export, API/headless, and browser flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Deliver notes and inert artifact upload/download but defer snapshots and typed links | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Deliver snapshot contracts and persistence without a learner-visible workspace flow | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| D. Add live Portfolio resolution or execute notebooks in this slice | no - Portfolio contracts and execution authority are unavailable and outside the CAP boundary | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A scores 14/14 because it delivers the complete enumerated SLI-0031
outcome, crosses the accepted Project boundaries end to end, has closed ADR
authority, and can be qualified independently before Assessment submission.
Its contracts and migrations are additive, object writes are content-addressed,
and learner-visible exposure remains removable without mutating accepted
snapshots, so reversibility and bounded risk score two.

Candidates B and C are viable packet-sized implementation cuts but not complete
vertical slices: each withholds part of the observable workspace-to-snapshot
journey, so value and end-to-end completeness score one. Candidate D crosses
explicit durable decision and CAP boundaries. Candidate A wins without a
tie-break and conforms to the current CAP-0007 slice manifest.

## Boundary Path

1. Versioned Project schemas define bounded workspace mutations, closed inert
   artifact metadata, safe reference records, typed domain links, immutable
   snapshots, downloads, and evidence-export meaning.
2. Project domain policy validates normalized names/paths, digests, provenance,
   classification, revision preconditions, idempotency, snapshot closure, and
   the absolute execution-denial boundary without importing frameworks or
   owning-module internals.
3. Project application operations coordinate Project-owned metadata and object
   ports. Typed domain-link validation calls only an owning module's public
   gateway; absent, stale, removed, or unauthorized owners remain explicit.
4. PostgreSQL stores Project-owned workspace revisions, resources, artifact
   manifests, domain-link references, idempotency records, and immutable
   snapshots without cross-schema foreign keys. A restrictive object adapter
   stores opaque content by digest outside the database and never executes it.
5. The protected FastAPI host obtains learner identity and permission from the
   server session, streams bounded upload/download/export data safely, and
   exposes the same reviewed operations to generated and headless clients.
6. The browser uses only the generated client to add and inspect work, recover
   from validation or stale-revision failures, download inert files, close a
   snapshot, and continue the live Project in clear learner language.
7. Focused and live qualification prove integrity, authorization, revision and
   replay behavior, snapshot immutability, continued mutation, safe export,
   execution denial, restart stability, containment, accessibility, and
   API/headless parity.

## Contracts, Data, and Provenance

Extend the Project contract family additively rather than changing Project
shell v1 meaning. The exact executable schemas must define closed request and
public-record shapes for workspace state and mutations, resource/reference
records, artifact manifests, domain links, snapshot intents and records,
download metadata, and an evidence-export manifest.

Every mutation is learner-scoped, server-authorized, idempotent, and bound to
an expected live workspace revision. Server-owned IDs, canonical UTC times,
accepted digests, storage locations, authorization facts, and state revisions
are never client authority. Artifact classification and provenance distinguish
learner-supplied source data, learner-created work, deterministic calculation,
simulation, model prediction, generated material, environment declarations,
assumptions, and narrative interpretation without claiming correctness.

Project-owned PostgreSQL tables retain normalized metadata, ordering,
idempotency fingerprints, accepted content digests, live revisions, link
references, and immutable snapshot manifests. Opaque bytes belong behind a
platform-owned restrictive object port and use content-addressed integrity; no
domain model contains a host path or provider payload. Snapshot digests use a
documented canonical serialization over the complete closed manifest. An exact
snapshot retry returns the original snapshot; changed intent conflicts.

Domain links are references, not copied domain state. The link record names the
owning module and public resource semantics plus exact version/as-of evidence
when the owner supplies it. Production composition may expose only admitted
owner gateways; no Portfolio gateway is included until its public contract is
accepted. Removing a live link never changes a closed snapshot.

Evidence export preserves the immutable snapshot manifest and authorized inert
artifact bytes through deterministic names and digests. It omits secrets,
credentials, local host paths, private authorization facts, and source content
the learner is not authorized to export. Import/restore is not implied unless
an exact bounded contract is deliberately included by a later packet within
this slice and proves revalidation; archive expansion is never assumed.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Save and resume | The learner adds notes, references, and inert artifacts, leaves the flow, and reopens the exact ordered workspace through the public API | application/PostgreSQL/API/browser/live |
| API/headless parity | A non-browser authenticated client performs the same supported workspace reads, bounded mutations, snapshot close, download, and export without browser-only state | API/live qualification |
| Inert admission | Supported bounded bytes with matching digest and complete provenance are stored as opaque content and returned with exact metadata | contract/domain/object adapter/PostgreSQL |
| Malformed or unsafe artifact | Traversal, links, archive-expansion requests, unsupported active media, digest mismatch, unknown type, excessive count or size, invalid provenance, and partial input fail closed without a live manifest entry | contract/domain/security/integration |
| No execution | Notebook, code, model, environment, and result artifacts cannot reach a kernel, subprocess, installer, network, secret store, provider, active renderer, or execution job | architecture/security/composition tests |
| Safe inspection and download | The learner sees plain metadata, source/classification limits, and passive allowlisted preview only when explicitly admitted; download uses safe headers and exact bytes | API/component/browser/security |
| Exact retry and stale revision | An unchanged idempotent retry returns the accepted mutation; changed reuse or stale concurrent revision fails without duplicate or overwritten work | domain/application/PostgreSQL/API |
| Many-valued links | Multiple distinct typed resource links can coexist without copying business state or granting owning-module persistence access | contract/application/architecture |
| Link denial and degradation | Unknown owner/type, unavailable owner, stale/removed target, missing permission, or cross-learner guess fails explicitly and confidentially; no dangling accepted live link is invented | application/API/security |
| Snapshot closure | One exact live revision closes to an immutable digest-bound snapshot, and an exact retry returns the same snapshot | contract/domain/PostgreSQL/API |
| Continue after snapshot | Later live edits advance the workspace revision but do not alter snapshot bytes, manifest, links, artifact versions, digest, or time | domain/PostgreSQL/API/browser |
| Export integrity | The authorized snapshot export reproduces its manifest and allowed bytes by digest without secrets, credentials, host paths, or unauthorized source data | application/object adapter/API/live |
| Authorization and confidentiality | Missing permission/session, caller-selected learner, cross-learner project/artifact/snapshot guesses, and deleted or unavailable objects fail without revealing private metadata | API/security/browser |
| Interruption and restart | Failed or interrupted metadata/object admission exposes no accepted partial artifact; accepted work and snapshots reopen after normal restart | adapter/PostgreSQL/live |
| Flexible valid shape | Valid resource and artifact counts, ordering, Unicode text, file names, optional metadata, classification combinations, and multiple snapshots do not depend on one fixture | compatibility/unit/component anti-rigidity tests |
| Accessible parity | Workspace, errors, provenance, download, and snapshot actions preserve labels, keyboard order, focus, error association, zoom/reflow, reduced motion, forced colors, and equivalent theme meaning | component/Chromium/design checks |
| No learning side effect | Workspace edits, links, artifact admission, snapshot closure, and export create no Assessment, completion, mastery, competency, or Learner-model record | application/PostgreSQL/live |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The intended seams are fixed here; exact files and tests are
refined just in time.

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0118 | Freeze additive workspace, inert-artifact, domain-link, snapshot, and export contracts plus pure Project domain policy | SLI-0030 | none | complete |
| WRK-0119 | Deliver Project-owned metadata/object persistence, application operations, migrations, protected API, and generated client | WRK-0118 | none | complete |
| WRK-0120 | Deliver the accessible generated-client workspace, artifact, download, snapshot, and continue-working browser flow | WRK-0119 | none | complete |
| WRK-0122 | Correct snapshot timestamp canonicalization and cover trailing-zero fractional precision | WRK-0120 | none | complete |
| WRK-0121 | Qualify the full contract, PostgreSQL, object, API/headless, browser, snapshot-integrity, export, denial, restart, accessibility, and containment boundary | WRK-0122 | none | ready |

## Verification and Qualification

Run schema and semantic compatibility over approved, boundary, reordered, and
malicious records; Project domain and application tests for revisions,
idempotency, immutable manifests, link validation, snapshot digests, continued
work, and export; restrictive object-adapter tests; real PostgreSQL migration,
concurrency, rollback, partial-failure, and restart evidence; protected API
success, streaming, authorization, safe-header, stale, replay, and
confidentiality tests; reviewed OpenAPI and generated-client reproduction; web
model, component, build, mocked Chromium, and isolated live browser/headless
qualification; architecture import/schema-ownership and explicit no-execution
tests; security, learner-language, accessibility, design, documentation,
planning, whitespace, and aggregate readiness gates.

Anti-rigidity evidence must vary valid resource/artifact/link/snapshot counts,
ordering, Unicode text and file names, supported classifications, optional
metadata, digest values, revisions, and learner-safe copy. Functional success
must not depend on one fixture, incidental timestamp or generated identifier,
exact card order beyond contract meaning, wording that is not safety-critical,
or visual styling that does not impair function or accessibility.

## Rollback and Migration

Contracts and database changes are additive and versioned. New Project
migrations require exact forward application, checksum stability, empty
development rollback, and refusal to describe deletion of retained artifacts or
snapshots as safe rollback. Object writes must stage and validate before durable
metadata acceptance; orphan cleanup is bounded and cannot delete content still
referenced by another accepted manifest.

Feature exposure may be removed while immutable accepted snapshot and artifact
records remain readable through compatible public operations. A rollback cannot
rewrite a snapshot, silently discard a live accepted mutation, change a digest,
or mutate a historical link. Breaking removal or reinterpretation follows
normal contract and migration governance.

## Stop Conditions

Stop for any execution, active rendering, archive expansion, network, secret,
runtime-image, package-installation, provider callback, live Portfolio adapter,
copied domain state, financial action or advice, Assessment submission,
completion/mastery mutation, general Workspace expansion, collaboration,
public sharing, external provider, organization tenancy, managed-cloud
protection/recovery, client-owned identity/authorization/revision/digest,
cross-module persistence access, cross-learner disclosure, unbounded storage,
breaking Project shell semantics, destructive retained-data migration, active
write-scope overlap, conflicting canonical authority, or material CAP-0007
drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential issue. Fix it locally when in
scope or defer optional cleanup to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery must reconcile Project vocabulary and module README; versioned
workspace/artifact/link/snapshot/export contracts; API and generated-client
documentation; object-storage and PostgreSQL ownership; inert-artifact threat
and security boundaries; provenance and data-use guidance; learner-facing
plain-language behavior; local operations; architecture verification; known
gaps; this slice; its bounded packets; and the planning register.

Completion evidence must identify exact candidate receipts and focused checks;
contract and migration compatibility; supported resource/artifact classes and
limits; object and metadata atomicity; revision and idempotency behavior;
download headers; domain-link authority and unavailable-owner behavior;
snapshot canonicalization, immutability, and continuation; export contents and
exclusions; browser and headless parity; authorization/privacy; zero
Assessment/Learner-model effects; restart and cleanup; accessibility; qualified
environments; assumptions; and residual gaps.

Evidence must explicitly state that no artifact was executed or actively
rendered, no result was independently reproduced, no live Portfolio or provider
integration was delivered, no Assessment submission or learner projection was
created, and no managed-cloud or production-recovery profile was qualified.

## Planning History

- 2026-10-16: Refined the second CAP-0007 manifest increment after SLI-0030
  completed. Candidate A scores 14/14 and delivers the complete API-first inert
  workspace-to-snapshot flow while preserving Project ownership, public-module
  boundaries, headless access, and explicit execution denial. The refinement
  conforms to the current CAP package and exposes no new decision gate.
- 2026-10-16: Refined JIT-A as WRK-0118. The packet freezes additive portable
  workspace, inert-artifact, typed-link, immutable-snapshot, and export
  contracts plus pure Project policy; persistence, public API, browser behavior,
  and every execution effect remain deferred.
- 2026-10-16: Activated WRK-0118 after revalidating CAP conformance, decision
  readiness, completed SLI-0030 dependency, branch ownership, and exact
  collision-free contract/domain scope. Packet-start froze the semantic
  acceptance set.
- 2026-10-16: Prepared WRK-0118's additive contract/domain candidate after the
  expanded compatibility and pure Project suites, broad backend
  architecture/contract/unit corpus, security, architecture, documentation,
  planning, compile, whitespace, and aggregate readiness checks passed.
- 2026-10-16: Closed WRK-0118 after exact-candidate review accepted the
  additive contract and pure-policy seam with no open findings. Persistence,
  public API, generated-client, and browser delivery remain in the next
  just-in-time packets.
- 2026-10-16: Refined JIT-B as WRK-0119. The packet delivers the Project-owned
  persistence and inert-object boundary through one protected public API and
  generated client for browser and headless consumers; the browser workspace
  remains the next packet.
- 2026-10-16: Activated WRK-0119 after revalidating its completed contract
  dependency, CAP/SLI conformance, decision readiness, API-first boundary, and
  collision-free exact scope. Packet-start froze its semantic acceptance set.
- 2026-10-16: Completed WRK-0119 at candidate
  `bfcdc1409e3281fe64f976bfa22fc286ec9ea19d`. The protected Project API now
  provides side-effect-free workspace reads, authorized revision/idempotency-
  guarded writes, verified inert artifact transfer, immutable snapshots, and
  evidence export through the reviewed generated-client boundary. All 879
  backend tests passed with PostgreSQL enabled, alongside the focused API,
  generated-client, architecture, security, documentation, planning,
  whitespace, exact-candidate, and 29-check readiness evidence.
- 2026-10-16: Refined JIT-C as WRK-0120. The packet delivers the
  generated-client learner workspace, inert file, snapshot, export, and
  continue-working flow without changing the completed API or moving domain,
  authorization, revision, or artifact policy into the browser.
- 2026-10-16: Activated WRK-0120 after revalidating the completed public API
  dependency, current CAP/SLI scope, decision readiness, generated-client-only
  boundary, and collision-free browser write scope.
- 2026-10-17: Completed WRK-0120 at exact reviewed candidate
  `0fe63b50e05adea65363c3c8b6502f13ee3316d1`. The learner-facing flow consumes
  only the generated public client, keeps files inert, binds live retries and
  immutable evidence to exact revisions and digests, preserves canonical
  Unicode path identity without rejecting valid records, and leaves all
  operations usable by headless clients. WRK-0121 now owns integrated
  qualification and slice closure.
- 2026-10-17: Refined JIT-D as WRK-0121. The packet extends the existing
  isolated live qualifier with the complete Project workspace journey and
  correlates generated-client browser, ordinary headless HTTP, PostgreSQL,
  object, restart, no-learning-effect, and cleanup evidence before slice
  closure. It changes no product behavior and requires no new decision.
- 2026-10-17: Activated WRK-0121 after revalidating the current CAP package,
  completed browser dependency, decision readiness, exact live-qualification
  scope, and absence of an active file collision. The packet adds evidence and
  qualifier coverage only; product authority remains unchanged.
- 2026-10-17: Released WRK-0121 after its live qualifier exposed intermittent
  checkpoint integrity failures. Direct service reproduction isolated two
  timestamp spellings at the digest boundary. WRK-0122 is the bounded
  correction prerequisite; no contract or durable decision changes.
- 2026-10-17: WRK-0122 reused the Project contract's canonical workspace
  timestamp strings for snapshot digest material and added a deterministic
  trailing-zero fractional-second regression. Focused Project unit, contract,
  and API verification passed, and exact-candidate controls recorded complete
  verification and independent technical evidence with no open findings.
  WRK-0121 may now resume integrated qualification.
