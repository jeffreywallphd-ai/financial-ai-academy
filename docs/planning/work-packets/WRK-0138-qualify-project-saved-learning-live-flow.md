---
id: WRK-0138
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-17
parent: SLI-0071
capability: CAP-0017
depends_on: [WRK-0137]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/personal-workspace.e2e.ts", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0071-organize-project-workspaces-snapshots-resources.md", "docs/planning/work-packets/WRK-0138-qualify-project-saved-learning-live-flow.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Project Saved-Learning Live Flow

## Objective and Deliverable

Deliver the final integrated evidence for SLI-0071. Extend the existing
isolated PostgreSQL, Python API, reviewed static browser, ordinary headless
HTTP, restart, and cleanup qualifier with one Project-reference Saved Learning
journey; map every slice acceptance statement to current evidence; reconcile
assurance claims; and close SLI-0071 without changing product behavior or
weakening controls.

The protected Personal-workspace and Project APIs remain the common browser,
command-line, service, and future headless-AI boundaries. Qualification must
not add a test-only route, browser-only authority, copied Project state,
artifact execution, or separate AI mode.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, architecture-contracts,
API/security, testing-quality, deployment-operations, interface-design, and
delivery-planning context; apply the change-impact matrix and decision
readiness; inspect CAP-0017, SLI-0071, WRK-0135 through WRK-0137, ADR-0011,
ADR-0012, ADR-0021, Personal-workspace and Project contracts and public
operations, PostgreSQL adapters, generated client, Saved Learning and Project
browser consumers, the approved-lesson live qualifier, affected tests,
assurance sources, known gaps, and nearest READMEs.

## Decisions and Assumptions

- Accepted focused Personal-workspace ownership, inert Project resources,
  reusable Project workspace, single-profile identity, module-owned
  PostgreSQL, generated-client, static-browser, and local-composition decisions
  are sufficient; no durable decision is open.
- The qualifier may observe public HTTP and exact isolated database counts but
  may not import backend internals into the browser, add test-only product
  behavior, or let direct SQL substitute for application authority.
- Existing exact-candidate evidence remains direct only where ancestry and
  unchanged affected files keep it current. Fresh cumulative checks own slice
  closure.
- The tracked static application is regenerated only from the accepted
  TypeScript source and exact lockfile so the isolated live topology exercises
  the same Project Saved Learning candidate qualified by WRK-0137.
- A functional, contract, or evidence-control defect routes to separately
  bounded corrective work. Harmless whitespace, optional wording,
  nonfunctional styling, generated values, or fixture order are fixed locally
  or left to CAP-0031 and do not trigger a re-review loop.

## In Scope

- Run the existing live Project browser journey first, then use exact safe
  Project identifiers from its bounded capture to save a Project workspace,
  immutable checkpoint, and inert file manifest into Saved Learning through
  the generated client.
- Organize Project and Curriculum references together; reload and inspect safe
  technical records; prove that the Personal workspace receives no artifact
  bytes, storage locator, download URL, private authorization fact, or
  executable seam.
- Observe the same accepted workspace through ordinary authenticated headless
  HTTP, prove exact replay and changed-key/stale-revision denial without lost
  or duplicate state, and show browser and non-browser consumers receive the
  same closed public document and deterministic policy.
- Prove Personal-workspace and Project state survive a normal application
  restart without reseeding; correlate exact isolated workspace, mutation,
  Project, checkpoint, and artifact rows while showing Saved Learning does not
  mutate Project, Curriculum, Content, Assessment, or Learner-model state.
- Exercise missing, malformed, guessed, unavailable, or unauthorized Project
  references confidentially without blocking unrelated saved records.
- Extend qualifier unit and architecture tests for capture handoff, closed
  Project reference shape, safe denial, headless/restart comparison,
  exact-row correlation, inert containment, flexible valid values, and cleanup.
- Run cumulative contract, domain, application, PostgreSQL, API,
  OpenAPI/generated-client, web, Chromium, architecture, security, language,
  design, documentation, planning, whitespace, dependency, exact-candidate,
  aggregate-readiness, completion, and independent technical-review checks.
