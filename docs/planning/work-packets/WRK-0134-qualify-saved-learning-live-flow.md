---
id: WRK-0134
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0070
capability: CAP-0017
depends_on: [WRK-0133]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/personal-workspace.e2e.ts", "backend/src/financial_ai_academy/modules/personal_workspace/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0070-save-learning-notes-bookmarks-collections.md", "docs/planning/work-packets/WRK-0134-qualify-saved-learning-live-flow.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Saved Learning Live Flow

## Objective and Deliverable

Deliver the final integrated evidence for SLI-0070. Extend the existing
isolated PostgreSQL, Python API, static-browser, headless HTTP, restart, and
cleanup qualifier with one Saved Learning journey; map every slice acceptance
statement to direct current evidence; reconcile assurance claims; and close
SLI-0070 without changing product behavior or weakening controls.

The protected Personal-workspace API remains the common browser, command-line,
service, and future headless-AI boundary. Qualification must not add a test-only
product route, browser-only authority, separate AI mode, or alternate workspace
model.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, architecture-contracts,
API/security, testing-quality, deployment-operations, interface-design, and
delivery-planning context; apply the change-impact matrix and decision
readiness; inspect CAP-0017, SLI-0070, WRK-0131 through WRK-0133, ADR-0021,
Personal-workspace contracts and public operations, Curriculum source reads,
PostgreSQL adapter and migration, generated client, Saved Learning browser
consumer, approved-lesson live qualifier, affected tests, assurance sources,
known gaps, and nearest READMEs.

## Decisions and Assumptions

- Accepted focused Personal-workspace ownership, single-profile identity,
  module-owned PostgreSQL, generated-client, static-browser, and local
  composition decisions are sufficient; no durable decision is open.
- The qualifier may observe public HTTP and exact isolated database counts but
  may not import backend internals into the browser, add test-only product
  behavior, or let direct SQL substitute for application authority.
- Existing exact-candidate evidence remains direct only where ancestry and
  unchanged affected files keep it current. Fresh cumulative checks own slice
  closure.
- A functional, contract, or evidence-control defect routes to a separately
  bounded corrective packet. Harmless whitespace, optional wording,
  nonfunctional styling, generated values, or fixture order are fixed locally
  or left to CAP-0031 and do not trigger a re-review loop.

## In Scope

- Add one live generated-client Chromium journey that enters Saved Learning
  from an approved opportunity or exact lesson, creates a Unicode note and
  labeled bookmark, creates and orders a collection, archives/restores and
  reorders learner-owned records, reloads the route, and writes a bounded
  public capture for the Python qualifier.
- Observe the same accepted workspace through ordinary authenticated headless
  HTTP, prove exact retry and changed-key/stale-revision denial without lost or
  duplicate state, and show that browser and non-browser consumers receive the
  same closed public document and policy.
- Prove Personal-workspace state and replay evidence survive a normal
  application restart without reseeding; correlate exact isolated workspace
  and mutation rows while preserving Curriculum, Content, Assessment, Learner
  model, and Project state.
- Extend qualifier unit tests for capture validation, headless/restart
  comparison, safe denial, closed public shape, exact-row correlation, and
  containment/cleanup behavior.
- Run cumulative contract, domain, application, PostgreSQL, API,
  OpenAPI/generated-client, web, Chromium, architecture, security, language,
  design, documentation, planning, whitespace, dependency, exact-candidate,
  aggregate readiness, completion, and independent technical-review checks.
- Reconcile this packet, SLI-0070, the register, architecture verification,
  module/browser/local-operation READMEs, and known gaps with exact results and
  residual unsupported profiles.

## Out of Scope

Any product contract, domain, application, adapter, migration, API, generated
client, browser behavior, seed meaning, identity, provider, dependency,
collaboration, sharing, organization tenancy, managed-cloud policy, arbitrary
file or URL support, semantic search, external execution, network/secret
access, Project or Portfolio resource adapters, Assessment/Learner-model
mutation, personalized financial advice or action, separate AI mode,
autonomous durable authority, remote push, or styling redesign. A needed
product or shared-control correction stops this qualification packet and
routes to bounded descendant work.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | Saved Learning UI, generated client, current approved-lesson tests | one Personal-workspace E2E scenario | Exercise the delivered browser against the real public API |
| Live orchestration | approved-lesson runner and its unit tests | named runner and unit-test files | Correlate browser capture, headless HTTP, PostgreSQL, restart, and cleanup |
| Product/contracts | Personal-workspace core, source gateway, persistence, host, OpenAPI, client, UI | none | Qualification observes frozen behavior only |
| Architecture containment | existing local-composition boundary checks | named architecture test only | Prevent alternate authority, extra servers, private imports, or unbounded artifacts |
| Documentation and assurance | nearest READMEs, architecture verification, known gaps | named files only where evidence changes truth | Keep direct and unqualified claims honest |
| Slice closure | SLI-0070, WRK-0134, register | named planning files | Record exact evidence and lifecycle closure |

## Contracts and Interfaces

Consume only `GET /api/v1/personal-workspace`, `POST
/api/v1/personal-workspace/mutations`, the accepted session operation,
Curriculum-owned public source routes, and the generated TypeScript client. The
browser capture contains only the complete accepted public workspace plus the
exact public mutation needed for replay; it contains no session secret,
learner identifier beyond accepted response meaning, database key, storage
path, credential, provider payload, lesson body, or private target content.

