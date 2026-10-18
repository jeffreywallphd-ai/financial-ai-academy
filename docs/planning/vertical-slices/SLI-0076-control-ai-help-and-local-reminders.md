---
id: SLI-0076
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: CAP-0018
depends_on: [SLI-0074]
decision_gates: []
---

# Vertical Slice: Control AI Help and Local Reminders

## Outcome and User Scenario

An authorized learner can choose whether future AI help should be available
only when they deliberately ask for it, keep that assistance off, and inspect,
change, reset, or download the choice through the same protected public API
used by browser and headless clients. The learner can separately record a
browser-only preference for future in-app learning reminders and can see that
reminders are not available yet. Neither choice invokes a model, admits a
provider, grants data permission, schedules work, or sends a notification.

## Scope Boundaries

### In Scope

- A separate Learner-model-owned, additive
  `learner-assistance-preferences/v1` family for one explicit `off` or
  `on_request` choice with stable identity, revision, canonical time and
  digest, bounded non-content history, reset, and portable export.
- Conservative `off` defaults. `on_request` means only that a later governed
  feature may offer an AI-help action that the learner must start each time;
  it is not a provider selection, model enablement, data-transfer permission,
  standing instruction, background action, or guarantee that help is
  available.
- One protected Learner-model public API and reviewed generated client for the
  AI-help profile, mutation, history, reset, and export. Browser and supported
  headless clients use the same learner context and contract.
- A platform-owned, versioned browser-local setting with closed `off` and
  `in_app_when_available` values, an `off` default, bounded local change
  summaries, reset, and a clearly separate local download.
- A plain-language `AI help and reminders` route that explains purpose,
  storage, current availability, downstream use, and the distinction between
  learner-owned portable settings and this-browser-only settings.
- Unavailable, malformed, denied, stale, conflict, and storage-failure states
  that preserve ordinary learning, fall back to `off`, and never claim a model
  call or notification occurred.
- Failure, privacy, accessibility, API/headless parity, and anti-rigidity
  evidence appropriate to both ownership boundaries.

### Out of Scope

- Model or provider admission, credentials, provider choice, prompt or tool
  execution, grounding, content generation, recommendation, tutoring,
  autonomous action, data egress, data-class permission, cost policy, or
  external model calls.
- Browser or operating-system notification permission prompts; email, SMS,
  mobile push, web push, service workers, background synchronization, queues,
  schedules, reminder generation, external delivery, or proof of delivery.
- Marketing consent, experiment consent, organization or guardian policy,
  billing, enterprise identity, tenancy, or managed-cloud configuration.
- Inferred assistance need, engagement profiling, hidden personalization, or
  use of either preference as Assessment evidence, competency, mastery,
  eligibility, authorization, grading, financial suitability, or an
  irreversible instruction.
- A second browser-owned copy of the learner AI-help profile, a headless
  meaning for the local reminder setting, or direct access to Learner-model
  persistence.

## Canonical Context and Decisions

- [CAP-0018](../capabilities/CAP-0018-set-learning-goals-and-preferences.md)
  defines the approved four-slice package and enumerates this increment.
- [SLI-0074](SLI-0074-record-learning-goals-experience-interests.md)
  establishes Learner-model preference ownership, protected public API,
  replay, bounded history, reset/export, privacy, and browser/headless parity.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  keeps explicit learner choices in Learner model while platform presentation
  and local-browser settings remain outside that module.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md)
  supplies the opaque current learner context; a caller cannot select a
  learner through the preference API.
- [ADR-0013](../../adr/ADR-0013-explicit-model-provider-opt-in.md) requires
  explicit provider admission, selection, and data-class permission and keeps
  every provider disabled by default. A learner preference cannot satisfy any
  of those gates.
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
  keep model output advisory and prohibit provider-specific payloads or direct
  SDK use outside admitted adapters. This slice performs no inference.
- [Learner Preferences Contract](../../architecture/contracts/learner-preferences-contract.md)
  prevents explicit preferences from becoming evidence, permission, inferred
  traits, or policy. The existing closed v1 document is not widened.
