---
id: WRK-0155
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0075
capability: CAP-0018
depends_on: [WRK-0154]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/dependencies.ts", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/design-system/tokens.css", "apps/web/src/features/presentation-preferences/PresentationPreferencesPage.tsx", "apps/web/src/features/presentation-preferences/PresentationPreferencesRoute.tsx", "apps/web/src/features/presentation-preferences/api.ts", "apps/web/src/features/presentation-preferences/model.ts", "apps/web/src/platform/presentation/presentation.tsx", "apps/web/src/platform/theme/theme.tsx", "apps/web/src/styles/app.css", "apps/web/src/styles/base.css", "apps/web/src/styles/presentation-preferences.css", "apps/web/tests/browser/presentation-preferences/presentation-preferences.spec.ts", "apps/web/tests/component/presentationApplication.test.tsx", "apps/web/tests/component/presentationPreferences.test.tsx", "apps/web/tests/component/theme.test.tsx", "apps/web/tests/unit/presentationPreferencesModel.test.ts", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "dev-tools/design/check_design_system.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/learner-presentation-preferences-contract.md", "docs/design/style-guide.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0075-set-accessible-display-preferences.md", "docs/planning/work-packets/WRK-0155-deliver-display-accessibility-browser-flow.md"]
generated_artifacts: []
base_revision: b2da74b396eeeb6d465f2ab65083565d0d36e094
claim_id: WRK-0155:fc065afe-0bde-4886-8c5f-05fba9ca4e97
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T21:56:49Z
---

# Agent Work Packet: Deliver the Display and Accessibility Browser Flow

## Objective and Deliverable

Deliver one plain-language `Display and accessibility` browser route that uses
the completed public presentation-preference API, lets an authorized learner
preview, save, cancel, reset, inspect, and export the four closed learner-owned
display choices, and keeps the existing local theme choice clearly separate.
Apply only complete validated presentation profiles across every route through
safe semantic root attributes and shared design-system tokens. Missing,
malformed, or unavailable learner settings must leave the whole application at
its accepted accessible baseline while the local theme control remains usable.

The observable result is one keyboard- and assistive-technology-usable settings
flow plus global browser presentation behavior. This packet does not perform
the final production-host, restart, real-PostgreSQL, or complete supported-
profile qualification owned by the dependent qualification packet.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the baseline,
`delivery-planning`, `interface-design`, and focused `testing-quality` context
packs. Revalidate CAP-0018, SLI-0075, WRK-0153, WRK-0154, ADR-0005, ADR-0006,
ADR-0009, decision readiness, the learner-presentation-preference architecture
and executable v1/API contracts, generated client operations, shared design
system and tokens, content/language standards, concurrent-work protocol, and
the Web and design-system READMEs.

Inspect the current application shell, router composition, single-profile
session, theme provider/control, learner-preference feature patterns, generated
client operation types, root and feature styles, component/browser tests, and
affected architecture/design/documentation checks before editing. Canonical
sources outrank this packet; stop on any conflict.

## Decisions and Assumptions

- Learner model remains the only authority for `text_size`, `text_spacing`,
  `reading_width`, and `motion`; the browser consumes the reviewed generated
  public client and does not recreate domain policy.
- Browser theme remains the existing platform-owned
  `system|light|dark` local-storage choice. It is not added to the learner
  profile, mutation, history, export, or headless contract.
- Runtime presentation uses only the complete closed values from WRK-0153 and
  applies them as `data-text-size`, `data-text-spacing`,
  `data-reading-width`, and `data-motion` on the document root. Feature code
  cannot accept CSS, arbitrary values, medical labels, or partial settings.
- Exact visual effects are expressed through shared `--faa-*` semantic tokens.
  Larger text, increased spacing, focused width, and reduced motion may make
  presentation more protective; they may not reduce existing text, target,
  contrast, content, or motion protections.
- Device/browser zoom, text scaling, forced colors, and reduced-motion signals
  retain precedence whenever they are more protective. Invalid or unavailable
  saved state removes no content and falls back to the accepted baseline.
