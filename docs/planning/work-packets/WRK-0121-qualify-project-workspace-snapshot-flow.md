---
id: WRK-0121
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0031
capability: CAP-0007
depends_on: [WRK-0123]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/project-workspace.e2e.ts", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0121-qualify-project-workspace-snapshot-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: 7977d7051a0cb9062525f61c40670de97f8f7835
claim_id: WRK-0121:ad1ab5d1-9e50-4d27-aadb-be307b2ba251
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T02:51:42Z
---

# Agent Work Packet: Qualify Project Workspace and Snapshot Flow

## Objective and Deliverable

Deliver the final integrated evidence for SLI-0031. Extend the existing
isolated PostgreSQL, Python API, static-browser, headless HTTP, restart, and
cleanup qualifier with one Project workspace journey; map every slice
acceptance statement to direct current evidence; reconcile assurance claims;
and close SLI-0031 without changing product behavior or weakening controls.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the delivery-planning, Project, API/security,
testing-quality, deployment-operations, and interface-design context; apply the
change-impact matrix and decision readiness; inspect CAP-0007, SLI-0031,
WRK-0118 through WRK-0120, ADR-0011, ADR-0012, Project contracts and public
operations, object and PostgreSQL adapters, migrations, generated client,
browser consumers, approved-lesson live qualifier, affected tests, assurance
sources, known gaps, and nearest READMEs.

## Decisions and Assumptions

- Accepted inert-artifact, reusable-Project, single-profile identity,
  module-owned PostgreSQL, generated-client, static-browser, and local
  composition decisions are sufficient.
- The Project API remains the shared browser and non-browser/headless boundary.
  The qualifier may observe public HTTP and exact isolated database counts but
  must not add a test-only product route or browser-only authority.
- Existing exact-candidate receipts remain direct evidence only where ancestry
  and unchanged affected files keep them current. Fresh cumulative checks own
  slice closure.
- Harmless whitespace, optional wording, or nonfunctional styling does not
  trigger a correction cycle. A functional or evidence-control defect routes
  to a separately bounded corrective packet.

## In Scope

- Add one live generated-client Chromium journey that creates an independent
  Project, reopens its workspace, saves Unicode notes and a safe HTTPS source,
  admits a bounded inert artifact with exact provenance, downloads exact bytes,
  closes a checkpoint, exports its evidence, continues live work, and records
  only bounded identifiers needed by the Python qualifier.
- Observe the same accepted workspace, artifact, checkpoint, and export through
  ordinary authenticated headless HTTP; prove exact retry, immutable snapshot,
  continued live revision, safe download headers, evidence correlation, and
  absence of browser-only state.
- Prove Project workspace metadata and object bytes survive a normal application
  restart without reseeding, while the checkpoint remains unchanged and the
  live workspace retains its later revision.
- Observe exact isolated Project, Assessment, and Learner-model persistence to
  prove the journey creates no submission, completion, mastery, competency, or
  learner-projection side effect.
- Extend qualifier unit tests for captured-result validation, headless/restart
  comparison, private-field denial, and containment/cleanup behavior.
- Run cumulative contract, domain, application, object, PostgreSQL, API,
  OpenAPI/client, web, Chromium, architecture, security, language, design,
  documentation, planning, whitespace, dependency, exact-candidate, readiness,
  and independent technical review checks.
- Reconcile this packet, SLI-0031, the register, architecture verification, and
  known gaps with exact results and residual unsupported profiles.

## Out of Scope

