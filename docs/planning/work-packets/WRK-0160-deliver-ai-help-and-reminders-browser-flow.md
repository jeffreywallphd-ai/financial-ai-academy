---
id: WRK-0160
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-18
parent: SLI-0076
capability: CAP-0018
depends_on: [WRK-0159]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/app/AppShell.tsx", "apps/web/src/app/main.tsx", "apps/web/src/app/router.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesPage.tsx", "apps/web/src/features/assistance-preferences/AssistancePreferencesRoute.tsx", "apps/web/src/features/assistance-preferences/api.ts", "apps/web/src/features/assistance-preferences/model.ts", "apps/web/src/styles/assistance-preferences.css", "apps/web/tests/browser/assistance-preferences/assistance-preferences.spec.ts", "apps/web/tests/component/assistancePreferences.test.tsx", "apps/web/tests/unit/assistancePreferencesModel.test.ts", "apps/web/tests/unit/browserBoundary.test.ts", "docs/architecture/contracts/learner-assistance-preferences-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0076-control-ai-help-and-local-reminders.md", "docs/planning/work-packets/WRK-0160-deliver-ai-help-and-reminders-browser-flow.md"]
generated_artifacts: []
base_revision: c702c8592392483f08fc7123b5006e2d0df18d2b
claim_id: WRK-0160:432added-1b15-4018-838c-4addf4632e52
claimed_by: codex-cap-0018
claimed_at: 2026-10-18T00:38:26Z
---

# Agent Work Packet: Deliver the AI Help and Reminders Browser Flow

## Objective and Deliverable

Deliver a plain-language `/preferences/assistance` browser route where an
authorized learner can inspect, save, reset, and separately download the
portable AI-help choice from the protected generated public client while also
controlling and separately downloading the browser-local future-reminder
choice. The route must remain useful when either ownership boundary is
unavailable, must make current non-availability unmistakable, and must not
enable a model, grant data permission, schedule work, request notification
permission, send a reminder, or create a browser-only copy of learner-owned
state.

## Required Context

Before any file change, read and follow repository-root `AGENTS.md` and
`docs/README.md`. Revalidate the current CAP-0018 package, SLI-0076,
WRK-0158, completed WRK-0159, the Learner Assistance Preferences contract,
the interface design and learner-language standards, the generated-client
boundary, the browser-local reminder adapter, the affected app shell/router,
the nearest feature patterns and README, and the tests that own those seams.
Apply the change-impact matrix and stop on conflicting canonical sources.

## Decisions and Assumptions

- The current approved CAP-0018 package and active SLI-0076 authorize this
  dependency-ordered browser packet. No lower-level approval exists or is
  requested.
- WRK-0158 fixes the `off | on_request` portable choice and separate
  `off | in_app_when_available` local choice. WRK-0159 supplies the protected
  public API and generated client. This packet consumes rather than widens
  either contract.
- `on_request` records only a preference for a possible future learner-started
  action. `in_app_when_available` records only future intent in this browser.
  Neither value proves that help or reminders are currently available.
- The public API remains independently usable by browser and headless clients.
  The local reminder choice has no API, learner identity, or headless meaning.
- Existing semantic tokens, reviewed icons, status components, session retry,
  request replay, safe-download, technical-disclosure, accessibility, and
  plain-language patterns are reused. No shared visual-system decision is
  introduced.

## In Scope

- Add a feature-owned model that closes portable profile/history/export
  responses, verifies canonical digest and exact retained-history correlation,
  maps failures safely, and prepares fresh exact mutation requests.
- Add loader/action/export adapters using only the reviewed generated public
  client and current single-profile session. Preserve exact unchanged-request
  retry after uncertain server responses and reject extra or malformed form
  fields before session or API access.
- Compose the existing browser-local reminder adapter without duplicating its
  storage key, schema, validation, digest, history, reset, or export logic.
  Local reads and writes remain usable when the learner API is unavailable;
  learner-owned controls remain usable when local storage is unavailable.
- Add a plain-language route with separate AI-help and reminder sections,
  separate save/reset confirmation and separate downloads, current
  non-availability disclosures, bounded recovery guidance, and exact technical
  records behind accessible disclosures.
- Add the route to the app shell and router while preserving keyboard, focus,
  responsive, theme, forced-color, reduced-motion, and ordinary navigation
  behavior.
- Add focused model, component, and Chromium coverage for valid choices,
  default/no-write reads, malformed and unavailable boundaries, exact replay,
  stale/conflict recovery, separate reset/download, no notification or model
  side effect, flexible valid shapes, accessibility, and learner language.