- Draft preview is transient browser presentation. Save sends one complete
  replacement with exact revision and key; cancel or navigation restores the
  last accepted profile. Reset creates a server-owned safe-default revision.
  Returning local theme to `system` remains a separate local action.
- The settings route may share an application client/session composition seam
  with the router, but it must not add a second API contract, Node server,
  backend import, or hidden cache authority.

## In Scope

- Add generated-client adapters and closed browser validation for profile,
  history, mutation result, and export correlation without adding or changing
  the public API or generated files.
- Add one global presentation provider/adapter that applies only validated
  accepted profiles, exposes a bounded preview/restore seam, and returns to safe
  defaults on unavailable or invalid profile data.
- Add shared semantic token application for the four closed root attributes,
  including more-protective device reduced motion and no feature-local palette,
  spacing scale, theme map, shadow, radius, or icon.
- Add `/preferences/display` as `Display and accessibility`, with task-focused
  control labels, immediate preview, save, cancel, server reset, separate
  `Use device theme`, history/export actions, storage-purpose disclosure, and
  an accessible `Technical record` for exact profile identity, revision,
  version, time, and digest.
- Keep local theme usable when the learner-owned preference service is denied,
  unavailable, or invalid. Provide safe, focused recovery copy and never render
  private or malformed payload fields.
- Add stable navigation and skip-link wording for the new route without
  removing the existing learning-preference route.
- Add unit, component, and focused mocked-Chromium evidence for safe value
  mapping, all valid combinations, draft restore, reset separation, exact
  generated-client calls, stale/uncertain failure, malformed/unavailable
  fallback, technical-record reachability, keyboard/focus, axe, narrow reflow,
  200-percent text, both explicit themes plus system, forced colors, and
  reduced motion.
- Synchronize Web, design-system, architecture, slice, packet, register, and
  verification documentation for the delivered boundary.

## Out of Scope

- Backend, migration, executable contract, OpenAPI, generated-client, identity,
  permission, or headless semantic changes; WRK-0154 owns those completed seams.
- Final production Python host plus static build, real PostgreSQL restart,
  cross-route live browser journey, complete supported-profile matrix, or
  qualification cleanup; those remain in the dependent JIT-D packet.
- AI-assistance, notification, organization, guardian, marketing, billing,
  consent, tenancy, cloud recovery, provider, model, network, or external-
  execution preferences.
- Medical or disability diagnosis, inferred need, assistive-technology
  detection, behavioral profiling, automatic settings, arbitrary CSS, custom
  fonts/scales, smaller text/targets, reduced contrast, forced motion, hidden
  content/actions, or a new feature-local visual system.
- Adaptive policy, evidence, competency, mastery, eligibility, permission,
  grading, recommendation, financial suitability, or irreversible action.
- New dependency, icon, mockup, screenshot baseline, analytics, telemetry,
  deployment, publication, or remote operation.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Public API/client | reviewed OpenAPI and generated presentation operations | none | Consume the already-generated browser/headless contract without divergence |
| App composition | shell, router, main, shared session/client construction | listed app files and new `dependencies.ts` | Add one route and one global safe presentation boundary |
| Presentation platform | root attributes, theme adapter, token precedence | new presentation adapter, theme adapter, tokens, base/app CSS | Apply complete safe values globally while keeping theme local and separate |
| Feature UI | learner-preference patterns and new display route | listed presentation-preference feature and CSS files | Deliver preview/save/reset/export in clear learner language |
| Verification | current model, component, theme, and focused browser patterns | listed new/affected tests and design checker only if a new shared invariant needs executable coverage | Protect behavior, accessibility, privacy, and anti-rigidity without freezing prose |
| Documentation | Web, design, architecture, assurance, planning | listed Markdown files | Keep root-attribute, token, storage, and residual qualification meaning synchronized |

