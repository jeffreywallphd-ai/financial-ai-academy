---
id: WRK-0176
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0084
capability: CAP-0020
depends_on: [WRK-0175]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/app/router.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesPage.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesRoute.tsx", "apps/web/src/features/lesson-reading/LessonReadingPage.tsx", "apps/web/src/features/lesson-reading/LessonRoute.tsx", "apps/web/src/features/personal-workspace/PersonalWorkspacePage.tsx", "apps/web/src/features/personal-workspace/PersonalWorkspaceRoutes.tsx", "apps/web/src/features/platform-help/FeatureGuidanceExplanation.tsx", "apps/web/src/features/platform-help/api.ts", "apps/web/src/features/platform-help/model.ts", "apps/web/src/features/practice-activity/PracticeActivityPage.tsx", "apps/web/src/features/practice-activity/PracticeActivityRoute.tsx", "apps/web/src/features/project-workspace/ProjectDetailPage.tsx", "apps/web/src/features/project-workspace/ProjectRoutes.tsx", "apps/web/src/styles/platform-help.css", "apps/web/tests/browser/assistance-preferences/assistance-preferences.spec.ts", "apps/web/tests/browser/lesson-reading/lesson-reading.spec.ts", "apps/web/tests/browser/personal-workspace/personal-workspace.spec.ts", "apps/web/tests/browser/practice-activity/practice-activity.spec.ts", "apps/web/tests/browser/project-workspace/project-workspace.spec.ts", "apps/web/tests/component/assistancePreferences.test.tsx", "apps/web/tests/component/lessonReadingPage.test.tsx", "apps/web/tests/component/personalWorkspace.test.tsx", "apps/web/tests/component/platformHelp.test.tsx", "apps/web/tests/component/practiceActivity.test.tsx", "apps/web/tests/component/projectWorkspace.test.tsx", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/platform-help-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0084-understand-feature-limits-and-safe-recovery.md", "docs/planning/work-packets/WRK-0176-deliver-bounded-feature-explanations.md"]
generated_artifacts: []
base_revision: 7bcc2166d002ec09813beb8164a2d9b602bd05d8
claim_id: WRK-0176:21ed9181-7574-4d81-9713-b6ab63c70cfb
claimed_by: codex-cap-0020
claimed_at: 2026-10-18T06:28:46Z
---

# Agent Work Packet: Deliver Bounded Feature Explanations

## Objective and Deliverable

Deliver one optional, reusable browser explanation for the five reviewed
SLI-0084 conditions: unavailable lesson version, uncertain practice write,
unavailable Saved learning source, inert Project artifact, and AI-help provider
execution not enabled. Read each explanation from the protected exact-version
Feature Guidance API through the generated client and place it beside the
owning feature's already-known public status.

The deliverable is presentation-only. It must preserve the owning feature's
status, actions, retry identity, authorization, and durable state. Missing,
denied, malformed, stale, or unavailable Guidance must leave the primary task
and its original safe action usable.

## Required Startup and Current Authority

Before planning edits, Required Startup was completed and reported: repository
entry and authority order; context-pack routing; prompt routing and machine
catalog; planning workflow and register; change-impact matrix; decision
readiness; CAP-0020; SLI-0084; completed WRK-0174/0175; Guidance contracts,
application/API, generated client, the five consuming features and tests; and
the complete interface-design, content-language, token, and icon rules.

The CAP-0020 package remains current, SLI-0084 is active, WRK-0175 completed
with the exact protected operation, and no listed decision gate applies. This
packet refines the already-enumerated bounded-feature-explanations seam and
requires no lower-level approval.

## In Scope

- Add runtime validation for the generated Feature Guidance response that
  checks exact surface, condition, mapping version, mapping-record identity,
  safe strings, closed action/reference shapes, uniqueness, and both digests.
- Add a generated-client reader with one unauthorized-session retry and a
  single optional unavailable outcome that never exposes rejected keys or raw
  transport details.
- Add a reusable accessible explanation component that keeps heading, reason,
  protected/uncertain outcome, and safe next actions in learner order.
- Render exact Help-topic actions as same-application links with a confined
  return target. Render any feature action only when the owning feature supplies
  an exact currently-safe handler; never infer or execute a write.
- Integrate the exact reviewed mappings at the five named public conditions,
  without deriving conditions from exception text, private values, internal
  enums, or repository details.
- Keep the existing owning status and action visible when Guidance loads,
  fails, changes valid wording/order/counts, or is absent.
- Reuse current semantic tokens and card/notice hierarchy in both themes; add
  no raw colors, custom theme map, unreviewed icon, or new global visual rule.
- Add flexible component and focused Chromium evidence for semantic content,
  optional failure, safe action ownership, keyboard/focus, theme/reflow, and
  changed valid record shapes without fixed prose or item counts.
- Synchronize Guidance ownership, API/headless parity, containment, and packet
  state in the architecture and planning sources.

## Out of Scope

