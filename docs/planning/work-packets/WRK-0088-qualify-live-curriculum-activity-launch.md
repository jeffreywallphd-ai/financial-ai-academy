---
id: WRK-0088
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0024
capability: CAP-0005
depends_on: ["WRK-0087"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/tests/browser/approved-lesson/curriculum-graph.e2e.ts", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/modules/adaptation/README.md", "deployments/local/README.md", "deployments/local/serve.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0024-open-and-return-to-an-eligible-activity.md", "docs/planning/work-packets/WRK-0088-qualify-live-curriculum-activity-launch.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py"]
generated_artifacts: []
base_revision: aac03a5fccdcb0b080bc3e4c8431e49cbb5b496e
claim_id: WRK-0088:28f852a3-4eee-4d9c-b3f2-3d2da7b997a6
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T13:04:25Z
---

# Agent Work Packet: Qualify Live Curriculum Activity Launch

## Objective and Deliverable

Complete SLI-0024 by extending the existing isolated approved-lesson harness so
real PostgreSQL repositories, the Python API/static host, the generated public
client, and pinned Chromium prove learner-controlled launch, exact lesson
opening, return after completion, current-position display, authorization
denial, and exact-version behavior. The reusable live fixture must expose two
coexisting immutable curriculum versions with deliberately reused and changed
exact resources so the test derives retained versus non-inherited completion
from server facts instead of one hard-coded graph shape.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the learning-adaptation, testing-quality,
interface-design, architecture-contract, and delivery-planning packs. Read the
change-impact matrix, decision readiness, CAP-0005, SLI-0024, WRK-0085 through
WRK-0087, ADR-0005, ADR-0009, ADR-0014, the adaptive-navigation contract, the
activity-launch and curriculum-graph schemas/compatibility corpus, the public
API snapshot and generated client, the local composition fixture, the live
runner and browser specifications, affected architecture tests, and the web,
Adaptation, host, and deployment READMEs.

## Decisions and Assumptions

- The generated public API remains the reusable application boundary. The
  browser is one client and receives no direct backend-internal dependency or
  authority, preserving non-UI and future headless use.
- The existing clean-start approved-lesson runner remains the only composed
  qualification harness. This packet may extend its explicitly enabled fixture
  seeding but creates no second runner, product seed path, or production state.
- The qualification-only fixture publishes a second exact curriculum version
  through the current Curriculum public operation. One lesson reference is
  deliberately reused; another uses a new placement backed by the same admitted
  immutable package so tests can prove exact-reference evidence behavior
  without inventing another package or migration.
- Browser expectations derive activity IDs, destinations, versions, and state
  from protected API records. Tests do not reproduce Adaptation policy,
  authorize a destination, or treat current position as durable state.
- Existing PostgreSQL 18.4, loopback Python host, same-origin static build,
  pinned Chromium, redaction, external-isolated-database acknowledgement, and
  exact teardown safeguards remain authoritative.

## In Scope

- Seed and architecture-test two immutable qualification graph versions using
  existing public composition operations only when the approved fixture flag is
  enabled.
- Prove the protected launch API rejects missing context, missing permissions,
  unavailable versions, assessment selections, and malformed/unknown activity
  choices without leaking destination, learner, graph, or state details.
- Launch every eligible lesson action through the rendered graph, validate the
  opened exact lesson path and complete return context, and prove list/map
  action parity without assuming a fixed number or specialized branch layout.
- Complete the approved lesson, return to the exact graph/activity, reload
  fresh server state, and show the lesson as both complete and current without
  fabricating durable launch history.
- Prove old and new exact routes coexist. Reused exact lesson resources may
  reuse retained evidence; a changed placement receives no inherited
  completion, and optional siblings remain visible and optional.
- Extend accessibility, keyboard, responsive/reflow, theme, forced-color,
  reduced-motion, interruption/reload, security-header, cleanup, and concise
  qualification-report evidence across the delivered launch/return flow.
- Reconcile architecture, module, host, deployment, web, slice, packet, and
  register statements with the exact live evidence and remaining gaps.

