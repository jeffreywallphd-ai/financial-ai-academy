---
id: WRK-0142
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0017
updated: 2026-10-17
parent: SLI-0072
capability: CAP-0017
depends_on: [WRK-0141]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/personal-workspace.e2e.ts", "deployments/local/README.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/vertical-slices/SLI-0072-search-and-refresh-saved-references.md", "docs/planning/work-packets/WRK-0142-qualify-saved-reference-live-parity.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: 6c2164363ece014fec25e94281fa73950761d096
claim_id: WRK-0142:7d3bcf09-1bf4-47dc-aa2d-fb66c1fbd856
claimed_by: codex-cap-0017
claimed_at: 2026-10-17T16:02:33Z
---

# Agent Work Packet: Qualify Saved-Reference Live Parity

## Objective and Deliverable

Close SLI-0072 with one cumulative local qualification of the delivered
Saved-learning query and explicit source-check flow. Prove that the generated
browser client and an ordinary cookie-backed headless client consume the same
protected public API, preserve deterministic query meaning and confidential
source authority, create no target-domain side effect, and retain identical
state through a normal host restart without reseeding.

This packet extends the existing approved-lesson qualification and its pure
runner tests. It does not add product behavior, loosen a contract, create a
browser-only path, define a headless AI mode, or make live infrastructure or
production-recovery claims.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed delivery-planning and
testing-quality context; change-impact matrix; decision-readiness register;
ADR-0009, ADR-0012, and ADR-0021; CAP-0017; SLI-0072; completed WRK-0139
through WRK-0141; Personal-workspace contract and assurance text; current
approved-lesson runner, browser journey, pure runner tests, local deployment
guide, web README, and nearest test configuration. Canonical sources govern
over this packet.

## Decisions and Assumptions

- WRK-0139 through WRK-0141 supply the complete contract, application,
  PostgreSQL, protected API, generated client, and browser behavior. This is a
  cumulative qualification packet and may not redefine those seams.
- The current isolated PostgreSQL 18.4 approved-lesson topology is sufficient.
  The exact query and refresh calls use the same single-profile session and
  same-origin Python host as the existing browser/headless journey.
- The browser capture may add only bounded public query, refresh, and expected
  correlation facts. It may not contain cookies, credentials, internal storage
  paths, private fingerprints, adapter internals, or provider payloads.
- A query is side-effect free. An exact refresh replay returns the accepted
  workspace without another owner call or mutation row. A new refresh remains
  record-only and the server derives learner, selector, owner access,
  replacement facts, validation time, and status.
- Live evidence covers the admitted current Curriculum and Project adapters.
  Confidential missing, denied, absent-adapter, and drift transitions remain
  directly covered by focused application/PostgreSQL/API suites; the live
  qualifier does not manufacture private owner failures or alter production
  fixture meaning.
- No schema or data migration is expected. Normal restart reuses the same
  database and object root with no seed flag.

## In Scope

- Extend the live Saved-learning browser journey to exercise Unicode text and
  closed filters through `queryPersonalWorkspace`, opaque forward paging where
  the fixture permits it, plain source-status display, safe available-source
  resume, and one explicit `Check source` request.
- Capture the exact public requested/applied query meaning, digest,
  continuation facts, refresh request, accepted workspace, and stable expected
  correlations needed by the runner. Keep the capture closed, bounded, and
  privacy-minimized.
- Extend the ordinary headless observation to call the protected query API,
  validate the complete result against the browser-observed workspace, replay
  the exact accepted refresh, and prove malformed, changed-key, stale-revision,
  or cross-query material fails with the existing confidential boundary where
  applicable.
- Correlate PostgreSQL workspace and replay rows before and after browser,
  headless query, exact refresh replay, and restart. Prove Curriculum, Project,
  Assessment, Learner-model, and artifact state remains unchanged.
- Reopen the same query and refresh evidence after a normal application restart
  without reseeding and compare stable public meaning and retained storage.
- Add pure runner tests for closed capture validation, query/result/digest and
  record correlation, exact public call order, privacy containment, side-effect
  freedom, exact replay, denial handling, restart comparison, variable record
  order/count, and optional continuation without fixed incidental prose.
