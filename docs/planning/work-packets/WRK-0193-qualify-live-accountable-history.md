---
id: WRK-0193
kind: work-packet
planning_status: verifying
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0108
capability: CAP-0026
depends_on: [WRK-0192]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/tests/browser/approved-lesson/accountable-history.e2e.ts", "backend/src/financial_ai_academy/modules/audit/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0108-inspect-accountable-history.md", "docs/planning/work-packets/WRK-0193-qualify-live-accountable-history.md", "tests/architecture/test_approved_lesson_boundaries.py", "tests/e2e/approved-lesson/README.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: []
base_revision: 4ea3269cb6ca1c336007799689dec3534ff3814c
claim_id: WRK-0193:9ff50d24-ea05-4731-b081-4acc5106e569
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T11:21:49Z
---

# Agent Work Packet: Qualify Live Accountable History

## Objective and Deliverable

Close SLI-0108 with isolated live evidence that the completed protected
accountable-history inspection and export operations return equivalent exact
documents to the reviewed generated TypeScript client and an ordinary
authenticated HTTP client for both lesson and completion roots. Prove repeated
and normal-restart stability, confidential denial, separate read/export
behavior, purpose-limited disclosure, read-only owner-state containment, safe
browser consumption, flexible valid shapes, and bounded cleanup in the existing
local qualification topology.

This packet changes qualification and direct evidence only. It does not add or
change product behavior, a public contract, browser presentation, storage,
retention, identity, permission, provider, model, or deployment topology.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered routed
delivery-planning, API/security/testing/deployment/interface, and provenance
context; the change-impact matrix and decision-readiness register; the approved
CAP-0026 package; active SLI-0108; completed WRK-0189 through WRK-0192; the
frozen accountable-history contract and compatibility corpus; pure Audit
composer; protected routes, generated client, runtime browser validator, and
learner panel; the cumulative local runner and replay tests; architecture,
security, cleanup, and direct Audit/provenance documentation; and nearest
contributor READMEs.

CAP-0026 authority remains current, WRK-0192 is complete, and no durable
decision applies. This is the final dependency-ordered seam already enumerated
by SLI-0108 and requires no slice- or packet-level approval.

## Decisions and Assumptions

- The approved lesson fixture, local single-profile session, protected public
  operations, reviewed OpenAPI/generated client, and disposable PostgreSQL
  topology are the accepted live surface.
- Exact lesson and completion selectors come from live protected public
  responses. No test may hard-code a production digest, learner identity,
  database row, or incidental entry count.
- Inspection equality means complete canonical `learner_review` document
  equality. Export equality means complete canonical `portable_evidence`
  wrapper equality, including the server-selected purpose and disclosed-
  content digest, when repeated before and after a normal restart.
- The browser qualification uses the generated client directly and validates
  the same closed response and export shapes used by the learner panel. The
  existing component and focused Chromium suites remain direct evidence for
  human rendering, keyboard, focus, reflow, themes, accessibility, and local
  download cleanup.
- Accountable-history operations are read-only. Once the existing lineage root
  is available, inspection and export must leave every non-Identity schema and
  the bounded application-data tree exact.
- Direct contract/core/API evidence remains authoritative for varied valid
  counts, diagnostics, missing links, redactions, malformed graphs, permission
  separation, and secret rejection. Live assertions compose that evidence
  without freezing fixture prose, array counts, or incidental order.

## In Scope

- Add one non-presentational Playwright qualification that imports only the
  generated client, creates its own opaque session, derives exact lesson and
  completion roots through public operations, reads and exports both roots,
  validates bounded public shapes, and writes one bounded capture.
- Compare generated-client documents and exports with a separate ordinary
  authenticated HTTP session, including exact roots, purposes, ordering,
  digests, transformations, gaps, diagnostics, redactions, and absence of
  answers, feedback, learner/session/permission facts, provider payloads,
  paths, locators, storage details, and internal diagnostics.
- Repeat both root reads and exports and repeat them after a normal application
  restart without reseeding. Require exact equality and confidential missing-
  session, query-selector, malformed-root, and guessed-completion failures.
- Compare privacy-safe non-Identity PostgreSQL fingerprints and the bounded
  application-data tree before and after inspection/export and restart reads.
  Confirm no Audit business copy, retained export, duplicate lineage reference,
  or owner mutation is introduced.
