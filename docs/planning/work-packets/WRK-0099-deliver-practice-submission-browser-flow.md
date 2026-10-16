---
id: WRK-0099
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0006
updated: 2026-10-16
parent: SLI-0027
capability: CAP-0006
depends_on: ["WRK-0098"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/router.tsx", "apps/web/src/features/practice-activity", "apps/web/src/styles/practice-activity.css", "apps/web/tests/browser/practice-activity", "apps/web/tests/component/practiceActivity.test.tsx", "apps/web/tests/component/practiceFixture.ts", "apps/web/tests/unit/practiceActivityModel.test.ts", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0027-submit-and-score-practice-attempt.md", "docs/planning/work-packets/WRK-0099-deliver-practice-submission-browser-flow.md"]
generated_artifacts: []
---

# Agent Work Packet: Deliver the Practice Submission Browser Flow

## Objective and Deliverable

Let an authorized learner answer one opened practice activity, use the
generated `submitPlacedPractice` client operation, and receive the saved
learner-safe result in an accessible browser flow. The page must preserve one
submission ID and exact response document across retry-safe transport failures,
render server-returned scoring and feedback without recomputing them, and keep
the public API available as the primary browser-independent boundary. This
packet does not plan a separate AI mode or give a browser, model, or agent
scoring or action authority.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository-
root `docs/README.md`; route through the baseline, interface-design, testing-
quality, security-risk, and delivery-planning context. Read the change-impact
matrix, decision readiness, CAP-0006, SLI-0027, WRK-0098, ADR-0005, ADR-0007,
ADR-0009, the Assessment and REST contracts, interface design system, style
and content guides, user-facing language standard, web/design-system READMEs,
icon rules, generated practice request/result types, current practice model,
loader, page, styles and tests, session adapter, router dependency patterns,
and concurrent-work protocol.

## Decisions and Assumptions

- Consume the generated `submitPlacedPractice` operation delivered by
  WRK-0098. Do not hand-author a parallel transport, call backend internals, or
  move scoring, authorization, time, IDs, completion, or evidence policy into
  the browser.
- Build the request only from the exact opened presentation and native form
  values. The browser creates one UUID submission ID when a complete response
  set is prepared; a retry after a transport or service-unavailable result
  reuses that exact ID and immutable request rather than reading changed form
  state.
- Validate the complete closed result before showing any score or feedback.
  Correlate placement, package, definition, practice, policy, item IDs, item
  versions, item types, scoring policies, response values, ordering, totals,
  referenced review resources, UUIDs, timestamp, and exact keys against the
  submitted/opened data. Fail the whole result closed on mismatch or private or
  unknown fields.
- Server-returned `correct`, score, outcome, applicable feedback, completion
  evidence, and time are authoritative. Browser code may format these values
  and associate result rows with visible questions; it may not infer the
  answer, compare choices, calculate correctness, or create completion meaning.
- Use plain learner language: `Check answers`, `Checking your answers…`,
  `Your result`, and bounded recovery text. Exact IDs, digests, policy values,
  evidence IDs, and timestamp remain in an accessible `Technical record`.
- The current core saves one completed attempt until SLI-0028 adds retry and
  history behavior. Do not promise that the presentation's higher maximum is
  currently executable; explain the present one-attempt boundary without
  changing the accepted attempt-policy contract.
- Reuse native controls, semantic tokens, the current icon pack, and existing
  page structure. No shared token, icon, component, or design-system decision
  is introduced.

## In Scope

- Add generated-type aliases, a pure request builder, and closed result
  validation/correlation helpers for all three supported response types and
  variable valid item, option, feedback-reference, and result counts.
- Add a session-aware submission adapter that calls only the generated public
  operation, retries one renewed unauthorized session at most, preserves the
  exact prepared request, and returns bounded learner-facing result states.
- Turn the existing question controls into one labeled form with required
  single-select, at-least-one multiple-select, and canonical fixed-decimal
  validation. Keep focus on the first incomplete or invalid field.
- Add submit, pending, saved-result, bounded denial, stale/conflict/completed,
  invalid-result, and retry-safe transport/unavailable states. Disable edits
  while pending and after a saved result; prevent duplicate in-flight writes.
- Render activity score/max, result summary, ordered per-question correct/
  review status, submitted response in learner terms, applicable feedback, and
  linked visible review-material titles without answer keys or private rules.
- Announce pending, error, and saved-result changes through appropriate live
  regions and move focus to the result or error summary after completion.
- Preserve light/dark/system meaning, keyboard operation, visible focus,
  narrow/zoom reflow, reduced motion, forced colors, and learner-language
  hierarchy using existing semantic assets.
- Add unit, component, and focused Chromium coverage and update web/planning
  documentation.

## Out of Scope

API/OpenAPI/generated-client changes; backend/domain/application/persistence or
migration changes; new response types; partial save or resume; a second
completed attempt; retry policy, attempt history, result comparison, review
navigation, projection rebuilding, or live fixture changes; answer keys or
private evaluator display; browser scoring; mastery, competency, adaptive
selection, recommendation, model/manual grading, AI tools or protocols,
autonomous authority, financial advice, cloud, tenancy, recovery, providers,
external execution, dependencies, shared design-system changes, or cosmetic
redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public API | generated schema/client and WRK-0098 evidence | none | Keep the reviewed headless-capable contract stable |
| Browser model and adapter | practice validator, session and loader patterns | practice feature model/API only | Build exact requests, call the generated operation, and fail results closed |
| Interface | current practice page, semantic styles, language/design rules | practice component and feature CSS | Collect answers and present saved server results accessibly |
| Composition | router dependency injection | practice submitter wiring only | Keep the generated client and session explicit and testable |
| Tests | practice unit/component/browser fixtures | bounded listed test paths | Prove three-type, flexible-shape, retry, denial, confidentiality and accessibility behavior |
| Documentation/planning | web README, SLI-0027 and register | listed files | Record API-first UI consumption and evidence |