- [Interface Design System](../../design/README.md),
  [Interface Design Standards](../../standards/interface-design-standards.md),
  and [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  require clear learner language, accessible interaction, equivalent themes,
  and available exact technical records without leading with raw enums.
- Decision readiness is sufficient inside the existing local learner,
  provider-disabled, and browser-local boundaries. The slice reaches no
  identity, tenancy, provider, licensing, queue, external-execution, recovery,
  or commercial decision gate.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SLI-0076: AI-help and local-reminder choices with unavailable disclosure | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| AI-help contract and API only | no; omits the approved learner-visible and local-reminder outcome | - | - | - | - | - | - | - | - |
| Local-reminder control only | no; omits the portable AI-help preference and headless contract | - | - | - | - | - | - | - | - |
| SLI-0077: qualify the complete CAP | no; depends on SLI-0076 completion | - | - | - | - | - | - | - | - |

## Selection Rationale

SLI-0076 is the only eligible next manifest increment and scores two on every
criterion. It gives the learner observable control and honest availability
information; crosses contract, application, persistence, API, generated
client, browser, and local-adapter boundaries without implementing AI or
notification delivery; operates entirely inside accepted decisions; has two
closed and separately owned contracts; depends only on completed SLI-0074;
has independently observable API, browser, local-storage, privacy, and failure
evidence; and is reversible through explicit reset and conservative fallback.

An API-only cut would leave the approved learner scenario and local choice
undelivered. A local-only cut would omit the portable learner-owned choice and
headless boundary. Combining execution or delivery with these controls would
cross unresolved provider, permission, queue, and external-action gates, so
execution remains deliberately excluded rather than treated as incomplete
work. SLI-0077 remains dependency-ineligible until this slice closes.

The refinement preserves the current CAP-0018 outcome, manifest, sequence,
constraints, risks, and non-goals. It adds, removes, and redefines no CAP slice,
so no renewed CAP approval or slice approval exists.

## Boundary Path

1. The authorized learner opens `AI help and reminders`.
2. The browser establishes the current opaque learner session and reads the
   closed AI-help profile plus correlated bounded history through the generated
   public client.
3. The platform local-settings adapter reads one versioned reminder envelope
   from this browser. Absent, malformed, unknown, or inaccessible storage
   projects `off` without blocking the learner-owned API or ordinary learning.
4. The page explains that AI help is off or may be offered only after a future
   feature admits a provider and the learner deliberately asks. It explains
   that reminders are not available and that the local choice sends nothing.
5. Saving the AI-help choice sends one closed mutation intent with exact
   revision and request identity. Learner model validates, applies, persists,
   and returns the complete next profile. Exact retry converges; changed-key
   reuse and stale revision write nothing.
6. Saving the reminder choice replaces one complete local envelope containing
   its current value, next revision, bounded non-content summaries, time, and
   integrity code. It makes no network request and registers no worker,
   permission, timer, service worker, or external subscription.
7. Resetting AI help creates one new learner-profile revision with `off`.
   Resetting reminders separately returns this browser to `off`; a partial
   cross-authority failure cannot be presented as one atomic reset.
8. Browser and ordinary headless clients can read, mutate, inspect history,
   reset, and export the same AI-help profile. Headless clients receive no
   reminder semantics because that setting belongs only to the current
   browser.

## Contracts, Data, and Provenance

The additive `learner-assistance-preferences/v1` family contains closed
profile, mutation-intent, history, and export documents. The profile contains
one server-owned profile ID, opaque learner ID, positive revision,
`assistance_mode`, canonical creation and update times, and canonical SHA-256
digest. The only v1 values are `off` and `on_request`. An absent stored profile
projects a deterministic revision-one `off` value without a read-side write.

Mutation intents carry one idempotency key, exact expected revision, and a
complete replacement or reset operation. They cannot carry learner, provider,
model, credential, prompt, content, tool, destination, data class, permission,
time, profile ID, digest, policy, evidence, recommendation, or notification
fields. Bounded non-content history contains resulting revision, operation,
time, and digest. Export binds the exact current profile and history to a clear
purpose and limitations; it is not provider consent, execution authority, or
proof that AI help exists.

The browser-local `local-learning-reminder-preference-v1` envelope contains no
learner identity or server authority. It contains its schema version, positive
revision, `off` or `in_app_when_available`, canonical local update time,
bounded non-content change summaries, and integrity code. A single adapter
owns its allowlisted storage key, validation, replacement, reset, export, and
safe fallback. Its download is visibly separate from the learner-owned export.
It never enters the API, learner profile, Assessment evidence, server logs, or
headless contract. The `in_app_when_available` value records only future local
intent; it creates no delivery claim or obligation.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Safe first open | A new learner sees AI help off and local reminders off without a read-side database or local-storage write | domain/application/PostgreSQL/browser |
| Accepted AI-help save | One `on_request` or `off` mutation advances exactly one server revision and is visible through browser and ordinary headless clients | contract/API/generated client/PostgreSQL |
| No implied authority | Selecting `on_request` does not enable a provider, grant data permission, call a model, create output, or alter eligibility, grading, or learning state | architecture/security/integration |
| Exact retry and conflict | Exact replay converges; changed-key reuse and stale revision return bounded confidential denials and write nothing | application/PostgreSQL/API |
| Local future intent | Selecting future in-app reminders updates only one validated browser envelope while the page still says no reminder will be sent today | local-adapter/component/Chromium |
| No notification side effect | The complete flow creates no permission prompt, service worker, timer, queue, subscription, email, push, SMS, or network notification request | unit/Chromium/network isolation |
| Separate reset | AI reset creates one server revision with `off`; reminder reset independently returns this browser to `off` | domain/API/local-adapter/browser |
| Separate downloads | The AI-help download contains the exact portable profile and bounded history; the local download contains no learner identity and is clearly browser-specific | contract/component/Chromium |
| Unavailable learner service | Ordinary learning and the local control remain usable; the page explains that the saved AI choice could not be loaded and applies no assistance authority | component/Chromium |
| Invalid local storage | Unknown values, versions, fields, history, or integrity codes fall back to `off` without blocking the page or overwriting evidence on read | unit/component |
| Closed input | Unknown fields and values, learner selectors, provider/model/data permission, execution, destination, policy, evidence, and notification-delivery fields fail closed | schema/domain/API/local-adapter |
| Privacy and isolation | Neither choice appears as Assessment evidence, competency, Adaptation eligibility, permission, grading, financial meaning, or another module's direct storage mutation | architecture/security/integration |
| Flexible valid shapes | Both valid AI choices, both valid local choices, zero through 100 summaries, generated IDs/times, and varied surrounding content remain usable without fixture-count or exact-copy assumptions | contract/component/live anti-rigidity |
| Accessible parity | Purpose, availability, forms, errors, reset, downloads, and technical records preserve equivalent content and actions with keyboard, focus, reflow, zoom, forced colors, reduced motion, and all themes | component/Chromium/design |
| Restart and cleanup | The learner-owned choice survives normal host restart; the browser-local choice survives a page reload in that browser; qualification removes only isolated topology and artifacts | PostgreSQL/Chromium/live runner |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The proposed dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0158 | Freeze AI-help preference contracts, closed semantics, local-reminder envelope and adapter rules, privacy limits, compatibility vectors, and pure core | none | none | complete |
| WRK-0159 | Compose Learner-model application, PostgreSQL persistence and migration, protected API, reviewed OpenAPI, and generated client | WRK-0158 | none | complete |
| WRK-0160 | Deliver the plain-language AI-help and reminders route through the generated client and browser-local adapter | WRK-0159 | none | ready |
| Reserved just in time | Qualify contracts, browser/headless parity, restart, unavailable behavior, privacy, accessibility, containment, anti-rigidity, and cleanup | browser packet | none | planned |

Detailed packet plans declare exact files, generated artifacts, checks, and
stop conditions immediately before each packet starts. Packet identifiers are
not consumed early, and no lower-level approval is requested.

## Verification and Qualification

Run JSON Schema and compatibility tests; pure domain tests; application,
repository, migration, API, and generated-client suites; local-setting adapter
unit and corruption tests; focused component and Chromium tests; and one
isolated live browser plus ordinary headless public-API journey.

Verify both closed values at each boundary; absent, malformed, denied,
unavailable, stale, and conflicting states; exact replay; newest-100 history;
reset/export; safe first read; restart and reload; no provider/model/network
execution; no notification permission, worker, timer, queue, or delivery; no
cross-authority atomicity claim; and no unrelated state change. Verify light,
dark, and device themes; keyboard and focus; narrow reflow; scaled text; forced
colors; and reduced motion. Prefer structural roles, actions, purpose, and
required meaning over frozen whole-copy assertions.

Run architecture/import, module and persistence ownership, security/privacy,
learner-language, design-system, documentation, planning, dependency, Python,
TypeScript, zero-warning lint, build, exact-candidate affected verification,
independent technical review, deterministic completion structure, and
`python dev-tools/agent/check_ready.py`. The live runner owns disposable
PostgreSQL, production API, static browser build, isolated browser state,
exact cleanup, and source-state noninterference.

## Rollback and Migration

The learner-owned contract and PostgreSQL objects are additive and versioned.
Migrations require forward, reapply, retained-data down-refusal, and
development-down evidence. Empty reads remain side-effect free. A code
rollback can remove an unreferenced endpoint and route but cannot silently
reinterpret or discard retained choices.

The local adapter defaults to `off` when absent or invalid. Its reset removes
or replaces only its allowlisted envelope and leaves learner-owned state,
theme, content, sessions, permissions, and other browser storage untouched.
No rollback requires contacting a provider, revoking external delivery, or
undoing model output because the slice creates none.

## Stop Conditions

Stop for any provider/model enablement; credentials; data-class permission;
prompt, tool, or model execution; background or autonomous action; notification
permission prompt or external delivery; queue, schedule, service worker, or
timer; provider consent, marketing, experiment, organization, or guardian
policy; hidden or inferred profiling; a preference used as evidence,
authorization, eligibility, grading, recommendation, financial suitability,
or irreversible action; caller-selected learner identity; browser state used
as server authority; direct cross-module storage; breaking contract change;
destructive migration; identity, tenancy, managed-cloud, licensing, recovery,
or commercial expansion; stale CAP approval; active write collision; or
material CAP-0018 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count or order, or an advisory readability
signal. Fix bounded inconsequential issues locally or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will add the AI-help preference contract, Learner-model ownership and
API documentation, persistence and migration evidence, reviewed OpenAPI and
generated client, browser-local reminder contract and storage disclosure,
plain-language settings guidance, and focused privacy, security,
accessibility, containment, replay, restart, and anti-rigidity evidence.

Completion evidence must identify exact affected boundaries and checks,
confirm that the generated API remains suitable for browser and headless use,
show that the local reminder choice never enters that API, and explicitly
state that no AI or notification execution was implemented or implied.

## Planning History

- 2026-10-17: Refined the next approved manifest increment after SLI-0074 and
  SLI-0075 completed. Deterministic selection found SLI-0076 eligible at 14 of
  14 and SLI-0077 dependency-ineligible. The refinement preserves CAP-0018 and
  requires no slice-level approval.