No file outside `write_scope` may change. Stop if implementation requires a
generated-client edit, backend/API change, new dependency, icon asset, contract
version, or broader shared-style decision than the exact four presentation
effects already authorized by SLI-0075.

## Contracts and Interfaces

Consume the generated operations for:

```text
GET  /api/v1/learner-presentation-preferences
POST /api/v1/learner-presentation-preferences/mutations
GET  /api/v1/learner-presentation-preferences/history
GET  /api/v1/learner-presentation-preferences/export
```

The browser adapter accepts only the frozen v1 profile, history, mutation, and
export fields. It independently verifies closed fields/values, UUID and bounded
identifier forms, canonical UTC times, digest and history correlation, complete
replacement/reset shape, and no extra private fields before presentation.

The platform presentation seam exposes behavior equivalent to:

```text
applyAcceptedPresentation(profile) -> root attributes
previewPresentation(completeDraft) -> root attributes
restoreAcceptedPresentation() -> root attributes
resetPresentationToBaseline() -> root attributes
```

Only `default|larger`, `default|increased`, `standard|focused`, and
`system|reduce` cross this seam. Theme continues to use only
`data-theme=system|light|dark` and local storage. The dependent qualification
packet receives a completed route, deterministic mocks/fixtures, stable root
attribute semantics, and focused browser test entry point; it receives no new
domain or external authority.

## Dependencies and Parallel Safety

WRK-0153 and WRK-0154 are complete and supply the closed contract, pure core,
persistence, public API, and generated client. WRK-0155 owns shared app
composition, theme, tokens, styles, browser feature, tests, and synchronized
documentation, so it is not parallel-safe with another SLI-0075 packet. JIT-D
depends on this exact delivered route and cannot start until WRK-0155 completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Safe global open | Valid saved settings exist | Any route opens | One complete validated profile applies through semantic root attributes without changing content or authority | unit/component/Chromium |
| Immediate preview and cancel | The settings route has an accepted profile | A learner changes any complete control set, then cancels or leaves | Preview updates immediately and the last accepted profile is restored without a write | component/Chromium |
| Accepted save and exact retry | A complete changed draft uses the current revision | Save succeeds or an uncertain unchanged form retries | One exact complete mutation is sent; the accepted profile is applied and an exact retry reuses the prepared request | unit/component |
| Safe reset separation | Learner settings and a local theme are both changed | The learner resets saved display choices | A new safe learner revision applies; theme stays unchanged until the separate `Use device theme` action | component/Chromium |
| Theme distinction | Any learner-owned display combination is active | System, light, or dark is selected | Equivalent content/actions remain and the page states that theme is stored only in this browser | theme/component/Chromium |
| Protective precedence | Larger text/spacing or reduced motion is saved | Browser zoom, forced colors, text scaling, or device reduced motion is more protective | No content/action is lost and the more-protective device behavior remains effective | Chromium/design |
| Service unavailable | Profile/history access is denied, unavailable, or invalid | Any route and the settings page render | Global presentation stays at baseline; the page explains what was not loaded; local theme remains usable | unit/component/Chromium |
| Stale or conflicting save | The server rejects the expected revision or key | A learner saves | No false success is shown; accepted presentation remains; recovery directs reload/review without exposing internals | unit/component |
| Closed response | A payload has an extra field, invalid value, malformed time/digest, or mismatched history | The browser validates it | No partial private data or unsafe attribute is applied | unit/component |
| Technical record and export | Valid correlated state is loaded | The learner opens details or downloads | Exact version, revision, times, digest, and validated export remain reachable without leading the primary task flow | component/Chromium |
| Anti-rigidity | Any of the 16 valid combinations, varied revisions/times/IDs, empty or longer bounded history, and varied surrounding content occur | The route and runtime adapter consume them | Behavior follows invariants rather than fixture count, exact prose, or one preferred combination | parameterized unit/component |
| Accessible reflow | Route is used by keyboard at narrow width, 200-percent text, forced colors, reduced motion, and every theme | Controls, preview, disclosure, save/reset, and navigation are exercised | Logical order, focus, labels, actions, contrast, reflow, and axe checks remain usable | Chromium/axe/design |

