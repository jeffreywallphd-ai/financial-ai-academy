---
id: WRK-0130
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0033
capability: CAP-0007
depends_on: ["WRK-0116", "WRK-0121", "WRK-0129"]
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/capabilities/CAP-0007-complete-applied-projects.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0033-qualify-complete-applied-project-capability.md", "docs/planning/work-packets/WRK-0130-qualify-complete-applied-project-capability.md"]
generated_artifacts: []
base_revision: 695daedd47242ed135b04940215794a5827ed195
claim_id: WRK-0130:69ab219b-cc2f-4e1f-9f07-a9ed3e756e2e
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T05:39:10Z
---

# Agent Work Packet: Qualify the Complete Applied Project Capability

## Objective and Deliverable

Run and reconcile the cumulative CAP-0007 qualification matrix, map every
capability and SLI-0033 acceptance statement to current exact evidence, update
the architecture and known-gap maps only where the result changes their truth,
and deterministically close SLI-0033 and CAP-0007. Produce a documentation-only
candidate unless qualification discovers a concrete evidence-control or
product defect.

The deliverable must preserve the protected Project API as the shared browser
and non-browser/headless boundary, Project resources as inert untrusted data,
and typed domain links as references rather than copied domain state. It must
not add a live Portfolio integration, execution authority, managed-cloud claim,
second product core, or test-only behavior.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`; route through the baseline, architecture-
contracts, API-security, testing-quality, deployment-operations, interface-
design, and delivery-planning context. Apply the change-impact matrix and
decision readiness. Inspect CAP-0007, SLI-0030 through SLI-0033, WRK-0109
through WRK-0129, ADR-0004, ADR-0008, ADR-0011, ADR-0012, Project and Assessment
contracts, affected module public operations and READMEs, migrations,
OpenAPI/generated client, Project browser consumers, approved-lesson qualifier,
affected tests, architecture-verification map, known gaps, and concurrent-work
protocol.

## Decisions and Assumptions

- Reuse the accepted Project contracts, implementation, adapters, API,
  generated client, browser flows, isolated live topology, and still-current
  focused evidence. Do not create another runner, server, database, seed,
  product route, or aggregate test solely to restate existing proof.
- Treat WRK-0116, WRK-0121, and WRK-0129 as direct focused evidence only where
  their exact candidates, ancestry, and unchanged affected files keep them
  current. Rerun checks when freshness is needed for CAP closure or this packet
  changes their inputs.
- Use the complete Project-focused matrix to verify cumulative meaning, not one
  brittle fixture. Preserve valid count, safe metadata, Unicode, ordering,
  generated identity, timestamp, and nonfunctional presentation variation.
- Record a claim as direct only when an executable check or controlled live
  qualification owns it. Distinguish shared-core contract and port evidence
  from unperformed managed-cloud composition, protection, and recovery.
- Treat a product, contract, persistence, generated-client, browser, or harness
  defect as new bounded implementation work. This packet may change only its
  named evidence and planning documents.
- Harmless whitespace, optional learner wording, nonfunctional styling,
  timestamps, generated IDs, or other inconsequential differences do not
  trigger a correction cycle. Fix them in scope or defer optional polish to
  CAP-0031.

## In Scope

- Validate Project shell/origin, workspace, resource, inert-artifact,
  typed-link, snapshot, export, learning-submission, completion-projection,
  Audit-reference, error, OpenAPI, and generated-client contracts.
- Run Project, Content, Curriculum, Assessment, Learner-model, Audit, and
  Identity domain/application/authorization/provenance/idempotency/replay/
  conflict/supersession suites needed to own the cumulative claims.
- Run real-PostgreSQL migration, atomicity, concurrency, rollback, source-
  preservation, interruption, restart, projection, and cross-learner suites.
- Run API success and denial suites, OpenAPI/generated-client reproduction,
  relevant web unit/component tests, TypeScript typecheck/lint/build, focused
  Project Chromium, and the isolated live PostgreSQL/Python/headless/Chromium
  workflow.
- Verify independent Projects create no learning completion, learning-bound
  submission retains exact immutable snapshot evidence, later workspace work
  does not rewrite prior evidence, and retry/supersession remain deterministic.
- Verify multiple typed references remain isolated owner-issued references and
  that stale, removed, unauthorized, and unavailable status is explicit without
  claiming live Portfolio behavior.
- Verify inert handling, passive allowlisting, resource bounds, no platform
  compute/network/secrets/packages/providers/callbacks, privacy, same-origin
  controls, shared-core meaning, restart durability, containment, and cleanup.
- Run accessibility, responsive/theme, learner-language, design-system,
  architecture, security, documentation, planning, dependency, whitespace,
  exact-candidate affected verification, fixed readiness, technical review, and
  deterministic completion checks.
- Reconcile CAP-0007, SLI-0033, this packet, the register, architecture map, and
  known gaps with exact evidence, assumptions, unqualified areas, and next work.
- Leave a clean committed CAP branch eligible for local main fast-forward after
  every deterministic closure condition passes.

## Out of Scope

Any product contract, schema, event, domain, application, adapter, persistence,
migration, API, generated-client, browser behavior, seed, fixture, dependency,
shared design asset, or product implementation change; live Portfolio or other
domain-provider integration; copied domain state; active rendering; arbitrary
or provider execution; market data; financial action or advice; instructor or
AI grading; mastery/competency/adaptive authority; collaboration; publishing;
external notification; tenancy; cloud deployment or recovery; a second
headless/AI core; remote push; or styling-only redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Product contracts and implementation | Project, Content, Curriculum, Assessment, Learner-model, Audit, Identity, migrations, API, generated client, browser | none | Qualify frozen behavior without changing authority or shape |
| Focused and live evidence | backend/web/browser suites and approved-lesson qualifier | none | Run current checks and map the exact claims they own |
| Architecture assurance | module/shared-core/inertness evidence map | `docs/architecture/assurance/architecture-verification.md` only if the cumulative result changes a claim | Keep direct, representative, and gap labels truthful |
| Verification gaps | repository gap inventory | `docs/assurance/known-verification-gaps.md` only if direct evidence changes the remaining gap | Preserve explicit unsupported behavior |
| Planning and CAP closure | CAP-0007, SLI-0033, WRK-0130, and register | named planning files | Record exact evidence, lifecycle closure, and next action |

## Contracts and Interfaces

Consume only accepted public Project, Project-workspace, Project-submission,
Assessment, Learner-model, Audit, Content, Curriculum, Identity, and session
contracts through registered schemas and public operations. The browser must
continue to use the generated TypeScript client; the non-browser observer must
continue to use authenticated HTTP against the same routes. Direct SQL is
evidence-only inside the disposable database and may not substitute for
application authority.

Evidence output is the packet's only new interface: a bounded acceptance map in
tracked planning/assurance documentation plus ignored verification records.
Tracked files contain no approval or reviewer metadata, learner identity,
credential, artifact bytes, host path, provider payload, or raw diagnostic.

## Dependencies and Parallel Safety

WRK-0116, WRK-0121, and WRK-0129 close the three behavior slices and supply
focused live evidence for shell/origin, workspace/snapshot, and learning-
submission behavior. WRK-0130 owns CAP-0007 closure and shared planning/
assurance documents, so it is not parallel-safe with another packet editing
those paths. It has no dependent packet inside CAP-0007.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| CAP acceptance closure | All three behavior slices are complete | The cumulative map is evaluated | Every CAP-0007 acceptance statement has direct or explicitly bounded representative evidence, or closure stops with a named gap | evidence map/completion gate |
| Independent journey | An authorized private-host learner | They create, reopen, edit, resume, snapshot, export, and continue an independent Project | Exact Project state persists and no Assessment or Learner-model completion appears | live Chromium/API/PostgreSQL |
| Learning-bound journey | Exact Content/Curriculum origin and immutable Project snapshots | The learner submits and reopens exact evidence, then continues live work and submits a later snapshot | Earlier snapshots/evidence remain immutable and supersession/history are deterministic | live Chromium/API/PostgreSQL |
| Ownership and provenance | Project, learning, evidence, projection, and Audit records | Cumulative suites inspect all crossings | Each module owns one canonical meaning and exact versions/digests cross only public boundaries | architecture/contract/application |
| Typed-link isolation | Zero or multiple synthetic owner-issued link references | Available and unavailable states are validated | References never copy domain state or imply a live Portfolio integration | contract/application/API/browser |
| Inert confinement | Code-like, data, environment, result, and financial-context artifacts | They are uploaded, inspected, downloaded, snapshotted, exported, and submitted | No artifact executes, actively renders, reaches network/secrets/providers, or gains truth/advice status | architecture/security/live |
| Replay and interruption | Accepted workspace, snapshot, and submission state | Exact retry, changed reuse, interrupted write/rebuild, and normal restart run | Replay is stable, conflicts are bounded, and prior complete state remains intact | application/PostgreSQL/API/live |
| Confidential authorization | Missing permission, selected identity, guessed IDs, and cross-learner requests | Protected operations are attempted | Requests fail closed without existence, artifact, or learner disclosure | API/security/live |
| Browser/headless continuity | One reviewed OpenAPI and generated client | Generated browser and ordinary non-browser clients traverse Project flows | Both observe the same server-owned contracts and shared core | OpenAPI/client/architecture/live |
| Compatibility and anti-rigidity | Valid count, content, metadata, ordering, ID, timestamp, copy, and style variation | Focused mutation suites run | Meaningful invariants hold without exact-fixture or presentation rigidity | contract/component/harness |
| Accessibility parity | Origin, workspace, artifact, snapshot, submission, history, and error states | Keyboard, focus, narrow view, themes, forced colors, reduced motion, and axe checks run | Content, action, state, and status meaning remain equivalent | component/Chromium/design |
| Recovery and cloud bounds | Existing and fresh local evidence | Migration, restart, rollback, and shared-port checks run | Private-host evidence is direct; managed-cloud composition and recovery remain unclaimed | PostgreSQL/live/docs |
| Containment | Cumulative qualification succeeds or fails | Teardown completes | Owned processes, containers, networks, and temporary artifacts are bounded and cleaned | runner/architecture/live |
| No silent expansion | A check exposes a product or durable-decision gap | The finding is evaluated | Closure stops and routes to new bounded work instead of editing product files here | scope/status evidence |

## Verification Commands

Run the commands named by SLI-0030 through SLI-0033 and their packets. At
minimum, run the complete Project contract/domain/application/API and real-
PostgreSQL suites, Project-related Learner-model and Audit suites, OpenAPI and
generated-client checks, relevant web unit/component tests, TypeScript
typecheck/lint/build, focused Project Chromium, approved-lesson harness and
architecture tests, the isolated full approved-lesson workflow, architecture/
security/language/design/documentation/planning/dependency/whitespace gates,
`python dev-tools/agent/check_ready.py`, exact-candidate affected verification,
technical review, and completion-structure checks required by the control
plane.

Record exact command results and distinguish current evidence reused from an
unchanged candidate from commands rerun in this packet. Never claim a suite or
environment that did not run successfully. Use bounded isolated PostgreSQL and
prepared Python/Node runtimes, and perform exact cleanup.

## Documentation and Evidence Update

Record the delivered learner outcome; exact candidate and qualifying receipt;
CAP acceptance map; browser/headless parity; provenance, typed-link isolation,
inertness, immutable snapshot/submission, replay, supersession, projection,
Audit, restart, authorization, accessibility, shared-core, containment, and
cleanup results; focused checks and environments; contract/client and migration
compatibility; documentation impact; assumptions; checks not performed;
residual risks; known gaps; and next CAP action.

State explicitly that live Portfolio integration, external providers, managed
cloud, production recovery, independent result reproduction, arbitrary
execution, collaboration, instructor workflows, public publishing, a separate
AI mode, and autonomous authority remain unqualified.

## Stop Conditions

Stop for any needed product or test-harness code change; breaking contract;
migration or retained-evidence correction; Project/module ownership drift;
private-data leak; browser/headless semantic difference; inaccessible
functional state; active artifact execution/rendering/network/secret behavior;
copied domain state; cross-module persistence access; destructive rollback;
live Portfolio/provider integration; financial action; instructor/AI/adaptive/
mastery authority; tenancy/cloud/recovery decision; unisolated qualification;
stale CAP package; active write collision; failed required check; material
CAP-0007 drift; or evidence that cannot truthfully support acceptance.

Do not stop or reopen review for harmless whitespace, optional copy,
nonfunctional styling, or another inconsequential in-scope documentation
correction. Keep the change proportionate and preserve functional controls.

## Required Handoff

Report `CAP-0007.SLI-0033.WRK-0130`; exact candidate and receipt; CAP acceptance
map; Project/module ownership; API/browser/headless parity; provenance,
typed-link isolation, inertness, snapshot/submission immutability, replay,
supersession, projection, Audit, PostgreSQL restart, and cleanup evidence;
authorization/privacy/accessibility/security/shared-core results; exact checks
and environments; changed files; documentation impact; assumptions and
remaining gaps. Confirm that no product behavior, live Portfolio integration,
provider, managed-cloud profile, external execution, financial action,
separate AI mode, or autonomous authority was added. Leave CAP-0007 eligible
for local main fast-forward when every deterministic closure condition passes.

## Implementation Evidence

- The focused backend matrix collected 223 Project contract, domain,
  application, Assessment, Curriculum, Learner-model, Audit, and protected-API
  cases. The non-API portion passed before the Windows sandbox blocked
  TestClient's internal socket pair; the exact two API files then passed nine
  tests with two expected PostgreSQL-only skips outside the sandbox. Combined
  result: 221 passed and two skipped, with no assertion failure.
- Current exact PostgreSQL 18.4 and live browser/headless evidence remains
  ancestral and unchanged: WRK-0116 at
  `62b60ca24196fded424f8de4896b8873f256ee13`, WRK-0121 at corrected candidate
  `92c45e4`, and WRK-0129 at `b36a321` with qualifying receipt digest
  `sha256:00f33304a7574507a9b6fa9bc38373efde13c74b4c60e366aca71d19cec64b01`.
  Together those runs cover disposable PostgreSQL migrations and atomicity,
  independent and learning origin, mutable workspace, inert resources, typed
  links, immutable snapshots/exports, exact learning submission, replay and
  conflict, supersession, projection/Audit correlation, authorization,
  restart, and exact cleanup.
- Under exact Node 24.14.0 and npm 10.8.2, reviewed generated-client
  reproduction, TypeScript typecheck, zero-warning lint, 267 web tests across
  17 files, the 126-module production build, and nine focused Project Chromium
  journeys pass. Browser and ordinary non-browser clients retain one protected
  API and server-owned identity/policy path.
- The approved-lesson replay qualifier and local-composition boundary matrix
  pass 45 tests; all 16 architecture fitness checks pass; security passes 10
  control groups; learner-language, design-system, documentation, planning,
  and whitespace checks pass; the JavaScript dependency audit reports zero
  vulnerabilities; and the fixed readiness gate passes all 29 checks.
- Initial sandbox attempts exposed only Windows environment constraints:
  Python socket-pair creation and temporary-directory rename/create operations
  were blocked before assertions. The exact commands passed outside the
  sandbox with the bounded repository temporary root. No source correction or
  weakened acceptance rule was needed.
- Direct automated accessibility evidence covers keyboard/focus behavior,
  associated status and errors, reflow-equivalent narrow views, reduced
  motion, forced colors, light/dark/system themes, and axe-backed Chromium.
  Manual screen-reader use, actual browser 200-percent zoom, non-Chromium
  browsers, and non-Windows visual baselines were not performed.
- Architecture evidence is direct for the shared domain/application core,
  public API and provider ports, inert handling, and private-host restart. It
  is representative only for future managed-cloud adapters; no managed-cloud
  composition, tenancy, protection, or recovery was run.
- No product implementation, contract, schema, migration, generated client,
  browser behavior, test harness, provider, or deployment composition changed.
  Existing architecture-verification and known-gap documentation remains
  accurate. Live Portfolio integration, external providers, managed cloud,
  production recovery, independent result reproduction, arbitrary execution,
  collaboration, instructor workflows, public publishing, financial action, a
  separate AI mode, and autonomous authority remain unqualified.

## Planning History

- 2026-10-17: Authored just in time after the three CAP-0007 behavior slices
  completed. The packet uses one documentation-only acceptance map and current
  focused evidence rather than a duplicate meta-runner. Any material product or
  harness defect stops this packet and routes to separately bounded work.
- 2026-10-17: Claimed from base revision `695daed` after validating current
  CAP membership, completed focused-qualification dependencies, decision
  readiness, exact documentation-only scope, and exclusive edit ownership.
- 2026-10-17: The cumulative acceptance matrix passed. Fresh focused/web/
  architecture/security/dependency/readiness checks agree with the current
  ancestral live PostgreSQL evidence, and no material product or harness gap
  requires a corrective packet.
