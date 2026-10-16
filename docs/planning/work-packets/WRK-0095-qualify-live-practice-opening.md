---
id: WRK-0095
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0026
capability: CAP-0006
depends_on: [WRK-0094]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/practice-activity.e2e.ts", "backend/src/financial_ai_academy/bootstrap/settings.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/modules/assessment/README.md", "backend/tests/unit/test_bootstrap_settings.py", "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-practice/manifest.json", "contracts/compatibility/lesson-package/v1/approved/intro-risk-return-practice/practices/practice-1.json", "deployments/local/README.md", "deployments/local/serve.py", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0026-open-versioned-practice-activity.md", "docs/planning/work-packets/WRK-0095-qualify-live-practice-opening.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: 09713e065a51780a9de86e468f3b6641a5bba819
claim_id: WRK-0095:794985f1-3344-4bf3-b378-0bfca600845f
claimed_by: codex-cap-0006
claimed_at: 2026-10-16T15:12:27Z
---

# Agent Work Packet: Qualify Live Practice Opening

## Objective and Deliverable

Complete SLI-0026 by extending the existing isolated approved-lesson harness
so real PostgreSQL repositories, restrictive filesystem content, the loopback
Python API/static host, a non-browser HTTP client, the generated browser
client, and pinned Chromium all open the same exact answer-safe practice
activity. Prove exact provenance, all three approved response shapes, denial
confidentiality, restart stability, and side-effect-free repeated reads without
adding submission, scoring, browser authority, or a separate AI mode.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the testing-quality and delivery-planning
context packs. Read the change-impact matrix, decision readiness, CAP-0006,
SLI-0026, WRK-0092 through WRK-0094, ADR-0005, ADR-0007, the Assessment and
content-package contracts, practice and lesson-package compatibility fixtures,
Curriculum practice placement and Assessment opening operations, protected API
and generated client, practice browser route, local composition, live runner,
architecture tests, affected READMEs, and concurrent-work protocol.

## Decisions and Assumptions

- Reuse the one clean-start approved-lesson qualification topology. Do not add
  another server, database harness, product seed path, or Node production host.
- Extend only the explicit approved-fixture path to admit the existing exact
  practice package and create its placement through public Content and
  Curriculum operations before application readiness. Ordinary startup stays
  seed-free.
- Make the package-scoped practice fixture carry the already-approved three-
  item compatibility definition so the live path exercises single select,
  multiple select, and fixed-decimal numeric entry without inventing a fourth
  response type or new semantic contract.
- Treat the protected public GET as the authoritative reusable interface. A
  cookie-preserving non-browser client and the generated browser client must
  observe the same exact stable presentation; neither receives an answer key,
  accepted numeric value or range, scoring object, feedback branch, learner
  selector, or mutation authority.
- Prove side-effect freedom by comparing bounded Assessment and learner-state
  storage counts before and after repeated headless practice reads. Browser
  evidence also asserts that practice opening issues no practice mutation.
- Existing PostgreSQL 18.4, loopback host, pinned Chromium, redaction,
  external-isolated-database acknowledgement, and exact cleanup controls remain
  authoritative.

## In Scope

- Align the approved lesson-package practice fixture with the existing closed
  three-item practice compatibility definition and update its exact bytes,
  size, and digest metadata.
- Admit the exact practice package and create one exact practice placement only
  under `--seed-approved-fixture`, using public services in deterministic order
  and failing readiness on any admission or placement failure.
- Add headless HTTP observation for session establishment and repeated exact
  practice GETs, including stable provenance, ordered three-type closure,
  private-field absence, browser-independent availability, and equality across
  a normal restart without reseeding.
- Correct the existing shared-settings practice-schema path derivation exposed
  by the first live startup and add a direct regression for the lesson,
  Assessment, practice, event, and migration directory relationships.
- Add before/after PostgreSQL counts proving open creates no practice attempt,
  response, score, completion, outbox, or learner projection evidence.
- Add live Chromium evidence for the generated-client route, all three native
  response controls, canonical numeric constraints, technical provenance,
  no submission action, no answer leakage, denial/missing paths, themes,
  keyboard/focus, narrow reflow, forced colors, reduced motion, and axe checks.
- Extend architecture and runner tests for seed isolation, public-operation
  order, failure containment, headless stable semantics, side-effect checks,
  restart behavior, report privacy, and exact cleanup.
