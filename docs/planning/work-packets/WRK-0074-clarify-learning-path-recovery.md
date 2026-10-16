---
id: WRK-0074
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0123
capability: CAP-0030
depends_on: ["WRK-0073"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/features/curriculum-graph/CurriculumGraphRoute.tsx", "apps/web/tests/component/curriculumGraph.test.tsx", "apps/web/README.md", "docs/planning/work-packets/WRK-0074-clarify-learning-path-recovery.md", "docs/planning/vertical-slices/SLI-0123-understand-learning-path-state-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: aabdff6111e3cfba467d91cceaa403f8a2922101
claim_id: WRK-0074:7b4f1a96-7717-44d3-b548-e5f755474e8b
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:11:08Z
---

# Agent Work Packet: Clarify Learning Path Recovery

## Objective and Deliverable

Apply the accepted learner-facing language contract to the curriculum route's
loading and bounded failure states. A learner understands what could not be
shown and the existing safe next action without graph, navigation, projection,
session-establishment, server, or pipeline terminology in the primary message.
Every existing state selection, retry/return action, and fail-closed boundary
remains unchanged.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`,
`learning-adaptation`, and `testing-quality` packs. Read CAP-0030, SLI-0123,
WRK-0068, WRK-0073, the content and interface standards, the curriculum route,
state model/API boundary, shared `StatusPanel`, focused component tests, and
`apps/web/README.md` before editing.

## Decisions and Assumptions

- Route state selection, private-session establishment, authorization, exact-
  version resolution, all-or-nothing graph/state validation, and navigation are
  unchanged; only presented words and focused evidence change.
- `Try again` and `Return to learning library` remain the only actions already
  authorized by each state. No fallback, latest version, or partial result is
  introduced.
- Safe descriptions state that protected or incomplete details were not shown
  without exposing internal validation, transport, or private facts.
- Tests protect state-to-title/action meaning and prohibited primary jargon,
  not entire prose. Whitespace and nonfunctional styling do not trigger review.

## In Scope

- Learning-path loading eyebrow, heading, description, and accessible status.
- Plain titles, descriptions, and action labels for invalid selection,
  unauthorized, forbidden, not found, unavailable, invalid response, and
  unexpected states.
- Focused component assertions for every state, safe actions, hidden ready
  content, loading meaning, and absence of avoidable technical words inside the
  route-owned status region.
- Minimal web README and planning/evidence reconciliation.

## Out of Scope

- Ready-page presentation completed by WRK-0073; Chromium/live qualification
  and slice closure reserved for JIT-C.
- Route parsing, loader/API/model/generated-client/session/authorization/
  validation behavior; new actions or fallback data; CSS, tokens, icons,
  layouts, localization, persistence, or external services.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Runtime boundary | route state model, loader/API, session and validators | none | Confirm safe state selection remains unchanged |
| Route presentation | curriculum route and shared StatusPanel | named route only | Clarify loading, failure, and action language |
| Focused evidence | route component tests | named curriculum component test | Protect bounded states/actions without prose rigidity |
| Documentation/planning | web README, packet, parent slice, register | named files | Reconcile delivered recovery language and evidence |

## Contracts and Interfaces

The packet consumes the unchanged closed `CurriculumGraphRouteState` union and
existing `onRetry`/`onCatalog` callbacks. It produces no API, schema, model,
route, persistence, event, or generated-client change.

JIT-C receives stable learner-facing headings/actions for browser assertions
while the same state machine continues to suppress protected and partial data.

## Dependencies and Parallel Safety

WRK-0073 is complete. This packet serially establishes route-owned wording
consumed by JIT-C and is not declared parallel-safe with another SLI-0123
packet. Its exact file lease does not block unrelated work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Loading | The route is loading or revalidating | Status renders | It says the learning path is loading without session/server/graph/projection wording | Component test |
| Invalid link | The URL does not identify one exact supported version | State renders | It says the learning-path link cannot be used and returns to the learning library without requesting protected facts | Component test |
| Session/access | Session establishment fails or access is forbidden | State renders | It explains that the path cannot be shown, leaks no path facts, and offers only the existing permitted action | Component test |
| Missing version | The exact version is absent | State renders | It says that version could not be found and does not imply a latest-version fallback | Component test |
| Temporary problem | The complete current path/state pair is unavailable | State renders | It asks the learner to try again and does not show stale or partial facts | Component test |
| Invalid response | The complete response fails validation | State renders | It says the path could not be shown safely without internal projection/check terminology | Component test |
| Unexpected problem | The request fails unexpectedly | State renders | It provides the existing retry action and exposes no technical/private detail | Component test |

## Verification Commands

- `npm --prefix apps/web test -- --run apps/web/tests/component/curriculumGraph.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0074`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Full Chromium qualification is owned by JIT-C. Docker, backend, database,
generated-client, and live tests are not required unless affected routing
selects them.

## Documentation and Evidence Update

Update `apps/web/README.md` only where bounded route language is described.
Update this packet, SLI-0123, and the register together. Store approval/reviewer
records only in the ignored local ledger/control state.

## Stop Conditions

Stop for changed route-state selection, session, authorization, exact-version,
retry/return, fallback, validation, privacy, graph/state, or provenance
semantics; a new action; contract/model/API changes; unresolved canonical
conflict; CAP drift; or a colliding lease. Do not stop or reopen review for
whitespace, copy fit, or nonfunctional visual polish.

## Required Handoff

Report revised loading/recovery meaning, preserved state/action boundaries,
focused and affected verification, aggregate readiness, assumptions, Chromium
work left to JIT-C, and any cosmetic issue deferred to CAP-0031.

## Completion Evidence

- Delivered learner-focused loading and bounded messages for invalid links,
  learner access, denied access, missing versions, temporary unavailability,
  invalid complete responses, and unexpected failures.
- Preserved the closed state switch and action wiring: invalid-selection and
  not-found return to the learning library; unauthorized, unavailable, and
  unexpected retry; forbidden and invalid-response remain non-actionable. No
  alternate version, stale/partial result, protected fact, or new action exists.
- Focused component qualification passed all 12 curriculum scenarios. Coverage
  includes the loading status region, all seven state titles, hidden ready
  content, prohibited internal jargon in route-owned messages, and retry/return
  callbacks without freezing whole prose.
- TypeScript typecheck, lint, design-system, planning, documentation, Git
  whitespace, and all 27 aggregate readiness checks passed. Exact candidate
  `457a23b22592e1602468a8ad09b721fd23fd29ed` received a qualifying affected-
  verification receipt at `.local-codex/control-plane/receipts/WRK-0074/`
  `457a23b22592e1602468a8ad09b721fd23fd29ed/`
  `20261016T101316Z-920da86d-640e-4d27-bc04-8509732f4092.json`.
- Independent R01 accepted the candidate with no substantive findings. Public
  contracts, loaders, models, APIs, generated clients, sessions,
  authorization, validation, route selection, persistence, and migrations are
  unchanged. Chromium qualification remains assigned to JIT-C; no cosmetic
  issue blocked delivery or required re-review.

## Planning History

- 2026-10-16: Refined SLI-0123 JIT-B around route-owned loading and bounded
  recovery language, unchanged fail-closed behavior/actions, focused semantic
  evidence, and explicit exclusion of ready-page and visual-polish work.
- 2026-10-16: Prepared the completed route-language change for exact-candidate
  submission after focused component, typecheck, lint, design, planning,
  documentation, whitespace, and aggregate-readiness checks passed.
- 2026-10-16: Completed WRK-0074 on exact candidate
  `457a23b22592e1602468a8ad09b721fd23fd29ed` after affected verification
  qualified and independent R01 accepted with no substantive findings.
