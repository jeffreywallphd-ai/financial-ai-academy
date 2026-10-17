---
id: WRK-0146
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0073
capability: CAP-0017
depends_on: [WRK-0145]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/personal-workspace.e2e.ts", "deployments/local/README.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/operations/community-backup-and-restore.md", "docs/security/community-learner-evidence-protection.md", "docs/planning/capabilities/CAP-0017-maintain-personal-learning-workspace.md", "docs/planning/vertical-slices/SLI-0073-qualify-personal-workspace-durability-boundaries.md", "docs/planning/work-packets/WRK-0146-qualify-personal-workspace-recovery-and-close.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 2797023c5c8824f620acaa36296e7b24d45f4cb4
claim_id: WRK-0146:6e208252-d4da-4e86-ad4b-fe2d8c11fa59
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T17:46:18Z
---

# Agent Work Packet: Qualify Personal Workspace Recovery and Close

## Objective and Deliverable

Close SLI-0073 and the delivered CAP-0017 boundary with one cumulative local
qualification. Prove that the generated browser and an ordinary cookie-backed
headless client receive the same current integrity-bound Personal-workspace
export, quota and removal failures preserve unrelated use, exact accepted
meaning survives normal restart, and a stopped disposable community topology
can restore the complete database and bounded application data into an empty
inactive target without mutating the source or any referenced aggregate.

The recovery exercise is controlled test evidence, not a supported backup
product. It must retain the accepted no-RPO/RTO, no-offsite, no-hostile-host,
no-managed-cloud, and no-production-recovery boundaries.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed delivery-planning, testing,
security, and operational context; change-impact matrix; decision-readiness
register; ADR-0008 and ADR-0021; CAP-0017; SLI-0073; completed WRK-0143 through
WRK-0145; Personal-workspace contract and v1 schema; community recovery and
security guidance; current approved-lesson runner, browser journey, pure runner
tests, local deployment guide, web README, and nearest test configuration.
Canonical sources govern over this packet.

The Required Startup was completed before this packet was authored. No
canonical conflict or unresolved decision gate was found.

## Decisions and Assumptions

- WRK-0143 through WRK-0145 supply the complete export, quota, removal,
  persistence, protected API, generated-client, and browser behavior. This
  packet qualifies those seams and may not redefine them.
- The only recovery target is a second uniquely named disposable PostgreSQL
  18.4 container plus a copied bounded application-data root under the runner's
  ignored temporary directory. The source application is stopped before the
  logical database capture and data-root copy.
- Empty-target refusal is a qualification guard, not a public restore API. It
  checks the target before any restore input is applied and proves a marker in
  the target remains unchanged after refusal.
- The exercise may use the pinned container's `pg_dump` and `pg_restore`
  commands. It records only versions, counts, digests, phases, and boolean
  results; it must not log the dump, DSN, cookies, learner-authored text,
  absolute temporary paths, credentials, or raw database rows.
- The restored host starts only after database and object-root comparison,
  uses a fresh session, and remains loopback-only with jobs, providers, and
  external network absent. The qualifier does not claim complete identity
  recovery or supported recovery tooling.
- The complete live recovery route runs only when the runner owns its default
  disposable PostgreSQL topology. The acknowledged external-database mode may
  not claim or attempt target recovery.
- No schema, data migration, package, dependency, or product behavior change is
  expected.

## In Scope

- Extend the live generated-browser capture with the exact export response
  that produced the downloaded JSON, including schema, canonical digest,
  generation time, and the complete validated workspace.
- Extend the ordinary headless observation to call the same bodyless protected
  export API and compare the complete closed response to the browser capture,
  allowing only a later valid server generation time while requiring identical
  workspace revision, workspace digest, and workspace meaning.
- Exercise the three public capacity outcomes at their exact accepted limit
  and first refused value through existing application/API tests or bounded
  live headless preparation. Prove query, export, removal, and unrelated valid
  mutation behavior remains available after refusal; do not make the browser
  create hundreds of controls merely to prove server policy.
- Capture a logical dump only after stopping the source application, copy and
  hash the exact bounded application data root, and prove the source database
  and files remain unchanged throughout target refusal and restore.
- Start an independent empty target, prove a populated-target marker is
  refused before restore, return the same target to a verified empty state,
  restore the logical dump, compare privacy-safe schema-wide fingerprints and
  bounded file-tree digests, then start the normal application without seed
  flags against that restored target.