- Update direct web, local deployment, architecture assurance, known-gap,
  slice, packet, and planning-register documentation with exact qualified and
  intentionally unqualified claims.

## Out of Scope

Backend/domain/application/repository/API/OpenAPI/generated-client/browser
feature changes; new fixture product meaning; direct database mutation to
simulate source failure; a new owner adapter; multiple learners; OIDC or
built-in credentials; remote/public binding; background refresh; worker or
analytics composition; arbitrary URL; source or target mutation; artifact
content, preview, download, expansion, or execution; vector or semantic search;
provider/model calls; headless AI or agent protocol; backup/restore, RPO/RTO,
availability, managed cloud, production distribution, multi-browser coverage,
dependency/lockfile change, shared design-system change, or styling polish.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | Existing Saved-learning approved-lesson journey and public query/refresh behavior | listed Personal-workspace e2e file | Capture generated-client query and source-check behavior in the established live topology |
| Headless/restart runner | Current capture closure, public client helpers, PostgreSQL snapshots, restart, report, cleanup | listed runner file | Compare browser/headless public meaning and durable replay without another application path |
| Runner unit evidence | Existing Personal-workspace capture, denial, storage, restart, and anti-rigidity tests | listed replay-qualification test file | Prove closure, containment, exact correlation, and flexible safe fixtures |
| Direct guidance | Current web, local qualification, assurance, and gap statements | listed Markdown files | Keep qualified and unqualified claims exact |
| Planning | SLI-0072, this packet, register | listed planning files | Close the final packet and slice evidence together |

No product implementation, executable contract, migration, generated client,
design asset, dependency, or deployment composition file may change.

## Contracts and Interfaces

The browser and headless journeys use only:

```text
POST /api/v1/session/single-profile
GET  /api/v1/personal-workspace
POST /api/v1/personal-workspace/query
POST /api/v1/personal-workspace/mutations
     mutation = { operation: "refresh_reference", record_id: <owned ID> }
```

The captured query must preserve the complete closed request, canonical applied
query, query digest, workspace revision, bounded records, and optional opaque
continuation. Returned records must exactly match records in the opened
workspace. The capture must not introduce a learner selector or any caller-
controlled source, status, replacement, permission, provenance, timestamp, or
destination authority.

The refresh capture includes the existing schema, idempotency key, expected
workspace revision, and record-only mutation. Exact replay must return the same
accepted workspace and preserve mutation counts; changed meaning under the
same key and stale revision retain the established confidential response.

## Dependencies and Parallel Safety

WRK-0141 is complete and supplies the generated browser flow. This packet owns
the existing live Personal-workspace browser fixture, shared e2e runner,
runner-unit tests, and direct qualification documentation. Those files are
shared high-churn qualification surfaces, so no packet is declared parallel-
safe. SLI-0072 closes only after this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Browser query | Five mixed Curriculum and Project records exist | Learner applies Unicode text and closed filters | Generated client returns one correlated closed page with canonical query/digest and only matching workspace-owned records | live Chromium/capture |
| Continuation flexibility | A bounded query has another page | Learner follows the opaque continuation | Complete query meaning and limit persist; no partial page exposes reorder authority | live Chromium or direct headless plus pure variable-shape case |
| Available source check | A retained admitted source is visible | Learner chooses `Check source` | Request carries only record ID in the existing envelope and accepted status remains server-derived | live Chromium/capture |
| Browser/headless parity | Browser capture is closed | Fresh cookie-backed client reads and queries | Headless result has identical public query meaning, records, status, and revision without UI or backend imports | live runner |
| Exact refresh replay | Browser refresh was accepted | Headless client repeats the complete request | Same accepted workspace returns without another mutation row or target effect | live runner/PostgreSQL |
| Confidential conflict | Replay meaning changes or revision is stale | Headless client submits the bounded invalid request | Existing public denial appears without learner, record, owner, selector, content, or storage disclosure | live runner |
| Target isolation | Browser/query/refresh/headless actions run | Direct storage snapshots are compared | Project, Curriculum, Content, Assessment, Learner-model, Audit, and inert artifact facts are unchanged | live runner/PostgreSQL |
| Normal restart | Exact browser/headless state was observed | Python host restarts on retained database and object root without seed flags | Query result, refresh replay, workspace, mutation evidence, and target counts retain identical public meaning | live runner |
| Closed capture | Extra/private/mismatched query or refresh material is written | Runner loads the capture | It fails before comparison or replay with no partial acceptance | pure pytest |
| Anti-rigidity | Safe record order/count, Unicode text, and optional cursor vary | Pure qualification corpus runs | Invariants pass without one fixture count, incidental order, exact copy, style, or unnecessary re-review | parameterized pytest |
| Cleanup | Qualification succeeds or fails | Runner exits | Only its named app, database composition, capture files, and bounded temporary root are removed | runner/finally |

