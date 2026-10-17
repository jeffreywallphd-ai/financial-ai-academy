---
id: WRK-0129
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0032
capability: CAP-0007
depends_on: ["WRK-0128"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/project-learning-submission.e2e.ts", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/learner_model/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0032-submit-a-project-snapshot-for-learning.md", "docs/planning/work-packets/WRK-0129-qualify-project-learning-submission-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify Project Learning Submission Flow

## Objective and Deliverable

Deliver the final integrated evidence for SLI-0032. Extend the isolated
PostgreSQL, Python API, reviewed static browser, generated-client, headless
HTTP, restart, and cleanup qualifier with one Project learning-submission
journey; map every slice acceptance statement to current direct evidence;
reconcile assurance claims; and close SLI-0032 without changing product
behavior or weakening the deterministic, privacy, provenance, or inert-artifact
controls delivered by WRK-0124 through WRK-0128.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, architecture-contracts, learning-
adaptation, API-security, testing-quality, deployment-operations, interface-
design, and delivery-planning context. Apply the change-impact matrix and
decision readiness. Inspect CAP-0007, SLI-0032, WRK-0124 through WRK-0128,
ADR-0011, ADR-0012, the Project-submission and Assessment contracts, Project,
Content, Curriculum, Assessment, Learner-model, Audit, and Identity public
operations, migrations, OpenAPI/generated client, Project browser consumers,
the approved-lesson qualifier, affected tests, assurance sources, known gaps,
and nearest READMEs.

## Decisions and Assumptions

- Accepted inert-artifact, Project lifecycle, module ownership, single-profile
  identity, PostgreSQL, generated-client, and local static-browser decisions
  are sufficient; no unresolved decision gate is crossed.
- Assessment remains authoritative for deterministic Project submission,
  immutable evidence, history, replay, and supersession. Learner model owns
  only rebuildable bounded activity completion, and Audit owns only append-
  oriented integrity references.
- The Project API is the shared browser and non-browser/headless boundary. The
  qualifier may inspect bounded public HTTP results and exact isolated database
  counts/correlations but must not add a test-only product route or duplicate
  business authority.
- Existing exact-candidate receipts remain packet evidence only where ancestry
  and unchanged affected files keep them current. Fresh cumulative checks and
  the live journey own slice closure.
- Harmless whitespace, optional wording, or nonfunctional styling cannot open
  a correction cycle. A functional or evidence-control defect routes to one
  separately bounded corrective packet.

## In Scope

- Add one live generated-client Chromium journey that starts a learning-linked
  Project from an exact approved brief/placement, records varied Unicode notes,
  safe sources, and multiple inert resources, closes two immutable snapshots,
  submits each exact snapshot against all ordered milestones, corrects one
  bounded incomplete mapping, and reopens retained superseding history.
- Capture only bounded public Project, snapshot, candidate, submission,
  evidence, event-reference, history, and completion facts needed for the
  Python qualifier. Exclude session secrets, learner identifiers, private
  storage locations, artifact bytes, answers, database keys, and stack traces.
- Observe the same candidate, exact evidence, ordered history, supersession,
  and bounded Project activity-completion meaning through ordinary
  authenticated headless HTTP. Prove the browser does not own hidden durable
  state or a separate contract.
- Prove exact retry reuses one accepted submission, changed reuse conflicts,
  independent Projects remain ineligible, later live Project work does not
  rewrite submitted snapshots/evidence, and malformed/cross-scope requests
  create no partial evidence or projection.
- Inspect the disposable PostgreSQL state to correlate one immutable
  Assessment aggregate per accepted request, occurrence ordering, retained
  supersession, Learner-model projection source references, and Audit integrity
  references without treating SQL as application authority.
- Restart the ordinary application without reseeding and prove the same public
  evidence/history/completion, projection source digest, Audit references, and
  inert snapshot meaning remain available; then prove deterministic replay is
  idempotent and bounded cleanup removes only the isolated topology.
- Extend qualifier unit tests for capture closure, headless/restart comparison,
  exact retry and count invariants, source/evidence/projection/Audit
  correlation, private-field denial, independent-Project denial, and cleanup.
- Run cumulative contract, domain, application, migration, PostgreSQL,
  concurrency, API, OpenAPI/client, web, Chromium, architecture, security,
  learner-language, design, documentation, planning, dependency, whitespace,
  exact-candidate, readiness, and independent-review checks.
- Reconcile this packet, SLI-0032, the register, architecture verification,
  known gaps, and only actually stale module guidance with exact evidence and
  explicit unsupported profiles.

## Out of Scope

Any product contract, domain, application, adapter, migration, API, generated
client, browser behavior, seed meaning, dependency, provider, identity,
tenancy, storage policy, artifact execution or active preview, archive
expansion, Portfolio integration, qualitative review, grading, mastery,
competency estimation, adaptive inference, financial action or advice,
managed-cloud composition, production recovery, external queues or execution,
separate AI mode, remote push, or styling redesign. A needed product or shared-
control change stops this evidence packet and routes to a bounded correction.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | Project UI, generated client, approved-lesson browser scenarios | one Project learning-submission E2E scenario | Exercise the delivered browser against the real public API |
| Live orchestration | approved-lesson runner and its unit tests | named runner and unit test | Correlate browser capture, headless HTTP, PostgreSQL, restart, projection, Audit, and cleanup |
| Product/contracts | completed Project, Assessment, Learner-model, Audit, API/client, browser implementation | none | Qualification observes frozen behavior only |
| Module guidance | current Project-submission consumer/owner statements | named Assessment, Learner-model, and Audit READMEs only if stale | Keep nearest ownership and evidence claims exact |
| Assurance | architecture verification and known gaps | named assurance files only when evidence changes their truth | Promote only directly qualified local claims |
| Slice closure | SLI-0032, WRK-0129, register | named planning files | Record exact evidence and lifecycle closure |

## Contracts and Interfaces

Consume only the accepted protected Project and Project-submission HTTP
operations and generated TypeScript client. The browser capture contains stable
public Project, snapshot, candidate, submission, evidence, source-reference,
history, and completion identifiers/digests/versions plus expected ordering; it
contains no session token, learner selector, storage locator, database key,
credential, private provider payload, artifact bytes, or internal diagnostic.

The Python observer uses the same server-owned single-profile session and
ordinary public routes. Direct SQL is evidence-only, confined to the
disposable database, and limited to counts and exact public-record
correlations. This packet produces no new public schema or runtime interface.
Approval and reviewer records remain only in ignored local storage.

## Dependencies and Parallel Safety

WRK-0124 through WRK-0128 provide the exact contracts, persistence, public
operations, projections, Audit references, generated client, and browser flow.
WRK-0129 owns the shared live qualifier and SLI-0032 closure sources, so it is
not parallel-safe with another writer in those paths. It must complete before
SLI-0033 selection begins.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete live journey | isolated PostgreSQL, Python host, reviewed static app, and exact approved learning source | Chromium creates a learning Project, closes snapshots, corrects a mapping, submits, and reopens | immutable evidence, superseding history, and bounded activity completion appear end to end | live Chromium/API/PostgreSQL |
| Browser/headless parity | captured public identities and current session | ordinary HTTP repeats candidate, evidence, history, and completion reads | exact versions, digests, ordering, mappings, supersession, and meaning match browser-observed state | live HTTP/capture |
| Exact retry and conflict | one accepted submission and its request identity | exact and changed retries run | exact replay returns the original evidence; changed reuse conflicts; no duplicate aggregate/event/projection/Audit row appears | API/PostgreSQL |
| Independent and invalid denial | independent origin or missing, duplicate, unknown, live-only, stale, guessed, cross-Project, or cross-learner input | candidate/read/submit routes are attempted | failure is bounded and creates no accepted evidence, projection, Audit reference, or private disclosure | API/security/live |
| Immutable later work | a submitted closed snapshot exists | the live workspace changes and a later snapshot is submitted | prior snapshot/evidence bytes remain stable; the new occurrence references the prior submission without rewriting it | API/PostgreSQL/live |
| Projection and Audit correlation | accepted Assessment events exist | Learner model rebuilds and Audit reconciles | exact public event/evidence sources produce one bounded completion view and append-only integrity references | PostgreSQL/headless |
| Restart and replay | accepted evidence, projection, and Audit references exist | the application restarts without reseeding and replay repeats | public results and source digests remain exact; replay is idempotent and no partial state appears | live restart/headless/PostgreSQL |
| Flexible valid shape | milestone/resource counts, kinds, ordering, Unicode, optional provenance, IDs, times, and two snapshots vary | cumulative suites and live flow run | valid meaning does not depend on one fixture, exact presentation, or single-resource shape | compatibility/unit/component/live |
| Accessible parity | correction, submission, history, and technical disclosures run with keyboard and constrained display settings | component and Chromium checks execute | focus, labels, status, reflow, themes, forced colors, and reduced motion preserve equivalent meaning | component/Chromium/design |
| No execution or advice | code-like and financial-context resources remain inert | they are mapped, submitted, and reopened | no bytes execute/render actively, no provider/network/secret is invoked, and no quality, mastery, competency, advice, or performance claim appears | architecture/security/language/live |
| Cleanup and honest limits | qualification succeeds or fails | teardown and evidence reconciliation run | exact process, container, network, and temp roots are bounded; managed cloud, production recovery, Portfolio/provider integration, execution, and separate AI mode remain unclaimed | runner/docs |

## Verification Commands

Run packet validation and planning integrity; the complete Project-submission
contract/conformance, Assessment policy/application/PostgreSQL, Project source,
Learner-model projection, Audit reconciliation, migration, concurrency,
rollback, restart, API success/denial, OpenAPI, and generated-client suites;
full web unit/component, TypeScript typecheck/lint/build, focused mocked Project
Chromium, and the isolated approved-lesson live workflow containing the new
Project learning-submission journey. Run architecture, security, learner-
language, design-system, documentation, dependency, and whitespace checks;
affected exact-candidate verification; `python dev-tools/agent/check_ready.py`;
one independent technical review; and the deterministic slice-completion gate.

Use the prepared Python/Node runtimes, repository-local Windows temporary root,
and the already allocated isolated disposable PostgreSQL container or an
equivalently explicit isolated database. Never claim a suite or environment
that did not pass, and always run exact cleanup.

## Documentation and Evidence Update

Record a concise scenario-to-evidence trace, exact candidate and receipt,
focused and cumulative check counts, environment, browser/headless parity,
immutable evidence/supersession, projection/Audit correlation, restart and
cleanup results, documentation impact, assumptions, residual risks, and
unsupported profiles. Update module or assurance sources only where new direct
evidence changes their truth; do not rewrite them merely to add a timestamp.

## Stop Conditions

Stop for missing evidence; a product/control failure outside this packet;
contract, migration, API, client, or browser behavior change; client-owned
identity, authorization, validation, completion, supersession, version, digest,
or time; retained-data loss; browser/headless semantic difference; active
artifact execution/rendering/network/secret behavior; private-data leak;
cross-module persistence access; unisolated qualification; provider, tenancy,
cloud, recovery, licensing, legal, commercial, model-authority, or external-
execution decision; active write collision; stale CAP package; or material
CAP-0007 drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
nonfunctional styling, or another inconsequential in-scope correction.

## Required Handoff

Report `CAP-0007.SLI-0032.WRK-0129`; exact candidate and receipt; scenario map;
contract/API/browser/headless parity; immutable evidence, replay, occurrence,
supersession, projection, and Audit evidence; PostgreSQL restart and cleanup;
authorization/privacy denials; accessibility, security, architecture, anti-
rigidity, inert-artifact, and no-advice evidence; exact checks/environments;
changed files; documentation impact; assumptions and residual gaps. Confirm no
product behavior, provider, managed-cloud profile, external execution, live
Portfolio integration, mastery/adaptive authority, separate AI mode, or
autonomous authority was added.

## Planning History

- 2026-10-17: Authored just in time after WRK-0128 completed. The packet adds
  the missing integrated Project learning-submission journey to the existing
  isolated live qualifier, then closes SLI-0032 from direct browser, headless
  HTTP, PostgreSQL, restart, projection, Audit, containment, accessibility, and
  cleanup evidence. It changes no product contract or authority and exposes no
  new decision gate or lower-level approval.
