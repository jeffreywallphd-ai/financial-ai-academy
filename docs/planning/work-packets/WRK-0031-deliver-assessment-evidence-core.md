---
id: WRK-0031
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0015
capability: CAP-0001
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["contracts/README.md", "contracts/learning/README.md", "contracts/learning/assessment", "contracts/events/README.md", "contracts/events/assessment", "contracts/compatibility/README.md", "contracts/compatibility/assessment", "contracts/compatibility/lesson-package/v1/approved", "backend/README.md", "backend/src/financial_ai_academy/modules/README.md", "backend/src/financial_ai_academy/modules/assessment", "backend/src/financial_ai_academy/modules/content", "backend/src/financial_ai_academy/modules/curriculum", "backend/src/financial_ai_academy/bootstrap", "backend/migrations", "backend/tests/contract/assessment", "backend/tests/unit/assessment", "backend/tests/unit/content", "backend/tests/unit/curriculum", "backend/tests/integration/assessment", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/contracts/assessment-contract.md", "docs/architecture/contracts/content-package-contract.md", "docs/architecture/modules/module-map.md", "docs/domain/README.md", "docs/security/community-learner-evidence-protection.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/assurance/known-architecture-gaps.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0015-submit-deterministic-knowledge-check.md", "docs/planning/work-packets/WRK-0031-deliver-assessment-evidence-core.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0031:dbaeef44-dcad-4324-ba64-5e99d8158ad9
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:26:44Z
---

# Agent Work Packet: Deliver the Assessment Evidence Core

## Objective and Deliverable

Deliver the Assessment-owned single-choice definition, deterministic scoring,
idempotent append-oriented evidence transaction, versioned event, and exact
Content/Curriculum public-facade adapters needed by SLI-0015.

## Required Context

Read AGENTS.md, repository/planning entry points, CAP-0001, SLI-0015, ADR-0005
through ADR-0009, module/contract/testing rules, and every affected facade,
adapter, migration, fixture, and test before editing.

## Decisions and Assumptions

The accepted ADRs fix ownership and runtime. The definition profile is limited
to one single-choice item. Content transports verified opaque bytes; Assessment
alone interprets and scores them. Completion evidence means only the declared
check threshold was met.

## In Scope

- Exact definition/event schemas and valid/invalid conformance fixtures.
- Content public retrieval of one declared exact opaque assessment resource.
- Assessment domain, facade, ports, public-facade adapters, PostgreSQL atomic
  repository, event evidence, and additive reversible migrations.
- Curriculum exact placement lookup through its public facade.
- Focused contract, domain, application, transaction, failure, idempotency,
  concurrency, and architecture tests.

## Out of Scope

HTTP/web delivery, projection/history, multiple items, grading extensions,
external messaging, and any mutable evidence or recovery guarantee.

## Expected File and Boundary Impact

Only paths in frontmatter may change. The new module follows domain ->
application/ports -> adapters -> composition. Cross-module adapters import
published facades only; database tables have no cross-module foreign keys.

## Contracts and Interfaces

The definition and event JSON Schemas are exact portable contracts. Python
public requests/results expose domain-safe identifiers and evidence references,
never storage keys or provider payloads.

## Dependencies and Parallel Safety

SLI-0001 supplies the immutable package, placement, identity, and PostgreSQL
seams. This packet is serial and has no parallel-safe peer.

## Acceptance Scenarios

- Correct and incorrect answers score reproducibly.
- Duplicate identical submission returns the original chain; conflicting reuse
  fails without mutation.
- malformed/stale definitions and missing placements write nothing.
- injected storage failure exposes no partial chain.
- concurrent identical requests produce one business attempt/event.

## Verification Commands

Run focused backend contract/unit/integration/architecture tests, migrations up
and down on disposable PostgreSQL, planning validation, and `git diff --check`.

## Documentation and Evidence Update

Update the module README and packet/slice/register evidence; do not change
canonical meaning unless implementation reveals a documented conflict.

## Stop Conditions

Stop on a durable-decision boundary, cross-module persistence access, mutable
scores, model/manual authority, or unbounded schema generalization.

## Required Handoff

Report contracts, invariants, migration behavior, focused checks, documentation
impact, limitations, and readiness of WRK-0032.

## Verification Progress

- Reused the conforming Assessment core from the repository's earlier
  knowledge-check branch while excluding its obsolete planning and
  control-plane state.
- The definition, presentation, submission, result, and completion-event
  schemas passed their approved and denial vectors. Focused domain,
  application, Content/Curriculum regression, and architecture tests passed
  82 checks.
- PostgreSQL 18.4 qualification passed all 7 focused migration, atomicity,
  replay, concurrency, rollback, and append-only tests. The complete backend
  suite then passed 151 tests against the disposable database.
- Architecture fitness passed 8 functions; documentation passed 187 Markdown
  files plus context and capability catalogs. No model/manual authority,
  client-selected learner, cross-module persistence access, or recovery claim
  was introduced.

## Planning History

- 2026-10-15: Authored immediately before work start within approved CAP-0001.
- 2026-10-15: Refined the fixture scope to the exact approved package directory,
  imported the conforming reusable implementation, and completed focused and
  cumulative backend qualification.