- Changing feature/domain/API status codes, authorization, persistence,
  request identity, retry semantics, artifact bytes, learner evidence, or the
  AI-help preference.
- Selecting a mapping from `latest`, substituting a different condition, or
  interpreting raw exception, log, provider, model, database, or policy data.
- Executing retries, reloads, navigation, downloads, saves, submissions,
  remediation commands, provider/model calls, or external URLs solely because
  Guidance described them.
- Adding provider/model integration, AI authority, financial advice, artifact
  execution/preview, managed-cloud support, telemetry, or external content.
- Corpus-wide freshness, broken-link, offline/restart, browser/headless parity,
  no-outbound, feature-state-containment, or final cleanup closure; the last
  SLI-0084 packet owns that cumulative evidence.
- Cosmetic restyling or unrelated copy cleanup; optional polish remains
  CAP-0031 work unless the user explicitly reprioritizes it.

## Contracts and Invariants

1. The owning feature determines whether a named condition exists before any
   Guidance request. Guidance never changes or broadens that condition.
2. The browser requests one literal mapping version, currently `1.0.0`; no
   latest alias, fallback condition, or substituted record is accepted.
3. Runtime validation requires the mapping digest and record digest supplied
   by the server, exact mapping-record identity, and closed shapes before any
   content is shown.
4. Guidance is optional. A loading, denied, missing, malformed, stale, or
   unavailable response renders no partial explanation and never blocks the
   owning task or removes its original safe action.
5. `open_help_topic` is the only record action that can become a link without a
   feature-owned handler. Other action kinds remain inert unless the owning
   feature explicitly supplies the matching safe operation.
6. An explanation never sends learner data, feature payloads, exception text,
   provider/model data, or private state to Guidance.
7. The primary copy follows result, protection/uncertainty, then next action;
   technical mapping, version, and digest facts remain outside primary prose.
8. Browser and future headless callers continue to use the same protected API
   contract; this packet adds no browser-only backend meaning.

## Condition Placements

| Surface | Public condition | Placement and preserved owning behavior |
| --- | --- | --- |
| Lesson | `exact-version-unavailable` | Beside the exact-version unavailable state; existing return/retry remains authoritative |
| Practice | `write-outcome-uncertain` | Beside an unavailable save/submission response; unchanged-request retry and reload remain feature-owned |
| Saved learning | `source-unavailable` | Beside retained work whose source is unavailable; saved learner work remains visible |
| Project | `artifact-inert` | Beside admitted inert artifacts; the existing original-file download remains feature-owned |
| AI help | `provider-execution-not-enabled` | Beside the learner-owned on-request choice; the preference does not call or authorize a provider/model |

## Change-Impact Trace

| Boundary | Direct impact | Consumers/evidence | Required treatment |
| --- | --- | --- | --- |
| Guidance browser adapter | generated response validation and optional reader | five feature routes/pages | reject invalid shapes atomically; one session retry |
| Shared UI | optional explanation component and semantic-token styles | five placements | preserve task hierarchy, keyboard, theme, reflow, and safe action ownership |
| Feature consumers | public-condition placement only | existing status/action models | no status derivation, mutation, or feature contract change |
| Help navigation | exact topic links and confined return target | platform Help route | same-origin closed paths only; no arbitrary destination |
| Architecture/planning | Guidance ownership, parity, evidence, packet state | module map, Help contract, assurance, SLI/register | keep status and boundary claims synchronized |

No database, backend, public API shape, provider, model, queue, identity,
tenancy, encryption, licensing, legal, or financial-calculation boundary changes.

## Acceptance Scenarios

| Scenario | Required result |
| --- | --- |
| Five exact conditions | Each named owning state may show the exact reviewed explanation and Help reference without changing the primary status or action |
| Optional failure | Denied, missing, malformed, stale, aborted, or unavailable Guidance shows no partial explanation and the owning feature remains usable |
| Safe action ownership | Help links stay same-application; no retry, reload, return, download, save, submit, or external action runs without an explicit owning handler |
| Exact correlation | Surface, condition, mapping version, mapping/record identity, ordered content, and both digests match before rendering |
| Flexible valid record | Wording, action/reference counts and order, and additional valid fields vary within contract bounds without fixed prose/count tests |
| Privacy and containment | Requests contain only three public keys; UI and failures reveal no learner, provider, exception, repository, or raw transport detail |
| Accessibility | Heading order, landmark/name, links/buttons, focus, light/dark, narrow reflow, 200-percent text, forced colors, and reduced motion preserve equivalent meaning/actions |

## Verification Plan

- Component tests for the reader/validator and reusable component: exact
  correlation, digest rejection, invalid/unknown shapes, optional failure,
  abort behavior, safe-action handlers, Help links, variable counts/order/copy,
  and no partial display.
- Focused component tests for all five placements, preserving the original
  feature status, action, learner-owned work, artifact download, and AI-help
  choice when Guidance is ready or unavailable.
- Focused Chromium tests for the five flows covering protected request facts,
  accessible reading order, keyboard/focus, theme, narrow layout, synthetic
  200-percent text, forced colors, reduced motion, optional failure, and no
  unexpected feature request or external navigation.
