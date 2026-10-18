---
id: WRK-0182
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0106
capability: CAP-0026
depends_on: [WRK-0181]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "backend/src/financial_ai_academy/bootstrap/composition.py", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_lineage_api.py", "backend/tests/unit/identity/test_identity_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0106-trace-learning-content-and-evidence-lineage.md", "docs/planning/work-packets/WRK-0182-expose-protected-learning-lineage-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 7d6393a5d78c0e0ac80a8fd05b07980c68578a29
claim_id: WRK-0182:3bbe039c-ab35-4940-9f88-223c92b2d56d
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T08:15:24Z
---

# Agent Work Packet: Expose the Protected Learning-Lineage API

## Objective and Deliverable

Expose the accepted Audit learning-lineage core through one protected,
transport-neutral FastAPI operation and the reviewed generated TypeScript
client. Browser, command-line, service, and future headless AI clients submit
the same closed `provenance-envelope/v1` root request and receive the same
bounded `LineageView` without backend imports or a browser-only policy path.

The packet also composes the accepted Content lineage adapter into the local
application and adds the least new single-profile read capability needed for
the operation. It stops before live PostgreSQL/restart qualification and does
not add learner-facing presentation.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was repeated and reported. The review covered delivery-
planning and architecture-contract context; the change-impact matrix; decision
readiness; the approved CAP-0026 package; refined SLI-0106; completed WRK-0180
and WRK-0181; provenance schemas; Audit public/core/adapter seams; Identity
permissions; application composition; API host/models/error policy; OpenAPI and
TypeScript generation; affected consumers/tests; and nearest READMEs.

Before implementation, repeat and report the applicable startup gate and
revalidate current authority, exact scope, dependencies, and file ownership.

## Decisions and Assumptions

- WRK-0181's exact public operations and `LineageView` remain the application
  authority. The host maps but does not recompute, reorder, infer, or repair a
  lineage graph.
- The protected operation is `POST /api/v1/audit/learning-lineage` with the
  existing closed request union: exact published lesson or exact retained
  knowledge-check completion. A completion learner is always supplied from the
  resolved server session and never accepted from the request document.
- The operation requires both `audit.lineage.read` and
  `curriculum.lesson.read`. The first is an additive application permission for
  lineage disclosure; the second preserves the existing exact learning-
  resource read boundary. Neither permission is caller-selectable.
- `AuditError(INVALID_CONTEXT)` remains confidential at the current API error
  boundary. Structural or type-invalid request documents fail as HTTP 400
  before Audit access; absent or mismatched retained learner context does not
  reveal resource existence.
- The response mirrors the frozen executable lineage schema exactly. OpenAPI
  and the TypeScript schema are generated artifacts and are never hand-edited.
- The local composition adds `ContentLearningLineageSource(content)` to
  `AuditService`; it creates no owner-table read, migration, or new data copy.

## In Scope

- Add strict discriminated Pydantic request models for the two frozen root
  kinds and closed response models for references, sources, envelopes, nodes,
  edges, incomplete links, root, bounds, and canonical view digest.
- Add one protected API route with authorization-before-Audit access,
  completion learner binding from the server session, strict request fields,
  bounded safe errors, stable operation ID, and no alternate selector.
- Add `audit.lineage.read` to the built-in single-profile permission set and
  prove the route also requires existing lesson-read authority.
- Compose the existing Content public adapter into Audit at the application
  root and update the OpenAPI schema fixture used by generation.
- Regenerate and verify the reviewed OpenAPI snapshot and generated TypeScript
  schema. Add compile-time/direct-client evidence that the operation is usable
  without a browser feature or backend import.
- Add focused API tests for both roots, exact mapping, denial ordering,
  malformed/unknown fields, confidential missing context, unavailable service,
  no payload leakage, flexible valid graph shape, and OpenAPI/client stability.
- Reconcile direct Audit/API/contract/module/assurance/planning documentation.

## Out of Scope

