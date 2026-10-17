---
id: WRK-0149
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: [WRK-0148]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/learner-preferences/api.ts", "apps/web/src/features/learner-preferences/model.ts", "apps/web/src/features/learner-preferences/LearnerPreferencesPage.tsx", "apps/web/src/features/learner-preferences/LearnerPreferencesRoute.tsx", "apps/web/src/styles/learner-preferences.css", "apps/web/tests/component/learnerPreferences.test.tsx", "apps/web/tests/unit/browserBoundary.test.ts", "apps/web/tests/unit/learnerPreferencesModel.test.ts", "docs/architecture/assurance/architecture-verification.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0149-deliver-learning-preferences-browser-flow.md"]
generated_artifacts: []
base_revision: 3e01a37d267cce74cc6efe4d25e77ceb0445c5b3
claim_id: WRK-0149:f3afecc7-1214-44a4-b1c9-41b5a42f595d
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T19:03:51Z
---

# Agent Work Packet: Deliver the Learning Preferences Browser Flow

## Objective and Deliverable

Deliver an accessible, responsive `Learning preferences` route that lets the
authorized learner understand why preferences are stored; view, add, revise,
order, archive, restore, and remove learning goals, self-described experience,
and interests; review bounded change history; reset the profile; and download
the portable export. Use only the WRK-0148 generated public client and server
session. Keep exact identifiers, revisions, timestamps, and integrity values
available in a `Technical record` without leading the ordinary task flow with
implementation language.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`.
Revalidate CAP-0018, SLI-0074, WRK-0148, ADR-0005, the learner-preference
contract, identity and public API contracts, interface design system, content
style guide, user-facing language standard, generated-client conventions,
current router/session patterns, browser boundary, and nearest web README.
Inspect the affected route, shell, feature, style, client, and test consumers.

No unresolved identity, tenancy, provider, model-authority, data-license,
encryption, recovery, legal, commercial, or external-execution decision is
needed. Stop if the implementation would change one of those durable choices.

## Decisions and Assumptions

- The learner-visible route is `/preferences/learning`; primary navigation
  calls it `Learning preferences`.
- The generated client is the only backend seam. The browser neither imports
  backend internals nor stores an authoritative preference copy locally.
- React Router loader/action functions establish or renew the existing
  single-profile server session and map closed HTTP results into bounded route
  states without showing raw errors or learner identifiers.
- Each form submits one exact expected revision and a fresh UUID idempotency
  key. An uncertain transport result retains the exact prepared request for a
  safe retry; a changed form abandons that retry and uses a fresh key.
- Ordinary copy describes goals, experience, and interests as learner-stated
  choices. It never calls them competency, mastery, evidence, eligibility,
  recommendation, suitability, or inferred profile data.
- Existing semantic tokens and reviewed icons are sufficient. No shared visual
  decision, feature-local color system, dependency, or generated asset changes.

## In Scope

- Add strict browser model validation and route states for the current profile,
  bounded history, mutation results, and export returned by the generated
  client.
- Add loader, action, and export adapters with one unauthorized-session retry,
  abort propagation, exact form parsing, safe error mapping, prepared-request
  retry, and post-success route revalidation or redirect.
- Add a plain-language page for empty and populated profiles, purpose and scope
  disclosure, add/edit forms, archive/restore/remove controls, deterministic
  reordering controls, reset confirmation, history, portable download, and a
  keyboard-operable `Technical record` disclosure.
- Add route, primary navigation, skip-link labeling, style import, and bounded
  feature CSS using existing semantic variables.
- Prove accessible names, focus after failures, keyboard-operable native
  controls, narrow layout, theme-neutral semantic styling, optional detail,
  varied Unicode text/count/order, safe retry, stale/conflict/unavailable
  recovery, history/export integrity, and no raw implementation detail.
- Synchronize the web README, architecture evidence, parent slice, packet, and
  planning register.

## Out of Scope

Backend, migration, OpenAPI, generated-client, identity, permission, session,
or contract changes; accessibility/theme/AI/notification preference storage;
automatic or suggested goals; inferred traits; competency/evidence/mastery;
recommendation or adaptive policy; organization tenancy; provider/model calls;
external notifications; import, account erasure, or managed-cloud recovery;
file uploads or arbitrary URLs; financial advice/action; new dependencies;
pixel-perfect styling; visual regression baselines; and complete live browser,
restart, PostgreSQL-race, containment, or cleanup qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated API | Current generated types and operations | none | Consume the reviewed public seam directly |
| Feature model/API | Existing route-state and retry patterns | New learner-preferences model and adapter files | Validate responses and compose session-aware operations |
| Browser UI | Shell, router, shared components, icons | New page/route plus bounded shell/router wiring | Expose the complete learner task |
| Design system | Tokens, themes, icon pack, responsive rules | One feature stylesheet and one import | Use established semantic presentation only |
| Tests | Browser boundary and component/unit conventions | Focused model/component and boundary cases | Prove behavior without freezing incidental prose/style |
| Docs/planning | Web README, architecture evidence, SLI/register | Listed records only | Keep boundary and delivery evidence synchronized |

No path outside `write_scope` may change. Stop if a shared token, icon asset,
generated client, backend route, dependency, or unlisted architecture boundary
becomes necessary.

## Contracts and Interfaces

The feature consumes the four generated operations from WRK-0148:

```text
GET  /api/v1/learner-preferences
POST /api/v1/learner-preferences/mutations
GET  /api/v1/learner-preferences/history
GET  /api/v1/learner-preferences/export
```

Loader data contains only a fully validated current profile and correlated
history. Action data is a closed success redirect or a learner-safe failure
with the minimum exact prepared request required for idempotent retry. The
export adapter validates schema, profile revision/digest, and correlated
history before starting a local JSON download.

Form parsers accept only the exact fields required for one frozen mutation
operation. Server-owned learner identity, object IDs, time, next revision,
digest, replay result, and persistence facts never come from browser fields.

## Dependencies and Parallel Safety

WRK-0148 is complete and fixes the generated-client, permission, persistence,
and error seams. WRK-0149 owns shared shell/router and new feature/test/style
paths, is not parallel-safe with another SLI-0074 packet, and must complete
before final live qualification is reserved or authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty start | An authorized empty profile | The route opens | Purpose, limitations, empty sections, and clear add actions appear without claiming inferred knowledge | model/component |
| Record varied choices | Valid Unicode goals, optional details, experience, and interests | The learner submits each form | The generated mutation operation receives exact revision/key/operation data and the current route refreshes | model/component |
| Revise and order | A populated profile with varied counts | The learner edits, archives/restores/removes, or changes order | One bounded mutation is submitted and all valid orders remain usable | component/anti-rigidity |
| Safe retry | A mutation result is uncertain | The unchanged form is retried | The exact prepared request is reused; changed fields use a fresh key | unit/component |
| Stale/conflict | The server rejects an old revision or changed key | The response returns | Focus moves to a plain-language recovery notice and no stale result is rendered | component |
| History | Correlated bounded summaries exist | The learner reviews changes | Non-content summaries are understandable and private prior values are not invented | model/component |
| Reset | A non-empty profile exists | The learner confirms reset | The exact reset mutation is sent and the warning distinguishes preferences from learning evidence/work | component |
| Export | Profile and history pass integrity checks | The learner downloads | A versioned JSON file is created and exact technical facts remain accessible | unit/component |
| Unsafe response | A response is malformed, mismatched, or partial | The route or download processes it | The UI fails closed with a safe next action and shows no partial private data | unit/component |
| Access failure | Session or permission is unavailable | The route opens or mutates | The page explains what could not happen, protects private detail, and offers a safe next step | component |
| Accessible flexibility | Narrow, themed, keyboard, forced-color, reduced-motion, empty/populated, and varied-text cases | The feature renders | Equivalent content/actions remain reachable without count- or pixel-specific assumptions | component/design |
| Boundary | The feature source is inspected | Tests run | It imports the generated client and web seams only, with no backend, local-storage authority, provider, inference, or financial behavior | boundary/architecture |

## Verification Commands

Run focused learner-preference model and component tests; browser-boundary and
generated-client usage checks; TypeScript typecheck, zero-warning lint, and web
build; learner-language, design-system, architecture, security, planning,
documentation, Python compilation where selected, and whitespace checks;
controller-selected exact-candidate verification; an independent technical
disposition; and `python dev-tools/agent/check_ready.py`.

Do not require a pixel snapshot or block on optional styling/copy polish that
does not impair meaning, function, accessibility, responsive use, or theme
parity. Complete mocked/live Chromium, PostgreSQL race, restart, containment,
and cleanup evidence in the final dependency-ordered qualification packet.

## Documentation and Evidence Update

Record the route, generated-client-only boundary, learner-safe purpose and
limitations, supported actions, retry/revision behavior, history/export
validation, technical-record treatment, accessibility and anti-rigidity
evidence, focused/affected checks, assumptions, and final qualification gaps.
Keep approvals, technical-review records, and verification receipts only in
ignored local control-plane storage.

## Stop Conditions

Stop for a backend/contract/generated-client change; caller-selected learner
identity; preference data used as evidence, competency, mastery, eligibility,
permission, recommendation, suitability, or irreversible action; inferred or
hidden profiling; organization tenancy; provider/model/network/credential use;
external notification; breaking contract; private-data leakage; local browser
state becoming authority; new dependency; shared design-token/icon change;
active write collision; conflicting canonical sources; or material CAP/SLI
drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, fixture count/order, or another inconsequential issue.
Fix it within scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0074.WRK-0149`; exact candidate and qualifying receipt;
route/navigation, generated-client usage, mutations and safe retries,
history/reset/export behavior, learner-safe language, accessibility,
responsive/theme/forced-color behavior, anti-rigidity cases, focused/affected/
architecture/security/aggregate checks, documentation impact, assumptions,
and residual live-qualification gaps. Confirm no backend, contract, generated
client, identity, persistence, inferred trait, evidence/competency,
recommendation, provider, external action, or financial behavior changed.