- Full Web unit suite, TypeScript check, zero-warning lint, production build,
  generated-client contract check, learner-language changed-scope check,
  design-system integrity, documentation/planning integrity, Git whitespace,
  and aggregate agent readiness.
- Select exact affected checks through the control plane after implementation;
  do not run unrelated live/database/provider gates merely for confidence.

## Anti-Rigidity Rules

- Do not assert complete paragraphs, starter record counts, incidental request
  timing, exact DOM nesting, CSS pixels, fixed viewport positions, or one action
  count when semantic roles and bounded facts are sufficient.
- Accept varied safe Unicode, wording, Help/action ordering, zero-to-five
  actions, one-to-ten Help references, themes, viewport widths, text scaling,
  forced colors, reduced motion, and feature-owned handler availability.
- Do not block for harmless whitespace, optional copy, fixture ordering,
  nonfunctional early-alpha styling, or advisory readability signals. Fix a
  bounded defect directly or record optional polish for CAP-0031.
- Block only a functional, safety, privacy, authorization, contract,
  accessibility, containment, or approved-scope failure.

## Claim, Scope, and Stop Conditions

Before implementation, consume the reserved ID, commit this plan, claim the
packet from the clean commit, run `packet-start`, acquire one exact exclusive
file lease for the declared write scope, and confirm no active overlap.

Stop for human direction only if implementation requires a new provider/model
call, external action or destination, arbitrary command, mutation/persistence,
feature-policy or status reinterpretation, new permission, identity/tenancy,
licensing/legal/commercial choice, breaking public contract, material slice/CAP
change, or an actual ownership collision. A test-only or copy/style correction
inside this outcome is not a new approval gate.

## Required Handoff

Report `CAP-0020.SLI-0084.WRK-0176`; exact candidate and receipt; reader and
runtime-validation boundaries; all five placements; safe-action ownership;
optional fallback; Help return confinement; browser/headless parity; privacy,
accessibility, and anti-rigidity evidence; focused/repository checks; changed
files; documentation impact; assumptions; and the remaining live-qualification
gap. Confirm no feature status/action, persistence, provider/model execution,
artifact execution, external action, learner authority, or financial behavior
changed.

## Verification Evidence

Implementation is complete pending exact-candidate qualification and
independent technical review. The browser revalidates exact mapping/record
correlation and both SHA-256 digests, retries one expired learner session, and
collapses every denied or invalid response to an optional unavailable outcome.
The shared accessible explanation is placed beside the exact lesson, practice,
Saved learning, Project artifact, and AI-help public conditions. Intrinsic
navigation is confined to an exact same-application Help topic; every other
action is inert unless the owning feature supplies its current safe handler.

Focused component qualification passes 87 tests across the shared adapter,
validator, component, and five placements. Focused Chromium qualification
passes all 58 scenarios after narrowing one legacy assertion to its actual
private Saved-learning request boundary; the unchanged broad run passed the
other 57 scenarios and the corrected scenario then passed directly. The suite
retains axe, keyboard/focus, light/dark, narrow/200-percent-text, forced-color,
reduced-motion, retry-identity, download, learner-work-retention, and
no-substitution evidence without freezing whole prose, item counts, pixels, or
unrelated shell requests.

The bounded correction makes the explanation heading level placement-owned:
the lesson not-found state now follows its `h1` with an `h2`, while placements
inside an existing feature section retain the default `h3`; the action heading
always follows one level below. Direct reader and validator regressions now
cover one-401 renewal with an exact second request, repeated denial without a
third request, failed renewal, abort propagation, mapping and guidance digest
rejection, recomputed mapping-record mismatch, recomputed unknown-field
rejection, varied valid copy/action/reference/applicability counts and order,
server-order rendering, and feature-owned handler gating. The corrected focused
typecheck and 28 platform-help/lesson component tests pass.

## Planning History

- 2026-10-18: Authored just in time after WRK-0175 completed. The packet
  delivers the approved five-condition optional browser explanation through
  the existing protected API while preserving all owning-feature authority and
  deferring cumulative live containment/cleanup to the final SLI-0084 packet.
- 2026-10-18: Activated from clean base `7bcc216` after confirming current CAP
  authority, completed WRK-0175 dependency, the exact five-condition scope,
  interface-language/design obligations, executable checks, and no unresolved
  decision or active ownership collision.
- 2026-10-18: Implemented the optional generated-client explanation across all
  five conditions with exact runtime correlation/digest validation, safe-action
  ownership, same-application Help navigation, no-partial fallback, and focused
  flexible component/Chromium coverage. Exact-candidate verification and
  independent review remain before closure.
- 2026-10-18: Added placement-owned semantic heading levels and direct
  high-risk reader/validator regression evidence for renewal, denial, abort,
  digest/correlation/shape rejection, flexible valid ordering, and explicit
  action ownership. Fresh exact-candidate verification remains before closure.
