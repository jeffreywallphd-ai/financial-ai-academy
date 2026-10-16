---
id: WRK-0075
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-plain-language-ui
updated: 2026-10-16
parent: SLI-0123
capability: CAP-0030
depends_on: ["WRK-0074"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/curriculum-graph/curriculum-graph.spec.ts", "apps/web/tests/browser/approved-lesson/curriculum-graph.e2e.ts", "apps/web/README.md", "docs/planning/work-packets/WRK-0075-qualify-plain-language-learning-path.md", "docs/planning/vertical-slices/SLI-0123-understand-learning-path-state-in-plain-language.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 43e4d6f4591809efd34ce44d174acea719afe3c3
claim_id: WRK-0075:d8b211db-2360-48cd-ba2d-b381ccb5fb7b
claimed_by: codex-plain-language-ui
claimed_at: 2026-10-16T10:15:20Z
---

# Agent Work Packet: Qualify the Plain-Language Learning Path

## Objective and Deliverable

Qualify the complete SLI-0123 learner journey in pinned Chromium using the
existing mocked curriculum suite and isolated live approved-lesson harness. The
evidence must show learner-focused learning-path, activity-status, reason, and
recovery language; complete accessible technical records; unchanged protected
API/UI parity and fail-closed behavior; and equivalent list/map, theme,
keyboard, responsive, forced-color, reduced-motion, and scaled-text behavior.

This packet changes browser evidence and documentation only. It does not alter
product runtime, contracts, graph/navigation policy, fixtures, or harness
orchestration.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Use the baseline, `interface-design`,
`learning-adaptation`, and `testing-quality` packs. Read CAP-0030, SLI-0123,
WRK-0073, WRK-0074, WRK-0066, the graph/navigation contracts, interface/content
standards, current mocked and live curriculum browser specifications, isolated
live runner, and `apps/web/README.md` before editing.

## Decisions and Assumptions

- Existing mocked and live harnesses are the authority. The packet updates
  assertions for changed presentation and does not create a new runner, server,
  database, fixture, browser configuration, or snapshot system.
- Browser evidence opens `Technical record` before asserting exact hidden facts
  and compares API facts with the UI without recomputing policy.
- Tests derive activity/card expectations from returned data or selected
  records; they do not freeze one fixture count, whole prose, or pixel styling.
- The live runner may use its pinned disposable PostgreSQL container and exact
  teardown. An environmental Docker failure is diagnosed separately from a
  product defect and does not authorize harness or product scope expansion.
- Whitespace-only, cosmetic, and nonfunctional style observations are
  nonblocking and belong in CAP-0031 unless explicitly pulled forward.

## In Scope

- Mocked Chromium assertions for learning-path headings, learner status labels,
  plain reasons, flexible activity/group/connection shapes, exact technical
  records, list/map parity, safe recovery, privacy, themes, axe, keyboard,
  narrow layout, forced colors, reduced motion, and 200-percent text.
- Live Chromium/API assertions for the same changed accessible names while
  retaining complete graph/state closure, exact state values, recorded reason
  explanations, reason references, policy/schema/time/digest provenance,
  denial, unsupported selectors, and missing-version confidentiality.
- Anti-rigidity corrections that derive counts from graph data, inspect only
  selected activity records, and assert roles/actions/required facts rather
  than full paragraphs.
- Web README and planning evidence reconciliation plus deterministic slice
  completion checks.

## Out of Scope

- Any product source, backend, contract, generated client, graph/state model,
  fixture, persistence, migration, session, authorization, policy, grading,
  mastery, recommendation, ranking, activity-launch, CSS, token, icon, layout,
  browser configuration, Docker composition, or runner-orchestration change.
- New visual snapshots, cross-browser claims, manual screen-reader claims,
  localization, external services, or formal readability conformance.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Mocked browser evidence | curriculum fixture, route, page, Playwright config | named mocked spec only | Qualify flexible plain-language behavior and safe states |
| Live browser/API evidence | live graph specification, runner, generated types | named live spec only | Preserve API/UI fact parity with revised presentation |
| Documentation/planning | web README, packet, parent slice, register | named files | Record exact qualification and close the slice |

## Contracts and Interfaces

Tests consume the unchanged generated `CurriculumGraph` and `NavigationState`
types, protected exact-version APIs, single-profile session, page roles, and
existing technical disclosures. They assert separate server-owned dimensions
and complete exact evidence but do not duplicate validation or policy.

No public or internal runtime interface changes. Completion hands SLI-0124 a
closed SLI-0123 and preserves the same application and test harnesses.

## Dependencies and Parallel Safety

WRK-0073 and WRK-0074 are complete and supply stable ready-page and recovery
names. This final packet overlaps the curriculum browser suites and planning
closure, so it is not parallel-safe with another SLI-0123 packet. Its exact
file lease leaves unrelated work available.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Complete learner view | A valid exact graph/state pair | The path opens | Learning-path headings, plain status dimensions/reasons, groups, connections, and no invented launch/mastery/recommendation appear | Mocked/live Chromium |
| Complete technical record | The learner opens path and activity disclosures | Technical facts are inspected | IDs, versions, schemas, digests, policy, exact time, sources, state values, reason codes/explanations/references, and relationship facts remain reachable | Mocked/live Chromium/API |
| Flexible path | Variable activities, shared groups, ungrouped activity, optional hints, and empty groups/connections | Views render | Expectations derive from returned data rather than fixed card counts or one layout | Mocked/live anti-rigidity |
| Peer views and access modes | View/theme/viewport/input/display settings change | Learner uses the page | Equivalent content/actions remain axe-clean, operable, non-overflowing, and motion-safe | Mocked/live Chromium |
| Bounded recovery | Access, exact version, response, or availability fails | State renders | Protected/partial facts remain hidden and learner-focused retry/return behavior stays unchanged | Mocked/live Chromium/API |
| Harness containment | Live qualification succeeds or fails | Runner exits | Its existing isolated database, process, filesystem, and browser resources are cleaned up exactly | Live runner |

## Verification Commands

- `npm --prefix apps/web run test:browser -- tests/browser/curriculum-graph`
- `python tests/e2e/approved-lesson/run.py`
- `npm --prefix apps/web test -- --run apps/web/tests/component/curriculumGraph.test.tsx`
- `npm --prefix apps/web run typecheck`
- `npm --prefix apps/web run lint`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected verification through `python dev-tools/control-plane/control_plane.py verify WRK-0075`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`
- the SLI-0123 deterministic completion gate with WRK-0073 through WRK-0075

Use the repository-pinned Node/npm/Chromium runtime and an isolated local temp
root. Run the live harness through its existing disposable database path; do
not weaken containment or substitute an unrelated environment.

## Documentation and Evidence Update

Update the web README only where the revised learner-language qualification is
described. Record exact mocked/live scenario counts, API/UI technical facts,
access modes, containment/cleanup, affected receipt, independent review,
assumptions, gaps, and slice closure in this packet and SLI-0123. Keep approval
and reviewer records only in ignored local state.

## Stop Conditions

Stop for any runtime, backend, contract, generated-client, graph/state/policy,
fixture, persistence, migration, session, authorization, activity-launch,
mastery, recommendation, ranking, CSS/token/icon, browser configuration,
composition, or harness-orchestration change; failed containment; conflicting
canonical authority; material CAP drift; or a colliding lease. Diagnose a
Docker/environment failure without broadening scope. Do not stop or reopen
review for whitespace, cosmetic, or nonfunctional visual polish.

## Required Handoff

Report exact candidate, mocked/live scenario counts, complete technical-record
and state parity, recovery/privacy behavior, theme/access/responsive results,
containment cleanup, focused/affected/aggregate checks, review, slice closure,
unchanged boundaries, assumptions, gaps, and any cosmetic item deferred to
CAP-0031.

## Planning History

- 2026-10-16: Refined SLI-0123 JIT-C as a browser-evidence-only packet that
  reuses the mocked and live curriculum harnesses, updates changed accessible
  names, derives flexible expectations from data, and closes the slice without
  product, harness, or styling changes.