No backend, public contract, generated artifact, database, migration,
dependency, lockfile, shared token, or icon may change.

## Contracts and Interfaces

Consume the opened `PracticePresentationResponseModel`, generated
`PracticeSubmissionRequestModel`, generated
`PracticeSubmissionResultResponseModel`, and protected
`POST /api/v1/curriculum/placements/{placement_id}/practice/submissions`.
Produce a pure prepared-submission value, a bounded submission-state union,
and accessible browser rendering. The request copies exact presentation
selectors and one response per presented item. The returned result must match
that request and presentation before display. Non-browser programs continue to
call the same HTTP operation without importing UI code.

## Dependencies and Parallel Safety

WRK-0098 is complete and supplies the reviewed POST and generated types. This
packet owns the practice feature directory, router wiring, focused test paths,
web README, SLI and register, so it is not parallel-safe with the final live
qualification packet. Complete it before WRK-0100 is authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete submission | One response for every ordered supported item | The learner chooses `Check answers` | One generated-client POST carries exact selectors, one stable UUID and the three closed response shapes | unit/component/browser |
| Server-owned result | The public API returns a valid mixed or all-correct result | The response is accepted | The page shows server scores, summary, submitted values, applicable feedback and review titles without recalculation or answer disclosure | unit/component/browser |
| Flexible shape | Valid activities and results vary item, option and reference counts and order within the contract | Request/result helpers run | No three-item fixture count or incidental order becomes product authority | unit/component |
| Incomplete or invalid input | A required choice is absent, a multiple-choice set is empty, or decimal text is noncanonical | Submission is attempted | No POST occurs, the first invalid control receives focus, and plain guidance identifies what to fix | component/browser |
| Safe retry | Transport or 503 failure occurs after a request is prepared | The learner chooses `Try again` | The identical immutable body and submission ID are resent once at a time; edited DOM values cannot alter it | unit/component/browser |
| Bounded denial | Session, permission, stale definition, conflicting ID reuse, or an existing completed attempt blocks the request | The result is handled | Learner-focused copy states whether work was saved and offers only a safe action without private or implementation detail | component/browser |
| Fail-closed result | A result has an unknown/private field, bad UUID/time/digest, mismatched selector/response, duplicate/missing item, bad total, or unknown reference | Validation runs | No partial score, feedback, identifier, or activity result is shown | unit/component/browser |
| Accessible state | Keyboard, narrow/zoom display, all themes, forced colors and reduced motion are used | The learner answers and reviews a result | Labels, focus, live announcements, content and actions remain equivalent with no overflow and no automated accessibility violation | browser/design |
| Headless continuity | The browser flow is implemented | A non-browser caller uses the POST | The API remains independently available and no UI-specific field or route is required | contract inspection |

## Verification Commands

Run focused practice model/component tests and the practice-activity Chromium
directory; generated-client reproduction; TypeScript typecheck, lint, full web
unit/component suite, and isolated production build; learner-language changed
and full checks; design-system, documentation, planning, architecture,
whitespace, exact-candidate affected verification, one independent technical
review, and the fixed aggregate readiness gate. Do not add backend, database,
or live qualification unless implementation crosses those boundaries.

## Documentation and Evidence Update

Update the web README with the generated POST dependency, form/result states,
retry-safe stable request, fail-closed result validation, API/headless
continuity, and deferred retry/history/live work. Update SLI-0027 and the
planning register with packet state, exact checks, candidate, receipt, review,
assumptions, and residual gaps. Keep approval and reviewer metadata only in the
ignored local ledger.

## Stop Conditions

Stop for a required API, generated-client, backend, schema, persistence,
migration, dependency, shared design-system, or icon change; ambiguity in
result confidentiality, response correlation, or whether a failed write was
saved; a need for browser scoring or answer data; partial-save, second-attempt,
history, mastery, adaptive, AI/model, external-action, identity, tenancy,
provider, recovery, legal, commercial, or advice authority; active scope
collision; conflicting canonical sources; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, generated ordering with unchanged meaning, or another
inconsequential in-scope correction. Fix it locally or defer optional polish to
CAP-0031.

## Required Handoff

Report the exact candidate; generated POST and stable retry request; all three
response shapes; result correlation and confidentiality; no browser scoring;
learner-language, error, focus, live-region, keyboard, theme, reflow, media and
accessibility behavior; focused, generated-client, typecheck, lint, build,
design, language, architecture, documentation, planning, aggregate, affected-
receipt and review results; changed paths; assumptions and gaps. Confirm that
the public API remains independently available and that backend/contracts,
generated artifacts, persistence, retry/history, live qualification, separate
AI-mode planning, autonomous authority, dependencies and external execution did
not change, leaving WRK-0100 dependency-ready.

## Implementation Evidence

Pending implementation.

## Planning History

- 2026-10-16: Authored just in time after WRK-0098 completed. The packet makes
  the browser a generated-client consumer of the already-qualified public API,
  retains stable direct/headless access, and adds no AI-specific mode or
  browser-owned scoring authority.