- Extend replay/unit evidence for capture closure, generated/direct parity,
  purpose/root/digest disagreement, changed meaning, restart mismatch,
  containment, flexible valid arrays, forbidden-field absence, and cleanup
  behavior without requiring Docker for routine feedback.
- Extend architecture checks so the live seam must use only protected public
  routes and the generated client and cannot import backend accountable-history
  internals or write an unbounded capture.
- Run focused accountable-history contract/core/API/client/browser evidence;
  replay, architecture, security, documentation, planning, design, learner-
  language, whitespace, complete local live, exact-candidate affected, and
  aggregate-readiness checks.
- Reconcile direct Audit, provenance-contract, architecture-verification,
  live-runner, slice, packet, and register evidence and close SLI-0108.

## Out of Scope

- Product implementation, schemas, compatibility meaning, OpenAPI or generated
  client regeneration, permissions, identity, browser components, styling,
  downloadable-content changes, storage, migration, or dependency changes.
- New roots, search, pagination, bulk export, import, history mutation or
  repair, retained export, signing, encryption, immutable storage, legal hold,
  retention/deletion policy, recovery products, or managed-cloud behavior.
- Organization, tenant, administrator, instructor, support, compliance, legal,
  public-audit, or external-party access.
- Provider/model use, external retrieval or execution, licensed market data,
  financial action, personalized advice, suitability, mastery, certification,
  public hosting, production scale, or availability claims.
- Optional wording or visual polish suitable for CAP-0031.

## Expected File and Boundary Impact

| Area | Allowed change | Reason |
| --- | --- | --- |
| Generated-client live test | one new non-UI Playwright file | prove typed generated-client/direct HTTP inspection and export parity |
| Cumulative runner/replay | bounded capture, strict public validation, repeat/restart comparison, containment, cleanup, and unit evidence | qualify the existing operations without product changes |
| Architecture evidence | focused source-boundary and capture assertion | keep qualification on protected public APIs and bounded local evidence |
| Audit/provenance/assurance docs | direct live-evidence and residual-gap statements | record only what the qualification proves |
| Planning | packet, SLI-0108, and register lifecycle/evidence | close the dependency-ordered slice |

No implementation, contract, generated schema/client, dependency, migration,
deployment topology, fixture meaning, product browser file, design-system, or
unrelated documentation path is writable. A discovered functional defect must
be routed to one bounded dependent correction packet before this packet closes.

## Contracts and Interfaces

1. The browser test calls only reviewed generated operations and types. The
   cumulative runner calls only protected public HTTP routes; neither imports
   backend accountable-history implementation or reads fixture/database facts
   to construct a request.
2. Lesson and completion selectors come from exact live protected responses.
   Learner, purpose, permission, latest-version, provider, and storage authority
   remain server-bound.
3. Generated and ordinary clients receive equal closed inspection and export
   documents for each root. Validation accepts every contract-valid bounded
   count, Unicode string, safe gap/diagnostic/redaction combination, and rejects
   unknown, private, or inconsistent data.
4. Inspection and export remain separate public calls. Missing session, query
   input, malformed roots, and guessed completion context fail without
   existence, learner, permission, chain, diagnostic, or storage disclosure.
5. Repeated and normally restarted reads preserve complete documents and
   digests. No export file or platform export record is retained by the server.
6. Non-Identity database fingerprints and the bounded application-data tree
   remain exact during accountable-history-only operations. Cleanup removes
   only runner-owned captures, browser output, database/container/network, and
   temporary roots.

## Dependencies and Parallel Safety

