---
id: WRK-0168
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0020
updated: 2026-10-18
parent: SLI-0082
capability: CAP-0020
depends_on: [WRK-0167]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/platform-help.e2e.ts", "backend/src/financial_ai_academy/modules/guidance/README.md", "deployments/local/README.md", "dev-tools/control-plane/README.md", "dev-tools/control-plane/check_platform_help.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0082-browse-search-approved-help.md", "docs/planning/work-packets/WRK-0168-qualify-platform-help-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Platform Help Live Flow

## Objective and Deliverable

Close SLI-0082 with reproducible evidence that the immutable reviewed Help
corpus works through the same protected public API for the generated browser
client and an ordinary headless HTTP client. Exercise exact browse/search,
kind filtering, cursor continuation, exact-version reads, safe rendering,
source binding, authorization, normal restart, offline-local operation,
accessibility, containment, and cleanup in the existing disposable PostgreSQL,
Python host, static build, and pinned Chromium topology.

The packet adds qualification and reusable affected-check selection only. It
does not change product behavior, the public contract, corpus meaning, ranking,
identity policy, persistence, provider/model behavior, or financial authority.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Revalidate the routed architecture-contract,
API/security, testing-quality, deployment-operations, interface-design, and
delivery-planning context; the change-impact matrix; decision readiness;
CAP-0020; SLI-0082; completed WRK-0165 through WRK-0167; the platform-help
contract and Guidance sources; generated client and browser flow; approved-
lesson runner and its pure replay tests; affected-check catalog; architecture
assurance; known gaps; and every nearest README.

The Required Startup was performed and reported before this planning change.
The current CAP package remains approved, every dependency is complete, and no
unresolved durable decision applies. Stop for conflicting authority, stale CAP
authority, an active ownership collision, or material CAP/slice drift.

## Decisions and Assumptions

- WRK-0165 through WRK-0167 supply the frozen contract, deterministic Guidance
  core, immutable source-bound corpus, protected API, generated client, and
  accessible Help routes. This packet may observe but not redefine them.
- The established approved-lesson topology is sufficient even though Help is
  read-only and database-independent: the ordinary application is composed with
  PostgreSQL and the same server-owned local session as other protected routes.
- Browser and headless clients use only the two public Guidance operations.
  Browser capture contains bounded public documents and expected facts, never a
  cookie, credential, learner selector, local path, approval/reviewer record, or
  private repository source.
- Offline-local evidence means the checked-in corpus remains available through
  a normally restarted loopback host while browser request observation reports
  no non-loopback request. It does not claim operating-system network isolation,
  remote-host support, managed cloud, or production availability.
- Exact source integrity is recomputed by the production corpus admission path
  and focused source-binding tests. The live journey proves the admitted public
  source key, title, version, fingerprint, topic digest, and corpus version are
  identical across browser, headless, and restart observations.

## In Scope

- Add an approved-lesson Chromium journey that browses Help, searches Unicode
  text, filters by one closed kind, follows an opaque continuation when present,
  opens exact topic versions and exact relations, returns to preserved search,
  inspects publication and technical facts, and records a closed public capture.
- Observe all browser requests and fail if Help causes a non-loopback request,
  a non-read Guidance request, or a request to an unapproved Guidance path.
- Exercise keyboard use, focus, 320-pixel reflow with 200-percent text, light,
  dark, and system-equivalent meaning, forced colors, reduced motion, and axe.
- Extend the Python runner with strict capture validation, fresh cookie-backed
  headless browse/search/filter/cursor and exact-version reads, authorization
  denial, browser/headless equivalence, read-only storage/source-state
  containment, normal restart comparison, and finally-path capture cleanup.
- Add pure runner tests for closed capture shape, corpus/search/topic
  correlation, source/publication chronology, exact relation identity, cursor
  continuity, confidential denial, varied valid records and nodes, restart
  equality, non-loopback refusal, and bounded-path cleanup.
- Add a self-bound focused platform-help Chromium wrapper, affected-check
  catalog mapping, and wrapper/catalog tests so later Help changes select their
  browser evidence without forcing the full live topology.
- Regenerate the exact static browser artifact and reconcile direct Web,
  Guidance, local-runtime, assurance, known-gap, and planning documentation.

## Out of Scope