## Out of Scope

New API or generated-client shapes; product launch policy; learner-selected
identity, permissions, destination, or state; persistent current position or
launch grants; graph authoring; package migration; inferred resource
equivalence; ranking, recommendation, automatic next-step selection, mastery or
competency claims; model/AI behavior; assessment execution; new provider,
queue, cloud, dependency, browser engine, remote binding, production recovery,
or separate headless-AI planning.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Qualification fixture | local composition and public Curriculum operations | `deployments/local/serve.py`, architecture test | Publish a second bounded exact graph only in explicit fixture mode |
| Live API/browser evidence | approved lesson and curriculum graph specifications | the two listed `.e2e.ts` files | Prove public launch, lesson, return, completion, version, denial, and accessibility behavior |
| Harness report | clean-start orchestration and redacted report | `tests/e2e/approved-lesson/run.py` | Describe the exact newly exercised boundary without secrets or overclaiming |
| Canonical and operational guidance | navigation contract, architecture map, relevant READMEs | listed documentation files | Keep API-first meaning and qualification claims synchronized |
| Planning evidence | packet, SLI-0024, register | listed planning files | Close the final dependency-ordered slice seam coherently |

No product domain/application/API implementation, OpenAPI or generated-client
source, persistence schema, migration, package/lockfile, design-system asset,
or ordinary non-qualification fixture may change.

## Contracts and Interfaces

The tests consume the protected exact-version graph, navigation-state, and
activity-launch GETs plus the generated browser client. A valid launch must
match exact curriculum/version/activity/resource identity, fresh graph and
projection provenance, and the server-derived same-origin lesson destination.
Return context is the all-or-none exact curriculum/version/activity tuple and
confers no authorization. The second graph version is published through
`CurriculumService.publish_curriculum_graph`; retained completion follows only
the exact source reference already recognized by the Learner-model boundary.

The runner report may add only concise booleans/text describing launch/return,
two-version evidence, authorization confidentiality, and cleanup. It must not
emit a DSN, cookie, learner identifier, answer, destination secret, provider
payload, or claim product/production/headless-AI qualification.

## Dependencies and Parallel Safety

WRK-0087 is complete and supplies the accepted API/UI launch and return
behavior. This packet is the final SLI-0024 seam and overlaps the shared live
fixture, browser specifications, runner, architecture test, and qualification
documentation, so it is not parallel-safe with another packet touching those
paths. It must preserve all earlier catalog, discovery, graph, lesson,
assessment, completion, security, and cleanup evidence.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| API-first launch | Established learner context and an eligible lesson state | Exact launch API and generated client are used | Server returns the correlated exact lesson destination and provenance; browser policy does not select it | live API/browser |
| Learner launch and return | Eligible lesson action in either peer graph view | Learner starts or reviews it, completes it, and returns | Exact lesson opens, full return context survives, fresh graph reloads, and selected activity is visibly complete/current | live browser/API |
| Authorization and invalid selection | Missing session/permission, assessment, unknown activity, malformed selector, or missing version | Launch is requested | Bounded denial contains no destination, learner, graph, projection, or partial state detail | live API |
| Exact versions | Two published immutable graph versions contain reused and changed exact lesson references | Both exact routes/state/launches are read after completion | Both coexist; reused exact reference may retain completion while changed placement remains incomplete | live API/browser |
| Flexible graph | Optional/shared/unbranched/reordered activities and multiple eligible lessons exist | Actions render in list and map | Facts, actions, and optional siblings remain equivalent without count/branch special cases | live anti-rigidity |
| Interruption and accessibility | Launch is superseded/reloaded or display/input mode changes | Learner continues | No unhandled failure or false current marker occurs; controls remain keyboard/axe/reflow/theme/forced-color/reduced-motion usable | live browser |
| Harness containment | Qualification succeeds or fails | Runner exits | Only its exact process, unique database container, and bounded temporary data root are removed | runner controls |

## Verification Commands