- Through a fresh protected headless session, compare the restored Personal
  workspace, export, exact replay, query meaning, target-state fingerprints,
  and mutation-row counts to the accepted source evidence.
- Add pure runner tests for closed export capture, chronology, digest binding,
  browser/headless comparison, maintenance ordering, empty-target refusal,
  source immutability, restore-result correlation, redaction, cleanup, varied
  safe record order/count, and recovery-helper failure paths.
- Update direct web, local deployment, operations, security, architecture,
  known-gap, slice, capability, packet, and planning-register documentation
  with the exact qualified and deliberately unqualified claims.

## Out of Scope

Product backup/restore commands or UI; public recovery API; in-place or
populated-target restore; production database roles; scheduled backup; remote
or public binding; retained recovery artifacts; retention or deletion policy;
encryption/key custody; offsite, immutable, ransomware-resilient, hostile-host,
RPO, RTO, availability, upgrade, cross-version, cross-installation, or managed-
cloud recovery; built-in credentials, OIDC, multi-user session recovery, or
complete identity recovery; multi-module portable export/import; merge;
provider, worker, model, or external execution; source-target mutation; schema,
OpenAPI, generated-client, dependency, migration, shared design-system, or
product browser behavior changes; styling polish.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Browser evidence | Current Saved Learning generated-client journey and download behavior | listed Personal-workspace e2e file | Capture the already delivered closed export without adding a second client path |
| Headless/recovery runner | Public-client observations, database fingerprints, process/container lifecycle, restart, report, cleanup | listed runner file | Prove export parity and one stopped-source, empty-target recovery drill |
| Runner unit evidence | Existing capture, storage, restart, denial, and anti-rigidity tests | listed replay-qualification test file | Prove closure, ordering, redaction, refusal, correlation, and failure cleanup |
| Direct guidance | Web, local, operations, security, assurance, and known-gap statements | listed Markdown files | Separate qualified exercise evidence from unsupported recovery claims |
| Planning | CAP-0017, SLI-0073, this packet, register | listed planning files | Record final packet, slice, and capability completion evidence |

No executable product contract, application operation, repository adapter,
migration, generated client, deployment composition, dependency, or design
asset may change.

## Contracts and Interfaces

Browser and headless parity uses only the existing protected public operations:

```text
POST /api/v1/session/single-profile
GET  /api/v1/personal-workspace
GET  /api/v1/personal-workspace/export
POST /api/v1/personal-workspace/query
POST /api/v1/personal-workspace/mutations
```

The export comparison requires exact `schema_version`, `workspace_digest`, and
complete `workspace`; `generated_at` may advance but must remain valid UTC and
not precede the restored workspace update time. The document contains no
session, permission, replay, credential, storage, source-content, artifact-
byte, provider, or execution material.

The recovery helper is internal to the qualification runner. Its accepted
input is only the runner-owned source container/data root and runner-owned
empty target. Its result is a bounded in-memory report of versions, counts,
digests, state comparisons, refusal proof, and cleanup. It exposes no product
operation and emits no reusable recovery artifact.

## Dependencies and Parallel Safety

