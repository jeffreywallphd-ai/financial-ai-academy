---
id: WRK-0061
kind: work-packet
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: SLI-0022
capability: CAP-0005
depends_on: ["WRK-0060"]
decision_gates: []
parallel_safe_with: []
write_scope: ["deployments/local/serve.py", "deployments/local/README.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/run.py", "apps/web/tests/browser/approved-lesson/curriculum-graph.e2e.ts", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0022-open-versioned-curriculum-graph.md", "docs/planning/work-packets/WRK-0061-qualify-live-curriculum-graph.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Live Curriculum Graph

## Objective and Deliverable

Qualify SLI-0022 through the real local composition: seed one synthetic
approved exact curriculum graph through Curriculum public operations, persist
it in disposable PostgreSQL, expose it through the protected API and static
same-origin Python host, and exercise the reviewed learner list/map route in
pinned Chromium. Reconcile deployment and web documentation and leave the
slice ready for deterministic closure.

## Required Context

Before editing, follow every applicable `AGENTS.md` and repository-root
`docs/README.md`; route through the baseline, curriculum/learning,
interface-design, testing-quality, security-risk, planning, and deployment
context. Read the change-impact matrix, decision readiness, CAP-0005,
SLI-0022, WRK-0058 through WRK-0060, Curriculum graph contract and
compatibility corpus, Curriculum public operations, local composition and its
architecture fitness tests, live qualification runner/config/spec, web graph
route and validator, deployment guide, and nearest READMEs.

## Decisions and Assumptions

The existing local qualification topology remains the reusable seam: one
loopback Python process serves both API and reviewed static assets against one
disposable PostgreSQL database and filesystem root. The synthetic graph is
derived from the reviewed compatibility fixture, adjusted only to the exact
seeded lesson package reference, and published through Curriculum's public
operation after every exact placement dependency exists. Normal startup stays
seed-free. Live checks supplement rather than replace contract, integration,
component, or mocked browser checks.

## In Scope

- Extend the explicit `--seed-approved-fixture` path to create every exact
  lesson/assessment placement required by the reviewed graph, adapt the primary
  lesson reference to the admitted package, retain same-kind optional sharing
  and an unbranched activity, recompute the graph digest through Curriculum's
  public helper, and publish exactly one approved graph through the public
  service before application readiness.
- Extend architecture tests to prove normal startup performs no graph mutation,
  seeding uses public operations in deterministic dependency order, a graph
  seed failure prevents readiness, and no repository adapter is bypassed.
- Add live Chromium evidence for exact-version API/UI parity, PostgreSQL-backed
  provenance and digest, list/map fact parity, light/dark/system and axe parity,
  keyboard/narrow/200-percent/reduced-motion/forced-color behavior, same-kind
  shared membership, an unbranched activity, unauthorized transport denial,
  missing exact-version behavior, and absence of launch or learner-state claims.
- Update the cross-system report and deployment/web documentation to describe
  the graph path, seed boundary, checks, cleanup, and remaining limitations.
- Run focused and aggregate backend, web, live, architecture, security,
  design, documentation, planning, diff, and readiness verification plus
  independent technical review.

## Out of Scope

Production fixture ingestion, browser-authored graph data, current/latest
aliases, graph mutation or authoring, activity launch, eligibility,
completion, mastery, adaptation, recommendations, enrollment, corrupting live
storage to duplicate repository tests, new deployment processes, external
databases without the existing isolation acknowledgement, or any production
availability/recovery claim.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Local composition | seed flags, public services, exact fixture, migration/startup order | listed `serve.py` and architecture test | Seed through public operations without weakening normal startup |
| Live qualification | Python runner, Playwright config/spec, static host | listed runner and new graph e2e spec | Prove the complete real path and bounded denials |
| Documentation | deployment and web READMEs | listed READMEs | State the newly qualified claim and residual gaps |
| Planning | SLI-0022, register, this packet | listed planning files | Record evidence and close the final packet/slice consistently |

## Contracts and Interfaces

No public contract changes. `build_local_app(..., seed_approved_fixture=True)`
adds the already reviewed graph to the existing explicit synthetic seed
transaction through `PublishCurriculumGraphRequest`; false leaves all graph
operations untouched. The e2e route is the existing
`/learn/curricula/investing-foundations/versions/1.0.0`, and transport checks
use the existing protected exact API path. The report gains a bounded graph
qualification statement without a new machine-readable public interface.

## Dependencies and Parallel Safety

WRK-0060 is complete and supplies the exact generated-client route. This packet
owns shared local composition, architecture fitness, and live e2e surfaces and
therefore has no parallel-safe peer. The currently running disposable
PostgreSQL composition may be reused for focused backend checks, but the live
runner must retain its own isolated resource ownership and cleanup.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live exact graph | Explicit fixture seed and empty PostgreSQL | App reaches readiness and learner opens exact route | Persisted graph facts, exact version/digest/time/sources, branches, activities, and relationships agree across API and UI | architecture/live Chromium |
| Flexible live shape | Same activity belongs to two optional branches and another activity has no branch | Both peer views render | Sharing and unbranched meaning remain visible without fixed counts or layout assumptions | live anti-rigidity |
| Protected/missing | No session or an unknown exact version is requested | Protected API/UI read runs | Bounded 401 or not-found appears without graph facts or substituted version | live transport/browser |
| Accessible parity | Three themes, map/list, keyboard, narrow/200-percent, reduced motion, forced colors | Learner uses live route | Content parity, focus, reflow, readable semantics, and axe checks pass | live Chromium/design |
| Seed isolation | Seed flag is absent or graph publication fails | Local composition starts | No graph mutation occurs, or readiness is prevented on explicit seed failure | architecture |
| Reusable cleanup | Qualification succeeds or fails | Runner exits | Only its exact process, database/container, and ignored data root are removed | runner/live report |

## Verification Commands

Run the work-packet and implementation-gate validators; focused local
composition architecture tests; complete backend tests against real disposable
PostgreSQL; OpenAPI/generated-client currency; complete web unit/component and
browser suites; production build; the live cross-system runner; architecture,
security, design-system, documentation, planning, diff, and all readiness
checks; control-plane exact-candidate verification; and independent technical
review. Preserve the existing safe cleanup behavior and redact an acknowledged
external DSN from diagnostics.

## Documentation and Evidence Update

Update the deployment and web READMEs, this packet, SLI-0022, and the planning
register. Completion evidence records exact seed/public-operation order,
database/API/browser path, themes/accessibility, anti-rigidity cases, denial
behavior, checks and results, cleanup, assumptions, known gaps, and explicit
confirmation that eligibility/adaptation remain outside the slice. Approval
and reviewer records stay only under ignored `.local-codex`.

## Stop Conditions

Stop for a public contract change, graph meaning not representable by the
reviewed fixture, direct adapter/database seeding, non-loopback or persistent
test resources, an authorization expansion, activity execution, learner-state
or adaptive meaning, a new production process/dependency, unsafe cleanup, an
unresolved exact reference, active scope overlap, or a material CAP/SLI
outcome, risk, order, or decision-posture change.

## Required Handoff

Report the exact live route and seed/public-operation order; PostgreSQL/API/UI
and provenance evidence; list/map, theme, accessibility, responsive, denial,
and anti-rigidity results; affected boundaries; documentation impact; cleanup;
residual limitations; packet and slice lifecycle outcomes; and whether the
next CAP-0005 slice is eligible.

## Planning History

- 2026-10-15: Authored just in time after WRK-0060 completion. The packet
  reuses the established loopback qualification harness and reviewed graph
  fixture, adds no public contract or decision gate, and keeps live evidence
  broad without turning synthetic seed behavior into production authority.