Run the focused local-composition architecture test; TypeScript typecheck and
lint; complete Vitest; production build; focused browser-spec discovery and
mocked curriculum/lesson Chromium suites; backend activity-launch contract,
unit, application, API/OpenAPI, and architecture checks; generated-client
generation check; documentation, planning, learner-language, design-system,
security, whitespace, and aggregate readiness checks. Run the updated live
runner through an explicitly acknowledged isolated PostgreSQL service or its
own pinned disposable container. Prepare one exact candidate, qualifying
affected-verification receipt, and independent technical review.

## Documentation and Evidence Update

Record launch/API/client/path correlation, denial confidentiality, completion
and return transition, exact current marker, two-version reused/changed-source
facts, flexible-shape behavior, accessibility/theme/reflow, PostgreSQL/Python/
static/Chromium topology, cleanup, exact commands and results, assumptions, and
remaining gaps in this packet and SLI-0024. Reconcile listed READMEs, contract,
and architecture verification without implying production, recovery,
multi-user, cross-browser, financial-advice, model, recommendation, mastery, or
future headless-AI qualification. Store approval/reviewer data only locally.

## Stop Conditions

Stop for a new or breaking public contract, product runtime launch policy,
durable launch/current state, caller-selected learner/destination/state,
completion transfer by inferred equivalence, package/content mutation,
production seed behavior, persistence/migration, ranking/recommendation/model/
mastery authority, assessment execution, provider/queue/cloud/dependency,
remote host or external action, failed containment/cleanup, active scope
collision, conflicting canonical authority, stale CAP approval, or material
CAP-0005/SLI-0024 drift.

Do not stop for bounded fixture/test corrections, harmless whitespace,
advisory wording, or nonfunctional styling. Fix those locally or defer optional
polish to CAP-0031 without another approval or review cycle.

## Required Handoff

Report the exact candidate; public API and generated-client evidence; launch,
return, completion, current-position, denial, two-version, flexible-shape,
accessibility, security, cleanup, focused, aggregate, receipt, and review
results; changed paths; documentation impact; assumptions and known gaps; and
confirmation that no product API, browser-only authority, durable state,
model/recommendation/mastery behavior, migration, provider, or separate AI mode
was added. Leave SLI-0024 ready for deterministic closure or return a bounded
blocker.

## Implementation Evidence

- The explicit approved-fixture path now publishes
  `investing-foundations@1.0.0` and `@1.1.0` through the existing Curriculum
  public operation. The second version changes the primary lesson placement and
  adds one optional activity that deliberately reuses the original exact
  placement/package source. Ordinary startup without the fixture flag remains
  unchanged.
- The isolated PostgreSQL 18.4, loopback Python/static host, and pinned Chromium
  runner passed all 8 live scenarios. Direct API and generated-client/browser
  evidence covered exact launch correlation, learner start/review, completion,
  return context, fresh complete/current display, list/map parity, bounded
  assessment/unknown/query/version denials without destination leakage, two
  exact routes, reused-source completion, changed-placement non-inheritance,
  accessibility, responsive display, security headers, and exact cleanup.
- The complete backend regression passed 426 tests with 34 environment-bounded
  skips; the focused activity-launch contract/policy/application/API suite
  passed 56 tests. Architecture fitness passed 15 checks and the approved
  lesson security gate passed 10 control groups.
- The complete web unit/component regression passed 151 tests; focused mocked
  curriculum/lesson Chromium qualification passed 13 tests. TypeScript
  typecheck, lint, production build, OpenAPI snapshot, generated client,
  learner-language, design-system, documentation, planning, and whitespace
  checks passed.
- No product domain/application/API shape, OpenAPI or generated-client source,
  persistence schema, migration, package dependency, browser-only authority,
  durable launch/current state, model, recommendation, mastery, provider,
  cloud, or separate headless-AI plan changed. The same public API remains
  available to UI and non-UI clients.

## Planning History

- 2026-10-16: Authored just in time after WRK-0087 completion. The packet
  reuses the existing isolated harness, publishes the approved slice's second
  exact qualification version through public application boundaries, keeps the
  API available to UI and non-UI clients, and adds no decision or lower-level
  approval gate.