## Verification Commands

Run:

```text
backend/.venv/Scripts/python.exe -m pytest tests/e2e/approved-lesson/test_replay_qualification.py -q
npm --prefix apps/web run test:browser -- apps/web/tests/browser/personal-workspace
npm --prefix apps/web run generate:api -- --check
npm --prefix apps/web run typecheck
npm --prefix apps/web run lint
npm --prefix apps/web run build
backend/.venv/Scripts/python.exe tests/e2e/approved-lesson/run.py
python dev-tools/architecture/check_architecture.py
python dev-tools/security/check_slice_security.py
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0142-qualify-saved-reference-live-parity.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Use the repository-pinned Python, Node 24, npm 10.8.2, Playwright Chromium,
and disposable Docker PostgreSQL 18.4 topology. Run an exact clean-candidate
affected-check plan, obtain a fresh qualifying receipt, and complete
proportionate independent technical review. The live runner owns its unique
ports, Compose project, processes, captures, and cleanup.

## Documentation and Evidence Update

Record exact browser/headless query and refresh parity; canonical query/digest
correlation; continuation coverage; record-only refresh and confidential
conflicts; query side-effect freedom; replay and mutation-row stability;
PostgreSQL restart; target-state isolation; cleanup; focused, live, security,
architecture, affected, aggregate, and independent technical results; changed
files; assumptions; and unqualified profiles. Approval and reviewer records
remain only in ignored local state.

## Stop Conditions

Stop for a required implementation, executable contract, OpenAPI, generated-
client, fixture-product, migration, or new-adapter change; learner-selected
identity; caller-controlled owner, selector, permission, status, replacement,
timestamp, provenance, or destination; differentiated source-failure
disclosure; direct target mutation; private database manipulation to create a
demo state; artifact activity; background/event coupling; new dependency;
provider/model/external execution; managed-cloud, tenancy, recovery, licensing,
or legal boundary; active scope collision; canonical conflict; stale CAP
package; or material SLI/CAP drift. Route an in-scope implementation defect to
one bounded correction packet instead of silently widening this qualification
packet.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally in scope or defer optional polish.

## Required Handoff

Report `CAP-0017.SLI-0072.WRK-0142`; exact candidate and receipt; live browser/
headless query and refresh parity; canonical query/digest and continuation;
record-only authority; replay/storage/restart and target-isolation evidence;
focused pytest/Chromium, architecture, security, affected, aggregate, and
independent technical results; changed files; documentation impact;
assumptions; unqualified profiles; and residual gaps. Confirm no product
implementation, contract, generated-client, migration, source mutation,
artifact execution, provider, managed-cloud, separate AI authority, or
financial action changed, then leave SLI-0072 closure-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0141 completed. This final packet
  extends the established disposable local qualifier to the delivered query
  and record-only source-check seam, while preserving the approved CAP, slice,
  API-first, confidentiality, and unqualified-production boundaries. No lower-
  level approval is required.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  closed-capture, public-API, exact write-scope, documentation, and planning
  validation passed without material CAP or slice drift.
- 2026-10-17: Activated from recorded base `6c21643` after validating the
  completed dependency, current CAP authority, qualification-only scope,
  exact file ownership, and absence of an active coordination collision.
