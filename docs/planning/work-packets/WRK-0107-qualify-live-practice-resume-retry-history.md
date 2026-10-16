---
id: WRK-0107
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0028
capability: CAP-0006
depends_on: ["WRK-0106"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/practice-activity.e2e.ts", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/src/financial_ai_academy/modules/curriculum/README.md", "backend/src/financial_ai_academy/modules/learner_model/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0028-resume-retry-and-compare-practice-attempts.md", "docs/planning/work-packets/WRK-0107-qualify-live-practice-resume-retry-history.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify Live Practice Resume, Retry, and History

## Objective and Deliverable

Complete SLI-0028 by extending the existing isolated approved-lesson harness to
prove the accepted draft, retry, review-target, and history behavior against
real PostgreSQL through both the generated browser client and an ordinary
cookie-backed non-browser client. Demonstrate conditional save and resume,
exact replay and stale-write protection, deterministic retry limits, immutable
attempt history, projection rebuild, normal-restart durability,
confidentiality, accessibility, and bounded cleanup without adding another API,
browser-owned policy, or a separate headless/AI core.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the baseline, practice, testing-quality,
security-risk, interface-design, and delivery-planning context. Read the change-
impact matrix, decision readiness, CAP-0006, SLI-0028, WRK-0102 through
WRK-0106, ADR-0005, ADR-0007, ADR-0008, the accepted practice draft/retry/
history/review contracts, affected module READMEs, generated client and browser
flow, established PostgreSQL integration suites, approved package fixture,
local composition, approved-lesson runner/tests/README, architecture evidence,
known gaps, and concurrent-work protocol.

## Decisions and Assumptions

- Reuse the existing uniquely named disposable PostgreSQL 18.4 container,
  restrictive temporary root, loopback Python API/static host, approved fixture
  seed, and pinned Chromium run. Do not create a second database, seed path,
  server, browser-specific backend, or product transport.
- Let the live generated browser client create a partial draft, reload it, and
  submit the first accepted attempt. Capture only closed public draft-save,
  progress, submission, and result documents needed for non-browser parity;
  never capture cookies, tokens, learner IDs, credentials, answer keys, private
  evaluator declarations, or internal event documents.
- Use fresh supported cookie sessions for direct public-API progress reads,
  exact draft replay, one stale conflicting replacement, and retained-state
  reads before and after normal host restart. Treat returned revision, retry
  eligibility, history order, and review targets as server-owned.
- Use the accepted real-PostgreSQL suites for concurrent final-slot,
  transaction rollback, migration round trip, retry limit, replay, and
  interrupted rebuild evidence. The live harness composes these accepted seams;
  it does not duplicate their private database logic in a browser test.
- Inspect only bounded categorical counts and public correlations needed for
  qualification. Exact ignored captures live under the runner's confined
  temporary root and are removed in `finally` cleanup.

## In Scope

- Extend the live practice scenario to save a valid partial response set,
  observe the returned server revision/time, reload and restore it, complete and
  submit through the generated client, inspect retry/history/review guidance,
  and preserve focus, live status, confidentiality, reflow, themes, forced
  colors, reduced motion, and axe evidence.
- Capture closed public request/result/progress documents for runner-controlled
  parity checks without private authority or submitted answers in history.
- Extend runner helpers to establish an independent supported session, validate
  the capture, read the same public progress state, replay the exact draft save,
  prove a different stale save conflicts without overwriting the current
  snapshot, and compare public state across normal host restart.
- Prove that accepted submission clears only the matching draft, increments
  retry state once, appends stable attempt order, retains earlier history, and
  selects declaration-ordered review targets from incorrect-item evidence.
- Run established contract, application, API, PostgreSQL, concurrency,
  rollback, migration, replay/rebuild, generated-client, browser, architecture,
  security, language, design, documentation, planning, and readiness checks.
- Extend focused harness and boundary tests for closed captures, API-only
  methods, exact replay/conflict ordering, restart sequencing, privacy-minimized
  reporting, artifact confinement, and cleanup.
- Reconcile web, Assessment, Curriculum, Learner-model, local-deployment,
  architecture-verification, known-gap, slice, packet, and register guidance.

## Out of Scope

Product API, OpenAPI, generated-client, schema, event, domain, application,
persistence, migration, scoring, policy, identity, seed, or provider changes;
new question types; cross-version draft migration; background sync; offline
merge; draft expiry; deletion or rewriting of attempts; browser-calculated
retry/history/review authority; answer or private-rule exposure; mastery,
competency, adaptation, recommendation, AI/model grading, a separate AI mode,
autonomous actions, financial advice, external providers, queues, cloud,
tenancy, managed recovery, arbitrary execution, dependencies, shared design
assets, or cosmetic redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Product core and public contracts | accepted practice contracts, services, adapters, migrations, API and generated client | none | Qualify frozen behavior without changing authority or shape |
| Live generated browser | current approved-lesson practice scenario | named practice e2e file | Exercise save, reload, submission, review, retry and history through the public client |
| Headless/restart harness | approved-lesson runner and focused tests | named runner/test files | Compare the same public state and exact writes across sessions and restart |
| Containment | current approved-lesson architecture test | named boundary test | Prevent private imports, direct product mutation, extra servers or unconfined artifacts |
| Guidance and assurance | nearest web/module/deployment/assurance documents | listed Markdown files | Record only demonstrated guarantees and residual gaps |
| Planning | packet, SLI-0028 and register | listed planning artifacts | Close the final dependency-ordered slice seam |

## Contracts and Interfaces

Consume the frozen `PracticePresentationResponseModel`,
`PracticeDraftSaveRequestModel`, `PracticeDraftResponseModel`,
`PracticeProgressResponseModel`, and practice submission/result contracts through
the generated browser client and ordinary HTTP JSON. Browser and non-browser
clients use the same opaque-session cookie and versioned routes. Captures and
reports must remain closed, learner-safe, and privacy-minimized. History exposes
item correctness and evidence references but never submitted answers, answer
keys, learner identity, raw events, persistence identifiers, or evaluator rules.

## Dependencies and Parallel Safety

WRK-0106 is complete and supplies the accepted generated-client browser flow.
This packet owns the shared approved-lesson runner, live practice scenario, and
SLI completion evidence, so it is not parallel-safe with another packet touching
those paths. Existing discovery, curriculum, launch, lesson, knowledge-check,
completion, practice-opening, submission, restart, security, and cleanup
scenarios must continue to pass unchanged.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live save and resume | Exact seeded practice and supported session | Browser saves a partial snapshot and reloads | Same response set, exact chain, positive revision and server time restore through the generated client | Chromium/API/PostgreSQL |
| Save replay and conflict | Retained draft and its public request | Headless client replays it, then sends a different stale snapshot | Replay returns current draft; conflict is bounded and retained state is unchanged | HTTP/PostgreSQL |
| Submission transition | Resumed draft is completed | Browser submits one attempt | One immutable attempt/event is retained, matching draft clears, retry count advances once and result remains answer-safe | Chromium/API/PostgreSQL |
| Retry and review | First attempt contains an incorrect item and attempts remain | Learner views progress and starts another attempt | Server-owned remaining count, stable review targets and earlier history remain visible; controls reset without deleting evidence | Chromium/API |
| History rebuild | Accepted attempts exist | Learner-model projection replays normally and after an interrupted rebuild | Ordered summaries and source digest reproduce; prior complete projection survives interruption | application/PostgreSQL/replay |
| Concurrent final slot | One attempt slot remains | Two distinct valid submissions contend | At most one is accepted, order is gap-free and no partial aggregate is retained | PostgreSQL/concurrency |
| Restart durability | Draft, attempt and projection are retained | Ordinary host restarts without reseeding | Direct progress read and exact replay return the same public meanings and bounded counts | HTTP/PostgreSQL/restart |
| Confidential denial | Missing session, private field, stale write or limit exhaustion occurs | Public client receives the denial | No learner, answer, evaluator, storage, credential or diagnostic detail is disclosed | API/browser/security |
| Accessible parity | Save, restored, conflict, review, retry, history and exhausted states render | Learner uses keyboard, narrow view, themes, forced colors or reduced motion | Meaning, actions, focus and live status remain equivalent with no color-only or horizontal-overflow dependency | Chromium/axe/design |
| Harness containment | Qualification succeeds or fails | Runner exits | Only exact processes, container and ignored temporary root are removed; report contains no secret or personal identifier | runner tests/live |

## Verification Commands

Run the practice contract/application/API and real-PostgreSQL progress and
submission suites, including concurrency, rollback, migration and rebuild
cases; approved-lesson runner and architecture tests; all web unit/component
tests; generated-client reproduction; TypeScript typecheck, lint and build;
focused mocked and live Chromium practice suites; then the full isolated
approved-lesson PostgreSQL/Python/headless/Chromium qualification. Run
architecture, security, learner-language, design-system, documentation,
planning, whitespace, exact-candidate affected verification, one independent
technical review, and the fixed aggregate readiness gate.

## Documentation and Evidence Update

Record exact browser/non-browser public-API parity, save/replay/conflict,
submission draft clearing, retry limit and attempt order, review-target and
history evidence, projection rebuild, migration/rollback, concurrency, restart,
denial/confidentiality, accessibility, topology, cleanup, exact checks,
assumptions, and remaining gaps. State that history is evidence-only and no
mastery, adaptive recommendation, separate AI mode, autonomous authority,
provider, cloud, or external execution was added.

## Stop Conditions

Stop for a product contract/API/client or accepted semantic change; migration
or seed change; browser-owned learner/revision/order/score/time/eligibility;
private answer/evaluator leakage; cross-module persistence access; destructive
evidence handling; failed containment; provider/queue/cloud/tenancy/recovery or
external-execution choice; AI/model/adaptive/mastery authority; dependency
change; conflicting canonical authority; stale CAP binding; or active write-
scope overlap. A product defect discovered by qualification returns to a new
bounded implementation packet rather than being hidden in harness code.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate and receipt; browser/generated-client/headless API
parity; save/resume/replay/conflict; draft clearing; retry/order/history/review;
concurrency, rollback, migration, rebuild and restart evidence; confidentiality,
accessibility, security, topology and cleanup; focused, live, affected,
aggregate, documentation and planning checks; changed paths, assumptions and
gaps. Confirm that no product API, policy, migration, browser authority,
separate AI mode, autonomous authority, provider, cloud or external execution
was added, and leave SLI-0028 ready for deterministic closure.

## Planning History

- 2026-10-16: Authored just in time after WRK-0106 completed. The packet reuses
  the existing isolated live topology, makes one generated-browser save/resume/
  submission flow and the same public documents observable to a fresh
  non-browser session, and combines that evidence with established PostgreSQL
  concurrency, rollback, migration and rebuild suites before slice closure.
