---
id: WRK-0036
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: ["WRK-0035"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/learner_model", "backend/migrations/learner_model", "backend/migrations/README.md", "backend/src/financial_ai_academy/modules/README.md", "backend/tests/unit/learner_model", "backend/tests/integration/learner_model", "backend/tests/architecture/test_module_boundaries.py", "docs/architecture/modules/module-map.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/assurance/known-architecture-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0036-deliver-learner-completion-projection.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0036:8ae1dcf8-ce35-4156-b514-bcd863e47ecd
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:47:56Z
---

# Agent Work Packet: Deliver the Learner Completion Projection

## Objective and Deliverable

Implement the Learner-model-owned, rebuildable lesson-completion projection and
evidence history from WRK-0035's typed Assessment event source, including an
atomic PostgreSQL rebuild that never replaces or mutates Assessment evidence.

## Required Context

Before changing files, read and follow `AGENTS.md`, `docs/README.md`, routed
architecture/data/testing/security context, CAP-0001, SLI-0016, WRK-0035,
ADR-0005, the Assessment public event source, module/dependency/data rules,
migration runner, existing module patterns/tests, and nearest README files.

## Decisions and Assumptions

Completion means only that bounded Assessment completion evidence exists for
the exact learner and placement. It is not mastery, competency, certification,
or advice. The projection is disposable and rebuildable; Assessment remains
the source of truth. Synchronous replay avoids the unresolved queue boundary.

## In Scope

Create Learner model domain/application/port/adapter/public seams, an adapter
over Assessment's public operation, additive PostgreSQL migrations, atomic
replace-from-complete-source semantics, stable source digests, exact provenance
history, and unit/architecture/real-PostgreSQL evidence for empty, exact,
duplicate, tampered, interrupted, and unavailable cases.

## Out of Scope

Audit, HTTP/generated client, UI, background delivery, checkpoints, mastery or
recommendations, multiple activity types, cross-learner access, backup/restore
tooling, and managed-cloud qualification.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Learner model | Accepted ownership and module patterns | New module-first boundary | Own derivation, public query, and projection vocabulary |
| Assessment adapter | WRK-0035 public operation only | Learner-model adapter | Map public events into owned evidence values without internal imports |
| PostgreSQL | Migration conventions and transactional tests | New `learner_model` migration stream/repository | Atomically rebuild derived rows in the owning schema |
| Architecture | Module map, gaps, fitness tests | Listed architecture docs/tests | Enforce public-only dependency and projection ownership |
| Planning/docs | Slice/register/packet and nearest READMEs | Listed files | Keep lifecycle and operational guidance current |

## Contracts and Interfaces

The public operation accepts one server-supplied learner ID and exact placement
ID and returns a bounded completion view with `completed`, a source-set digest,
and ordered history. Each history entry retains source event, attempt, evidence,
package, assessment, item, policy, score, and completion time. The response
contains no answer, feedback, provider binding, storage shape, mastery, or
recommendation.

## Dependencies and Parallel Safety

WRK-0035 is complete. This packet consumes only its public typed operation and
owns new module/schema paths. It remains serial because the following Audit/API
packets depend on its final public view and shared planning artifacts.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty evidence | Assessment returns no events | Open completion | Return incomplete with empty history and stable digest | unit/integration |
| Exact completion | One valid exact event exists | Rebuild/open | Return completed with all source provenance | unit/integration |
| Duplicate replay | Same source is opened repeatedly | Rebuild | Retain one history row and same source digest | integration |
| Interrupted replace | Existing valid projection and injected failure | Rebuild | Transaction rolls back to the complete prior view | integration |
| Invalid source | Duplicate identity, mismatch, unsupported token, or bad score | Derive | Fail before persistence and preserve prior projection | unit |
| Source/storage unavailable | Assessment query or PostgreSQL fails | Open completion | Return bounded unavailable error without false completion | unit/integration |

## Verification Commands

Run Learner-model unit and real PostgreSQL integration suites, Assessment
regressions, backend architecture/full tests, docs/planning checks,
`git diff --check`, and applicable security/readiness checks if shared gates
change.

## Documentation and Evidence Update

Record module ownership, public types, replay/rebuild rules, migration and down
path, exact counts/environment, interruption and duplicate evidence, queue and
mastery non-claims, remaining Audit/API/UI work, and CAP conformance.

## Stop Conditions

Stop if the projection reads Assessment SQL, mutates source evidence, requires
a queue/delivery guarantee, infers mastery, exposes another learner, loses
source references, or makes recovery/cloud claims outside ADR-0008.

## Required Handoff

Report derived semantics, exact provenance, atomicity/replay behavior, tests,
migration/rollback impact, known gaps, and readiness of WRK-0037.

## Verification Progress

- Added the module-first Learner-model boundary and public completion view.
  Completion is true only when exact validated Assessment evidence exists; the
  view retains event, attempt, evidence, package, Assessment, item, policy,
  score, and time references and labels the result as a bounded knowledge-check
  completion rather than mastery.
- Added an Assessment-public-only adapter plus a stable source-set digest and
  deterministic ordering/validation rules. Mismatched context, versions,
  identities, timestamps, or scores fail before persistence.
- Added the isolated `learner_model` migration stream and atomic replace
  repository. Empty evidence is explicit, repeated replay retains one derived
  set, and an injected mid-rebuild failure rolls back to the prior complete
  projection. The down migration removes only rebuildable derived state.
- Seventeen focused unit/architecture tests and three real PostgreSQL 18.4
  integration tests passed. The full backend suite passed 159 tests with 22
  environment-gated skips; the backend architecture suite contains nine direct
  checks, the aggregate architecture fitness suite passed eight, documentation
  verified 190 Markdown files and catalogs, planning verified 66 artifacts,
  and the diff check passed with line-ending warnings only.
- Audit, API/client, browser history, background delivery, recovery tooling,
  and managed-cloud profiles remain outside this packet. No queue or mastery
  decision was introduced.

## Planning History

- 2026-10-15: Authored immediately after WRK-0035 completed; the public replay
  source fixes the consumer contract and no unresolved decision or CAP drift
  was found.
- 2026-10-15: Delivered and qualified the rebuildable Learner-model projection
  with real PostgreSQL replay and interruption evidence.