The Python observer uses the same public routes and server-owned single-profile
session. Direct SQL is evidence-only inside the disposable database and is
limited to counts and safe correlation of the already public workspace/replay
meaning. This packet creates no new public schema or runtime interface.

## Dependencies and Parallel Safety

WRK-0131 through WRK-0133 provide the exact contract, server, generated-client,
and browser candidates. WRK-0134 owns the shared live qualifier and SLI-0070
closure files, so it is not parallel-safe with another writer in those paths.
It must finish before SLI-0071 begins.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete live journey | isolated PostgreSQL, Python host, reviewed static app, and approved learning source | Chromium uses the generated client | notes, bookmarks, ordered collections, lifecycle actions, reload, and exact technical records work end to end | live Chromium/API/PostgreSQL |
| API/headless parity | browser-captured public workspace and current session | ordinary HTTP repeats reads and an exact accepted mutation | public state, replay result, provenance, revision, and policy match without browser-only storage | live HTTP/capture |
| Retry and conflict | accepted key/revision plus changed and stale requests | replay and conflicts run | exact replay is stable; changed reuse and stale work do not duplicate or overwrite state | API/PostgreSQL |
| Source and authority isolation | exact Curriculum-owned references and learner-owned workspace records | the complete journey and database evidence are inspected | source state is not copied or mutated; workspace references grant no permission | architecture/API/PostgreSQL |
| Restart persistence | accepted workspace and replay rows exist | the application restarts without reseeding | public read and exact replay preserve complete meaning and row counts | live restart/headless |
| Authorization and privacy | missing session/permission, selected learner, guessed IDs, bad origin, or unavailable source | protected operations are attempted | failures are bounded and reveal no private learner, storage, or hidden-source detail | API/security/live |
| Atomic limits and interruption | record, text, collection, membership, revision, and persistence boundaries | overflow or simulated failure occurs | no partial workspace/replay state appears and unrelated accepted data remains usable | domain/PostgreSQL |
| Flexible valid shapes | Unicode, empty and populated state, varied counts/order, optional labels, IDs, and times vary | cumulative suites and live flow run | meaning does not depend on one fixture, incidental copy, generated value, or styling | compatibility/unit/component/live |
| Accessible parity | learner actions run with keyboard, focus, reflow, themes, forced colors, and reduced motion | Chromium and design checks execute | content, action, status, error, and technical-record meaning remain equivalent | component/Chromium/design |
| Cleanup and honest limits | qualification succeeds or fails | teardown and evidence reconciliation run | exact process, container, network, and temp root are bounded; managed cloud, domain adapters, external execution, and separate AI mode remain unclaimed | runner/docs |

## Verification Commands

Run packet validation, implementation gate, and planning integrity; complete
Personal-workspace contract/conformance, domain/application/source-gateway,
PostgreSQL migration/atomicity/replay/conflict/restart/isolation, protected API
success/denial, OpenAPI reproduction, generated-client reproduction and usage
typecheck; full web unit/component, TypeScript typecheck/lint/build, focused
mocked Personal-workspace Chromium, and the isolated approved-lesson workflow
containing the new live journey.

Run approved-lesson runner unit and architecture tests; module/import and
persistence-ownership checks; security, learner-language, design-system,
documentation, planning, dependency, Python compilation, and whitespace
checks; affected exact-candidate verification; `python
dev-tools/agent/check_ready.py`; one independent technical review; and the
deterministic SLI-0070 completion gate. Use prepared runtimes and an isolated
disposable PostgreSQL topology. Never claim a command or environment that did
not pass, and always run exact cleanup.

## Documentation and Evidence Update

Record the delivered learner outcome; scenario-to-evidence trace; exact
candidate and receipt; focused and cumulative results; environment;
contract/API/browser/headless parity; provenance, source isolation,
idempotency, concurrency, PostgreSQL restart, accessibility, containment, and
cleanup; documentation impact; assumptions; checks not performed; residual
risk; unsupported profiles; CAP-package conformance; and material-drift
assessment. Update assurance claims only where executable evidence changes
their truth. Approval and reviewer records remain ignored local state.

## Stop Conditions

Stop for missing evidence; product or shared-control failure outside this
packet; contract, migration, or browser-behavior change; client-owned identity,
authorization, revision, provenance, or policy; retained-data loss;
browser/headless semantic difference; source copying or mutation; private-data
leak; cross-module persistence access; unisolated qualification; provider,
licensing, tenancy, cloud, recovery, model-authority, legal/commercial, or
external-execution decision; active write collision; stale CAP package; or
material CAP-0017 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
nonfunctional styling, generated values, fixture order, or another
inconsequential in-scope correction.

## Required Handoff

Report `CAP-0017.SLI-0070.WRK-0134`; exact candidate and receipt; scenario map;
contract/API/browser/headless parity; provenance and source isolation;
revision/idempotency/conflict; PostgreSQL restart and no-target-effect evidence;
accessibility, security, architecture, containment, and cleanup; exact checks
and environments; changed files; documentation impact; assumptions and
residual gaps. Confirm that no product behavior, Project/domain adapter,
provider, managed-cloud profile, arbitrary file, external execution,
Assessment/Learner-model effect, financial action, separate AI mode, or
autonomous authority was added.

## Planning History

- 2026-10-17: Authored just in time after WRK-0133 completed. The packet adds
  the missing integrated Saved Learning journey to the existing isolated live
  qualifier, then closes SLI-0070 from direct browser, headless HTTP,
  PostgreSQL, restart, containment, and cleanup evidence. It changes no product
  contract or authority and exposes no new decision gate.
