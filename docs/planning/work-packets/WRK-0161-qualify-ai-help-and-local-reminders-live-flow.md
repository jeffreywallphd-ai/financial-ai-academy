---
id: WRK-0161
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-18
parent: SLI-0076
capability: CAP-0018
depends_on: [WRK-0160, WRK-0162, WRK-0163]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/assistance-preferences.e2e.ts", "backend/src/financial_ai_academy/modules/learner_model/README.md", "deployments/local/README.md", "dev-tools/control-plane/README.md", "dev-tools/control-plane/check_assistance_preferences.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0161-qualify-ai-help-and-local-reminders-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: a01b0fc3baffdddd0fa1361ddff84a272d71972c
claim_id: WRK-0161:92a5e8ee-06a4-4186-bc23-b8c41cf6ff77
claimed_by: codex-cap-0018
claimed_at: 2026-10-18T01:30:28Z
---

# Agent Work Packet: Qualify AI Help and Local Reminders Live Flow

## Objective and Deliverable

Close SLI-0076 with reproducible evidence that the accepted AI-help profile
works through the same protected public API for browser and ordinary headless
clients, while the future reminder choice remains browser-local, inert, and
separately controlled. Exercise the exact candidate through disposable
PostgreSQL, the production Python host, the static browser build, and pinned
Chromium without changing product behavior.

This packet may extend the reusable affected-check catalog with a focused
assistance-preferences browser check. It does not add an AI provider, model
call, notification capability, schedule, queue, worker, timer, or server-side
meaning for the local reminder choice.

## Required Context

Before implementation, revalidate `AGENTS.md`, `docs/README.md`, the routed
repository startup sources, CAP-0018,
SLI-0076, WRK-0160 completion, current decision readiness, the assistance
contracts and public API, browser and local-storage implementation, approved-
lesson runner, affected-check catalog, nearest READMEs, consumers, and tests.
Stop for any canonical conflict, stale CAP package, missing dependency,
unresolved durable decision, active write collision, or material scope drift.

## In Scope

- Reproducible live browser, ordinary headless API, PostgreSQL, restart,
  privacy, accessibility, containment, anti-rigidity, and cleanup evidence.
- A focused self-bound assistance-preferences Chromium wrapper and affected-
  check selection for future candidate verification.
- Pure capture/replay validation and direct assurance, runtime, and planning
  documentation updates.

## Out of Scope

- Product behavior, contracts, schemas, migrations, generated clients,
  dependencies, deployment composition, shared design-system decisions, AI or
  notification execution, and any server meaning for the local reminder.
- Corrections to a discovered product defect; route such work to a separately
  bounded packet without widening this qualification seam.

## Expected File and Boundary Impact

| Boundary | Owned change | Evidence target |
| --- | --- | --- |
| Focused browser selection | Add a self-bound assistance-preferences Chromium wrapper and catalog mapping | Assistance route or focused specs always select their browser check |
| Live Chromium | Add the approved-lesson assistance journey | Safe defaults, separate saves/resets/downloads, accessibility, reload, and no notification side effect |
| Headless public API | Extend the approved-lesson runner through generated public shapes | Read, mutate, history, export, reset, replay, and conflict parity without UI imports |
| PostgreSQL | Inspect only the isolated assistance profile, change, and mutation tables | Default no-write, exact correlations, restart durability, and bounded history |
| Local browser authority | Capture and validate the versioned reminder envelope and local export | No learner identity, API meaning, delivery claim, or server write |
| Containment | Compare unrelated state and observe network/platform side effects | No evidence, mastery, eligibility, provider, model, permission, schedule, notification, or delivery change |
| Documentation | Update direct runtime and assurance guidance | Claims match executed evidence and remaining exclusions |
| Planning | Update this packet, SLI-0076, and register together | Deterministic completion projection |

No unlisted product, contract, schema, migration, generated-client, dependency,
deployment-composition, shared design-system, or other planning file is in
scope. A real defect must be routed to separately bounded corrective work.

## Contracts and Interfaces

Browser and headless qualification consume only the current session and the
protected `learner-assistance-preferences` profile, mutations, history, and
export endpoints. The runner may inspect only the three isolated assistance-
preference tables for exact correlation, plus privacy-safe fingerprints or
counts for unrelated state.

The versioned capture records the current profile, bounded history, export,
exact replay request, concurrency requests and expected outcome classes,
table correlations, and a browser-local reminder summary. It must not contain
session secrets, caller-selected learner identity, credentials, provider or
model payloads, prompts, arbitrary learner content, evidence, competency,
recommendations, notification destinations, database connection details, or
unbounded diagnostics. The browser-local summary must contain no learner
identity and must never be projected as API state.

