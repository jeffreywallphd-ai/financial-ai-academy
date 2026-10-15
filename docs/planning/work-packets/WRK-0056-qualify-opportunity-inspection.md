---
id: WRK-0056
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0020
capability: CAP-0004
depends_on: ["WRK-0055"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "tests/e2e/approved-lesson/run.py", "deployments/local/README.md", "apps/web/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0020-inspect-and-compare-learning-opportunities.md", "docs/planning/work-packets/WRK-0056-qualify-opportunity-inspection.md"]
generated_artifacts: []
base_revision: 8c7b168b886e94f40bd9d79b37ddb88f854755aa
claim_id: WRK-0056:3a48660e-dd4f-4ffc-9299-d786c26d5dff
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T21:12:04Z
---

# Agent Work Packet: Qualify Opportunity Inspection

## Objective and Deliverable

Qualify the completed detail and comparison experience through the existing
isolated PostgreSQL 18.4 database, same-origin Python/static application,
restrictive filesystem storage, and pinned Chromium. Deliver deterministic
live evidence for exact current facts, ordered comparison, available-only
continuation, changed/malformed selection, accessibility, portability, and
exact-resource cleanup without introducing a provider, background job, saved
state, new contract, or broader runtime.

## Required Context

Before editing, follow every applicable `AGENTS.md` and `docs/README.md`; route
through deployment-operations, API/security, interface, testing-quality, and
delivery-planning context; read the change-impact matrix, decision readiness,
planning/concurrency guidance, CAP-0004, SLI-0020, completed WRK-0053 through
WRK-0055, the discovery and Identity contracts, local deployment, backend/web
and Curriculum READMEs, current fixture composition, cross-system runner, live
Chromium scenarios, architecture assurance map, known gaps, and nearest tests.

## Decisions and Assumptions

The accepted live topology and opt-in three-classification corpus from
WRK-0051 are sufficient. All three records intentionally resolve to the same
reviewed lesson package and placement while differing in identity,
classification facts, availability, and order. That corpus may qualify exact
detail/comparison behavior without inventing a non-lesson destination or
changing production seed composition.

## In Scope

- Extend the live Chromium scenario from the current catalog into one exact
  detail route and a two-record comparison selected in deliberate learner
  order, then continue only the available record to the exact lesson.
- Prove exact opportunity/package/provenance/projection facts, cursor-free
  catalog return, comparison order, planned-record non-execution, and no
  ranking, recommendation, eligibility, or partial substitution.
- Prove changed detail and changed/malformed comparison routes fail closed
  against the live current generation without rendering fallback records.
- Run axe against live detail and comparison states and retain security-header,
  cookie, no-session API confidentiality, exact lesson/completion, query, and
  portable cleanup evidence already owned by the shared runner.
- Update the runner's emitted evidence description and reconcile deployment,
  web, architecture assurance, known-gap, slice, packet, and register docs.
- Run focused and aggregate checks, affected verification, and independent
  technical review before closing the slice.

## Out of Scope

New fixture records or kinds, a non-lesson destination, backend/API/schema or
browser-source changes, generated static changes, saved comparisons,
cross-page selection, enrollment, eligibility, prerequisite completion,
ranking, recommendation, learner progress, provider integration, production
seed or rebuild scheduling, migrations, dependencies, remote/cloud binding,
or non-Chromium/manual screen-reader qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | current approved-lesson catalog/query/lesson scenario | approved-lesson Playwright scenario | Extend the same real topology through detail and comparison |
| Qualification report | cross-system runner | runner evidence description only | Report the newly exercised routes without changing topology or cleanup |
| Operational guidance | local deployment and web READMEs | listed READMEs | Record exact live coverage and retained limits |
| Assurance reconciliation | architecture verification and known gaps | listed assurance docs | Promote only the directly executed detail/comparison claim |
| Lifecycle | slice, packet, register | listed planning docs | Keep packet and slice state synchronized |

## Contracts and Interfaces

The packet consumes discovery-v1, the existing protected browse/query
operations, generated browser client, exact detail/comparison URL contracts,
single-profile session, exact lesson destination, the opt-in public Curriculum
fixture corpus, and the current static build unchanged. Browser assertions use
public UI and HTTP behavior only; they do not read repositories, databases,
private provider facts, or cursor internals.

## Dependencies and Parallel Safety

WRK-0055 is complete and supplies the final static interface. This packet owns
the shared live scenario, runner report, assurance reconciliation, and
SLI-0020 closure files, so it is intentionally serial and not parallel-safe.

## Acceptance Scenarios

| Scenario | Required outcome |
| --- | --- |
| Exact live detail | Catalog detail opens one current identity with exact package, provenance, generation, availability, return path, and exact available-lesson action |
| Ordered live comparison | Planned then available selections render in that order with complete facts, no winner/score, detail links for both, and exact lesson execution only for the available record |
| Changed/malformed selection | Missing detail, partly missing comparison, and one-ID comparison produce bounded states with no partial or substituted record |
| Accessibility and themes | Live detail/comparison axe checks pass and mocked theme, keyboard, reflow/text-scale, reduced-motion, and forced-color evidence remains green |
| Context confidentiality | No-session browse/query requests disclose no record, count, cursor, identity, provider, or storage fact |
| Exact continuation | The available comparison record opens the reviewed placement and retained completion path without latest-version substitution |
| Portable cleanup | PostgreSQL, Python/static, Chromium, and isolated filesystem are the only live participants; unique container and data root are removed |
| Anti-rigidity | Ordinary approved-fixture startup still works without the opt-in query corpus, and detail/comparison requires no saved state or extra service |

## Verification Commands

Run packet/planning/claim/start and lease controls; focused live-scenario source
and architecture checks; complete web unit/component and focused mocked
Chromium suites; generated-client currency, typecheck, lint, production build,
static boundary and dependency checks; complete backend, contract, integration,
architecture, security, design, documentation, planning, and diff checks; the
isolated Docker/PostgreSQL qualification through
`backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py`; affected
control-plane verification; independent technical review; and
`python dev-tools/agent/check_ready.py`. Docker qualification is mandatory; an
unavailable host is environmental failure, not completion evidence.

## Documentation and Evidence Update

Record exact detail/comparison identities, facts, order, action policy,
changed/malformed states, accessibility, security/confidentiality, static
digest, topology and cleanup, checks, unsupported destinations/profiles, and
residual gaps. Do not place local approval or reviewer records in tracked
artifacts.

## Stop Conditions

Stop for a new fixture or public contract; changed discovery meaning;
production/implicit seeding; private repository or database access from the
browser; partial comparison; ranking, recommendation, eligibility, enrollment,
progress, or saved state; a provider, queue/job, migration, dependency,
non-lesson execution, remote/cloud binding, weakened security/header/cleanup
posture, overlapping scope, unresolved durable decision, or material
CAP-0004/SLI-0020 outcome, manifest, order, risk, or decision drift.

## Required Handoff

Report exact live detail and comparison facts/order/actions; changed and
malformed behavior; accessibility, confidentiality, security headers, static
digest, PostgreSQL/Python/filesystem/Chromium topology and cleanup; all checks;
documentation impact; residual gaps; and CAP/SLI conformance.

## Planning History

- 2026-10-15: Authored just in time after WRK-0055 completion. The packet
  reuses WRK-0051's accepted isolated topology and opt-in corpus to qualify the
  final interface without new runtime, contract, fixture authority, durable
  state, decision, or material CAP drift.