- Reconcile this packet, SLI-0071, the register, architecture verification,
  module/browser/local-operation READMEs, and known gaps with exact results and
  residual unsupported profiles.

## Out of Scope

Any product contract, domain, application, adapter, migration, API, generated
client, browser behavior, Project creation meaning, identity, provider,
dependency, collaboration, sharing, organization tenancy, managed-cloud
policy, arbitrary URL or external-drive resource, semantic search, active
preview, artifact download through Personal workspace, archive expansion,
external execution, network/secret access, Portfolio integration,
Assessment/Learner-model mutation, personalized financial advice or action,
separate AI mode, autonomous durable authority, remote push, or styling
redesign. A needed product or shared-control correction stops this
qualification packet and routes to bounded descendant work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | Project and Saved Learning UI, generated client, current approved-lesson tests | one Personal-workspace E2E scenario | Exercise exact Project references against the real public APIs |
| Live orchestration | approved-lesson runner and its unit tests | named runner and unit-test files | Hand off the bounded Project capture, then correlate browser, headless HTTP, PostgreSQL, restart, and cleanup |
| Product/contracts | Personal-workspace and Project core, persistence, host, OpenAPI, client, UI | none | Qualification observes frozen behavior only |
| Architecture containment | existing local-composition boundary checks | named architecture test only | Prevent alternate authority, private imports, bytes, execution, or unbounded artifacts |
| Documentation and assurance | nearest READMEs, architecture verification, known gaps | named files only where evidence changes truth | Keep direct and unqualified claims honest |
| Slice closure | SLI-0071, WRK-0138, register | named planning files | Record exact evidence and lifecycle closure |

## Contracts and Interfaces

Consume only the accepted session operation, Project public reads, `GET
/api/v1/personal-workspace`, `POST /api/v1/personal-workspace/mutations`, and
the generated TypeScript client. The browser receives exact Project selectors
through a bounded qualification capture containing only already public safe
documents. The Personal-workspace capture contains the complete accepted
public workspace plus one exact public mutation for replay; it contains no
cookie, session secret, database key, object-store key, storage path,
credential, provider payload, artifact bytes, source body, or private target
content.

The Python observer uses the same public routes and server-owned single-profile
session. Direct SQL is evidence-only inside the disposable database and is
limited to exact counts and safe correlation of already public meaning. This
packet creates no public schema or runtime interface.

## Dependencies and Parallel Safety

WRK-0135 through WRK-0137 provide the exact contract, server, generated-client,
and browser candidates. WRK-0138 owns the shared live qualifier and SLI-0071
closure paths, so it is not parallel-safe with another writer in those files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete live journey | isolated PostgreSQL, Python host, reviewed static app, and one live Project with a checkpoint and inert file | Chromium uses exact contextual save links and the generated client | workspace, checkpoint, and inert-file references coexist with Curriculum records and remain organized after reload | live Chromium/API/PostgreSQL |
| API/headless parity | browser-captured public workspace and current session | ordinary HTTP repeats reads and an exact accepted mutation | public state, replay result, provenance, revision, and policy match without browser-only storage | live HTTP/capture |
| Exact Project correlation | bounded Project capture and saved references | public documents and database evidence are compared | every reference binds the exact Project, workspace revision, checkpoint digest, or inert manifest facts and no copied content | browser/headless/PostgreSQL |
| Retry and conflict | accepted key/revision plus changed and stale requests | replay and conflicts run | exact replay is stable; changed reuse and stale work do not duplicate or overwrite state | API/PostgreSQL |
| Confidential target failure | malformed, missing, guessed, unavailable, or unauthorized Project selectors | protected operations are attempted | failures reveal no protected existence or private state and unrelated saved records remain usable | API/security/live |
| No target mutation | Project, Curriculum, Assessment, and Learner-model state is measured | references are saved, organized, archived, removed, replayed, and reopened | target state and evidence counts remain unchanged | architecture/API/PostgreSQL |
| Inert containment | a saved Project file manifest exists | Saved Learning is inspected and replayed | no bytes, object locator, active preview, download, archive, subprocess, network, package, or execution seam is exposed | architecture/security/live |
| Restart persistence | accepted Project references and replay rows exist | the application restarts without reseeding | public read and exact replay preserve complete meaning and row counts | live restart/headless |
| Flexible valid shapes | Unicode, varied Project IDs, revisions, digests, manifest kinds/sizes, optional safe fields, generated IDs/times, and mixed order | cumulative suites and live flow run | meaning does not depend on one fixed count, presentation detail, generated value, or styling | compatibility/unit/component/live |
| Accessible parity | learner actions run with keyboard, focus, reflow, themes, forced colors, and reduced motion | cumulative browser and design checks execute | content, action, status, error, and technical-record meaning remain equivalent | component/Chromium/design |
| Cleanup and honest limits | qualification succeeds or fails | teardown and evidence reconciliation run | exact process, container, network, capture files, and temp root are bounded; managed cloud, collaboration, later adapters, and separate AI mode remain unclaimed | runner/docs |