## Dependencies and Parallel Safety

WRK-0160 is complete and supplies the generated-client browser flow, exact
retry behavior, separate local adapter, and product tests. This packet owns
the shared approved-lesson runner, static build, affected-check catalog,
assurance sources, and SLI-0076 closure paths. It is not parallel-safe with
another writer on those surfaces.

Claim the packet from a recorded base revision, acquire one-owner leases for
every write-scope path, complete it before any dependent work, and preserve
all approval and reviewer records only in ignored local control-plane storage.

## Decisions and Assumptions

- CAP-0018 remains the current approved package and SLI-0076 remains an
  enumerated approved slice; WRK-0160 is complete.
- Accepted identity, learner-context, module-ownership, deterministic-policy,
  provider-disabled, and browser-local boundaries are sufficient. This packet
  reaches no unresolved durable decision gate.
- The existing disposable approved-lesson topology, generated public client,
  and pinned Chromium remain the supported qualification path.
- `on_request` remains a stored learner preference only. It does not admit or
  select a model/provider, grant data permission, or authorize execution.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe first open | Fresh learner and browser storage | Chromium opens AI help and reminders | Both choices show off and neither database nor local storage is written on read | Chromium/PostgreSQL/storage |
| Browser AI save | Safe default | Learner saves `on_request` | One public mutation advances one durable revision and claims no provider or model execution | Chromium/API/PostgreSQL |
| Browser-local reminder | Safe default | Learner saves future in-app reminders | Only the allowlisted local envelope changes and the page still says reminders are unavailable | Chromium/storage/network |
| Separate downloads | Both choices have changed | Learner downloads each record | AI export matches the public profile/history; local export has no learner identity or server authority | Chromium/capture |
| Separate reset | Both choices have changed | Learner resets each control independently | AI reset creates one server revision; local reset affects only this browser | Chromium/API/storage |
| Browser/headless parity | Browser state is captured | Ordinary cookie-backed client reads, mutates, resets, and exports | Public AI-help meaning matches without browser imports or local reminder semantics | runner/public HTTP |
| Exact replay | Accepted mutation exists | The identical request is retried | Same result returns and no second revision/change/mutation is created | HTTP/PostgreSQL |
| Changed-key race | Two payloads reuse one fresh key | Requests serialize | One meaning wins and the other is confidentially denied without duplicate durable meaning | HTTP/PostgreSQL |
| Stale-revision race | Two fresh keys target one revision | Requests serialize | One advances and one is stale; no update is lost or duplicated | HTTP/PostgreSQL |
| Unavailable independence | Learner service or local storage is malformed/unavailable | Route opens or an action fails | Ordinary learning remains usable; each boundary fails independently and conservatively | Chromium/component |
| No execution side effect | Complete browser journey runs | Network and platform APIs are observed | No model/provider request, notification permission, service worker, timer, queue, subscription, or delivery occurs | Chromium/network |
| Accessibility parity | Route has loaded | Keyboard, focus, narrow reflow, 200% text, forced colors, reduced motion, and themes are exercised | Purpose, actions, status, errors, and technical records remain reachable and equivalent | Chromium/design |
| Restart durability | Correlated server state exists | Python host restarts normally | Profile, history, export, exact replay, and rows remain stable; the same browser-local envelope survives page reload only | restart/API/PostgreSQL/browser |
| Privacy and isolation | Qualification completes | Unrelated state fingerprints are compared | No evidence, mastery, eligibility, grading, provider, model, permission, notification, or financial state changes | runner/security/architecture |
| Closed capture | Capture is private, malformed, or inconsistent | Pure verifier loads it | Qualification fails before comparison or mutation | pure pytest |
| Cleanup | Qualification succeeds or fails | Runner exits | Only its named topology, captures, browser artifacts, build, and bounded temporary root are cleaned | runner/finally |
| Anti-rigidity | Valid IDs, times, choice combinations, and bounded history vary | Focused and live checks run | Meaning is asserted without frozen whole-copy, fixture-count, or irrelevant visual assertions | unit/Chromium/live |

## Verification Commands

Run packet and planning validation; focused affected-check catalog tests; pure
runner/capture tests; assistance contract, domain, application, repository,
migration, API, and generated-client suites; full Web tests, typecheck,
zero-warning lint, and build; the focused assistance-preferences Chromium
check; and the complete isolated approved-lesson workflow.

Also run architecture/import and persistence-ownership checks; security and
privacy checks; learner-language and design-system checks; documentation,
planning, dependency, Python compilation, and whitespace checks; controller-
selected exact-candidate verification; independent technical review;
deterministic slice closure; and `python dev-tools/agent/check_ready.py`.
Use repository-prepared Python, Node 24, npm 10.8.2, pinned Playwright
Chromium, and runner-owned disposable PostgreSQL. Record only checks that
actually pass, and always execute exact cleanup.

