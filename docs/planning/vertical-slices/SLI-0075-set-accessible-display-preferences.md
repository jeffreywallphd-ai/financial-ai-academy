---
id: SLI-0075
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: CAP-0018
depends_on: [SLI-0074]
decision_gates: []
---

# Vertical Slice: Set Accessible Display Preferences

## Outcome and User Scenario

An authorized learner can choose safe reading and presentation preferences,
choose light, dark, or device theme, preview the result immediately, save or
reset the choices, and understand where each choice is stored and applied.
Learner-owned presentation preferences remain available through a protected
public API for browser and headless clients. Theme remains a platform display
setting in the local browser and has no headless, evidence, policy, or content
meaning.

## Scope Boundaries

### In Scope

- A separate Learner-model-owned, additive
  `learner-presentation-preferences/v1` family for explicit text size, text
  spacing, reading width, and motion choices with stable identity, revision,
  canonical time/digest, bounded non-content history, reset, and export.
- Closed safe values that can preserve or improve the accessibility baseline:
  default or larger text, default or increased spacing, standard or focused
  reading width, and device motion behavior or reduced motion. No choice may
  request smaller text, forced animation, hidden content, or a reduced target.
- The existing platform-owned `system`, `light`, and `dark` theme setting,
  labeled as stored in this browser, with `system` as its safe default.
- A plain-language `Display and accessibility` route with immediate preview,
  explicit save/reset behavior, purpose and storage disclosures, accessible
  technical records, and usable unavailable/failure states.
- A presentation application boundary that applies only complete validated
  learner settings to semantic root attributes and existing design-system
  tokens. Device/browser zoom, forced colors, and reduced-motion signals retain
  precedence whenever they are more protective.
- One protected public API and reviewed generated client for profile, history,
  mutation, reset, and export behavior. The browser is one client rather than
  a second preference authority.
- Flexible-shape, failure, privacy, accessibility, and anti-rigidity evidence,
  including safe baseline rendering when the preference service or browser
  storage is unavailable.

### Out of Scope

- Medical or disability diagnosis; inferred accessibility needs; assistive-
  technology detection; behavioral profiling; engagement-derived settings; or
  organization, guardian, marketing, billing, or legal-consent policy.
- A feature-local color palette, parallel theme map, raw color/spacing scale,
  reduced contrast, smaller controls, forced motion, content removal, hidden
  technical evidence, or any preference that weakens WCAG baselines.
- Font downloads, user-authored CSS, arbitrary scale values, browser extension
  behavior, operating-system settings, screen-reader configuration, or
  guaranteed conformance claims.
- AI-assistance and local notification preferences, which remain in SLI-0076.
- Cross-device theme synchronization, theme meaning in headless clients,
  organization tenancy, managed-cloud recovery, or provider/model behavior.
- Adaptive eligibility, recommendation, assessment, competency, mastery,
  permission, grading, financial suitability, or irreversible action.

## Canonical Context and Decisions

- [CAP-0018](../capabilities/CAP-0018-set-learning-goals-and-preferences.md)
  defines the approved four-slice package and requires safe, explicit,
  reversible preferences.
- [SLI-0074](SLI-0074-record-learning-goals-experience-interests.md) establishes
  the Learner-model preference ownership, protected API, exact replay, history,
  reset/export, privacy, and headless/browser parity patterns reused here.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) and
  the module map keep explicit learner preferences in Learner model while
  design-system behavior remains platform-owned.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md) supplies
  the current opaque local learner context; callers cannot select a learner.
- [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md)
  keeps one static React client using generated public API clients.
- [Learner Preferences Contract](../../architecture/contracts/learner-preferences-contract.md)
  prevents explicit preferences from becoming evidence, policy, permission,
  or inferred traits. The closed SLI-0074 v1 document is not widened.
- [Interface Design System](../../design/README.md),
  [Style Guide](../../design/style-guide.md), and
  [Interface Design Standards](../../standards/interface-design-standards.md)
  govern theme, semantic tokens, accessibility, responsive behavior, and
  synchronized shared-style changes.