Any product contract, domain, application, adapter, migration, API, generated
client, browser behavior, seed, fixture, dependency, provider, identity,
tenancy, storage policy, artifact execution or active preview, archive
expansion, Portfolio integration, assessment submission, grading, mastery,
competency, adaptive authority, financial action or advice, managed-cloud
composition, production recovery, external execution, separate AI mode, remote
push, or styling redesign. A needed product or shared-control change stops this
evidence packet and routes to bounded correction.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | Project UI, generated client, current approved-lesson tests | one Project workspace E2E scenario | Exercise the delivered browser against the real public API |
| Live orchestration | approved-lesson runner and its unit tests | named runner and unit test | Correlate browser capture, headless HTTP, persistence, restart, and cleanup |
| Product/contracts | Project core, persistence, host, OpenAPI, client, UI | none | Qualification observes frozen behavior only |
| Assurance | architecture verification and known gaps | named assurance files only if current claims change | Keep direct and unqualified evidence honest |
| Slice closure | SLI-0031, WRK-0121, register | named planning files | Record exact evidence and lifecycle closure |

## Contracts and Interfaces

Consume only the accepted protected Project HTTP operations and generated
TypeScript client. The browser capture contains stable public Project,
artifact, and snapshot identifiers plus expected digests/revisions; it contains
no session secret, learner identifier, database key, object path, credential,
or private provider payload. The Python observer uses the same public routes
and server-owned single-profile session. Direct SQL is evidence-only and is
limited to counts and exact public-record correlations inside the disposable
database.

This packet produces no new public schema or runtime interface. Its new
interface is a bounded live qualification record plus tracked planning and
assurance evidence. Approval and reviewer records remain ignored local state.

## Dependencies and Parallel Safety

WRK-0118 through WRK-0120 provide the exact contract, server, generated-client,
and browser candidates. WRK-0121 owns the shared live qualifier and SLI-0031
closure files, so it is not parallel-safe with another writer in those paths.
It must finish before SLI-0032 begins.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete live journey | isolated PostgreSQL, Python host, and reviewed static app | Chromium uses the generated client | an independent Project accepts note, source, inert file, checkpoint, export, and later edit end to end | live Chromium/API/PostgreSQL |
| API/headless parity | captured public identifiers and current session | ordinary HTTP repeats supported reads/download/export | headless results match browser-observed revisions, digests, bytes, and snapshot facts | live HTTP/capture |
| Retry and concurrency | accepted request keys and expected revisions | exact retry, changed reuse, and stale write run | exact replay is stable; conflicts do not duplicate or overwrite work | API/PostgreSQL |
| Inert containment | code-like and data-like bytes are admitted only as opaque artifacts | metadata, download, export, and architecture are inspected | exact bytes remain downloadable but never execute, expand, render actively, call a provider, or gain secrets/network | object/API/security/architecture |
| Snapshot integrity | a checkpoint closes at one exact Project/workspace revision | live work continues and evidence is exported | the snapshot record and digest remain immutable while the live revision advances | API/PostgreSQL/Chromium |
| Restart persistence | accepted workspace, object, and snapshot state exists | the application restarts without reseeding | public reads, download, export, and retry preserve exact meaning and bytes | live restart/headless |
| Authorization and privacy | invalid session, origin, ownership, identity, artifact, or snapshot input | protected routes are attempted | failures are bounded and reveal no private storage or cross-learner facts | API/security/live |
| No learning side effect | the Project journey completes | isolated schemas are inspected | no Assessment event/submission or Learner-model projection/history is created | PostgreSQL evidence |
| Flexible valid shape | Unicode, counts, ordering, optional metadata, classifications, IDs, and times vary | cumulative suites and live flow run | valid meaning does not depend on one fixture, exact copy, or visual styling | compatibility/unit/component/live |
| Accessibility parity | learner actions run with keyboard, narrow layout, themes, and forced settings | Chromium and design checks execute | content, actions, focus, status, and technical records remain equivalent | component/Chromium/design |
| Cleanup and honest limits | qualification succeeds or fails | teardown and evidence reconciliation run | exact process, container, network, and temp root are bounded; managed cloud, production recovery, Portfolio, execution, and separate AI mode remain unclaimed | runner/docs |

## Verification Commands