- Reconcile the affected architecture evidence, known gaps, deployment, host,
  Assessment, web, slice, packet, and register documentation.

## Out of Scope

Practice submission, response persistence, deterministic scoring execution,
feedback selection, attempt limits, retry/resume/history behavior, completion
or mastery evidence, adaptive selection, recommendation ranking, AI-authored
items, model grading, autonomous actions, a special AI protocol, another API,
product discovery/navigation changes, production seed data, schema migration,
provider/queue/cloud behavior, tenancy, recovery, external execution, new
dependencies, or styling-only cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Approved fixtures | practice and package compatibility corpus | listed practice definition and manifest | Exercise the accepted three-type contract through real package admission |
| Local composition | public Content/Curriculum services and explicit fixture seed | `deployments/local/serve.py`, architecture test | Seed an exact practice only in qualification and preserve startup isolation |
| Shared settings path | derived contract-directory properties | settings module and one focused unit test | Repair the existing practice-schema sibling path required by the real host |
| Headless/live evidence | protected API, PostgreSQL state, restart and cleanup runner | runner and its focused unit test | Prove non-browser access, stable provenance, no mutations, and restart parity |
| Browser evidence | generated practice client and delivered route | one new approved-lesson spec | Prove the same public presentation and accessible interaction live |
| Assurance and guidance | architecture map, gaps, nearest READMEs | listed documentation | State only directly demonstrated API/headless/browser evidence and gaps |
| Planning evidence | packet, SLI-0026, register | listed planning files | Close the final dependency-ordered SLI-0026 seam coherently |

No product domain/application/API contract, OpenAPI or generated-client source,
persistence schema or migration, package dependency, shared design asset, or
ordinary startup behavior may change. The bounded shared-settings path
correction is permitted only to resolve the already-declared practice schema.

## Contracts and Interfaces

Consume the frozen practice-definition and answer-safe presentation v1
contracts, `CreatePracticePlacementRequest`,
`open_placed_practice(OpenPlacedPracticeRequest)`, and protected
`GET /api/v1/curriculum/placements/{placement_id}/practice`. Produce only
qualification fixtures, stable observation helpers, executable live evidence,
and documentation. Headless and browser observations must correlate placement,
package, practice, definition, item, policy, option, resource, version, and
digest fields while rejecting or omitting private answer/scoring/feedback
fields. Repeated GETs and normal restart must preserve meaning and storage
counts; no client may select learner identity or scoring behavior.

## Dependencies and Parallel Safety

WRK-0094 is complete and supplies the accepted browser route. This packet is
the final SLI-0026 seam and overlaps the shared approved fixture, local seed,
live runner, browser suite, assurance map, and slice evidence, so it is not
parallel-safe with another packet touching those paths. It must preserve every
existing discovery, curriculum, launch, lesson, knowledge-check, completion,
restart, security, and cleanup scenario.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| API/headless opening | Established supported session and exact seeded placement | A non-browser client issues repeated protected GETs | Stable answer-safe three-type presentation and exact provenance return without UI state or private fields | live HTTP/runner unit |
| Browser opening | Same exact seeded placement | Generated client opens the practice route | Purpose, instructions, policy, references, technical record, and all three response controls equal public API facts | live Chromium/API |
| Side-effect-free read | Bounded Assessment and learner-state counts | Practice is read repeatedly | Attempt, response, score, completion, outbox, and learner projection/history counts remain unchanged | PostgreSQL/live |
| Restart stability | Seeded database and filesystem remain, application restarts without seeding | Headless practice read repeats | Exact stable presentation is unchanged and no fixture mutation is required | live restart |
| Confidentiality and denial | Missing session/permission, unknown placement, or unexpected private field | API or browser path is used | Bounded response reveals no practice, answer, scoring, feedback, learner, or storage detail | live API/browser |
| Three closed shapes | Valid reordered options and single, multiple, numeric items | Live response renders | Native controls preserve server order and canonical decimal requirements without fixture-count authority | contract/live browser |
| Accessible parity | Keyboard, narrow display, themes, forced colors, and reduced motion are used | Learner reviews the live activity | Meaning and operation remain equivalent, focus is visible, no horizontal overflow occurs, and axe reports no violation | live Chromium |
| Harness containment | Qualification succeeds or fails | Runner exits | Only its exact process, database container, and bounded temporary root are removed; report contains no secret or learner identifier | runner tests/live |

