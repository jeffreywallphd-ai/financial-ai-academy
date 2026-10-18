---
id: WRK-0183
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0106
capability: CAP-0026
depends_on: [WRK-0182]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/learning-lineage.e2e.ts", "backend/src/financial_ai_academy/modules/audit/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0106-trace-learning-content-and-evidence-lineage.md", "docs/planning/work-packets/WRK-0183-qualify-live-learning-lineage.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/README.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: f46c7c638c44913481a38295f42d2ed8eef9c1c9
claim_id: WRK-0183:f9adb934-f2ff-421d-87c7-824ba19faea5
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T08:33:43Z
---

# Agent Work Packet: Qualify Live Learning Lineage

## Objective and Deliverable

Close SLI-0106 with isolated live evidence that the completed protected
learning-lineage API returns equivalent canonical documents to the reviewed
generated TypeScript client and an ordinary authenticated HTTP client for both
accepted root kinds. Prove stable exact replay across normal host restart,
confidential denial, non-Identity database and owner-file containment, flexible
bounded graph handling, and bounded cleanup in the existing local qualification
topology.

This packet changes qualification and direct evidence only. It does not add a
learner-facing lineage page, public operation, schema, lineage root, storage,
migration, provider/model behavior, or alternate authorization path.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was repeated and reported. The review covered the routed
delivery-planning and architecture-contract packs; change-impact and decision-
readiness rules; the approved CAP-0026 package; active SLI-0106; completed
WRK-0180 through WRK-0182; the protected route and generated client; the local
composition and live runner; replay, architecture, security, and cleanup tests;
direct Audit/provenance/assurance documentation; and nearest contributor
READMEs.

CAP-0026 authority remains current, WRK-0182 is complete with a qualifying
exact-candidate receipt and accepted independent review, and no durable decision
applies. This is the final dependency-ordered seam already enumerated by
SLI-0106 and requires no lower-level approval.

## Decisions and Assumptions

- The approved fixture, local single-profile session, protected API, reviewed
  OpenAPI, and generated TypeScript client are the accepted live surface.
- The generated-client journey obtains exact lesson and completion selectors
  from public live responses. Qualification must not hard-code a production
  digest, learner ID, database row, or incidental node/edge count.
- Exact replay means complete canonical lineage equality, including ordering
  and view digest, before and after normal restart without reseeding. Server-
  issued session and timestamps outside the lineage document are not compared.
- Browser-process and ordinary HTTP sessions may add Identity rows. The
  qualification requires every non-Identity schema and the bounded owner object
  tree to remain exact across repeated lineage reads once the first lineage
  request has deterministically reconciled the retained completion Audit
  reference.
- Contract/core/API tests remain direct evidence for malformed graphs,
  changed-same-identity conflicts, incomplete links, bounds, and varied valid
  Unicode/source shapes. Live assertions compose that evidence without
  inventing a fixed fixture topology.

## In Scope

- Add one non-presentational Playwright qualification that imports the generated
  API client, creates its own opaque session, resolves the live exact lesson and
  retained completion selectors through public operations, reads both lineage
  roots, and captures only the two closed public documents.
- Compare the generated-client documents with a separate ordinary authenticated
  HTTP session, including exact root/resource identities, canonical ordering,
  view digests, flexible valid node/edge/incomplete-link arrays, and absence of
  private learner, answer, feedback, permission, provider, path, and locator
  fields.
- Read both roots repeatedly and after a normal application restart without
  reseeding; require exact canonical equality and confidential missing-session,
  query-selector, and guessed-completion failures.
- Compare privacy-safe non-Identity PostgreSQL fingerprints and the bounded
  application-data file tree before and after the lineage phase and restart
  reads. Confirm no duplicate Audit record or owner mutation is introduced.
- Extend replay/unit tests for capture validation, generated/direct parity,
  changed meaning, restart mismatch, containment, flexible graph counts/order,
  and cleanup-path behavior without requiring Docker for routine feedback.
- Extend architecture checks so the cumulative runner must use only the public
  route and generated client and cannot import backend lineage internals.
- Run the focused provenance/core/API/client, replay, architecture, security,
  documentation, planning, whitespace, complete local live, affected-candidate,
  independent-review, and aggregate-readiness checks.