- Product, contract, schema, corpus, ranking, application, API, OpenAPI,
  generated-client, identity, permission, session, dependency, migration,
  persistence, deployment-composition, design-system, or feature behavior.
- A browser-only corpus, direct repository Markdown read, source refresh,
  external link, remote content, semantic/vector search, generated answer,
  personalization, search analytics, provider/model call, mutable authoring,
  learner evidence, grading, eligibility, recommendation, or financial action.
- A correction to a discovered product defect. Route a substantive defect to a
  separately bounded dependent packet without weakening live evidence.
- Operating-system firewall isolation, supported backup/recovery, remote/public
  hosting, multi-browser certification, managed cloud, production load,
  availability, RPO/RTO, or a separate headless AI mode.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live Chromium | Delivered Help feature, generated client, browser support | one approved-lesson Help journey | Exercise the exact learner-visible API path |
| Live orchestration | Existing sessions, restart, snapshots, report, cleanup | approved-lesson runner | Compare browser/headless public meaning and local restart behavior |
| Pure qualification | Existing capture and restart verifier patterns | approved-lesson runner tests | Fail closed without relying only on infrastructure |
| Affected checks | Current bound browser wrappers and catalog tests | new Help wrapper plus exact catalog/test entries | Select focused Help Chromium evidence for later candidates |
| Static browser | Accepted Web source and lockfile | `apps/web/dist` only as generated output | Serve the candidate actually qualified by the Python host |
| Product implementation | Contract, Guidance core/corpus/API/client/browser | none | Qualification may not silently fix or widen behavior |
| Direct guidance | Web, Guidance, runtime, assurance, known-gap sources | listed Markdown files | Match claims to evidence and exclusions |
| Planning | SLI-0082, this packet, register | listed planning files | Close the final packet and slice deterministically |

No unlisted product, contract, corpus, schema, migration, generated-client,
dependency, shared-design, deployment-composition, or planning file is writable.

## Contracts and Interfaces

Browser and headless clients consume only:

```text
POST /api/v1/session/single-profile
GET  /api/v1/guidance/platform-help
GET  /api/v1/guidance/platform-help/{topic_id}/versions/{topic_version}
```

The session bootstrap is allowed only to establish server-owned context. Help
itself is read-only. The capture contains one closed version marker, initial
and filtered search documents, any continuation page, exact topic documents,
exact relation targets, and safe expected source/publication facts. It excludes
cookies, credentials, learner IDs, permissions, local paths, Git metadata,
approval/review data, authoring locators, rejected private input, arbitrary
diagnostics, model/provider data, and repository document bytes.

Headless comparison validates complete response equality where inputs are
identical and semantic equality across restart. It does not import browser or
backend internals. Persistence snapshots are evidence-only and must remain
exactly unchanged during the Help phase.

## Dependencies and Parallel Safety

WRK-0167 is complete and supplies the generated-client browser flow. This
packet owns the shared approved-lesson runner, static build, affected-check
catalog, assurance sources, and SLI-0082 closure paths, so it is not parallel-
safe with another writer on those surfaces. SLI-0082 closes only after this
packet completes.

Claim from the current clean recorded base, run packet-start, acquire exact
file leases immediately before edits, retain one owner through verification,
and keep approval and reviewer records only in ignored local storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live browse and search | Authorized loopback session and admitted corpus | Chromium browses, searches Unicode text, and filters by kind | Stable server order, normalized query, exact facts, and empty/populated behavior remain visible without client ranking | Chromium/capture |
| Cursor continuation | A page has an opaque continuation | Browser and headless clients follow it | Both preserve bound query/filter/corpus meaning and receive the same next exact identities | Chromium/HTTP |
| Exact topic and relation | A result and related topic exist | Each exact link opens | Safe nodes, applicability, publication, sources, digest, and exact relation identity match the public documents; no latest substitution occurs | Chromium/HTTP |
| Source integrity | Checked-in canonical sources and corpus are admitted | Live facts are compared with focused production-source checks | Source key/title/version/fingerprint plus topic/corpus digests are exact and no path or repository bytes leak | runner/focused tests |
| Authorization confidentiality | Fresh client omits or invalidates server session | Search or exact read is attempted | 401/403 occurs without corpus count, topic body, source facts, or rejected input disclosure | HTTP/security |
| Browser/headless parity | Closed browser capture exists | Fresh ordinary HTTP repeats equivalent operations | Complete ordered public meaning matches without UI or backend imports | runner/public HTTP |
| Offline local restart | Initial parity is established and non-loopback traffic is observed | Normal Python host restarts without reseeding | Same checked-in corpus and exact documents remain available; browser Help made no non-loopback request | restart/network observation |
| Read-only containment | Help browser/headless phases run | Persistence and unrelated-source fingerprints are compared | No module state, evidence, preference, permission, provider/model, or financial fact changes | runner/architecture |
| Accessible flexibility | Counts, Unicode, node shapes, themes, viewport, zoom-equivalent text, forced colors, and motion vary | Chromium uses Help by keyboard | Equivalent content/actions remain reachable without fixed prose, count, pixel, or incidental-order assumptions | Chromium/axe |
| Closed evidence | Capture is extra, missing, private, inconsistent, stale, or outside its owned root | Pure verifier loads it | Qualification fails before comparison or further requests | pure pytest |
| Focused future selection | A Help source, style, model, or focused browser check changes | Affected-check planning runs | The self-bound platform-help Chromium check is selected without requiring unrelated browser suites | catalog tests |
| Cleanup | Qualification succeeds or fails | Runner exits | Only its named topology, capture, browser artifacts, build, and bounded temporary root are removed | runner/finally |