## Verification Commands

Run practice contract and lesson-package conformance; focused Content,
Curriculum, Assessment, API, PostgreSQL, local-composition architecture, runner
unit, web model/component, and generated-client checks; TypeScript typecheck,
lint, production build, focused mocked practice Chromium, and the full isolated
approved-lesson PostgreSQL/Python/headless/Chromium runner. Run OpenAPI/client
reproduction, architecture, security, learner-language, design-system,
documentation, planning, whitespace, exact-candidate affected verification,
one independent technical review, and aggregate readiness. Use the explicit
external database acknowledgement only for a genuinely isolated database;
otherwise use the runner's unique pinned disposable container.

## Documentation and Evidence Update

Record exact package/practice identity, three response types, headless and
browser parity, repeated-read and restart stability, storage-count invariance,
denial/confidentiality, accessibility, topology, cleanup, checks, assumptions,
and remaining gaps. Do not imply practice submission, scoring, feedback,
attempt policy enforcement, completion, mastery, AI, production, recovery,
multi-user, or non-Chromium qualification. Store approval and reviewer records
only in the ignored local ledger.

## Stop Conditions

Stop for a new or breaking product contract/API/client shape, product seed or
runtime mutation, persistence schema/migration, answer/scoring/feedback data in
the public response, practice write behavior, client-selected learner/policy,
cross-module storage access, provider/queue/cloud/tenancy/recovery/external
execution, AI/model/adaptive authority, dependency change, failed containment,
active scope collision, conflicting canonical authority, stale CAP approval,
or material CAP-0006/SLI-0026 drift.

Do not stop for bounded fixture/test corrections, harmless whitespace,
advisory wording, or nonfunctional styling. Fix those locally or defer optional
polish to CAP-0031 without another approval or review cycle.

## Required Handoff

Report the exact candidate; public API/generated-client/headless parity;
three-shape presentation; repeated-read, storage, restart, denial,
confidentiality, accessibility, security, topology, and cleanup evidence;
focused, live, affected, aggregate, contract, documentation, and planning
results; changed paths; assumptions and gaps; and confirmation that no product
API, submission, scoring, feedback, evidence, migration, browser authority,
AI mode, provider, cloud, or external execution was added. Leave SLI-0026 ready
for deterministic closure or return one bounded blocker.

## Implementation Evidence

- The approved practice package now carries the existing immutable three-item
  definition and passes both practice-definition and lesson-package contract
  conformance with exact manifest size and digest metadata.
- The explicit qualification seed admits the package and creates its lesson and
  practice placements through public Content and Curriculum operations. Normal
  startup remains seed-free, and a focused settings regression preserves the
  sibling lesson, Assessment, practice, event, and migration contract roots.
- The isolated live run passed against PostgreSQL 18.4, the loopback Python
  API/static host, a cookie-backed non-browser client, the generated browser
  client, and pinned Chromium. All 10 live browser scenarios passed, including
  the exact three-shape practice and bounded denial scenarios.
- Repeated protected API reads returned identical answer-safe provenance,
  created no attempt, response, score, completion, outbox, or learner projection
  records, and retained the same meaning after a normal host restart without
  reseeding. No public API or generated-client shape changed.
- Focused Python evidence passed 112 tests plus 4 subtests; the full web
  unit/component suite passed 181 tests; typecheck, lint, production build,
  OpenAPI snapshot reproduction, generated-client reproduction, architecture,
  documentation, planning, design-system, security, learner-language, and
  whitespace checks passed.

## Planning History

- 2026-10-16: Authored just in time after WRK-0094 completion. The packet
  reuses the existing isolated topology, strengthens the approved fixture with
  the already-frozen three-type definition, and makes browser-independent
  public API access plus side-effect-free restart behavior first-class live
  evidence without planning or implementing a separate AI mode.
- 2026-10-16: Claimed from base revision `09713e0` after dependency,
  authority, decision, exact-scope, and file-collision checks passed.
- 2026-10-16: The first contained live startup exposed an extra `v1` segment in
  the existing derived practice-schema directory. Expanded scope to the shared
  settings property and one direct regression; no API, domain, persistence, or
  product behavior changed.