WRK-0192 is complete and supplies the generated-client-only learner panel and
strict runtime response closure over the completed protected operations. This
packet edits the shared cumulative live runner, replay tests, architecture
assertions, assurance, and SLI/register files, so it is not parallel-safe with
another writer on those paths. Begin from a clean base, claim once, run the
packet-start control, and acquire one exclusive lease over the declared files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Exact lesson parity | The approved exact lesson is published | Generated and ordinary clients derive, inspect, and export its exact root | Both receive the same purpose-limited documents without lesson body or locator data | Playwright/headless/live |
| Exact completion parity | A retained knowledge-check completion exists | Both clients derive, inspect, and export its evidence ID and occurrence | Both receive the same bounded history without answer, feedback, score, or learner data | Playwright/headless/PostgreSQL |
| Separate operations | Inspection is valid and export is requested independently | The two reviewed operations run | Server-selected purposes remain exact and no inspection response becomes a retained export | API/live |
| Exact replay and restart | Both roots and purposes were captured | Operations repeat and the host restarts without seed flags | Complete documents, wrappers, and digests remain exact | live/replay |
| Confidential denial | Session is absent or a query, malformed, or guessed root is supplied | A public operation is called | A bounded denial exposes no private, permission, lineage, provider, or storage detail | live/security |
| Read-only containment | Inspection and export phases execute | Database and file fingerprints are compared | Non-Identity rows and bounded owner files remain exact | live/PostgreSQL/filesystem |
| Flexible valid history | Entry, transformation, gap, diagnostic, redaction, Unicode, and timestamp shapes vary within frozen bounds | Validators and parity assertions run | Valid shapes qualify without fixture counts, exact prose, snapshots, or incidental storage order | contract/replay anti-rigidity |
| Accessible browser behavior retained | The live API qualification is combined with focused panel evidence | Full affected checks run | Human content, actions, focus, reflow, themes, forced colors, reduced motion, and download cleanup remain usable | component/Chromium/design |
| Cleanup | Qualification succeeds or fails | Finally paths run | Only named runner-owned resources and captures are removed | live/control plane |

## Verification Commands

- focused accountable-history contract, compatibility, core, application,
  protected API, Identity, OpenAPI, generated-client, runtime model, component,
  and lesson Chromium checks from WRK-0189 through WRK-0192
- `python tests/e2e/approved-lesson/test_replay_qualification.py`
- focused Playwright execution of `accountable-history.e2e.ts` through the
  existing isolated host, followed by the complete approved-lesson runner
- `python tests/architecture/test_approved_lesson_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/content/check_learner_language.py --changed`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Use the repository-prepared Node 24/npm 10.8.2, backend Python environment,
pinned Chromium, and disposable PostgreSQL 18.4 composition. Freeze one exact
candidate and run the tracked affected plan. No external or production resource
is authorized or claimed. Verification and review records remain only in
ignored local control-plane storage.

## Stop Conditions

Stop for a functional, security, accessibility, confidentiality, parity,
restart, containment, or cleanup defect that requires a public contract or
product change; conflicting canonical authority; stale CAP authority; another
module's internal table or implementation; copied owner payload; a new root,
permission, persistence path, migration, or dependency; retention, legal,
encryption, signing, recovery, or immutable-storage authority; external action;
file collision; or material CAP-0026/SLI-0108 drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
generated formatting, valid count/order/Unicode variation, nonfunctional
styling, or another inconsequential issue. Fix bounded qualification or
documentation defects locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0108.WRK-0193`; exact candidate and local qualifying
evidence; generated and ordinary client parity; lesson/completion inspection
and export equality; denial, purpose limitation, restart, containment,
anti-rigidity, accessibility, and cleanup evidence; focused and complete
checks; documentation impact; migration/rollback status; assumptions; residual
gaps; slice/CAP conformance; and unresolved decisions. Confirm no product,
contract, browser behavior, persistence, provider/model, external-action,
tenancy/admin, financial, retention, or authorization behavior changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0192 completion. The packet uses
  the existing generated client and cumulative disposable topology to qualify
  the two-root inspection/export seam and close SLI-0108 without adding product
  behavior, a heavyweight routine gate, or lower-level approval.
- 2026-10-18: Activated from clean base `4ea3269` with one bounded owner after
  revalidating the approved CAP package, completed WRK-0192 dependency, exact
  qualification-only scope, local decision posture, and ownership isolation.
- 2026-10-18: Implemented the bounded generated-client live capture, strict
  public-shape replay validator, ordinary HTTP parity, repeat/restart equality,
  confidential denials, accountable-history-only database/file containment,
  cleanup, and public-boundary architecture checks. The full 93-test replay
  suite, 50 focused backend tests, complete 535-test Web suite, 17 focused
  architecture tests plus four subtests, TypeScript, zero-warning lint,
  disposable PostgreSQL/Chromium topology, security, design, learner-language,
  documentation, planning, and whitespace checks passed. The completion
  selector's existing rebuildable Learner-model refresh is explicitly outside
  the accountable-history-only containment window.