- Learner-facing components, routes, visual graphs, history pages, styling,
  accessibility presentation, download, export, or administrative inspection.
- Live host/PostgreSQL/restart/client parity, process observation, cleanup, or
  full slice closure; WRK-0183 owns those exact qualification effects.
- New provenance root kinds, arbitrary graph query or traversal, graph writes,
  mutation/repair, pagination, latest-version aliases, search, bulk reads, or
  unrestricted Audit access.
- Owner-table access, copied lesson/evidence payloads, answers, feedback,
  scores, raw learner identity, source locators, provider data, secrets, paths,
  permission state, or private diagnostics.
- Tenancy, organization policy, managed cloud, retention/recovery, signing,
  legal hold, provider/model use, queue, external execution, financial action,
  personalized advice, or public-hosting policy.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Composition | inject the completed Content lineage source into Audit | make the accepted shared core available at runtime |
| Identity/API | additive read permission, strict request/response models, one protected route and schema stub | bind server authority and publish one transport |
| Contracts/client | reviewed OpenAPI snapshot and generated TypeScript schema plus direct usage assertions | preserve browser/headless parity |
| Tests | focused Identity, API, generated-client, and boundary evidence | prove authorization, shape, confidentiality, and reproduction |
| Architecture/docs/planning | exact listed Audit, host, module, contract, assurance, slice, packet, and register sources | record implemented ownership and remaining live gap |

No domain meaning, persistence, migration, browser feature, design system,
deployment, provider/model, or unrelated module file is writable.

## Contracts and Interfaces

1. The request is the exact frozen `schema_version: "1.0.0"` discriminated
   union. Published lesson requires package ID, version, and lowercase SHA-256
   digest. Completion requires placement, evidence ID, and positive occurrence.
2. The response preserves the frozen root, node, edge, incomplete-link,
   truncation, ordering, timestamp, integrity, and view-digest meaning without
   adding transport metadata or omitting required nullability.
3. Authorization happens before request-specific Audit access. The client may
   not submit learner, actor, session, permission, producer, owner, provider,
   path, locator, arbitrary relation, or graph payload.
4. Published-lesson requests call `read_published_lesson_lineage`; completion
   requests call `read_knowledge_check_completion_lineage` with the resolved
   learner ID. The host never calls repositories or owner implementations.
5. Safe failures use the existing API error envelope and omit rejected input,
   graph counts, identifiers, digests, source existence, and raw exceptions.
6. OpenAPI operation ID `readLearningLineage` and the generated TypeScript
   request/response shapes are the only public client authority.

## Dependencies and Parallel Safety

WRK-0181 is complete with a qualifying exact-candidate receipt and no open
technical finding. This packet changes shared composition, Identity permission,
API/OpenAPI/generated-client, architecture, slice, and register files, so it is
not parallel-safe with another writer on those paths. WRK-0183 waits for this
exact route and client surface.

Claim from the current clean base, run packet-start, acquire exact-file leases,
and retain one owner through verification. Approval and reviewer records remain
only in ignored local state.

## Acceptance Scenarios

