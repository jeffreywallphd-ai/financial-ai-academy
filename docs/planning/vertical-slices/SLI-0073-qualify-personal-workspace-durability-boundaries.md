---
id: SLI-0073
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: CAP-0017
depends_on: ["SLI-0070", "SLI-0071", "SLI-0072"]
decision_gates: []
---

# Vertical Slice: Qualify Personal Workspace Durability and Boundaries

## Outcome and User Scenario

A learner can remove saved records or collections, obtain an integrity-bound
versioned view of their Personal workspace through the same protected public
API used by browser and headless clients, and resume unaffected saved work
after a retry, interruption, application restart, or qualified community
database recovery. Quota and recovery failures explain what happened and the
next safe action without exposing storage or implementation details.

The slice closes CAP-0017 by directly qualifying the workspace's existing
ownership, reference, removal, replay, and capacity invariants. It adds the
smallest owner-level export seam needed for later portable-record composition;
it does not implement the multi-module export, download, import, or restore
workflow owned by CAP-0019.

## Scope Boundaries

### In Scope

- Freeze an additive, versioned Personal-workspace export-view contract that
  contains one complete authorized workspace projection, its canonical digest,
  exact schema version, and generation time. It contains no source content,
  permission grant, target payload, artifact bytes, storage key, provider
  payload, credential, session, or implementation record.
- Expose that owner-level view through a protected public application and HTTP
  operation used by the generated TypeScript client, browser, command-line,
  service, and future headless-AI consumers under the existing server-owned
  learner context and Personal-workspace read permission.
- Keep record and collection deletion on the existing revision-bound,
  idempotent `remove_record` and `remove_collection` mutations. Removal also
  removes workspace-owned collection membership but never calls, changes, or
  deletes a referenced Curriculum or Project aggregate.
- Preserve exact replay, optimistic concurrency, first-materialization,
  canonical digest, query continuation, and target-reference integrity through
  removal, export-view generation, failure, retry, restart, and recovery.
- Turn the accepted limits of 200 records, 50 collections, and 100 unique
  records per collection into deterministic, public, plain-language quota
  failures with a safe action. Reaching one limit must not block unrelated
  reads, searches, removals, exports, or mutations within other limits.
- Prove that the Personal-workspace PostgreSQL aggregate and replay records are
  included in a controlled community logical recovery exercise, restore only
  to an empty inactive target, retain exact accepted meaning, and make no RPO,
  RTO, offsite, hostile-host, or managed-cloud guarantee.
- Qualify browser/headless equivalence, keyboard and focus use, semantic
  headings and controls, accessible status and recovery text, reflow, 200
  percent zoom, reduced motion, forced colors, and light/dark/system themes.
- Prove deployment-neutral domain, application, contract, and generated-client
  semantics without adding a local/cloud fork. Only the implemented local
  topology receives live operational qualification.
- Include failure and anti-rigidity coverage for empty and full workspaces,
  zero and maximum memberships, varied Unicode text, mixed references, optional
  fields, different valid counts and order, interrupted writes, stale revision,
  exact retry, unavailable optional adapters, and harmless additive metadata.

### Out of Scope

- A combined learner-record manifest, background export job, resumable archive,
  artifact download, import, populated-target merge, or user-facing restore;
  those remain in CAP-0019.
- Whole-account erasure, retention schedules, legal deletion guarantees,
  backup-copy deletion, or a physical database purge. Restoring an older
  community recovery set can reintroduce records removed after that set.
- Managed-cloud tenancy, encryption, retention, backup, recovery objectives,
  availability, or organization policy; those remain decision-required.
- Cloud drive synchronization, collaboration, instructor access, publication,
  arbitrary files, provider storage, background source polling, or a cross-
  module transaction.
- Copying or deleting target content, mutating Project, Curriculum, Assessment,
  Learner model, Audit, Identity, Market data, Portfolio, or AI state, or
  treating an export view as permission or authoritative evidence.
- Active artifact preview, download, execution, package installation,
  subprocess use, external network access, provider callback, financial action,
  or separate AI mutation authority.