WRK-0145 is complete and supplies the generated browser export flow. This
packet owns the high-churn approved-lesson browser fixture and runner plus the
direct recovery/assurance documentation, so no packet is declared parallel-
safe. SLI-0073 and CAP-0017 close only after this packet completes and the
slice acceptance is reconciled.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Browser/headless export parity | Browser downloaded one current export | Fresh protected headless client calls the public export API | Closed schema, workspace, revision, and digest are identical and generation chronology is valid | Chromium/capture/live runner |
| Export confidentiality | Mixed Curriculum and Project references exist | Export is captured and normalized | No source content, permission, replay, secret, storage, artifact byte, provider, or execution field appears | runner/pure failure corpus |
| Capacity continuity | Each exact workspace limit is reached | First over-limit mutation is refused | Prior state is unchanged and query, export, removal, and unrelated valid work continue | application/API/live or focused tests |
| Maintenance ordering | Source state is accepted | Recovery capture begins | Application is stopped before database/file capture and no source mutation occurs afterward | runner/process/storage fingerprints |
| Populated target refusal | Independent target contains one marker | Restore is requested | Restore input is not applied and the marker remains unchanged | runner/pure helper test |
| Empty target restore | Target is inactive and verified empty | Logical database and bounded data root are restored | Exact schema fingerprints, workspace/replay meaning, and file digest match the source before activation | PostgreSQL/filesystem/live runner |
| Restored public use | Restored host starts without seed flags | Fresh headless session reads, queries, exports, and exactly replays | Same accepted meaning returns without duplicate mutation or target-domain change | live API/PostgreSQL |
| Source and target isolation | Refusal, restore, and restored reads run | Both topologies are compared | Source remains unchanged and Curriculum, Project, Assessment, Learner-model, Audit, and content facts retain exact fingerprints | runner/PostgreSQL |
| External topology boundary | Caller supplies an acknowledged external database | Runner reaches recovery phase | Recovery is not attempted or claimed because the runner does not own the target lifecycle | runner unit/error path |
| Redacted evidence | Recovery succeeds or fails | Report and diagnostics are emitted | Only allowlisted phases, versions, counts, digests, and booleans appear | pure pytest/live report |
| Anti-rigidity | Safe order, count, Unicode, optional labels, timestamps, and additive report metadata vary | Pure qualification corpus runs | Invariants pass without exact prose, incidental fixture counts, or one ordering | parameterized pytest |
| Cleanup | Qualification succeeds or fails | Runner exits | Source and target apps, containers, dumps, copied data, captures, and temporary root are removed within the owned boundary | runner/finally |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest tests/e2e/approved-lesson/test_replay_qualification.py -q
npm --prefix apps/web run test:browser -- apps/web/tests/browser/personal-workspace
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run build
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0146-qualify-personal-workspace-recovery-and-close.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use repository-pinned Python, Node 24, npm 10.8.2, Playwright Chromium,
Docker, and two uniquely named disposable PostgreSQL 18.4 containers. The
exact clean candidate requires affected verification, a fresh qualifying
receipt, proportionate independent technical review, and successful cleanup.

## Documentation and Evidence Update

Record exact browser/headless export parity; capacity continuity; maintenance
ordering; source immutability; populated-target refusal; empty-target database
and bounded-file restore; restored fresh-session read/query/export/replay;
target-domain isolation; cleanup; focused, live, security, architecture,
affected, aggregate, and independent technical results; changed files;
assumptions; and all unqualified recovery profiles. Approval and reviewer
records remain only in ignored local state.

## Stop Conditions

Stop for a required product backup/restore implementation; executable contract,
OpenAPI, generated-client, migration, fixture-product, dependency, or product
browser change; production credential or database-role design; retained or
external recovery artifact; encryption/key custody; populated/in-place merge;
session or identity recovery claim beyond the existing local single-profile
boundary; managed-cloud, RPO/RTO, availability, retention, legal, provider,
model, or external-execution decision; source mutation; unbounded path or
container cleanup; active scope collision; canonical conflict; stale CAP
package; or material SLI/CAP drift. Route an in-scope qualification defect to
one bounded correction packet instead of silently widening this packet.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report `CAP-0017.SLI-0073.WRK-0146`; exact candidate and receipt; export parity
and confidentiality; exact capacity continuity; stopped-source ordering;
populated-target refusal; empty-target database and bounded-file recovery;
restored fresh-session public API and exact replay; source/target isolation;
focused pytest/Chromium, architecture, security, affected, aggregate, and
independent technical results; changed files; documentation impact;
assumptions; unqualified profiles; and residual gaps. Confirm no product
backup/restore API, schema, generated client, migration, provider, managed-
cloud, separate AI authority, artifact execution, or financial action changed.

## Planning History

- 2026-10-17: Authored just in time after WRK-0145 completed. The packet uses
  the delivered generated-client export and established disposable local
  qualification topology to prove browser/headless parity and one tightly
  bounded stopped-source, empty-target recovery exercise. It adds no product
  recovery surface or support claim, remains within approved CAP-0017 and
  SLI-0073, and requires no lower-level approval.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  recovery-boundary, exact write-scope, executable-check, documentation, and
  planning validation passed with no material CAP or slice drift.
- 2026-10-17: Activated from the recorded base after the implementation gate
  confirmed current CAP authority, the completed WRK-0145 dependency, the
  bounded qualification-only scope, resolved decisions, and no active write
  collision.
- 2026-10-17: Advanced to verification after the generated-browser/headless
  export comparison, focused capacity suites, normal restart, stopped-source
  logical capture, populated-target refusal, empty-target restore, restored-
  session revocation, fresh-session replay, source isolation, redacted report,
  and bounded cleanup all passed in the disposable local topology.