Run packet validation and planning integrity; complete Project workspace
contract/conformance, domain/application, object-adapter, PostgreSQL migration,
concurrency, rollback, restart, API success/denial, OpenAPI, and generated-client
suites; full web unit/component, TypeScript typecheck/lint/build, focused mocked
Project Chromium, and the isolated approved-lesson live workflow containing the
new Project journey. Run architecture, security, learner-language,
design-system, documentation, dependency, and whitespace checks; affected
exact-candidate verification; `python dev-tools/agent/check_ready.py`; one
independent technical review; and the deterministic slice-completion gate.

Use the prepared Python/Node runtimes and an isolated disposable PostgreSQL
container or explicitly acknowledged isolated external database. Never claim a
suite or environment that did not pass, and always run exact cleanup.

## Documentation and Evidence Update

Record a concise scenario-to-evidence trace, exact candidate and receipt,
focused and cumulative check counts, environment, browser/headless parity,
artifact and snapshot integrity, restart and cleanup result, zero learning-state
effects, documentation impact, assumptions, residual risks, and unsupported
profiles. Update assurance sources only where the new evidence changes their
truth; do not rewrite them for timestamps.

## Stop Conditions

Stop for missing evidence; product/control failure outside this packet;
contract or migration change; client-owned identity, authorization, revision,
digest, or policy; retained-data loss; browser/headless semantic difference;
active artifact execution/rendering/network/secret behavior; private-data leak;
cross-module persistence access; unisolated qualification; provider, tenancy,
cloud, recovery, licensing, legal, commercial, model-authority, or external-
execution decision; active write collision; stale CAP package; or material
CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
nonfunctional styling, or another inconsequential in-scope correction.

## Required Handoff

Report `CAP-0007.SLI-0031.WRK-0121`; exact candidate and receipt; scenario map;
contract/API/browser/headless parity; artifact containment; snapshot integrity;
PostgreSQL restart and zero-learning-effect evidence; accessibility, security,
architecture, containment, and cleanup; exact checks and environments; changed
files; documentation impact; assumptions and residual gaps. Confirm that no
product behavior, provider, managed-cloud profile, external execution, live
Portfolio integration, assessment/mastery effect, separate AI mode, or
autonomous authority was added.

## Planning History

- 2026-10-17: Authored just in time after WRK-0120 completed. The packet adds
  the missing integrated Project workspace journey to the existing isolated
  live qualifier, then closes SLI-0031 from direct browser, headless HTTP,
  PostgreSQL, restart, containment, and cleanup evidence. It changes no product
  contract or authority and exposes no new decision gate.
- 2026-10-17: Released back to ready after the live journey reproduced a real
  snapshot-digest defect outside this qualification-only write scope. WRK-0122
  owns the bounded canonical-timestamp correction; this packet resumes after
  that prerequisite completes.
- 2026-10-17: Reclaimed from clean base `55a5737` after WRK-0122 completed with
  exact verification and no open technical findings. The packet resumes the
  isolated live Project qualifier without expanding product authority or its
  declared write scope.
- 2026-10-17: Released again after the live export check proved that FastAPI
  expanded a canonical fractional timestamp with a trailing zero and thereby
  changed the exact public JSON used by clients to verify `export_digest`.
  WRK-0123 owns the Project-only API serialization correction; this packet
  resumes after that prerequisite completes.
- 2026-10-17: Reclaimed after WRK-0123 completed, then released before
  packet-start or any file lease when the current instruction redirected work
  to CAP-0012, CAP-0024, and CAP-0027 package revalidation. No implementation
  or qualification result changed; the packet remains ready to resume.
- 2026-10-17: Reclaimed from clean base `7977d70`; packet-start confirmed the
  unchanged evidence-only acceptance set. All 28 focused qualifier tests and
  the isolated PostgreSQL 18.4/Python/static/generated-client/headless/pinned-
  Chromium workflow passed, including all 11 browser scenarios and bounded
  teardown. Exact-candidate checks and independent review remain before close.
