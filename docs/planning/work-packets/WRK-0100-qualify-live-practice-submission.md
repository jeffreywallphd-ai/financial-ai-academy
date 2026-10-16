---
id: WRK-0100
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0027
capability: CAP-0006
depends_on: ["WRK-0099"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/practice-activity.e2e.ts", "backend/src/financial_ai_academy/modules/assessment/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0027-submit-and-score-practice-attempt.md", "docs/planning/work-packets/WRK-0100-qualify-live-practice-submission.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: 7c2ad0689b481a1821e01602b79a77acc341c6a2
claim_id: WRK-0100:be0945de-34f3-4272-a4ff-1d51e3508fdc
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T16:45:33Z
---

# Agent Work Packet: Qualify Live Practice Submission

## Objective and Deliverable

Complete SLI-0027 by extending the existing isolated approved-lesson harness so
one generated-browser submission and the same captured public request from a
cookie-preserving non-browser client produce one deterministic, durable
practice result against real PostgreSQL. Prove exact replay, conflict and
attempt-limit refusal, atomic evidence, confidentiality, accessibility, and
normal-restart stability while keeping the versioned public API as the single
browser-independent boundary. Do not add a separate AI mode, agent protocol,
or autonomous authority.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, testing-quality, security-risk,
interface-design, and delivery-planning context packs. Read the change-impact
matrix, decision readiness, CAP-0006, SLI-0027, WRK-0096 through WRK-0099,
ADR-0005, ADR-0007, ADR-0009, the Assessment and REST contracts, the approved
practice package, submission/result/completion-event schemas, Assessment
application and PostgreSQL/API tests, generated client, browser flow, local
composition, approved-lesson runner and its nearest tests/READMEs, architecture
evidence map, known gaps, and concurrent-work protocol.

## Decisions and Assumptions

- Reuse the existing uniquely named PostgreSQL 18.4 container, restrictive
  filesystem root, loopback Python API/static host, approved fixture seed, and
  pinned Chromium run. Do not create another product seed, database topology,
  server, or Node production host.
- Let the live generated browser client perform the first successful write.
  Capture only its bounded public request and learner-safe public result in the
  runner's ignored temporary root. Never capture a cookie, token, learner ID,
  database credential, private definition, answer key, or evaluator declaration.
- Reuse that exact request body and submission ID through a fresh cookie-backed
  non-browser session for exact replay before and after normal restart. This
  proves browser/headless parity without inventing a second transport.
- Use a minimally changed copy of the captured request to prove conflicting ID
  reuse, and a fresh submission ID with the same answers to prove the current
  one-completed-attempt boundary. Neither refusal may alter the original result
  or append partial evidence.
- Inspect bounded Assessment-owned table counts and exact retained identifiers
  before and after replay, refusal, and restart. Do not read private definition
  bytes or another module's tables to decide product behavior.
- Keep the live report privacy-minimized and categorical. Exact qualification
  artifacts remain ignored and are removed with the runner's bounded temporary
  root in `finally` cleanup.

## In Scope

- Extend the live practice Chromium scenario to answer all three supported item
  types, submit through the generated client, and verify the learner-safe saved
  result, technical record, focus/live-region behavior, answer confidentiality,
  and the absence of a second in-flight write.
- Emit one bounded ignored capture containing only the exact public request and
  public result needed for independent replay qualification.
- Add runner helpers that validate the capture's closed public shape, establish
  a separate supported session, replay the exact request, exercise conflicting
  reuse and the existing completed-attempt refusal, and reject drift or leaked
  private fields.
- Add PostgreSQL observations proving exactly one practice attempt, one response
  and score per definition item, one completion record, and one correlated
  outbox event, with no additional rows after replay, refusal, or restart.
- Stop and restart the ordinary host without reseeding, repeat the exact
  headless replay, compare the complete public result and retained counts, and
  leave existing learner-completion replay evidence intact.
- Extend focused runner and architecture tests for API-only methods, capture
  confinement, public-field closure, replay identity, refusal behavior, count
  invariance, restart sequencing, redacted reporting, and cleanup.
- Reconcile the affected web, Assessment, local-deployment, architecture,
  verification-gap, slice, packet, and register documentation.

## Out of Scope

New or changed product API/OpenAPI/generated-client contracts; domain,
application, persistence, migration, scoring, feedback, identity, or attempt
policy behavior; a second practice placement or product seed; partial save,
resume, retries, attempt history, comparison, review navigation, projection
consumption, mastery, competency, adaptation, recommendation, AI/model grading,
AI tools or protocols, autonomous actions, financial advice, providers, queue,
cloud, tenancy, recovery, external execution, dependencies, shared design
assets, or cosmetic redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public API and core | frozen schemas, API and Assessment tests | none | Qualify accepted behavior without changing authority or shape |
| Live browser | generated-client practice route and existing live spec | one approved-lesson practice spec | Produce the first exact attempt and verify accessible learner output |
| Headless/restart harness | current approved-lesson runner and focused unit tests | two named Python files | Replay the same public document, inspect bounded evidence, restart, and contain artifacts |
| Architecture containment | current harness source-boundary test | one named architecture test | Prevent private/internal or additional-server shortcuts |
| Guidance and assurance | nearest READMEs, architecture map, known gaps | listed documents | Record only directly demonstrated claims and residual gaps |
| Planning | packet, SLI-0027, register | listed artifacts | Close the final dependency-ordered slice seam |

No product implementation, contract, OpenAPI snapshot, generated client,
database migration, package fixture, dependency, lockfile, shared design token,
or icon may change.

## Contracts and Interfaces

Consume the frozen practice request/result v1 contracts and protected
`POST /api/v1/curriculum/placements/{placement_id}/practice/submissions` through
the generated browser client and ordinary HTTP JSON. Produce only executable
qualification helpers, bounded ignored evidence, categorical report fields, and
documentation. The public result must correlate its submission, placement,
package, definition, practice, policy, item, response, scoring, feedback,
review-reference, completion, and timestamp values while excluding learner
identity, request fingerprint, answer values, private evaluator rules, storage
details, and diagnostics.

## Dependencies and Parallel Safety

WRK-0099 is complete and supplies the accepted accessible browser consumer.
This final slice packet owns the shared live runner, practice browser scenario,
and SLI evidence, so it is not parallel-safe with another packet touching those
paths. Existing discovery, curriculum, launch, lesson, knowledge-check,
completion, practice-opening, restart, security, and cleanup scenarios must
remain intact.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live browser write | Exact seeded three-shape practice and supported session | Learner answers and checks answers | One generated-client POST saves and displays the complete learner-safe result with correct focus and live status | Chromium/API |
| Headless exact replay | Browser capture and a fresh supported session | Non-browser client sends the identical public body | Original result returns byte-for-meaning equal with no new evidence rows | HTTP/PostgreSQL |
| Conflicting replay | Existing submission ID and one changed public response | Non-browser client posts the conflict | Bounded conflict reveals no private fact and original evidence remains unchanged | HTTP/PostgreSQL |
| Attempt limit | Completed practice and a new submission ID | Same learner posts the same answers | Existing completed-attempt refusal returns and no second aggregate is retained | HTTP/PostgreSQL |
| Atomic evidence | First valid submission | Retained state is inspected | One attempt, per-item response/score closure, one completion and one outbox event correlate to exact versions and IDs | PostgreSQL/live |
| Restart durability | Saved aggregate and stopped host | Ordinary host restarts without seeding and exact headless replay repeats | Complete result and counts remain unchanged | HTTP/PostgreSQL/restart |
| Confidential denial | Missing session or malformed/private public payload | Public endpoint or browser handles it | Bounded response/UI discloses no learner, answer, evaluator, storage or diagnostic detail | API/browser |
| Accessible parity | Themes, keyboard, narrow display, forced colors and reduced motion | Learner submits and reviews the live result | Meaning, actions, focus, reflow and axe evidence remain equivalent | Chromium/design |
| Harness containment | Qualification succeeds or fails | Runner exits | Only exact process, container and ignored temporary root are removed; report carries no secret or personal identifier | runner tests/live |

## Verification Commands

Run focused Assessment practice contract/application/API/PostgreSQL suites;
approved-lesson runner and architecture unit tests; web practice model/component
tests; generated-client reproduction; TypeScript typecheck, lint, build and
focused mocked practice Chromium; then run the full isolated approved-lesson
PostgreSQL/Python/headless/Chromium qualification. Run architecture, security,
learner-language, design-system, documentation, planning, whitespace,
exact-candidate affected verification, one independent technical review, and
the fixed aggregate readiness gate. Use external database acknowledgement only
for a genuinely isolated database; otherwise use the runner's disposable
container.

## Documentation and Evidence Update

Record exact request/result parity, deterministic scoring, replay/conflict/
attempt-limit behavior, atomic evidence, outbox correlation, restart durability,
denial/confidentiality, accessibility, topology, cleanup, checks, assumptions,
and remaining gaps. State that browser and future headless clients share the
same public API while no separate AI mode or autonomous authority was planned
or implemented. Keep approval and reviewer records only in the ignored ledger.

## Stop Conditions

Stop for a new or breaking product contract/API/client shape, scoring or policy
change, migration, product seed, second placement, private answer/evaluator data
in public evidence, client-selected learner/time/score/evidence, cross-module
storage ownership, destructive retained-data handling, failed containment,
provider/queue/cloud/tenancy/recovery/external execution, AI/model/adaptive
authority, dependency change, active scope collision, conflicting canonical
authority, stale CAP approval, or material CAP-0006/SLI-0027 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, or another inconsequential in-scope correction. Fix it
locally or defer optional polish to CAP-0031.

## Required Handoff

Report the exact candidate; public API/generated-client/headless parity; all
three response shapes; deterministic result and atomic evidence; replay,
conflict, attempt-limit and restart results; denial/confidentiality,
accessibility, security, topology and cleanup evidence; focused, live, affected,
aggregate, contract, documentation and planning checks; changed paths;
assumptions and gaps. Confirm that no product API, scoring policy, migration,
browser authority, separate AI mode, autonomous authority, provider, cloud, or
external execution was added. Leave SLI-0027 ready for deterministic closure.

## Planning History

- 2026-10-16: Authored just in time after WRK-0099 completed. The packet reuses
  the existing isolated topology, makes the browser's exact public request the
  shared replay input for a non-browser client, and qualifies durable practice
  evidence across normal restart without planning a separate AI mode or adding
  another transport or authority boundary.
- 2026-10-16: Claimed from base revision `7c2ad06` after the implementation
  gate confirmed current CAP authority, completed dependency, decision
  readiness, exact qualification scope, and no active ownership collision.
- 2026-10-16: Implemented the qualification-only extension. One generated-
  client Chromium submission now supplies a closed public request/result
  capture that an ordinary cookie-backed HTTP client replays before and after
  a normal host restart. The harness proves one atomic PostgreSQL aggregate,
  exact replay identity, bounded conflict and completed-attempt refusals,
  unchanged row counts, confidential denials, and no private answer or learner
  fields in retained qualification artifacts or reporting.
- 2026-10-16: Pre-review evidence passed: 104 focused Assessment contract/unit
  tests, 16 protected API integration tests, 36 runner/architecture tests plus
  four subtests, the full 202-test web suite, typecheck, lint, static build,
  generated-client reproduction, architecture, security, learner-language,
  design, documentation, planning, whitespace, and the 29-check aggregate
  readiness gate. The isolated live PostgreSQL/Python/Chromium run passed all
  ten scenarios and demonstrated all three response types, browser/headless
  public-API parity, atomic evidence, exact replay, confidential refusals, and
  restart durability without reseeding.
- 2026-10-16: Submitted exact candidate `7869614` for fresh affected
  verification and independent technical review. Lifecycle-only planning
  changes after this point do not alter that candidate.
- 2026-10-16: Completed at exact candidate `7869614`. The fresh eight-check
  affected-verification receipt qualified with authoritative digest
  `sha256:f99ffe498e0bf036eb722d19948fcfd9876e85f5e3b4f18d72598925ce983cc5`,
  and independent review R01 accepted the candidate with no findings. The live
  browser and non-browser clients share the public API, while separate AI-mode
  planning and autonomous authority remain out of scope.