- Reconcile direct Audit, provenance-contract, architecture-verification,
  live-runner, slice, packet, and register evidence and close SLI-0106.

## Out of Scope

- Learner-facing pages, visual graphs, export/download, retention controls,
  administrative inspection, styling, accessibility presentation, or CAP-0031
  polish.
- New lineage roots or adapters for Project, practice, portfolio, market data,
  datasets, models, recommendations, jobs, providers, or administration.
- Owner-state mutation, graph repair, pagination, search, latest-version
  aliases, bulk traversal, arbitrary query languages, or unrestricted Audit.
- New database/object storage, migrations, indexes, queues, background workers,
  caches, recovery products, legal hold, signing, immutable infrastructure, or
  managed-cloud behavior.
- Tenancy, organization policy, identity-provider choice, provider/model use,
  external retrieval/execution, licensing, financial action, personalized
  advice, public hosting, or production availability claims.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Generated-client live test | one new non-UI Playwright file | prove typed client and direct HTTP parity |
| Cumulative runner/replay | bounded capture, public reads, exact comparison, containment, restart, cleanup, and unit evidence | qualify the existing route without product changes |
| Architecture evidence | focused source-boundary assertion | keep the live seam on public APIs/generated client |
| Audit/provenance/assurance docs | direct live-evidence and residual-gap statements | record only what the qualification proves |
| Planning | packet, SLI-0106, and register lifecycle/evidence | close the dependency-ordered slice |

No implementation, public contract, generated schema/client, dependency,
migration, deployment topology, fixture meaning, browser route/component,
design-system, or unrelated documentation path is writable.

## Contracts and Interfaces

1. The generated test must call only reviewed operations and generated request/
   response types. Backend imports or fixture-file parsing are forbidden.
2. The lesson selector comes from the exact live published lesson response. The
   completion selector comes from retained public completion history for the
   server-bound learner; neither client supplies learner or permission values.
3. Direct and generated clients receive byte-equivalent JSON meaning for each
   root. Validation permits every contract-valid bounded count/order/Unicode/
   incomplete-link shape and rejects unknown or private fields.
4. Missing session, query input, and guessed completion context fail through
   bounded public errors without chain counts, identifiers, digests, learner,
   owner payload, or storage detail.
5. Repeated and restarted reads preserve the complete canonical document and
   view digest. The host restarts against retained PostgreSQL and object roots
   with no fixture seed or external request.
6. Non-Identity database fingerprints and the bounded application-data tree
   remain exact during lineage-only reads. Cleanup removes only runner-owned
   captures, browser output, database/container/network, and temporary roots.

## Dependencies and Parallel Safety

WRK-0182 is complete and supplies the protected route, additive permissions,
runtime composition, reviewed OpenAPI, and generated client. This packet edits
the shared cumulative live runner, replay tests, architecture assertions,
assurance, and SLI/register files, so it is not parallel-safe with another
writer on those paths. Begin from a clean base, claim once, run packet-start,
and acquire one exclusive lease over the declared files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact lesson parity | The approved exact lesson is published | Generated and ordinary clients derive and post the exact selector | Both return the same canonical lesson lineage without body or locator data | Playwright/headless/live |
| Exact completion parity | One retained knowledge-check completion exists | Both clients derive its exact evidence and occurrence | Both return the same evidence/Audit/Assessment/Content chain without answer, score, feedback, or learner data | Playwright/headless/PostgreSQL |
| Exact replay and restart | Both accepted views were captured | Reads repeat and the local host restarts without seed flags | Complete documents and view digests remain exact and no duplicate Audit record appears | live/replay |
| Confidential denial | Session is absent, query input is present, or completion context is guessed | The public route is called | A bounded 400/401/confidential failure exposes no chain or private detail | live/security |
| Owner containment | Lineage-only phases execute | Database and file fingerprints are compared | Non-Identity rows and owner files remain exact | live/PostgreSQL/filesystem |
| Flexible valid graph | Node, edge, source, Unicode, ordering, optional time, and incomplete-link shapes vary within frozen bounds | Validators and parity assertions run | Valid shapes qualify without fixture counts, prose, snapshots, or incidental storage order | contract/replay anti-rigidity |
| Cleanup | Qualification succeeds or fails | Finally paths run | Only named runner-owned resources and captures are removed | live/control plane |