- Synchronize the web README, contract documentation, slice, packet, and
  planning register.

## Out of Scope

Backend, persistence, migration, OpenAPI, generated-client regeneration,
contract widening, import, erasure, provider or model admission, credentials,
provider/model selection, data-class permission, prompt/tool/model execution,
grounding, generation, AI output, recommendation, tutoring, inference,
background or autonomous action, network egress beyond the existing protected
preference API, notification permission, service worker, timer, schedule,
queue, subscription, email, SMS, push, reminder generation or delivery,
Assessment evidence, competency, mastery, eligibility, grading, financial
meaning, organization/guardian policy, tenancy, billing, dependency changes,
shared design-token changes, or style-only polish unrelated to function.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated public client | Assistance operations and closed generated types | No | Preserve browser/headless API parity without handwritten transport |
| Feature model/API | Existing preference validators, session retry, mutation and download patterns | New assistance-preference feature files only | Close private responses and compose server/local ownership safely |
| Local reminder platform adapter | Storage key, validation, mutation, reset, export, failure semantics | No | Consume the single platform-owned local authority without duplication |
| Router and shell | Preference routes, loading/error boundaries, primary navigation and skip labels | `router.tsx`, `AppShell.tsx`, `main.tsx` | Expose one accessible route using established composition |
| Interface | Shared components, tokens, icons, preference layouts | Feature page and feature stylesheet | Deliver plain-language controls without a parallel design system |
| Tests | Model, component, browser, boundary and anti-rigidity patterns | Listed focused test files | Prove closure, independence, accessibility, containment and no side effect |
| Documentation/planning | Web behavior, contract consumption, slice and register | Listed docs | Keep executable and planning evidence synchronized |

No path outside `write_scope` may change. Stop if backend, generated client,
local-reminder platform source, shared token/icon assets, dependencies, live
cross-system runner, or another unlisted shared boundary must change.

## Contracts and Interfaces

The loader returns one closed composite route state with independent
learner-owned and browser-local branches. A learner-service failure cannot
erase or disable the local branch; a local-storage or Web Crypto failure cannot
erase or disable a validated learner-owned branch. Absent server state is the
deterministic revision-one `off` profile supplied by the API. Absent, malformed,
unknown, or inaccessible local state presents a conservative `off` fallback
without a read-side write.

Server forms carry only one fresh idempotency key, exact expected revision,
and the closed replacement or confirmed reset fields. They never carry learner,
profile, time, digest, provider, model, prompt, data class, permission, output,
evidence, destination, policy, or reminder fields. Exact retry reuses the
complete prepared request; a newly changed intent receives a new key.

Local forms carry only a closed save/reset intent and reminder mode. The action
rereads the platform adapter's current envelope rather than trusting client-
supplied revision, history, time, digest, or storage facts, then records one
canonical current time. It makes no session or public API call. Unknown fields
or values fail before storage mutation. No notification API, permission prompt,
worker, timer, scheduler, queue, subscription, or delivery client is used.

The portable download is freshly read from the public export operation and
must match the profile revision and digest displayed on screen. The local
download is freshly validated by the platform adapter, contains no learner
identity, and is visibly named as this-browser-only. Changed or malformed
responses create no file. Exact versions, revisions, times, digests, integrity
codes, operations, and limitations remain reachable under `Technical record`
without leading the ordinary task flow.

Primary language must state that neither AI help nor reminders are available
on this screen today; saving records a choice only. Use learner-facing labels
rather than enum names, storage terminology, provider terminology, request
keys, schemas, digests, or implementation terms in ordinary flow.

## Dependencies and Parallel Safety