## Completion Evidence

- Exact candidate `0706a0adede07b6f361e685e7f6d0b8caca24733` produced a fresh,
  stable qualifying receipt for the same candidate; all nine selected affected
  checks passed. The ignored local receipt retains the complete command log.
- The `/preferences/learning` route uses only the generated public client and
  server session for strict current-profile/history reads, exact bounded
  mutations, idempotent uncertain-result retry, stale-write recovery,
  integrity-checked export, and revalidation after accepted changes.
- Canonical profile digests, entry/profile chronology, monotonic bounded
  history, latest-result correlation, and export chronology fail closed.
  Irreversible removals require named confirmation, and duplicate valid
  learner wording retains position-specific accessible control names.
- The complete web suite passed 403 tests. Typecheck, zero-warning lint,
  static build, 17 architecture tests, 10 security control groups,
  learner-language, design-system, documentation, planning, whitespace, and
  the 29-part aggregate readiness gate passed.
- No backend, executable contract, OpenAPI, generated client, identity,
  persistence, inferred trait, learning evidence, competency, recommendation,
  provider, external action, or financial behavior changed in this packet.
- Live Chromium, simultaneous PostgreSQL races, normal restart, ordinary
  headless HTTP parity, containment, accessibility, and exact cleanup remain
  for the final dependency-ordered qualification packet.