## Verification Commands

- focused provenance, learning-lineage core, protected API, Identity, OpenAPI,
  generated-client, TypeScript, and lint checks from WRK-0180 through WRK-0182
- `python tests/e2e/approved-lesson/test_replay_qualification.py`
- focused Playwright execution of `learning-lineage.e2e.ts` through the existing
  isolated host, followed by the complete approved-lesson runner
- `python tests/architecture/test_approved_lesson_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Use the repository-prepared Node 24/npm 10.8.2, backend Python environment,
pinned Chromium, and disposable PostgreSQL 18.4 composition. Freeze one exact
candidate, run the tracked affected plan, and obtain one independent technical
disposition. No external or production resource is authorized.

## Stop Conditions

Stop for a functional, security, confidentiality, parity, restart, containment,
or cleanup defect that requires a public contract or product change; conflicting
canonical authority; missing current CAP authority; another module's internal
table/implementation; copied owner payload; a new root or migration; unbounded
traversal/export; an external action; a write-scope collision; or material
CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
generated formatting, valid graph count/order variation, nonfunctional styling,
or another inconsequential issue. Fix bounded test/documentation items locally
or defer presentation polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0106.WRK-0183`; exact candidate and receipt; generated and
ordinary client parity; exact lesson/completion roots and view digests; denial,
restart, containment, anti-rigidity, and cleanup evidence; focused and complete
checks; documentation impact; migration/rollback status; assumptions; residual
gaps; slice/CAP conformance; and unresolved decisions. Confirm no UI, provider/
model, external-action, tenancy, financial, storage, or authorization behavior
changed.

## Completion Evidence

- Exact candidate: `a80214ea8370e863301c715742b0bb6fe00f97d8`.
- Qualifying affected-check receipt:
  `sha256:9ea5f1fe0fc606c35700552da6a8157c03e18e076670333cdc73619822e27a3b`.
- The generated TypeScript client and a separate ordinary authenticated HTTP
  session returned the same complete canonical documents for the exact lesson
  and completion roots. The live evidence run produced lesson view digest
  `5a0f8c34d2cea21440029dc0db77cc2e171b9f5ff9308ade8ecb7de14416d97b`
  and completion view digest
  `d781da1da54d7ab2b4f0f9e73977cc199ec359dfa59913e0e756c8c597e3dfc6`.
- Missing session, query input, and guessed completion context failed with
  bounded confidential responses. Repeated public reads and a normal host
  restart without reseeding preserved the complete documents and view digests.
  Non-Identity database and bounded application-data fingerprints remained
  exact after the first deterministic Audit reconciliation.
- Flexible graph replay, disagreement, private-field, one-node, and restart-
  drift evidence passed 90 tests; the focused architecture suite passed 16
  tests plus four subtests; the focused provenance/core/API/Identity suite
  passed 64 tests. TypeScript, zero-warning lint, architecture, ten security
  control groups, documentation, planning, whitespace, and all 30 aggregate-
  readiness checks passed.
- The exact-candidate affected plan selected eight checks; all passed,
  including the cumulative disposable PostgreSQL 18.4, generated-client,
  headless, normal-restart, containment, and cleanup workflow. Independent
  review accepted the candidate with no actionable finding.
- No migration, rollback action, dependency, product implementation, UI,
  provider/model, external action, tenancy, financial authority, storage
  topology, or public contract changed. Browser presentation, export,
  retention, public hosting, and managed-cloud posture remain later work.

## Planning History

- 2026-10-18: Authored just in time after WRK-0182 completion. The packet uses
  the existing generated client and cumulative disposable topology to qualify
  the frozen two-root public seam and close SLI-0106 without adding product
  behavior, a heavyweight routine gate, or lower-level approval.
- 2026-10-18: Activated from clean base `f46c7c6` with one bounded owner and an
  exclusive lease over the exact qualification, evidence, and planning files.
- 2026-10-18: Submitted exact candidate `a80214e` after focused and direct live
  evidence passed. The tracked eight-check affected plan then produced a
  qualifying receipt against that unchanged commit.
- 2026-10-18: Completed at exact candidate `a80214e` after accepted independent
  review and a 30-of-30 aggregate-readiness pass. The packet closes SLI-0106
  without adding presentation, export, retention, or managed-cloud scope.