WRK-0159 is complete and fixes the protected API/generated-client dependency.
WRK-0160 owns the route, shell navigation, focused feature source, focused
tests, feature documentation, and the SLI/register projection. It is not
parallel-safe with another SLI-0076 packet and must complete before final live
qualification is reserved or authored.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Conservative first open | No stored learner profile and no local envelope | Learner opens the route | Both choices show off, with no read-side write or implied availability | unit/component/Chromium |
| Portable AI-help save | Valid revision and `on_request` choice | Learner saves | One exact generated-client mutation advances one revision and reload shows the accepted choice | unit/component/Chromium |
| No AI authority | Either portable choice | Learner saves or resets | No provider, model, permission, prompt, output, recommendation, evidence, or unrelated state is created | boundary/component/Chromium |
| Local future intent | Local storage is available | Learner records future in-app reminders | Only the allowlisted local envelope changes and the screen still says no reminder is sent today | unit/component/Chromium |
| No notification side effect | Any local choice | Learner saves, resets, reloads, or downloads | No permission prompt, notification API, worker, timer, schedule, queue, subscription, or notification network request occurs | component/Chromium/network |
| Independent failure | Learner API or local storage is unavailable | Route opens or an action fails | The other ownership branch remains usable with clear bounded recovery guidance | component/Chromium |
| Exact retry and conflict | A server response is uncertain, stale, or conflicts | Learner retries or reloads | Unchanged retry preserves the exact request; stale/conflict writes no extra state and guides refresh | unit/component |
| Separate reset | Either choice is not off | Learner confirms one reset | Only that authority returns to off; no false atomic cross-boundary reset is claimed | component/Chromium |
| Separate safe downloads | Both choices are available | Learner downloads each record | Portable export matches displayed server revision/digest; local export has no learner identity and is clearly browser-specific | unit/component/Chromium |
| Malformed data | Server or local response has unknown fields, values, broken digest, time, history, or correlation | Route validates it | Unsafe branch fails closed to a bounded state and creates no download or overwrite | unit/component |
| Accessible plain language | Keyboard, narrow viewport, scaled text, themes, forced colors, reduced motion | Learner completes each flow | Equivalent content/actions/focus remain usable and technical detail stays optional | component/Chromium/design |
| Flexible valid shapes | Both choices and varied valid history lengths/times surround unrelated content | Tests render and mutate | Behavior follows invariants rather than fixed wording, count, order, IDs, or fixture values | parameterized unit/Chromium |
| Headless parity retained | Generated public operations remain unchanged | Non-browser caller uses the API | Same portable profile/history/export remain available without rendering the route; local reminders remain absent | boundary/client contract |

## Verification Commands

Run focused feature-model, local-adapter regression, component, route, and
Chromium suites; generated-client boundary and browser-boundary checks;
TypeScript type checking and zero-warning lint; production build; learner-
language, design-system, security and architecture checks; documentation and
planning validation; whitespace checks; controller-selected exact-candidate
verification; one independent technical disposition; and
`python dev-tools/agent/check_ready.py`. Browser checks must cover keyboard and
focus, axe, 320-pixel reflow, 200-percent text, light/dark/system themes,
forced colors, reduced motion, malformed/unavailable branches, network
containment, and exact cleanup. Add no dependency or generated-client change.

## Documentation and Evidence Update

Document the route, separate ownership and downloads, safe default and
recovery behavior, generated-client/headless parity, local-only meaning,
current non-availability, and explicit no-execution/no-delivery limits. Record
focused and affected checks, accessibility, containment, anti-rigidity,
assumptions, and remaining live-qualification gaps. Keep approval, review, and
verification-receipt records only in ignored local control-plane storage.

## Stop Conditions

Stop for any provider/model admission, credentials, selection, data-class
permission, prompt/tool/model execution, output, recommendation, background
action, network egress outside the protected preference API, notification
permission or delivery, service worker, timer, scheduler, queue, subscription,
learner inference, evidence/competency/mastery/eligibility/grading/financial
meaning, organization/guardian/tenancy/billing behavior, caller-selected
learner identity, browser state used as server authority, local reminder
entering the API, direct backend import, handwritten transport, public schema
change, generated-client drift, dependency change, shared design-system
change, active write collision, conflicting canonical sources, or material
CAP-0018/SLI-0076 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count or order, or another inconsequential
issue. Fix bounded items locally or defer optional styling to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0076.WRK-0160`; exact candidate and qualifying receipt;
route and navigation behavior; independent server/local states, saves, resets,
downloads and failures; generated-client/headless parity; learner language,
privacy, accessibility, containment, anti-rigidity, focused/affected/aggregate
checks; documentation impact; assumptions; and residual live-qualification
gaps. Confirm no backend, migration, OpenAPI/generated client, provider/model,
data permission, AI output, notification permission or delivery, evidence,
competency, recommendation, external action, or financial behavior changed.

## Planning History

- 2026-10-17: Authored just in time after WRK-0159 completed. The packet
  composes the protected portable API and the separately owned local adapter
  into one plain-language browser flow while preserving independent failure,
  headless API parity, no-execution/no-delivery boundaries, and no lower-level
  approval within the current CAP-0018 package.
- 2026-10-17: Activated from recorded base `c702c85` after confirming the
  current CAP package, completed WRK-0159 dependency, bounded browser-only
  scope, resolved decision posture, and no active coordination collision.