| Scenario | Expected evidence |
| --- | --- |
| Exact lesson root | An authorized caller posts the exact lesson selector and receives the accepted bounded Content/source graph and digest |
| Exact completion root | The same route binds the session learner and returns the accepted evidence/Audit/Assessment/Content chain |
| Protected read | Missing session, missing lineage permission, or missing lesson permission returns confidential 401/403 before Audit access |
| Closed request | Wrong discriminator, unknown field, learner/permission selector, malformed identifier/version/digest, bool/nonpositive occurrence, query, or alternate payload returns bounded 400 |
| Bounded owner failure | Missing/conflicting/unavailable retained meaning maps through the safe existing error envelope without partial lineage or resource disclosure |
| Confidential response | No learner/session, lesson body, answer, score, feedback, locator, storage/provider, permission, or private diagnostic appears |
| Flexible valid graph | Zero-to-many sources, valid Unicode, variable bounded nodes/edges, incomplete links, and canonical order serialize without fixture-count assumptions |
| Headless client parity | Reviewed OpenAPI and generated TypeScript expose `readLearningLineage`; a direct non-browser client compiles against the same operation |
| Runtime composition | Local composition reaches Content only through its public operation and Audit only through public application methods |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/integration/api/test_single_profile_lineage_api.py backend/tests/unit/identity/test_identity_service.py -q`
- `backend\.venv\Scripts\python.exe -m financial_ai_academy.hosts.api.generate_openapi --check`
- run the pinned TypeScript client generator in check mode, generated-client
  contract tests, TypeScript compilation, and zero-warning lint
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Freeze an exact candidate, run the tracked affected-check plan and qualifying
verification, then obtain one independent technical disposition. Broader live,
restart, and cleanup work remains WRK-0183 rather than an automatic full-suite
gate.

## Stop Conditions

Stop for stale CAP authority; an unresolved identity/tenancy/public-hosting
decision; a need for organization policy; a breaking contract; another module's
table or implementation; copied owner payload; caller-selected learner or
permission; unbounded traversal/export; source locator or confidential evidence
disclosure; a migration; a new root kind; an external action; a write-scope
collision; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
generated formatting, valid graph variation, nonfunctional styling, or another
inconsequential issue. Fix bounded items locally or defer presentation polish
to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0106.WRK-0182`; exact candidate and receipt; route,
permission, server-bound learner, request/response contracts, error and
confidentiality behavior, composition, OpenAPI/generated-client reproduction,
focused and architecture/security evidence, documentation impact,
migration/rollback status, assumptions, residual live gap, CAP conformance, and
unresolved decisions. Confirm no UI, provider/model, external-action, tenancy,
or financial authority changed.

## Completion Evidence

- Exact candidate: `45df26ab19ad75929ec65b4f288230c3b5209550`.
- Qualifying affected-check receipt:
  `sha256:54246d7d68cd64570547bad87125c8e59e0cd6aaade11ff9e4c928a20486f152`.
- `POST /api/v1/audit/learning-lineage` accepts only the frozen exact lesson or
  completion root union. Completion learner identity is taken from the opaque
  server session, and both `audit.lineage.read` and
  `curriculum.lesson.read` are required before Audit access.
- The response maps the canonical bounded `LineageView` and excludes learner,
  session, permission, lesson body, answer, score, feedback, locator, provider,
  storage, path, and private diagnostic data. Runtime composition reaches
  Content only through the accepted Audit adapter and public Content operation.
- The focused API and Identity suite passed 15 tests. OpenAPI and generated-
  client reproduction, direct TypeScript client use, typecheck, zero-warning
  lint, architecture fitness, ten security control groups, documentation,
  planning, whitespace, and all 30 aggregate-readiness checks passed.
- The first affected receipt exposed only a shell runtime mismatch (Node 20/npm
  11). Rebinding the existing repository-prepared Node 24/npm 10.8.2 runtimes
  produced the qualifying receipt against the unchanged exact candidate.
- Independent technical review accepted the candidate with no actionable
  material finding. No migration or rollback action is required, and no UI,
  provider/model, external action, tenancy, financial, or alternate authority
  was introduced. Live restart and containment evidence remains WRK-0183.

## Planning History

- 2026-10-18: Authored just in time after WRK-0181 completion. The packet
  exposes the frozen two-root application seam through one protected API and
  generated client, adds only a bounded read permission, and preserves live
  restart/containment qualification for WRK-0183 without lower-level approval.
- 2026-10-18: Submitted exact candidate `45df26a` after the focused API and
  Identity suite, OpenAPI and generated-client reproduction, TypeScript
  compilation and lint, architecture, security, documentation, planning,
  whitespace, and aggregate-readiness checks passed.
- 2026-10-18: Completed at exact candidate `45df26a` with a qualifying receipt
  and accepted independent review. The protected browser/headless seam is now
  stable for WRK-0183 live restart and containment qualification.