## Verification Commands

Run packet and planning validation; focused affected-check catalog and pure
capture/restart tests; platform-help contract, Guidance domain/application/
corpus/API/source-binding suites; OpenAPI and generated-client reproduction;
full Web unit/component/contract tests, typecheck, zero-warning lint, and build;
the focused platform-help Chromium wrapper; and the complete isolated approved-
lesson workflow.

Also run architecture/import and source-authority checks; security, privacy,
active-content, advice-language, and AI-authority checks; learner-language and
design-system checks; documentation, planning, dependency, Python compilation,
and whitespace checks; controller-selected exact-candidate verification; one
independent technical review; deterministic slice closure; and
`python dev-tools/agent/check_ready.py`. Use repository-prepared Python, Node
24, npm 10.8.2, pinned Chromium, and runner-owned disposable PostgreSQL 18.4.
Record only successful checks and always execute exact cleanup.

## Documentation and Evidence Update

Record the exact candidate and qualifying receipt; focused-browser selection;
browser/headless parity; deterministic search/cursor and exact-topic results;
source/publication/digest correlation; authorization confidentiality;
non-loopback observation; normal restart; read-only containment; accessibility;
anti-rigidity; cleanup; checks; assumptions; unsupported profiles; and residual
gaps. Update only the direct sources in `write_scope`. Keep approval/reviewer
records out of tracked files.

## Stop Conditions

Stop for a required product, contract, schema, corpus, ranking, migration,
OpenAPI, generated-client, identity, dependency, feature, or deployment-
composition change; inconsistent browser/headless meaning; a source binding or
topic digest mismatch; a non-loopback Help request; durable state mutation;
private-data or repository-path disclosure; raw or active content; provider/
model execution; semantic search, personalization, analytics, grading,
eligibility, recommendation, financial action, or unsupported guarantee;
unisolated infrastructure; managed-cloud, tenancy, recovery, licensing, legal,
or commercial expansion; stale CAP authority; active collision; or material
CAP-0020/SLI-0082 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, generated values, fixture count/order, or another
inconsequential qualification correction. Fix it in bounded scope or defer
optional polish to CAP-0031.

## Required Handoff

Report `CAP-0020.SLI-0082.WRK-0168`; exact candidate and receipt; focused Help
browser selection; browser/headless API parity; deterministic search/filter/
cursor and exact-version results; source/publication/digest integrity;
authorization confidentiality; non-loopback observation; normal restart;
read-only state containment; accessibility; anti-rigidity; cleanup; focused,
live, security, architecture, and aggregate checks; changed files;
documentation impact; assumptions; unsupported profiles; and residual gaps.
Confirm no product implementation, contract, corpus, generated client,
identity, persistence, provider/model, external content/action, learner-policy,
or financial behavior changed, then leave SLI-0082 closure-ready.

## Planning History

- 2026-10-18: Authored just in time after WRK-0167 completed. This is the
  smallest final qualification seam for SLI-0082: it reuses the established
  disposable local topology, preserves one protected API for browser and
  headless callers, and adds focused future Help-browser selection without a
  product, contract, decision, or lower-level approval change.
