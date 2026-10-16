---
id: WRK-0065
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0023
capability: CAP-0005
depends_on: ["WRK-0063"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/src/features/curriculum-graph/api.ts", "apps/web/src/features/curriculum-graph/model.ts", "apps/web/src/features/curriculum-graph/CurriculumGraphPage.tsx", "apps/web/src/features/curriculum-graph/CurriculumGraphRoute.tsx", "apps/web/src/styles/curriculum-graph.css", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/component/curriculumGraphFixture.ts", "apps/web/tests/component/curriculumGraph.test.tsx", "apps/web/tests/unit/curriculumGraphModel.test.ts", "apps/web/tests/browser/curriculum-graph/curriculum-graph.spec.ts", "docs/planning/work-packets/WRK-0065-annotate-curriculum-navigation-state.md", "docs/planning/vertical-slices/SLI-0023-explain-deterministic-curriculum-state.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 7bfc1f5309a6849e5e9144052817d74d2de9f269
claim_id: WRK-0065:95fa1506-cd73-4029-a75e-43f441434c58
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T00:57:44Z
---

# Agent Work Packet: Annotate Curriculum Navigation State

## Objective and Deliverable

Extend the existing exact-version curriculum route so an authorized learner
sees the complete server-evaluated navigation state beside every activity in
both list and map views. The browser must validate and join the closed graph
and navigation-state responses as one all-or-nothing projection, present
completion, eligibility, requirement, availability, and reasons as separate
non-color meanings, and never calculate eligibility or expose an activity-
launch action.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the learning-adaptation, interface-design,
testing-quality, architecture-contract, and delivery-planning context. Read the
change-impact matrix, decision readiness, CAP-0005, SLI-0023, WRK-0062,
WRK-0063, ADR-0005, ADR-0009, ADR-0014, the adaptive-pathway and navigation-
state contracts, interface design system, style guide, interface standards,
token and icon documentation, web README, generated client, current curriculum
graph model/loader/page/route/styles, and nearest contract, unit, component,
and mocked-browser tests.

## Decisions and Assumptions

- The generated `getCurriculumNavigationState` operation is authoritative for
  activity state. The browser validates and presents it but does not reproduce
  the Adaptation rule, infer completion, reinterpret reasons, or verify domain
  digests by reimplementing backend canonicalization.
- The route remains
  `/learn/curricula/:curriculumId/versions/:curriculumVersion`. It first
  validates the exact graph, then reads the navigation projection for the same
  identity. A valid page requires matching graph identity/digest and exactly
  one state per graph activity in graph order; any mismatch fails the complete
  page closed.
- One unauthorized response may renew the existing opaque session and replay
  the whole exact read once. No query, fragment, learner selector, policy
  selector, cached projection, stale graph, or partial successful response is
  accepted.
- Existing semantic tokens, cards, status icons, peer-view controls, and
  responsive graph layout are sufficient. The packet adds no shared visual
  rule, token, icon, dependency, or saved view preference.
- Assessment completion remains `unavailable` when that is what the server
  reports. Presentation must explain the bounded source limitation without
  inventing an incomplete, mastery, or competency meaning.

## In Scope

- Add a deeply typed browser alias and whole-response validator for the
  generated navigation-state response: closed keys, v1 identifiers and strict
  versions, timestamps, digests, enums, reason/reference bounds and
  uniqueness, unique activity states, exact graph identity/digest, and exact
  graph-ordered activity closure.
- Extend the curriculum loader to read both protected operations through the
  existing single-profile session, retry the complete pair once after an
  unauthorized response, and return bounded states without stale or partial
  graph facts.
- Present the four orthogonal dimensions for every activity with explicit text
  and reviewed status icons, followed by all server reasons and referenced
  graph identities. Keep equivalent text, order, and relationships in list and
  map views.
- Replace the structure-only notice with precise deterministic-navigation
  language that distinguishes completion from mastery and explains that the
  server—not the browser—evaluates current eligibility.
- Preserve the current no-launch boundary, exact graph provenance, list/map
  parity, keyboard order, theme parity, narrow and 200-percent reflow, forced
  colors, and reduced motion.
- Add direct excessive-rigidity tests for more than three reason references,
  multiple reasons, reordered/variable activities, optional locked states,
  shared optional branches, unbranched activities, and absent presentation
  hints while retaining strict identity and provenance closure.

## Out of Scope

Opening an activity, destination selection, current-position or return
history, completion mutation, curriculum-version migration presentation,
recommendation order, automatic next action, mastery or competency labels,
model output, experiment or ranking data, learner-selected identity, policy
selection, persisted eligibility, a new assessment-completion meaning, graph
mutation, enrollment, authoring, organization policy, a design-system change,
or live PostgreSQL/static-host qualification retained by the next packet.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generated-client boundary | navigation operation/types and current graph loader/session renewal | curriculum-graph `api.ts`, `model.ts`, client usage test | Validate and join two exact protected projections without handwritten transport authority |
| Learner presentation | current graph page/route, tokens, icons, styles | listed graph page, route, and stylesheet | Add equivalent non-color state and explanation annotations without launch behavior |
| Verification | graph fixtures and current model/component/browser suites | listed focused test files | Prove closed joins, bounded failures, parity, accessibility, and flexible compatible shapes |
| Documentation/planning | web README, SLI-0023, register | listed docs and this packet | Keep delivered boundary, packet state, and retained live qualification explicit |

## Contracts and Interfaces

`NavigationState` aliases the generated
`NavigationStateResponseModel`. `navigationStateIsSafe(value, graph)` accepts
only a complete closed v1 projection whose curriculum identity, version, graph
digest, and ordered unique activity IDs exactly match the already validated
graph. It validates transport constraints but treats reason text, state enums,
policy identity/version, timestamps, source-set digest, and projection digest
as server facts; it does not derive or rank them.

`CurriculumGraphRouteState.ready` contains both validated values. The loader
returns no graph-only ready state. Presentation receives the pair and looks up
state by exact activity ID only after closure is proven. Each activity exposes
human-readable labels for completion, eligibility, requirement, and
availability plus the full ordered reason list and references. List and map
continue to render the same semantic subtree.

## Dependencies and Parallel Safety

WRK-0063 is complete and supplies the accepted protected operation, corrected
v1 response, generated types, authorization behavior, and exact-candidate
evidence. This packet owns the current graph model/loader/page/style/test
surfaces and is not parallel-safe with the final live-qualification packet.
No backend, contract, generated client, router, token, icon, or persistence
file may change.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete state | Exact graph and matching navigation projection are returned | Route loads | Every activity shows completion, eligibility, requirement, availability, and ordered explanations in both views | loader/component/browser |
| Completed prerequisite | A server projection marks a prerequisite completed and its dependent eligible | Page renders | Both facts and exact server reasons appear without a mastery claim or browser recomputation | component/browser |
| Optional locked branch | Shared optional work is locked or unavailable | Either peer view renders | Optional meaning remains separate and visible; it never becomes a hidden requirement | component anti-rigidity |
| Flexible reasons and graph shape | Reasons contain four or more unique references, multiple entries, changed sibling order, absent hints, shared branches, or unbranched activities | Validation and rendering run | Compatible complete projections remain usable without fixed counts or specialized branches | unit/component anti-rigidity |
| Projection mismatch | Graph digest, identity, activity count/order, duplicate IDs, fields, bounds, enum, timestamp, or reason reference is invalid | Loader validates | Entire page becomes bounded invalid-response with no graph-only or partial state | unit/loader/component |
| Protected read | Session is missing/expired, either operation is denied, or a service is unavailable | Loader runs | One bounded state appears; a single unauthorized replay refetches the complete pair | unit/browser |
| Client tampering | Query, fragment, browser state, or disabled styling is changed | Route is requested | No server eligibility is created and invalid selection is rejected before transport | unit/browser |
| Accessible parity | Theme, keyboard, narrow/reflow, reduced-motion, or forced-color conditions vary | Learner uses list and map | State text, reasons, order, focus, and actions remain equivalent and axe-clean | browser/design |

## Verification Commands

Run the packet validator; focused graph model, loader, component, and mocked
Chromium tests; generated-client determinism and usage checks; TypeScript
typecheck, lint, complete Vitest suite, production build, design-system,
architecture, documentation, planning, diff, and aggregate readiness checks.
Prepare an exact candidate, qualifying control-plane receipt, and independent
technical review before completion. The live PostgreSQL/Python/static-host
browser path remains the next packet.

## Documentation and Evidence Update

Update the web README, this packet, SLI-0023, and the planning register. Record
the exact validation/join contract, state and reason presentation, bounded
failure mapping, list/map parity, anti-rigidity shapes, accessibility and theme
checks, exact test counts, assumptions, and retained live-qualification gap.
Keep approval and reviewer data only in ignored local stores.

## Implementation Evidence

The exact curriculum route now reads the protected graph and Adaptation
navigation projection as one atomic browser result. A 401 from either request
invalidates the opaque session once and rereads the complete pair; denied,
missing, unavailable, malformed, or graph/state-mismatched responses never
produce a graph-only page. The closed browser validator enforces the v1
identifier, strict version, timestamp, digest, enum, explanation, reference,
and reason bounds plus exact graph identity/digest and one unique state per
activity in graph order. It does not recompute a domain digest or Adaptation
policy.

Every activity card in both peer views presents completion, eligibility,
requirement, and availability as separate text fields, then preserves every
ordered server explanation and reference. Assessment completion remains
visibly unavailable when reported that way; optional locked work remains
optional; shared optional branches and unbranched activities remain visible.
The route adds no activity action, mastery or competency judgment,
recommendation, rank, model output, learner/policy selector, persistence, or
saved browser state.

Candidate preparation produced these results:

- graph/navigation model, loader, and component tests: 26 passed;
- focused Chromium graph tests: 5 passed, including axe-clean list/map and
  theme parity, keyboard use, narrow and 200-percent text reflow, forced
  colors, reduced motion, denial, malformed input, and unavailable/mismatched
  projection behavior;
- complete Vitest suite and generated-client determinism: 119 passed;
- TypeScript typecheck, lint, and production build: passed;
- design-system validation: 125 light/global tokens and 56 reviewed icons;
- architecture fitness functions: 13 passed;
- aggregate agent readiness: ready, 27 of 27 checks passed;
- qualifying affected-verification receipt and independent technical review:
  accepted with no actionable findings.

Direct anti-rigidity evidence accepts multiple reasons, four reason
references, variable/reordered activity sets when the exact state closure
follows graph order, absent presentation hints, shared optional branches,
unbranched activities, optional locked states, and variable branch and
relationship sets. Exact identity, provenance, response closure, reference
bounds, and graph-order matching remain strict. Live PostgreSQL/Python/static-
host qualification remains the final SLI-0023 packet.

## Stop Conditions

Stop for a navigation-state v1 or graph-contract change, client-side policy or
digest recomputation, inferred assessment completion, activity launch or
return history, model/ranking/recommendation/mastery authority, persistence,
learner or policy selectors, partial/stale presentation, a new dependency,
token, icon, shared visual rule, active scope collision, material CAP/SLI
drift, stale CAP approval, conflicting canonical authority, or external action
outside current authority.

## Required Handoff

Report the exact candidate; validated graph/state join and loader behavior;
state/reason display matrix; list/map parity; malformed/denial behavior;
anti-rigidity, theme, accessibility, responsive, focused, aggregate, receipt,
and review evidence; changed paths and documentation; assumptions and known
gaps; and confirmation that no launch, client policy, model, ranking, mastery,
recommendation, persistence, or new authority was added. Leave the final
SLI-0023 qualification packet dependency-ready or return a bounded blocker.

## Planning History

- 2026-10-16: Authored just in time after WRK-0063 completion. The packet
  consumes the accepted generated operation, keeps state server-authoritative,
  annotates the existing peer views through the current design system, and
  retains live cross-system qualification for the final SLI packet without
  changing the approved CAP-0005 package or opening a decision gate.
- 2026-10-16: Activated after revalidating the current CAP binding, completed
  WRK-0063 dependency, exact browser-only scope, decision posture, and absence
  of active scope conflicts.
- 2026-10-16: Implemented the all-or-nothing graph/navigation read, closed v1
  browser validation, equivalent list/map state and reason annotations, and
  flexible-shape regression corpus. Entered exact-candidate verification after
  the focused browser, complete web, build, design, and architecture gates
  passed; live composed-system qualification remains JIT-D.
- 2026-10-16: Completed at exact candidate `e82a572` after focused and complete
  web, Chromium accessibility/theme/reflow, design, architecture,
  documentation, planning, aggregate readiness, qualifying-receipt, and
  independent technical-review gates passed with no open findings.