- [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  keep primary settings and failures in clear learner terms while exact
  versions, revisions, times, and digests remain in `Technical record`.
- Decision readiness is sufficient inside the local learner and existing
  design-system boundaries. This slice reaches no identity, tenancy, provider,
  model-authority, recovery, licensing, or external-execution decision gate.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SLI-0075: safe display preferences and preview | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| SLI-0076: AI-assistance and local notification choices | yes | 2 | 1 | 2 | 1 | 2 | 2 | 2 | 12 |
| SLI-0077: complete preference qualification | no; SLI-0075 and SLI-0076 are incomplete | - | - | - | - | - | - | - | - |

## Selection Rationale

SLI-0075 is the highest-scoring eligible increment. It produces immediate
learner-visible value, reuses the complete SLI-0074 preference lifecycle, and
has closed authority boundaries: Learner model owns explicit portable reading
choices; the platform theme adapter owns only browser presentation. Its safe
defaults, device-precedence rules, and existing design-system verification make
the change observable and reversible without a durable decision.

SLI-0076 remains eligible but is not selected yet. Its preference controls are
valuable, but downstream AI and notification capabilities are intentionally
unavailable, so its first increment has less end-to-end observable effect and
requires more contract definition. SLI-0077 is dependency-ineligible until
both setting slices complete.

The refinement conforms to the current CAP-0018 outcome, manifest, order,
constraints, risk posture, and non-goals. It adds, removes, and redefines no
CAP slice, so no renewed CAP approval or slice approval exists.

## Boundary Path

1. The authorized learner opens `Display and accessibility`.
2. The browser establishes the current opaque learner session and reads one
   closed presentation-preference profile plus correlated bounded history
   through the generated public client.
3. The platform theme adapter reads only the allowlisted local value and falls
   back to `system` when storage is absent, malformed, or unavailable.
4. The learner changes a control. A preview adapter validates the complete
   draft and applies safe semantic root attributes without writing learner
   state; cancel or navigation restores accepted values.
5. Saving sends one closed mutation intent with exact revision and request
   identity. Learner model validates, applies, persists, and returns the full
   next profile. Exact retry returns the same accepted result; changed-key and
   stale-revision requests write nothing.
6. The accepted profile is applied globally through design-system tokens.
   Browser/OS zoom, forced colors, and reduced motion remain authoritative when
   they are more protective.
7. Theme changes apply immediately through the existing platform adapter and
   persist only in this browser. The UI states this distinction and never sends
   theme as learner evidence or API authority.
8. Reset creates a new learner-preference revision containing safe defaults;
   returning theme to `system` is a separate local action so a partial cross-
   authority failure cannot be mistaken for an atomic reset.
9. Browser and ordinary headless clients can read, mutate, inspect history,
   reset, and export the same learner-owned presentation profile. Headless
   clients receive no theme semantics because theme changes only rendering.

## Contracts, Data, and Provenance

The additive `learner-presentation-preferences/v1` contract has closed profile,
mutation-intent, history, and export documents. The profile contains one
server-owned profile ID, opaque learner ID, positive revision, `text_size`,
`text_spacing`, `reading_width`, `motion`, canonical creation/update times, and
a canonical SHA-256 digest. Initial allowlists are:

- `text_size`: `default` or `larger`;
- `text_spacing`: `default` or `increased`;
- `reading_width`: `standard` or `focused`; and
- `motion`: `system` or `reduce`.

These names express presentation choices, not disability, medical, assessment,
competency, or inferred-trait facts. `default` means the accepted accessible
design-system baseline; it does not undo browser/OS protections. `system`
motion follows the device signal, while `reduce` can only remove additional
motion. Exact token values and root-attribute behavior belong to the shared
design system and must be synchronized with its docs, executable tokens,
consumers, and tests.

Mutation intents carry one idempotency key, expected revision, and a complete
replacement of the four allowlisted choices or one reset operation. They carry
no learner, permission, time, profile ID, digest, medical label, CSS, token,
provider, model, evidence, recommendation, or policy field. History is bounded
and non-content: resulting revision, operation, time, and digest only. Export
binds the exact current learner-owned profile and history to purpose and
limitations. Empty storage projects stable safe defaults without a read-side
write.

Theme uses the existing closed local `system|light|dark` adapter and storage
key. It is visibly labeled as local to this browser, excluded from the Learner-
model contract and history, and reset to `system` when malformed or explicitly
requested. Browser-local values cannot select content, learner, permission,
policy, evidence, or an API result.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Safe first open | A new learner sees accepted baseline choices without a read-side database write; device theme and motion behavior remain in effect | domain/application/PostgreSQL/browser |
| Immediate preview | Changing each reading control updates the labeled preview before save, preserves all content/actions, and cancel/navigation restores accepted values | component/Chromium |
| Theme distinction | System, light, and dark apply immediately with equivalent content and the page explains that theme is stored in this browser | theme unit/component/Chromium |
| Accepted save | One exact mutation advances one revision and the result applies across routes through semantic attributes and tokens | contract/API/generated client/browser |
| Headless parity | An ordinary authenticated non-browser client observes and changes the same learner-owned profile, history, reset, and export meaning without UI imports | public HTTP/PostgreSQL |
| Exact retry and conflict | Exact replay converges; changed-key reuse and stale revision return bounded confidential denials and write nothing | application/PostgreSQL/API |
| Safe reset | Reset creates one new learner profile revision with baseline values; local `Use device theme` remains a separate reversible action | domain/API/browser |
| Protective precedence | Forced colors, 200-percent zoom, text scaling, device reduced motion, and keyboard focus still work with every saved setting | Chromium/design |
| Unavailable preference service | Existing learning routes retain safe baseline rendering; the settings page explains what was not loaded and leaves the local theme control usable | component/Chromium |
| Invalid local theme | Unknown or inaccessible browser storage falls back to system without blocking content, focus, or learner-owned settings | unit/component |
| Closed input | Unknown fields/values, arbitrary scales/CSS, learner selectors, medical labels, policy/evidence fields, malformed times/digests, and incomplete orders fail closed | schema/domain/API |
| Privacy and isolation | Display choices never appear as Assessment evidence, competency, Adaptation eligibility, permission, recommendation, financial meaning, or another module's storage mutation | architecture/security/integration |
| Flexible valid shapes | All valid combinations, default values, additional history entries, generated IDs/times, and varied page content remain usable without fixture-count or exact-copy assumptions | contract/component/live anti-rigidity |
| Theme parity and reflow | Light, dark, and system modes preserve the same information/actions at narrow width, increased spacing, larger text, focused width, forced colors, and reduced motion | Chromium/axe/design |
| Restart and cleanup | Accepted learner-owned choices survive a normal host restart; qualification removes only its isolated topology and artifacts | PostgreSQL/live runner |

## Agent Work Packets

Packet IDs are reserved and authored one at a time immediately before the
packet starts. Proposed dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0153 | Freeze learner presentation-preference contracts, safe value semantics, platform-theme boundary, compatibility vectors, pure core, and design-system application rules | none | none | complete |
| WRK-0154 | Compose Learner-model application, PostgreSQL persistence/migrations, protected API, reviewed OpenAPI, and generated client | WRK-0153 | none | complete |
| WRK-0155 | Deliver global presentation application plus the plain-language display/settings preview and existing local theme control | WRK-0154 | none | complete |
| WRK-0157 | Close the shared learner and presentation exact-replay split-read race window | WRK-0155 | none | verifying |
| WRK-0156 | Qualify contracts, browser/headless parity, restart, accessibility/device precedence, privacy, isolation, anti-rigidity, and cleanup | WRK-0155, WRK-0157 | none | ready |

Detailed packet plans will declare exact files, generated artifacts, checks,
and stop conditions immediately before each packet starts. Packet identifiers
are not consumed early, and no lower-level approval is requested.

## Verification and Qualification

Run JSON Schema/compatibility and pure domain tests; application/repository/API
suites; real-PostgreSQL migration, atomicity, replay, conflict, reset, restart,
and isolation evidence; reviewed OpenAPI and generated-client reproduction;
theme/presentation adapter unit tests; settings model/component tests; focused
mocked and isolated live Chromium; and one ordinary headless public-API journey.

Verify both themes and system mode; every valid preference combination; safe
fallback; keyboard/focus; axe; responsive reflow; 200-percent zoom and text
scaling; forced colors; device and explicit reduced motion; no content/action
loss; OS/browser precedence; unavailable/malformed states; and flexible
records/copy. Test that cosmetic differences and advisory language signals do
not reopen functional delivery.

Run architecture/import, module/persistence ownership, security/privacy,
learner-language, design-system, documentation, planning, dependency, Python,
TypeScript, zero-warning lint, build, exact-candidate affected verification,
independent technical review, deterministic completion structure, and
`python dev-tools/agent/check_ready.py`. The final live runner owns disposable
PostgreSQL, production Python API, static browser build, exact cleanup, and
source-state noninterference.

## Rollback and Migration

The new learner-owned contract and database objects are additive and versioned.
Migrations require forward, reapply, retained-data down refusal, and development
down evidence. Empty reads remain side-effect free. A code rollback can remove
an unreferenced endpoint and UI but cannot silently reinterpret or discard
stored learner choices.

Presentation attributes default to no override when absent or invalid. Removing
an optional application adapter returns rendering to the accepted design-system
baseline. Theme rollback removes no learner data and returns the local browser
setting to `system`; it does not rewrite the learner-owned profile.

## Stop Conditions

Stop for inferred or medical traits; assistive-technology detection; arbitrary
CSS or scale values; smaller text/targets; reduced contrast; forced animation;
hidden content/actions/evidence; feature-local theme maps or tokens; a mockup
treated as authority; browser state used as API/domain authority; preferences
used as Assessment evidence, competency, mastery, eligibility, permission,
grading, recommendation, financial suitability, or irreversible action;
cross-module storage access; a breaking contract change; destructive migration;
identity/tenancy/managed-cloud expansion; provider/model/network/credential use;
external notification or execution; stale CAP approval; active write collision;
or material CAP-0018 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count/order, or an advisory readability
signal. Fix bounded inconsequential issues locally or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will document the new learner-owned presentation contract, safe value
meaning, local theme boundary, precedence and fallback rules, purpose/privacy
limitations, design-system application, protected API/headless access,
accessible preview/settings flow, reset/export behavior, and exact qualification
evidence. Completion records exact candidates and receipts, affected boundaries,
checks/results, privacy and anti-rigidity results, assumptions, unsupported
profiles, and residual gaps without tracked approval or reviewer metadata.

## Planning History

- 2026-10-17: Selected after SLI-0074 completed. SLI-0075 scored 14/14;
  SLI-0076 scored 12/14 because its downstream consumers are not yet delivered;
  SLI-0077 remains dependency-ineligible. The refinement preserves the approved
  CAP-0018 manifest and needs no slice-level approval.
- 2026-10-17: Authored WRK-0153 just in time to freeze the additive
  learner-owned presentation-preference contract and pure core before any
  persistence, API, browser, or runtime-presentation work starts.
- 2026-10-17: Completed WRK-0153 with the closed four-choice contract family,
  deterministic replacement and reset core, bounded history/export,
  compatibility vectors, privacy and theme separation, safe-value denials,
  and 79 focused contract/domain checks. Persistence, public API, runtime
  application, and browser behavior remain later packet boundaries.
- 2026-10-17: Authored WRK-0154 just in time for module-owned persistence,
  protected public API, OpenAPI, and generated-client delivery using the
  completed WRK-0153 contract without starting runtime or browser behavior.
- 2026-10-17: Completed WRK-0154 with atomic learner-owned persistence, four
  protected browser/headless API operations, reviewed generated client parity,
  coherent profile-and-history snapshots, reset/replay/concurrency coverage,
  safe export, theme exclusion, and additive migration evidence. Runtime
  presentation and browser controls remain in the next dependency-ordered
  packet.
- 2026-10-17: Authored WRK-0155 just in time for the global safe presentation
  adapter and the plain-language display/settings browser flow using WRK-0154's
  completed public API and generated client. Final production-host, restart,
  and complete live profile qualification remain in JIT-D.
- 2026-10-17: Activated WRK-0155 after deterministic validation and a
  collision-free claim on the current CAP branch.
- 2026-10-17: WRK-0155 entered verification after the generated-client browser
  flow, global presentation adapter, shared token effects, and focused evidence
  were implemented on one exact candidate.
- 2026-10-17: Returned WRK-0155 to active delivery for bounded mutation-result,
  startup-read, and affected-check corrections. The correction adds no durable
  decision or product scope beyond the approved display-preference outcome.
- 2026-10-17: WRK-0155 re-entered verification after exact save/reset result
  correlation, route-authoritative startup supersession, and affected Chromium
  selection were added with focused regression coverage.
- 2026-10-17: Returned WRK-0155 to active delivery to isolate the required
  presentation-preferences Chromium check from unrelated screenshot and Project
  suites. Existing suites remain unchanged and independently selectable.
- 2026-10-17: WRK-0155 re-entered verification with a dedicated authenticated
  focused Chromium wrapper and precise affected-path selection; existing lesson,
  Project, and live suites retain their independent routes.
- 2026-10-17: WRK-0155 returned to active delivery to retain the documented
  Project browser self-qualification route and make its presentation-profile
  and saved-learning query dependencies deterministic without widening the
  product outcome.
- 2026-10-17: WRK-0155 re-entered verification with the Project check's
  documented self-qualification routes restored and both focused Chromium
  boundaries passing.
- 2026-10-17: Completed WRK-0155 with the public-client display route, global
  validated presentation application, separate local theme, exact save/reset
  correlation, deterministic focused browser boundaries, and aggregate
  readiness evidence. Live production-host and restart qualification remains.
- 2026-10-17: Authored WRK-0156 just in time as the final live qualification
  seam for browser/headless parity, all valid profiles, PostgreSQL restart,
  protective browser behavior, privacy/isolation, and exact cleanup.
- 2026-10-17: Marked WRK-0156 ready after deterministic packet, dependency,
  contract, decision, write-scope, and planning validation.
- 2026-10-17: Activated WRK-0156 from the current CAP branch after a
  collision-free bounded claim.
- 2026-10-17: Moved SLI-0075 and WRK-0156 to verification after the complete
  live browser/headless/PostgreSQL workflow passed all 16 profiles, safe race
  serialization, restart durability, source-state isolation, theme exclusion,
  protective browser behavior, accessibility, and bounded cleanup; focused and
  broader repository checks also passed with no product or contract change.
- 2026-10-17: Returned the slice and unchanged WRK-0156 projection to ready so
  the legacy compatibility claim can be replaced by a controller-native claim
  that supports exact-candidate receipts. Passing implementation evidence and
  scope remain unchanged.
- 2026-10-17: Re-activated the unchanged slice through the lease-aware
  controller so WRK-0156 can bind exact-candidate verification and independent
  review evidence to its current claim.
- 2026-10-17: Returned SLI-0075 to verification after its live evidence now
  proves exact replay-revision coverage, history-digest binding, unique valid
  keys, and the captured accepted replay in addition to the previously passing
  browser, headless, restart, privacy, accessibility, and cleanup paths.
- 2026-10-17: Returned the slice to active delivery after repeated live
  schedules exposed a shared exact-replay split-read window. WRK-0157 is the
  bounded application correction; WRK-0156 resumes only after it completes.
- 2026-10-17: WRK-0157 entered verification after refreshing committed replay
  before stale classification closed the shared split-read window in focused,
  real-PostgreSQL, and complete live browser/headless evidence.
