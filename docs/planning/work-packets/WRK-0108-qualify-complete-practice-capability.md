---
id: WRK-0108
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0029
capability: CAP-0006
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/capabilities/CAP-0006-practice-and-demonstrate-understanding.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0029-qualify-complete-practice-capability.md", "docs/planning/work-packets/WRK-0108-qualify-complete-practice-capability.md"]
generated_artifacts: []
base_revision: 0a51e615f692ef41fd09ab59fb01465ad360f0d7
claim_id: WRK-0108:a1e9ff60-892c-4fae-bccf-dfefb64bae93
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T19:13:45Z
---

# Agent Work Packet: Qualify the Complete Practice Capability

## Objective and Deliverable

Run and reconcile the cumulative CAP-0006 qualification matrix, map every
capability and SLI-0029 acceptance statement to current exact evidence, update
the architecture and known-gap maps only where the result changes their truth,
and deterministically close SLI-0029 and CAP-0006. Produce an independently
reviewable documentation-only candidate unless qualification discovers a
concrete evidence-control or product defect.

The deliverable must preserve the public API as the shared browser and
non-browser/headless boundary. It must not add a second AI mode, product core,
transport, authority path, or test-only claim that exceeds observed behavior.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`; route through the baseline, practice,
testing-quality, security-risk, interface-design, and delivery-planning context
packs. Read the change-impact matrix, decision readiness, CAP-0006, SLI-0026
through SLI-0029, WRK-0092 through WRK-0107, ADR-0004, ADR-0005, ADR-0007,
ADR-0008, the Assessment and content-package contracts, affected module and
deployment READMEs, executable contract catalogs, approved practice fixture,
practice implementation and consumers, OpenAPI/generated client, browser
tests, approved-lesson qualifier, architecture-verification map, known gaps,
and concurrent-work protocol.

## Decisions and Assumptions

- Reuse the exact accepted practice contracts, implementation, adapters, API,
  generated client, browser flow, isolated live topology, and still-current
  focused evidence. Do not create another runner, server, database, seed,
  product route, or aggregate test merely to restate existing proof.
- Treat the current fresh WRK-0107 live candidate and its qualifying receipt as
  direct evidence for unchanged live boundaries. Rerun checks when freshness
  is needed for CAP closure or this packet changes their inputs.
- Use the complete practice-focused test matrix to verify cumulative meaning,
  not one brittle fixture. Preserve canonical order-insensitive response and
  multiple-selection semantics and variable valid counts.
- Record a claim as direct only when an executable check or controlled live
  qualification owns it. Keep local/cloud shared-core evidence distinct from
  an unqualified managed-cloud deployment claim.
- Treat a product, contract, persistence, generated-client, browser, or harness
  defect as new bounded implementation work. This packet may update only the
  named evidence and planning documents.
- Harmless whitespace, learner-facing wording, optional nonfunctional styling,
  timestamps, generated IDs, or other inconsequential differences do not
  trigger a correction and re-review cycle. Fix them in scope or defer optional
  polish to CAP-0031.

## In Scope

- Validate all versioned practice definition, presentation, submission/result,
  event, draft, retry, review-target, history, error, OpenAPI, and generated-
  client contracts and compatibility corpora.
- Run deterministic scoring, application, authorization, provenance,
  idempotency, retry, review-selection, replay, and rebuild suites.
- Run SQLite where applicable and real-PostgreSQL persistence, migration,
  concurrency, rollback, atomicity, source-preservation, and interruption
  suites across Assessment, Curriculum, Learner model, Audit, and Identity.
- Run API success and denial suites, OpenAPI/generated-client reproduction,
  web unit/component tests, TypeScript typecheck/lint/build, focused practice
  Chromium, and the isolated live PostgreSQL/Python/headless/Chromium workflow.
- Verify keyboard, focus, live-region, reflow, reduced-motion, forced-color,
  light/dark/system-theme, answer-confidentiality, same-origin, architecture,
  shared-core, containment, cleanup, learner-language, and design evidence.
- Run planning, documentation, security, whitespace, fixed readiness, exact-
  candidate affected verification, and one independent technical review.
- Reconcile CAP-0006, SLI-0029, this packet, the register, architecture map, and
  known gaps with exact results, assumptions, unqualified areas, and next work.
- Run deterministic SLI and CAP completion checks and leave a clean committed
  CAP branch eligible to fast-forward to local main.

## Out of Scope

Any product contract, schema, event, domain, application, adapter, persistence,
migration, API, generated-client, browser behavior, seed, fixture, dependency,
shared design asset, or product implementation change; new item/scoring/policy
families; model/manual grading; AI-authored content; mastery, competency, or
adaptive authority; recommendations; instructor review; financial advice;
external providers; arbitrary execution; job queues; tenancy; cloud deployment;
managed recovery; production operations; a second headless/AI core; remote
push; or styling-only redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Product contracts and implementation | practice contracts, modules, migrations, API, generated client and browser | none | Qualify frozen behavior without changing authority or shape |
| Focused and live evidence | backend/web/browser suites and approved-lesson qualifier | none | Run existing checks and map their exact owned claims |
| Architecture assurance | module/shared-core map and evidence ownership | `docs/architecture/assurance/architecture-verification.md` only if the cumulative result changes a claim | Keep direct, representative, and gap labels truthful |
| Verification gaps | repository gap inventory | `docs/assurance/known-verification-gaps.md` only if a directly qualified boundary changes the remaining gap | Preserve explicit unqualified behavior |
| Planning and capability closure | CAP-0006, SLI-0029, WRK-0108 and register | named planning files | Record lifecycle, exact evidence, CAP conformance and next action |

## Contracts and Interfaces

Consume only the accepted public practice and session contracts through their
registered schemas and public operations. The browser must continue to use the
generated TypeScript client; the live non-browser observer must continue to use
ordinary authenticated HTTP against the same routes. No private module import,
database access, browser-local scoring, caller-selected learner context, or
test-only product endpoint may substitute for those contracts.

Evidence output is the packet's only new interface: a bounded acceptance map in
tracked planning/assurance documentation plus ignored verification receipts and
review records. Tracked files contain no approval or reviewer metadata, learner
identity, credential, response, answer, private evaluator, storage payload, or
raw diagnostic.

## Dependencies and Parallel Safety

SLI-0026 through SLI-0028 and WRK-0092 through WRK-0107 are complete and supply
all product behavior and focused evidence. WRK-0108 owns CAP-0006 closure and
the shared planning/assurance documents, so it is not parallel-safe with any
packet editing those paths. It has no dependent packet inside CAP-0006.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| CAP acceptance closure | All three behavior slices are complete | The cumulative map is evaluated | Every CAP acceptance statement has direct evidence or closure stops with an explicit gap | evidence map/completion gate |
| Complete journey | Exact approved practice and supported session | Browser saves, resumes, submits, reviews, retries and inspects history | Server-owned deterministic meaning persists across reload and restart | live Chromium/API/PostgreSQL |
| API/headless continuity | Same public contracts and server-owned session | Browser and ordinary non-browser clients perform supported operations | Both use one API/core and return correlated answer-safe meaning | OpenAPI/client/architecture/live |
| Deterministic authority | Valid and invalid structured inputs | Scoring, retry, replay, conflict and rebuild run | Only deterministic server policy changes durable evidence; failures remain bounded | contract/application/PostgreSQL |
| Confidentiality and provenance | Success and denial paths | Public results, history, errors and reports are inspected | Exact provenance remains while learner identity, answers, evaluators, credentials and storage details stay private | API/security/harness |
| Compatibility and anti-rigidity | Valid count, order, metadata, copy and style variation | Focused mutation suites run | Meaningful invariants hold without exact-copy, count, timestamp, ID or visual rigidity | contract/component/harness |
| Accessibility parity | All learner practice states | Keyboard, narrow view, themes and assistive checks run | Content, action, focus and status meaning remain equivalent | component/Chromium/design |
| Migration and recovery bounds | Existing and fresh practice evidence | Migrations, rollback, restart and rebuild run | Accepted evidence is preserved; derived state rebuilds; managed-cloud recovery remains unclaimed | PostgreSQL/live/docs |
| Containment | Cumulative qualification succeeds or fails | Runner teardown completes | Exact process, container and ignored artifacts are bounded and cleaned | runner/architecture/live |
| No silent expansion | A check exposes a product or decision gap | Packet evaluates the finding | Closure stops and routes to a new packet or decision instead of editing product files here | scope/status evidence |

## Verification Commands

Run the commands named by SLI-0026 through SLI-0029 and their packets. At
minimum, run the complete practice contract/unit/API and real-PostgreSQL suites,
all web unit/component tests, TypeScript typecheck/lint/build, OpenAPI and
generated-client checks, focused mocked and live practice Chromium, approved-
lesson harness/architecture tests, the isolated full approved-lesson workflow,
architecture/security/language/design/documentation/planning/whitespace gates,
`python dev-tools/agent/check_ready.py`, exact-candidate affected verification,
and the independent review plus completion-structure checks required by the
control plane.

Record exact command results and distinguish checks reused from unchanged
fresh candidates from commands rerun in this packet. Never claim a suite or
environment that did not run successfully.

## Documentation and Evidence Update

Record the delivered learner outcome; exact candidates and qualifying receipt;
packet/slice/CAP acceptance mapping; focused, live, database, browser,
accessibility, security, architecture, build, documentation, planning, and
readiness results; contract/client compatibility; migration/rollback/recovery
meaning; documentation impact; assumptions; checks not performed; residual
risks; known gaps; and next CAP action.

State explicitly that the API remains directly usable by future headless and AI
clients while a separate AI mode, autonomous authority, provider, cloud profile,
managed recovery, and external execution remain unplanned or unqualified.

## Stop Conditions

Stop for any needed product or test-harness code change; breaking contract;
migration or retained-evidence correction; private-data leak; browser/headless
semantic difference; inaccessible functional state; cross-module persistence
access; destructive rollback; model/adaptive/mastery authority; external
execution; provider/queue/tenancy/cloud/recovery decision; stale CAP package;
active write collision; unisolated qualification; failed required check;
material CAP drift; or evidence that cannot truthfully support acceptance.

Do not stop or reopen review for harmless whitespace, optional copy, styling,
or another inconsequential in-scope documentation correction. Keep the change
proportionate and preserve high-confidence blocking rules.

## Required Handoff

Report `CAP-0006.SLI-0029.WRK-0108`; exact candidate and receipt; CAP acceptance
map; API/browser/headless parity; deterministic scoring/evidence/retry/history;
contract and client compatibility; concurrency/rollback/migration/rebuild and
restart evidence; confidentiality/accessibility/security/shared-core results;
containment and cleanup; exact checks and environments; changed files;
documentation impact; assumptions and remaining gaps. Confirm that no product
implementation, API, migration, provider, cloud, external execution, separate
AI mode, or autonomous authority was added. Leave CAP-0006 ready for local main
integration when every deterministic closure condition passes.

## Implementation Evidence

- The cumulative focused backend matrix passes 218 non-PostgreSQL practice
  checks: 130 executable contract and compatibility cases, 58 deterministic
  domain/application cases, and 30 protected public-API cases. The latest
  unchanged real-PostgreSQL matrix from WRK-0107 passes 220 migration,
  atomicity, conditional-write, concurrency, rollback, source-preservation,
  replay, and interrupted-rebuild checks.
- The web matrix passes 210 unit, component, and generated-client tests across
  15 files. TypeScript typecheck, zero-warning lint, reviewed client
  reproduction, and the production build all pass; the build transforms 117
  modules.
- Focused Chromium qualification passes 11 practice journeys covering every
  supported response shape, validation focus, save/resume, retained history,
  exact retry, session renewal, completed-attempt handling, narrow reflow,
  forced colors, denial, and private-field fail-closed behavior.
- The approved-lesson qualifier and architecture harness pass 39 tests plus
  four parameterized subtests. The unchanged exact WRK-0107 candidate
  `5706f9a94df400e2858bd524a1557062d9e01d41` supplies the isolated ten-scenario
  PostgreSQL/Python/public-API/headless/Chromium result and qualifying receipt
  digest `sha256:8283dd42cbb16b2901790a339270d078b0268fd9abf5c09083efdafa8d769270`.
- Architecture passes 16 tests; security passes 10 control groups;
  learner-language, design-system, documentation, planning, whitespace, and
  build checks pass; and the fixed aggregate readiness gate passes all 29
  checks. A Windows sandbox temporary-directory denial and missing symlink
  privilege were rerun with the bounded workspace temp directory and the
  prepared runtime outside the sandbox; neither exposed a product defect.
- Architecture evidence is direct for the deployment-neutral shared core and
  local public API and representative for future-cloud adapter portability.
  Managed-cloud composition, adapter parity, protection, and recovery were not
  performed and remain unqualified.
- Direct accessibility evidence covers automated Chromium and axe-backed
  component checks, keyboard/focus behavior, reflow-equivalent narrow
  viewports, reduced motion, forced colors, themes, and design-system
  validation. Manual screen-reader operation, actual browser 200% zoom,
  non-Chromium browsers, and non-Windows visual baselines were not performed
  and remain known residual gaps.
- Public presentation, submission, progress, draft, and session operations
  remain the single authority for browser and supported non-browser clients.
  The browser uses the generated client; the live non-browser observer uses
  ordinary authenticated HTTP. No browser-only scoring, identity, retry,
  completion, evidence, or history authority was found.
- No product source, contract, schema, event, migration, API, generated client,
  UI, provider, deployment composition, or test harness changed. The existing
  architecture-verification and known-gap maps remain accurate, so this packet
  does not rewrite them merely to produce a newer timestamp.
- Managed-cloud deployment and recovery, organization tenancy, external
  providers, background delivery, model grading, adaptive/mastery authority,
  arbitrary execution, a separate AI mode, and autonomous action remain
  deliberately unqualified CAP non-goals.

## Planning History

- 2026-10-16: Authored just in time after SLI-0029 refinement. The packet uses
  one documentation-only acceptance map and current exact evidence rather than
  another meta-runner or duplicate API. Any material product or harness defect
  stops this packet and routes to separately bounded work.
- 2026-10-16: Claimed from base revision `0a51e61` after revalidating the CAP
  binding, refined slice, completed dependencies, decision readiness, exact
  documentation-only scope, and absence of an active file collision.
- 2026-10-16: Cumulative qualification passed across contracts, deterministic
  core, protected APIs, real PostgreSQL, generated clients, web, focused and
  live Chromium, headless HTTP observation, architecture, security,
  accessibility, build, documentation, planning, whitespace, and all 29
  readiness checks. The documentation-only candidate is ready for exact-
  revision submission and independent review.
- 2026-10-16: Independent R01 found no product defect and accepted the counts,
  ancestry, receipt, API/headless assertions, and unchanged assurance maps. It
  requested two bounded evidence corrections: classify future-cloud portability
  as representative rather than direct and list the unperformed manual,
  browser, zoom, and platform accessibility qualifications.
