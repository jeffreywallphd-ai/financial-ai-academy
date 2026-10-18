---
id: WRK-0191
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0108
capability: CAP-0026
depends_on: [WRK-0190]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/src/generated/api-client/schema.d.ts", "apps/web/tests/contract/client-usage.ts", "apps/web/tests/contract/generated-client.test.mjs", "backend/src/financial_ai_academy/hosts/README.md", "backend/src/financial_ai_academy/hosts/api/app.py", "backend/src/financial_ai_academy/hosts/api/generate_openapi.py", "backend/src/financial_ai_academy/hosts/api/models.py", "backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/application/service.py", "backend/src/financial_ai_academy/modules/audit/public.py", "backend/src/financial_ai_academy/modules/identity/application/service.py", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/integration/api/test_single_profile_accountable_history_api.py", "backend/tests/unit/audit/test_accountable_history_service.py", "backend/tests/unit/identity/test_identity_service.py", "contracts/api/README.md", "contracts/api/openapi.json", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0108-inspect-accountable-history.md", "docs/planning/work-packets/WRK-0191-expose-protected-accountable-history-api.md"]
generated_artifacts: ["apps/web/src/generated/api-client/schema.d.ts", "contracts/api/openapi.json"]
base_revision: 470adfa02528aea677761b0800aa57289390d354
claim_id: WRK-0191:c2179f70-7338-44fb-b22a-fac993728873
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T10:30:37Z
---

# Agent Work Packet: Expose the Protected Accountable-History API

## Objective and Deliverable

Expose the completed Audit accountable-history core through separate protected
inspection and portable-evidence operations, reviewed OpenAPI, and the generated
TypeScript client. Browser, command-line, service, and future headless AI
clients submit the same closed root selector and receive the same authoritative,
purpose-limited document without importing backend internals or reimplementing
redaction, diagnostics, ordering, or digest policy.

The packet adds only local single-profile read/export permissions and stops
before learner-facing presentation or live restart/database qualification.

## Required Context

Before this planning edit, the repository Required Startup was completed and
reported. Review covered planning and architecture-contract context, change
impact, decision readiness, the approved CAP-0026 package, active SLI-0108,
completed WRK-0189 and WRK-0190, frozen accountable-history contracts, Audit
core/public/application seams, Identity permissions, API models/error policy,
OpenAPI/client generation, consumers, tests, and nearest READMEs.

Before implementation, repeat and report the applicable startup gate and
revalidate current authority, exact scope, dependency completion, generated
artifacts, and file ownership.

## Decisions and Assumptions

- The request is the exact frozen `accountable-history/v1` lesson-or-completion
  union. A completion learner is resolved from the opaque server session and is
  never accepted from request data.
- `POST /api/v1/audit/accountable-history` selects `learner_review` on the
  server and requires `audit.history.read` plus `curriculum.lesson.read`.
- `POST /api/v1/audit/accountable-history/export` selects
  `portable_evidence` on the server and requires `audit.history.export` plus
  `curriculum.lesson.read`. Inspection permission alone cannot authorize export.
- Both operations first use the accepted Audit lineage application methods and
  then the completed pure composer. They do not access another module's
  repository, table, or implementation.
- The export response is the exact bounded JSON wrapper. It is composed on
  demand and never retained, signed, encrypted, queued, or written to a path.
- Audit errors stay behind the existing confidential API error boundary.
  Structurally invalid requests fail with bounded HTTP 400 responses before
  request-specific Audit access.
- OpenAPI and the TypeScript schema are generated artifacts and are not
  hand-edited.

## In Scope

- Add application/public operations that read the already authorized real
  lineage and produce either the learner-review document or portable wrapper.
- Add strict Pydantic response models for the frozen root, entries,
  transformations, missing links, diagnostics, redactions, document, and export.
- Add separate protected inspection and export routes with authorization before
  Audit access, session-bound completion identity, no query input, stable
  operation IDs, safe errors, and no caller-selected purpose.
- Add `audit.history.read` and `audit.history.export` to the local
  single-profile permissions without changing identity or tenancy models.
- Regenerate and verify reviewed OpenAPI and TypeScript schemas, including
  direct headless client usage evidence for both operations.
- Test both roots, permission separation, denial ordering, exact mapping,
  malformed/unknown fields, confidential failures, variable bounded history,
  deterministic export, no retained output, and forbidden-field absence.
- Reconcile direct Audit, host, API-contract, module, assurance, planning, and
  generated-client documentation.

## Out of Scope

- Browser routes, components, downloads, styling, disclosures, accessibility
  presentation, or screenshots; WRK-0192 owns that consumer.
- Live PostgreSQL/restart/process/client parity and cumulative slice closure;
  WRK-0193 owns that qualification.
- New roots, arbitrary traversal, pagination, search, bulk export, retained
  files, export history, signing, encryption, recovery, or mutation/repair.
- Owner payloads, lesson bodies, answers, scores, feedback, profile attributes,
  learner selectors, provider data, secrets, locators, paths, raw exceptions,
  private diagnostics, or permission state in a response.
- Organization, tenant, administrator, instructor, support, compliance, legal,
  public-audit, managed-cloud, provider/model, queue, external-action,
  financial-action, advice, or suitability authority.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Audit application/public | four exact root-and-purpose operations over completed lineage and composer seams | keep policy and composition server-authoritative |