- Styling-only polish beyond functional and accessible use. Optional visual
  polish remains CAP-0031 work unless the user moves it earlier.

## Canonical Context and Decisions

- [CAP-0017](../capabilities/CAP-0017-maintain-personal-learning-workspace.md)
- [SLI-0072](SLI-0072-search-and-refresh-saved-references.md)
- [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md)
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
- [Personal Workspace Contract](../../architecture/contracts/personal-workspace-contract.md)
- [Personal Workspace v1](../../../contracts/learning/personal-workspace/v1/README.md)
- [Personal Workspace Module](../../../backend/src/financial_ai_academy/modules/personal_workspace/README.md)
- [Community Backup and Restore](../../operations/community-backup-and-restore.md)
- [Community Evidence Protection](../../security/community-learner-evidence-protection.md)
- [Local/Cloud Capability Parity](../../architecture/deployment/local-cloud-capability-parity.md)
- [CAP-0019](../capabilities/CAP-0019-export-portable-learning-records.md)
- [Decision Readiness](../../adr/decision-readiness.md)

ADR-0021 authorizes a focused Personal workspace, explicit versioned export
views, module-owned PostgreSQL state, bounded quotas, removal, idempotency, and
community recovery participation. ADR-0008 defines the private-host,
maintenance-mode, empty-target community recovery boundary. These decisions
are sufficient for the selected slice. Managed-cloud policy is unresolved but
is not selected or inferred here; the shared-core semantics remain reusable
while operational cloud qualification stays out of scope.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Add the narrow owner export view and close cumulative removal, quota, recovery, accessibility, and shared-core qualification | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Add a workspace-wide physical purge plus a complete downloadable portable archive | yes | 2 | 1 | 1 | 1 | 0 | 1 | 0 | 6 |
| C. Implement coordinated multi-module backup/restore and managed-cloud recovery in this slice | no | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 4 |
| D. Add tests and prose only, leaving export and quota behavior implicit | no | 1 | 0 | 2 | 1 | 2 | 2 | 2 | 10 |

## Selection Rationale

Candidate A wins without a tie-break. It completes the CAP's directly
observable Personal-workspace boundary, uses accepted contracts and recovery
policy, preserves one API for browser and headless consumers, and remains
independently reversible. Its owner-level export view is a reusable input to
CAP-0019 rather than a competing cross-module export system.

Candidate B is technically possible but scores poorly because physical purge,
retention, recovery-copy behavior, and a full archive would mix later policy
and CAP-0019 concerns into this closeout slice. Candidate C is ineligible: it
would select unresolved managed-cloud policy and bypass the ordered portable-
records capability. Candidate D is ineligible because evidence alone cannot
complete the manifest's explicit export and actionable quota boundary.

Every score follows the fixed criteria. Value measures a learner-visible safe
result; end-to-end measures one usable public path; decisions measures current
authority; contracts measures exact existing or additive shapes; independence
measures freedom from later CAPs; verification measures direct observability;
and reversibility measures bounded rollback risk.

The selected refinement preserves SLI-0073's CAP outcome, dependencies, and
material-change boundary. It adds no slice, external effect, managed-cloud
claim, or durable decision and requires no renewed CAP package.

## Boundary Path

1. An authenticated caller with Personal-workspace read authority requests the
   current workspace or its export view. The host derives learner identity and
   rejects caller-selected learners or unknown input before workspace access.
2. Personal workspace reads only its own module repository, validates the full
   current aggregate against the v1 contract, and constructs an export envelope
   with exact schema version, canonical digest, and server-derived time.
3. The protected API returns the same closed export shape through the reviewed
   OpenAPI contract and generated client. Browser and headless clients may save
   the response, but it grants no target permission and contains no target or
   artifact content.
4. A record or collection removal uses the existing expected revision and
   idempotency key. The pure domain operation updates only workspace-owned
   records, ordering, and membership.
5. PostgreSQL atomically stores the new aggregate and replay evidence. Exact
   retry returns the accepted result; changed-key reuse, stale revision,
   interruption, or storage failure leaves the earlier complete state intact.
6. Capacity validation maps each closed limit to one bounded quota outcome.
   Reads, query, export, removal, and unrelated valid mutations continue.