## Verification Commands

Run packet validation, implementation gate, and planning integrity; complete
Personal-workspace Project-reference contract/conformance, domain/application/
Project-gateway, PostgreSQL migration/atomicity/replay/conflict/restart/
isolation, protected API success/denial, OpenAPI reproduction, generated-client
reproduction and usage typecheck; full web unit/component, TypeScript
typecheck/lint/build, focused mocked Project Saved Learning Chromium, and the
isolated approved-lesson workflow containing the new live journey.

Run approved-lesson runner unit and architecture tests; module/import and
persistence-ownership checks; inert-artifact/security, learner-language,
design-system, documentation, planning, dependency, Python compilation, and
whitespace checks; affected exact-candidate verification; `python
dev-tools/agent/check_ready.py`; one independent technical review; and the
deterministic SLI-0071 completion gate. Use prepared runtimes and an isolated
disposable PostgreSQL topology. Never claim a command or environment that did
not pass, and always run exact cleanup.

## Documentation and Evidence Update

Record the delivered learner outcome; scenario-to-evidence trace; exact
candidate and receipt; focused and cumulative results; environment;
contract/API/browser/headless parity; Project correlation, provenance,
idempotency, concurrency, PostgreSQL restart, target non-mutation, inert
containment, accessibility, cleanup; documentation impact; assumptions;
checks not performed; residual risk; unsupported profiles; CAP-package
conformance; and material-drift assessment. Update assurance claims only where
executable evidence changes their truth. Approval and reviewer records remain
ignored local state.

## Stop Conditions

Stop for missing evidence; a product or shared-control failure outside this
packet; contract, migration, generated-client, or browser-behavior change;
client-owned identity, authorization, revision, provenance, or policy; copied
Project content or transferred ownership; retained-data loss; browser/headless
semantic difference; private-data leak; artifact bytes or execution through
Personal workspace; direct cross-module persistence access; unisolated
qualification; provider, licensing, tenancy, cloud, recovery, model-authority,
legal/commercial, or external-execution decision; active write collision;
stale CAP package; or material CAP-0017 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
nonfunctional styling, generated values, fixture order, or another
inconsequential in-scope correction.

## Required Handoff

Report `CAP-0017.SLI-0071.WRK-0138`; exact candidate and receipt; scenario map;
contract/API/browser/headless parity; exact Project correlation and provenance;
revision/idempotency/conflict; PostgreSQL restart, target non-mutation, and
inert-containment evidence; accessibility, security, architecture, cleanup;
exact checks and environments; changed files; documentation impact;
assumptions and residual gaps. Confirm that no product behavior, target
ownership, artifact execution, Portfolio/domain adapter, provider,
managed-cloud profile, arbitrary external file, Assessment/Learner-model
effect, financial action, separate AI mode, or autonomous authority was added.

## Planning History

- 2026-10-17: Authored just in time after WRK-0137 completed. The packet adds
  the missing integrated Project-reference Saved Learning journey to the
  existing isolated live qualifier, then closes SLI-0071 from direct browser,
  headless HTTP, PostgreSQL, restart, containment, and cleanup evidence. It
  changes no product contract or authority and exposes no new decision gate.