| Identity/API | two additive local permissions, strict response models, two protected routes | separate inspect and export authority |
| Contracts/client | reviewed OpenAPI and generated TypeScript plus direct usage assertions | preserve headless/browser parity |
| Tests | focused Audit-service, API, Identity, generated-client, and module evidence | prove purpose, authorization, shape, and confidentiality |
| Docs/planning | only the listed Audit, host, API, architecture, slice, packet, and register sources | record delivered surface and residual browser/live gaps |

No domain contract meaning, persistence, migration, Content or Assessment
implementation, browser feature, design-system, deployment, provider/model, or
unrelated module file is writable.

## Contracts and Interfaces

1. Both request bodies use the frozen exact union: exact published lesson or
   exact retained completion. They do not accept learner, purpose, permissions,
   producer, owner, provider, path, locator, graph, or export settings.
2. Inspection emits the frozen document with purpose `learner_review`; export
   emits the frozen wrapper whose nested document has purpose
   `portable_evidence`. The host maps but does not recompute either result.
3. Authorization occurs before request-specific Audit access. Read and export
   dependencies are distinct and both retain lesson-read authority.
4. Safe failures use the existing envelope and omit rejected values, existence,
   counts, digests, learner/session facts, raw exceptions, and internal paths.
5. Operation IDs are `readAccountableHistory` and
   `exportAccountableHistory`; their reviewed OpenAPI shapes are the only public
   client authority.
6. No operation writes Audit or owner state. Equivalent authorized exports from
   equivalent lineage return identical disclosed content and timestamps derived
   from that lineage.

## Dependencies and Parallel Safety

WRK-0190 is complete with current exact-candidate evidence and no open finding.
This packet changes shared Audit application/public, Identity permission,
API/OpenAPI/generated-client, architecture, slice, and register files, so it is
not parallel-safe with another writer on those paths. WRK-0192 waits for these
exact client operations.

Claim from the current clean base, run packet-start, acquire exact-file leases,
and retain one owner through verification. Approval and reviewer records remain
only in ignored local state.

## Acceptance Scenarios

| Scenario | Expected evidence |
| --- | --- |
| Lesson inspection | An authorized exact lesson request returns the completed learner-review document and frozen digest |
| Completion inspection | The route binds the session learner and returns the bounded completion history without private evidence payload |
| Separate export authority | Inspection-only permission can read but receives confidential 403 on export before Audit access |
| Portable export | An export-authorized caller receives the exact portable wrapper twice with equal canonical content and no retained record |
| Closed server purpose | Caller-supplied purpose or export option is rejected; each route selects its one purpose |
| Confidential denial | Missing session, missing permission, another learner, unknown root, malformed request, or unavailable Audit discloses no existence or validation detail |
| Variable history | Zero-to-many valid sources, bounded transformations/gaps, Unicode identifiers, and optional facts serialize without fixture-count assumptions |
| Forbidden fields | Learner/session, lesson body, answer, score, feedback, locator, provider, secret, storage, path, permission, and raw diagnostic fields are absent |
| Headless client | The generated public client compiles direct calls for both operations with no browser feature or backend import |
| Boundary direction | The host uses Audit public methods; Audit reaches Content/Assessment only through accepted lineage ports and no repository shortcut |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit/test_accountable_history_service.py backend/tests/integration/api/test_single_profile_accountable_history_api.py backend/tests/unit/identity/test_identity_service.py -q`
- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit backend/tests/integration/api/test_single_profile_accountable_history_api.py backend/tests/contract/accountable_history -q`
- `backend\.venv\Scripts\python.exe -m financial_ai_academy.hosts.api.generate_openapi --check`
- run the pinned generated-client check, contract test, TypeScript compilation,
  and zero-warning lint commands selected by the controller
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Freeze an exact candidate, run the controller-selected affected plan and
qualifying verification, then obtain one independent technical disposition.
Broader browser and live restart/containment work remains in WRK-0192 and
WRK-0193 rather than becoming an automatic full-suite gate here.

## Stop Conditions

Stop for stale CAP authority; unresolved identity, tenancy, public-hosting,
retention, encryption, signing, recovery, legal/commercial, or managed-cloud
policy; organization/admin access; a breaking frozen contract; another module's
table or implementation; copied owner payload; caller-selected learner/purpose;
unbounded traversal/export; retained output; source locator or confidential
evidence disclosure; migration; new root; external action; file collision; or
material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
generated formatting, valid count/order/Unicode variation, nonfunctional
styling, or another inconsequential issue. Fix bounded defects locally or defer
presentation polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0108.WRK-0191`; exact candidate and receipt; routes,
permissions, server-selected purpose and learner binding; response/export
contracts; error/confidentiality behavior; OpenAPI/client reproduction; focused
and architecture/security evidence; documentation impact; migration/rollback;
assumptions, residual browser/live gaps, CAP conformance, and unresolved
decisions. Confirm no retained export, UI, provider/model, external action,
tenancy/admin, or financial authority changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0190 completion. The packet
  exposes separate protected review and export operations through one
  server-authoritative core and generated client, preserves API/headless parity,
  and leaves browser consumption and cumulative live qualification to dependent
  packets without adding a lower-level approval.
- 2026-10-18: Activated from clean base `470adfa` after confirming current CAP
  authority, completed dependency, resolved local decision posture, exact
  generated/public write scope, and no active file-ownership collision.