7. The browser presents export, quota, removal, and retry meaning in plain
   learner language while retaining exact versions and digests in an
   accessible technical record or downloaded document.
8. A disposable local recovery exercise captures the database through the
   accepted maintenance boundary, restores to an empty inactive target, and
   replays protected browser/headless reads against the same shared core.

## Contracts, Data, and Provenance

Add one closed v1 export-view schema around the accepted workspace document.
The envelope carries `schema_version`, `workspace_digest`, `generated_at`, and
the complete validated `workspace`. The digest is SHA-256 over canonical
compact sorted-key UTF-8 JSON of the workspace document. It proves exact view
meaning, not authenticity, permission, legal retention, or external
interoperability.

The export view is read-only and generated from one authorized current
aggregate. It contains learner-authored notes, bookmarks, collections, order,
archive state, safe typed references, versions, times, and provenance already
admitted by the v1 workspace schema. It contains no mutation replay rows,
database identifiers, authorization policy, sessions, credentials, raw source
content, Project workspace material, artifact bytes, storage locations,
provider payloads, or execution controls.

Record and collection removal remain ordinary workspace mutations rather than
target deletion. Removing a record also removes only its workspace-owned
collection memberships and order entry. It does not erase source-domain facts,
immutable evidence, audit evidence, or older external recovery copies. Exact
replay retains the accepted post-removal result without resurrecting content.

Quota meaning is closed at 200 records, 50 collections, and 100 unique member
record IDs in one collection. The public failure distinguishes capacity from
malformed input without reporting private record content. It states the limit
and safe actions—remove or reorganize saved work—while preserving unrelated
operations. Changing those limits later is a versioned policy/contract change,
not a browser constant.

Community recovery operates on confidential PostgreSQL state, not the portable
export view. The qualification records schema/version/digest/count evidence and
never stores learner note bodies, target payloads, credentials, or absolute
local paths in logs or receipts. The export view remains the future portable-
records composition seam; database recovery remains same-installation recovery.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Authorized export view | Browser and headless callers receive the same closed versioned workspace and canonical digest under server-owned learner context | contract/application/API/client/live |
| Export confidentiality | The view contains only workspace-owned records and retained safe reference facts; source content, permissions, replay rows, secrets, storage, and artifact bytes are absent | contract/security/API |
| Removal isolation | Removing a record or collection updates order and membership only in Personal workspace and leaves every referenced target and unrelated module unchanged | domain/PostgreSQL/architecture/live |
| Exact retry and interruption | Exact replay returns one accepted post-removal result; stale revision, changed-key reuse, and an interrupted write preserve the earlier complete state | application/PostgreSQL/API |
| Record capacity | The 200th record is accepted, the 201st is refused with a quota outcome, and query, export, removal, and valid unrelated mutations continue | contract/application/API/browser |
| Collection capacity | The 50th collection and 100th unique member are accepted; the next is refused without changing prior membership or blocking other workspace use | contract/domain/API/browser |
| Reference integrity | Export, removal, restart, and recovery preserve exact retained type, owner, selector, version/as-of, status, timestamps, and provenance | contract/PostgreSQL/live |
| Optional-adapter isolation | Export and removal remain available when one source adapter is absent or unavailable; no target refresh or cross-module access is attempted | application/API/security |
| Accessible recovery | Keyboard and assistive-technology users can understand quota/removal/export status and reach a safe retry or navigation action in supported themes and layouts | component/browser/accessibility |
| Local restart | Accepted records, replay meaning, queries, and export digest survive a normal local application restart | PostgreSQL/API/browser/headless |
| Empty-target community recovery | A controlled database capture restores exact workspace and replay meaning to an empty inactive target, revokes no guarantees into existence, and refuses a populated target | operations/PostgreSQL/security/live |
| Deployment-neutral core | Architecture checks prove local composition uses the same domain/application/contracts/clients intended for future cloud composition, with no managed-cloud operational claim | architecture/contract |
| Anti-rigidity | Empty, sparse, full, reordered, mixed-reference, Unicode, optional-field, and harmless additive-metadata cases preserve the same invariants without special fixture counts | property/parameterized/browser |