## Planning History

- 2026-10-17: Authored just in time after WRK-0148 completed. The packet
  delivers the observable learner preference flow through the fixed generated
  public client, reuses repository route/session/design patterns, preserves
  API/headless authority, and requires no lower-level approval within the
  current CAP-0018 package.
- 2026-10-17: Activated from recorded base `3e01a37` after confirming the
  completed API dependency, exact browser-only scope, current design and
  language standards, resolved decision posture, and no active collision.
- 2026-10-17: Implemented the complete `/preferences/learning` browser flow
  through the generated public client, including strict response validation,
  exact mutation envelopes, safe prepared-request retry, stale-write recovery,
  bounded history, confirmed reset, integrity-checked export, accessible
  technical details, and responsive semantic-token presentation. Typecheck,
  zero-warning lint, the 403-test web suite, static build, architecture,
  learner-language, design-system, security, documentation, planning,
  whitespace, and the 29-part aggregate readiness gate passed. Live Chromium,
  simultaneous PostgreSQL races, restart, containment, and cleanup remain in
  the dependency-ordered final qualification packet.
- 2026-10-17: Hardened exact profile digest and chronology validation,
  irreversible item-removal confirmation, position-aware accessible control
  names, progressive revision disclosure, and unexpected-failure recovery
  guidance without widening the generated-client-only boundary. Focused,
  full-web, type, lint, build, architecture, security, language, design,
  documentation, planning, whitespace, and aggregate-readiness checks passed.
- 2026-10-17: Completed the generated-client browser flow at exact candidate
  `0706a0a` with all selected and aggregate checks passing. The dependency-
  ready next increment is the final qualification-only packet.
