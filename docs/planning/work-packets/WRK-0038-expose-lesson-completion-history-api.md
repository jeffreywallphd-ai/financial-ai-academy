---
id: WRK-0038
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0016
capability: CAP-0001
depends_on: ["WRK-0037"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/hosts/api", "backend/tests/integration/api", "contracts/api/openapi.json", "apps/web/src/generated/api-client", "deployments/local/serve.py", "backend/README.md", "apps/web/README.md", "docs/architecture/modules/module-map.md", "docs/architecture/assurance/architecture-verification.md", "docs/security/community-learner-evidence-protection.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0016-reopen-retained-lesson-completion.md", "docs/planning/work-packets/WRK-0038-expose-lesson-completion-history-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client/schema.d.ts"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0038:a9da6a55-da80-4dac-a953-d686305f9e4b
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:53:53Z
---

# Agent Work Packet: Expose the Lesson Completion History API

## Objective and Deliverable

Compose Audit reconciliation and Learner-model rebuild behind one protected,
server-learner-bound completion-history API and regenerate the reviewed OpenAPI
snapshot and TypeScript client.

## Required Context

Before changing files, read and follow `AGENTS.md`, `docs/README.md`, routed
API/identity/security/testing context, CAP-0001, SLI-0016, WRK-0035 through
WRK-0037, ADR-0005/0006/0008/0009, public module operations, FastAPI models/
error handling, composition/migrations, generated-client tooling, local host,
tests, and nearest README files.

## Decisions and Assumptions

The endpoint resolves learner identity only from the protected session. It
reconciles Audit before rebuilding/returning Learner-model state so a newly
visible completion never bypasses its integrity reference. The host composes
public operations but owns no scoring or completion policy.

## In Scope

Apply Learner-model and Audit migration streams in local composition, construct
their adapters/services, add an exact-placement GET response with bounded
history/provenance, map safe errors, regenerate OpenAPI/client artifacts, and
test success, empty, denial, forged identity, stale/malformed evidence, Audit
failure, projection failure, and unavailable configuration.

## Out of Scope

Browser presentation, background delivery, administrative Audit endpoints,
cross-learner or bulk history, mutable state, new identity modes, recovery,
cloud deployment, and changes to scoring/submission contracts.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Composition | Existing service/migration order | Bootstrap and local host | Construct module-owned adapters and apply isolated streams |
| API | Identity dependency, errors, response models | Host models/app/generator and focused tests | Add thin protected workflow and bounded transport shapes |
| Generated contract | Reviewed OpenAPI and generator | Snapshot/client generated outputs | Keep web authority reproducible |
| Architecture/security docs | Implemented seams and protection status | Listed canonical/nearby docs | Record exact composition and remaining limits |
| Planning | Slice/register/packet | Listed artifacts | Keep lifecycle synchronized |

## Contracts and Interfaces

`GET /api/v1/curriculum/placements/{placement_id}/completion` accepts no
learner selector. Its response exposes placement, completed state, bounded
meaning, source digest, rebuild time, and ordered history with source event,
attempt, evidence, exact package/Assessment/item/policy tokens, score, and
completion time. It omits learner/provider IDs, answers, feedback, Audit rows,
storage details, mastery, advice, and recommendation meaning.

## Dependencies and Parallel Safety

WRK-0037 is complete. This packet integrates the stable Assessment,
Learner-model, Audit, and Identity public operations and must finish before the
browser packet consumes the generated client.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact completion | Authorized learner and retained event | GET history | Reconcile Audit, rebuild projection, return exact bounded history | API integration |
| Empty completion | No source event | GET history | Return incomplete with empty history | API integration |
| Missing/forged context | No session or client identity header/field | GET history | Deny before consumer calls or disclosure | security/API |
| Audit failure | Audit conflicts or is unavailable | GET history | Fail closed before projection return | workflow/API |
| Projection failure | Audit succeeds but Learner model fails | GET history | Return bounded unavailable and no fabricated view | workflow/API |
| Unconfigured services | Composition omits either consumer | GET history | Return 503 bounded unavailable | API |
| Generated currency | Host model changes | Run generators/checks | Reviewed snapshot/client are byte-current | contract tests |

## Verification Commands

Run focused API/identity tests, all backend tests, OpenAPI and generated-client
generation/check, web typecheck, architecture/security/docs/planning checks,
and `git diff --check`.

## Documentation and Evidence Update

Record operation ordering, response/denial semantics, migration composition,
generated artifacts, exact counts, docs impact, unsupported profiles, remaining
UI/qualification work, and CAP conformance.

## Stop Conditions

Stop on client-selected learner authority, leakage of private evidence/Audit
rows, business policy in the host, cross-schema reads, a queue requirement,
contract incompatibility, or identity/recovery/cloud scope expansion.

## Required Handoff

Report endpoint and response, ordering/failure behavior, generators, tests,
composition changes, residual gaps, and readiness of WRK-0039.

## Verification Progress

- Added the server-learner-bound exact-placement completion endpoint. It accepts
  no learner selector, calls Audit first, then atomically rebuilds Learner-model
  state, and returns bounded completion/history provenance without learner,
  provider, answer, feedback, Audit-row, storage, mastery, or advice data.
- Local composition now applies the isolated Learner-model and Audit migration
  streams and constructs both consumers from the Assessment public source.
  Missing services, Audit conflict/unavailability, projection failure, missing
  session, and client-authority headers fail closed.
- The reviewed OpenAPI snapshot and generated TypeScript client were regenerated
  and passed byte-current checks; the web application typechecked successfully.
- Nine focused completion/Assessment API tests passed. The complete backend
  suite passed 171 tests with 25 environment-gated skips. A fresh disposable
  PostgreSQL 18.4/same-origin Python composition applied every stream and passed
  two live Chromium scenarios, then removed its exact container and data root.
- Aggregate architecture passed eight fitness functions, security passed ten
  control groups, documentation verified 192 Markdown files and catalogs,
  planning verified 68 artifacts, and the diff check passed with line-ending
  warnings only. Browser history presentation remains WRK-0039.

## Planning History

- 2026-10-15: Authored after Assessment replay, Learner-model projection, and
  Audit references completed; no unresolved decision or CAP drift was found.
- 2026-10-15: Delivered the protected Audit-first completion-history API,
  current generated client, and clean local migration composition.