## Agent Work Packets

Packet IDs are reserved and authored one at a time immediately before each
packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0143 | Freeze the owner export view, quota outcome, removal/recovery semantics, compatibility fixtures, and pure contract behavior | SLI-0070 through SLI-0072 | none | complete |
| WRK-0144 | Deliver application, PostgreSQL, protected API, OpenAPI, generated-client, replay, and authorization behavior for export and actionable quota boundaries | WRK-0143 | none | complete |
| WRK-0145 | Deliver plain-language browser export, quota, removal, retry, technical-record, and accessibility behavior through the generated client | WRK-0144 | none | complete |
| WRK-0146 | Qualify cumulative browser/headless export parity, maximum bounds, interruption, target isolation, restart, stopped-source empty-target community recovery, containment, cleanup, and CAP closure | WRK-0145 | none | active |

Dependent packets are not claimed until their predecessor is complete. The
sequential default avoids shared contract, client, API, UI, and local-live
qualification collisions. A packet may later declare an exact independent
test or documentation scope parallel-safe only when accepted inputs and
reciprocal non-overlap are explicit.

WRK-0145 completed with the exact generated-client export download, closed
response validation, attempt-bounded authorization recovery, plain-language
capacity guidance, accessible status, mixed-reference coverage, and proof
that no Curriculum or Project owner operation was invoked. JIT-D remains the
single cumulative live recovery and slice-closure seam.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; canonical export-digest and
confidentiality tests; pure removal, membership cleanup, exact-limit, over-
limit, Unicode, optional-field, and anti-rigidity tests; application and
PostgreSQL exact-replay, stale-revision, interruption, restart, and target-
isolation tests; protected API authorization and error tests; reviewed OpenAPI
and generated-client reproduction; TypeScript response-boundary tests; web
unit/component and focused Chromium accessibility tests; and one disposable
live browser plus ordinary headless HTTP journey.

The controlled recovery qualification must capture the disposable community
PostgreSQL topology through its maintenance boundary, refuse a nonempty target,
restore to an empty inactive target, confirm exact workspace and replay
meaning, and avoid RPO/RTO, offsite, hostile-host, or managed-cloud claims.
External backup media and production recovery are not qualified.

Run architecture/import, shared-core, persistence-ownership, target non-
mutation, private-field, inert-resource, learner-language, design-system,
security, documentation, planning, whitespace, typecheck, zero-warning lint,
build, exact-candidate affected verification, independent technical review,
completion structure, and `python dev-tools/agent/check_ready.py`. Incidental
count, ordering, prose, or nonfunctional style differences do not trigger a
full correction loop; test the invariant or defer optional polish to CAP-0031.

## Rollback and Migration

The export envelope and quota error are additive within a versioned contract
family. Existing workspace aggregates remain byte-compatible and need no eager
rewrite. Prefer the existing JSON aggregate and replay tables; if a persistence
change becomes necessary, prove forward, reapply, development-down, retained-
data refusal, and real-PostgreSQL behavior before delivery.

A code rollback may remove an unused export entry point while preserving every
accepted workspace aggregate, mutation replay, and removal result. It must not
reinterpret removed records, resurrect collection membership, delete source
targets, weaken limits, or present a database recovery set as a portable
learner export. Recovery-test artifacts remain disposable and are cleaned only
within their exact isolated topology.

## Stop Conditions

Stop for whole-account erasure or retention policy; deletion of recovery
copies; managed-cloud tenancy, encryption, storage, backup, recovery, RPO/RTO,
or availability; a cross-module export manifest or import; populated-target
merge; direct access to another module's persistence or object storage; copied
source content; target mutation or deletion; export of secrets, sessions,
credentials, replay internals, artifact bytes, or provider payloads; active
artifact behavior; cloud sync; collaboration; background jobs; destructive
migration; breaking contract change; stale CAP package; active write collision;
conflicting canonical authority; or material CAP-0017 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish.

## Documentation Impact and Completion Evidence