## Verification Commands

Run the focused browser model/component suite first:

```powershell
npm --prefix apps/web test -- apps/web/tests/unit/presentationPreferencesModel.test.ts apps/web/tests/component/presentationApplication.test.tsx apps/web/tests/component/presentationPreferences.test.tsx apps/web/tests/component/theme.test.tsx
npm --prefix apps/web run test:browser -- tests/browser/presentation-preferences/presentation-preferences.spec.ts
```

Then run TypeScript typecheck, zero-warning lint, static build, generated-client
currency/usage checks, design-system, learner-language, architecture, security,
planning, documentation, and whitespace checks. Run the exact-candidate affected
verification route, obtain one independent technical disposition, and run
`python dev-tools/agent/check_ready.py` before completion. Record as a residual
gap that final production-host, real-PostgreSQL restart, complete live browser
parity, and qualification cleanup remain JIT-D rather than fabricating that
evidence in this packet.

## Documentation and Evidence Update

Document the delivered route, plain-language actions, global root attributes,
shared token effects, preview/restore behavior, safe fallback, device
precedence, local theme boundary, API/client reuse, technical record, tests,
assumptions, and residual live qualification in the Web README, style guide,
learner-presentation architecture contract, architecture verification map,
SLI-0075, this packet, and the planning register. Update the design checker only
if necessary to lock a new shared executable invariant; do not create a broad
style or copy gate.

Keep exact verification receipts and technical dispositions in ignored local
control-plane storage. Never add approval/reviewer identity, decision, date,
authority reference, reviewed scope, or history to tracked artifacts.

## Stop Conditions

Stop for a canonical conflict; stale CAP package; active scope collision;
breaking or widened public contract; generated-client or backend change;
medical/inferred profiling; arbitrary CSS or scale input; smaller text/targets;
reduced contrast; forced animation; hidden content/actions; feature-local theme
or token map; browser storage used as learner/API authority; device protections
weakened; preferences used as evidence, competency, eligibility, permission,
recommendation, grading, financial meaning, or irreversible action; new
identity, tenancy, provider, model, network, credential, recovery, deployment,
dependency, external execution, or publication choice; or verification that
exposes an unresolved architecture decision.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count/order, advisory readability signals,
or another bounded inconsequential issue. Fix it locally when safe or defer
optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0075.WRK-0155`; exact candidate and receipt; route and
learner-facing actions; generated-client calls; accepted/draft/reset/theme
separation; root attributes and token effects; device precedence; invalid and
unavailable fallback; technical-record/export privacy; all valid combinations;
focused component/browser/accessibility/build/design/language/architecture/
security/aggregate checks; documentation impact; assumptions; and residual
JIT-D live qualification. Confirm no backend/API/generated-client, medical or
inferred trait, evidence/competency, adaptive policy, provider/model, external
action, or financial behavior changed.

## Planning History

- 2026-10-17: Authored just in time after WRK-0154 completed. The packet
  consumes its reviewed public contract and generated client, delivers the
  approved SLI-0075 runtime/browser boundary, leaves final live qualification
  to JIT-D, and requires no lower-level approval inside CAP-0018.
- 2026-10-17: Activated after deterministic validation and a collision-free
  claim on the current CAP-0018 branch.
- 2026-10-17: Entered verification with the public-client display route,
  complete accepted/draft/reset application seam, separate local theme,
  shared presentation tokens, and focused unit/component/Chromium evidence in
  place. Final live host and restart qualification remains in JIT-D.
- 2026-10-17: Returned to active delivery for bounded corrections to mutation-
  result correlation, startup-read supersession, and affected Chromium-check
  selection. The correction preserves the approved slice outcome and public
  contract while adding the exact control-plane browser wrapper, catalog, and
  test files needed to bind browser evidence to the submitted candidate.