## Documentation and Evidence Update

Record the exact candidate and qualifying receipt; focused-browser selection;
browser/headless API parity; default no-write; separate browser-local reminder
authority; exact replay and concurrency outcomes; history/export and database
correlations after restart; unrelated-state noninterference; privacy,
accessibility, containment, cleanup; executed checks; assumptions; unsupported
profiles; and remaining gaps. Update only the direct Web, Learner-model, local
runtime, architecture-assurance, known-gap, packet, slice, and register sources
listed in `write_scope`. Keep approval and reviewer records out of tracked
files.

## Stop Conditions

Stop for a required product, contract, schema, migration, OpenAPI, generated-
client, dependency, browser-feature, local-adapter, or deployment-composition
change; inconsistent browser/headless meaning; server authority for the local
reminder; non-serialized concurrency; retained-data loss; private-data leak;
provider/model admission or execution; notification permission or delivery;
service worker, timer, queue, or schedule; hidden inference; a preference used
as evidence, competency, eligibility, grading, recommendation, suitability,
or irreversible action; direct cross-module persistence mutation; unisolated
infrastructure; identity, tenancy, licensing, managed-cloud, recovery, legal,
or commercial expansion; stale CAP authority; active collision; or material
CAP-0018/SLI-0076 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, generated values, fixture count or order, or another
inconsequential qualification correction. Fix bounded inconsequential issues
locally or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0076.WRK-0161`; exact candidate and receipt; focused
assistance-browser selection; browser/headless API parity; default no-write;
separate local reminder authority, saves, resets, and downloads; exact replay
and concurrency matrix; history/export and PostgreSQL restart correlations;
source-state noninterference; privacy, accessibility, containment, cleanup;
focused/live/security/architecture/aggregate checks; changed files;
documentation impact; assumptions; unsupported profiles; and residual gaps.
Confirm that no product implementation, contract, generated client, identity,
provider, model, notification delivery, inferred trait, external action, or
financial behavior changed, then leave SLI-0076 closure-ready.

## Planning History

- 2026-10-18: Authored just in time after WRK-0160 completed. The packet is
  the smallest final qualification seam that closes SLI-0076 through the
  existing disposable local topology and adds deterministic focused-browser
  selection for future assistance-preference changes. No durable decision or
  lower-level approval is required.
- 2026-10-18: Activated from recorded base `860802c` after validating the
  completed dependency, current CAP authority, exact file ownership, and no
  active coordination collision. Delivery remains qualification-only.
- 2026-10-18: Returned to ready after live Chromium received a valid
  digest-bound microsecond API timestamp that the assistance browser validator
  rejected. WRK-0162 owns the bounded product correction; this packet resumes
  afterward without weakening evidence or widening qualification scope.
- 2026-10-18: Reactivated from recorded base `80b8eef` after WRK-0162
  completed. The original live qualification changes were restored without
  widening file ownership, behavior, or decision authority.
- 2026-10-18: Returned to ready after the assistance browser and headless race
  phases passed, then the complete live workflow exposed equivalent fractional-
  second widths across the existing Project completion and history responses.
  WRK-0163 owns that bounded compatibility correction; this packet resumes
  afterward without weakening correlation or widening qualification scope.
- 2026-10-18: WRK-0163 completed with exact microsecond-preserving correlation
  and a qualifying affected-check receipt. This packet is unblocked to resume
  complete live qualification from the corrected candidate.
- 2026-10-18: Reactivated from recorded base `a01b0fc` after WRK-0163
  completed. The original qualification changes were restored with their exact
  ownership and without widening product behavior or decision authority.
- 2026-10-18: The complete isolated workflow passed with generated-browser and
  ordinary headless API parity, exact replay and all three concurrency cases,
  PostgreSQL correlation, normal restart, local-reminder separation, unrelated-
  state noninterference, no model or notification execution, recovery/replay,
  and bounded cleanup. Focused Chromium, pure replay, full Web, typecheck,
  zero-warning lint, Python compilation, and all 29 aggregate readiness checks
  also passed before exact-candidate submission.
- 2026-10-18: Entered exact-candidate verification after every declared live,
  focused, pure, Web, planning, documentation, compilation, whitespace, and
  aggregate readiness check passed.
- 2026-10-18: Tightened the live containment evidence to allow only harmless
  reads, the exact session-bootstrap POST, and the exact assistance-mutation
  POST. Notification-permission and service-worker counters are now asserted
  on both sides of the deliberate document reload so earlier calls cannot be
  hidden by a fresh page marker.