Delivery updates the Personal-workspace executable contract, architecture and
module guidance, API/OpenAPI and generated-client documentation, Saved Learning
browser guidance, local recovery operations, security/containment and
architecture assurance, known gaps, packet artifacts, this slice, the CAP
closure evidence, and the planning register.

Completion identifies exact packet candidates and receipts; scenario-to-test
evidence; export digest and confidentiality; quota and removal semantics;
browser/headless parity; exact replay, interruption, restart, and empty-target
database recovery; target non-mutation; optional-adapter isolation;
accessibility; compatibility and migration impact; assumptions; unqualified
profiles; residual gaps; and CAP-package conformance. Local approval and review
records remain ignored; no slice or packet approval is requested.

## Planning History

- 2026-10-17: Refined the final CAP-0017 manifest increment after SLI-0070
  through SLI-0072 completed. Candidate A scores 14/14 and closes the Personal-
  workspace boundary with one owner-level export view plus cumulative removal,
  quota, durability, accessibility, and community-profile qualification.
  Multi-module portability remains CAP-0019, managed-cloud policy remains out
  of scope, and the refinement does not materially change the CAP package.
- 2026-10-17: Refined JIT-A as WRK-0143 around the additive owner export
  envelope, canonical digest, exact quota meanings, pure removal cleanup,
  compatibility, privacy, and anti-rigidity evidence. Application, persistence,
  API/client, browser, and live recovery behavior remain later packet seams.
- 2026-10-17: Activated WRK-0143 from the recorded base after revalidating the
  current CAP package, completed slice dependencies, exact contract-only scope,
  decision readiness, and absence of an active write collision.
- 2026-10-17: Completed WRK-0143 with the closed owner export envelope,
  canonical digest and chronology checks, exact quota meanings, removal
  isolation, compatibility fixtures, anti-rigidity coverage, and corrected
  validation precedence. Application, persistence, public API/client, browser,
  and live recovery delivery remain in the dependent packet seams.
- 2026-10-17: Refined JIT-B as WRK-0144 around the application export
  operation, protected JSON route, exact public quota outcomes, existing
  PostgreSQL replay/restart behavior, and reviewed OpenAPI/generated-client
  seam. It adds no migration, browser feature, import, or recovery policy.
- 2026-10-17: Activated WRK-0144 from the recorded base after revalidating the
  completed contract dependency, current CAP package, resolved decision
  posture, exact API/application/test scope, and absence of a write collision.
- 2026-10-17: Advanced WRK-0144 to verification after focused application,
  API, generated-client, and real-PostgreSQL qualification.
- 2026-10-17: Completed WRK-0144 with one protected server-authoritative export
  operation, closed OpenAPI/generated-client parity, distinct capacity outcomes,
  and PostgreSQL zero-write, replay, removal, and restart evidence. Browser
  controls and cumulative recovery qualification remain in JIT-C and JIT-D.
- 2026-10-17: Refined JIT-C as WRK-0145 around a generated-client export
  download, current-workspace response binding, exact quota guidance, removal
  and retry continuity, technical facts, accessibility, and anti-rigidity. The
  packet adds no backend, contract, persistence, or recovery-policy change.
- 2026-10-17: Activated WRK-0145 from the recorded base after revalidating the
  completed WRK-0144 dependency, current CAP package, exact browser/test/docs
  scope, resolved decisions, and absence of an active write collision.
- 2026-10-17: Advanced WRK-0145 to verification after delivering the explicit
  current-revision export download, closed browser validation, accessible
  failure/technical states, and capacity-specific recovery guidance without
  changing the public API, persistence, or recovery policy.
- 2026-10-17: Refined JIT-D as WRK-0146 around the delivered export and the
  existing disposable live topology. The bounded exercise compares browser
  and headless export meaning, exact capacity continuity, normal restart, a
  stopped-source logical database and data-root capture, populated-target
  refusal, empty-target restore, source and target isolation, and cleanup. It
  adds no supported recovery product or broader operational claim.
- 2026-10-17: Activated WRK-0146 from the recorded base after the packet and
  implementation gates confirmed its completed dependency, current CAP
  authority, exact qualification scope, resolved decision posture, and absence
  of an active coordination collision.
