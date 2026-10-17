---
id: WRK-0150
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0074
capability: CAP-0018
depends_on: [WRK-0149]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/learner-preferences.e2e.ts", "backend/src/financial_ai_academy/modules/learner_model/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0074-record-learning-goals-experience-interests.md", "docs/planning/work-packets/WRK-0150-qualify-learning-preferences-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Qualify the Learning Preferences Live Flow

## Objective and Deliverable

Close SLI-0074 with one cumulative local qualification of the delivered
learner-preference contracts, protected API, PostgreSQL persistence, generated
browser client, and ordinary headless HTTP path. Prove the complete learner
journey, exact retry and simultaneous-write semantics, restart durability,
privacy and source-state containment, accessibility, flexible valid shapes,
and exact cleanup in the established disposable approved-lesson topology.

This packet adds qualification and direct assurance evidence only. It does not
change product behavior, introduce a browser-only or AI-specific authority,
weaken the contract, or make managed-cloud, backup, availability, or
production-recovery claims.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Apply the routed architecture-contracts,
API/security, testing-quality, deployment-operations, interface-design, and
delivery-planning context; the change-impact matrix; and decision readiness.
Inspect CAP-0018, SLI-0074, completed WRK-0147 through WRK-0149, ADR-0005,
learner-preference contracts and compatibility vectors, generated client,
browser flow, Learner-model application/PostgreSQL adapters, protected host,
approved-lesson runner and browser journeys, runner tests, nearest READMEs,
architecture assurance, known gaps, and exact static-build behavior.

No identity, tenancy, provider, model-authority, licensing, encryption,
recovery, legal, commercial, or external-execution decision is open for this
bounded local qualification. Canonical sources govern over this packet.

## Decisions and Assumptions

- WRK-0147 through WRK-0149 supply the frozen contract, implementation,
  protected API, generated client, and learner-visible flow. This packet may
  observe them but may not redefine them.
- The established loopback Python host, tracked reviewed static build,
  disposable PostgreSQL 18.4 container, single-profile server session, and
  runner-owned temporary root are sufficient for local evidence.
- Browser and ordinary non-browser clients use the same four public learner-
  preference operations and the same server-owned learner identity,
  permission, validation, idempotency, optimistic revision, and persistence
  policy.
- Concurrent requests use separate cookie-backed HTTP clients for the same
  server-owned local learner. Direct SQL is evidence-only and never substitutes
  for application mutation authority.
- Same-key/same-payload races must converge on one accepted revision and replay
  result. Same-key/changed-payload races must produce one accepted result and
  one confidential conflict. Different-key/same-revision races must produce
  one accepted result and one stale-revision denial, with no lost or duplicate
  durable change.
- Captures contain only bounded public request/result and expected-correlation
  facts. They contain no cookies, credentials, raw connection strings, private
  storage locators, implementation payloads, or learner-selected identity.
- Harmless whitespace, optional wording, nonfunctional styling, generated
  values, and fixture order do not reopen a review loop. Fix them in scope or
  defer optional polish to CAP-0031.

## In Scope

- Add one approved-lesson Chromium journey for empty open, Unicode and duplicate
  learner wording, create/revise/order/archive/restore/remove, explicit removal
  confirmation, history, reset, export, interruption-safe retry, and reopening.
- Exercise keyboard and named-control behavior, focus after failures, narrow
  reflow, light/dark/system-equivalent semantics, forced colors, reduced motion,
  technical-detail disclosure, and no request before destructive confirmation.
- Capture a closed public profile/history/export plus exact accepted mutation
  material and browser-observed correlations for headless/restart comparison.
- Extend the Python runner with strict capture validation, ordinary cookie-
  backed headless reads/mutations/export, exact replay, changed-key and stale
  denials, and simultaneous PostgreSQL race cases through public HTTP.
- Correlate exact current profile, bounded changes, and accepted mutation rows;
  prove each race creates only its allowed durable result and that reset/history/
  export facts match the public contract.
- Compare privacy-safe before/after fingerprints for Curriculum, Content,
  Assessment, Project, Personal workspace, Audit, completion, practice, and
  other non-preference Learner-model facts so preference actions cannot become
  evidence, mastery, eligibility, permission, recommendation, or suitability.
- Stop and restart the normal Python host without reseeding; prove the profile,
  history, export, exact replay, and PostgreSQL correlations retain meaning.
- Extend pure runner tests for closed capture shape, canonical digest and
  chronology correlation, concurrent outcome matrices, record counts,
  confidentiality scans, variable valid wording/count/order, restart equality,
  source-state non-interference, and finally-path cleanup.
- Regenerate the tracked static browser from the exact accepted sources and
  synchronize direct web, Learner-model, local-deployment, architecture,
  known-gap, slice, packet, and planning-register evidence.

## Out of Scope

Product contract, domain, application, repository, migration, API, OpenAPI,
generated-client, browser-feature, identity, permission, or session changes;
new fixtures with product meaning; multiple real learners or organizations;
OIDC or built-in credentials; remote/public binding; inferred traits;
competency, evidence, grading, eligibility, recommendation, experimentation,
financial suitability or advice; provider/model calls; separate AI mode;
autonomous authority; external notifications; background jobs; analytics;
managed cloud; backup/restore tooling; RPO/RTO; production load; multi-browser
certification; dependency or lockfile change; shared design-token/icon change;
pixel baselines; or styling redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live Chromium | Delivered feature, generated client, browser support | one new approved-lesson journey | Exercise the exact learner-visible public-API path |
| Live orchestration | Runner startup, sessions, snapshots, restart, cleanup | approved-lesson runner | Correlate browser, headless HTTP, races, PostgreSQL, restart, and cleanup |
| Pure qualification | Existing capture, denial, restart, and anti-rigidity tests | runner test module | Prove fail-closed evidence logic without relying only on infrastructure |
| Static browser | Accepted TypeScript source and exact lockfile | `apps/web/dist` only as generated output | Serve the candidate actually qualified by the Python host |
| Product implementation | Contracts, core, persistence, host, generated client, feature | none | Qualification may not silently fix or widen product behavior |
| Direct guidance | Web/module/local READMEs, assurance, known gaps | listed Markdown sources | Keep qualified and intentionally unqualified claims exact |
| Planning | SLI-0074, this packet, register | listed planning files | Close the final packet and slice evidence together |

No unlisted product, contract, migration, dependency, shared design-system, or
deployment-composition file may change.

## Contracts and Interfaces

Browser and headless clients consume only:

```text
POST /api/v1/session/single-profile
GET  /api/v1/learner-preferences
POST /api/v1/learner-preferences/mutations
GET  /api/v1/learner-preferences/history
GET  /api/v1/learner-preferences/export
```

The capture must contain a closed version marker; current public profile,
history, and export; exact replayable request; race requests and expected
outcome classes; and safe expected correlations. It must not contain session
material, caller-selected learner identity, permission state, database keys,
connection details, provider/model data, inferred traits, evidence, scores,
recommendations, or arbitrary diagnostics.

The runner may inspect only isolated `learner_model.preference_profiles`,
`learner_model.preference_changes`, and
`learner_model.preference_mutations` rows for exact preference correlation,
plus privacy-safe counts or hashes for unrelated schemas. All durable writes
must enter through the protected public mutation API.

## Dependencies and Parallel Safety

WRK-0149 is complete and supplies the generated-client browser flow. WRK-0150
owns the shared approved-lesson runner, tracked static build, assurance sources,
and SLI-0074 closure paths, so it is not parallel-safe with another writer in
those surfaces. SLI-0074 closes only after this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Empty live open | Fresh isolated topology and authorized local learner | Chromium opens Learning preferences | Stable empty profile appears without a database write and purpose/scope remain plain | Chromium/API/PostgreSQL |
| Complete browser journey | Unicode, optional detail, duplicate wording, varied counts/order | Learner creates, edits, orders, archives/restores, confirms removal, resets, and exports | Generated client preserves exact accepted public state and every reachable action remains named and usable | Chromium/capture |
| No premature removal | One populated item | Keyboard or pointer reaches Remove before confirmation | No POST occurs until the named confirmation is checked | Chromium/network |
| Browser/headless parity | Closed browser capture | Ordinary cookie-backed client reads and exports | Profile, history, revision, digest, purpose, limits, and result meaning match without UI imports | runner/public HTTP |
| Exact replay race | Two clients submit the same key and payload together | Both requests finish | Both observe the same accepted result and only one next revision/change/replay row exists | public HTTP/PostgreSQL |
| Changed-key race | Two clients submit one key with different payloads together | Requests serialize | One result is accepted, one is a confidential conflict, and only accepted meaning persists | public HTTP/PostgreSQL |
| Stale-revision race | Two fresh keys target one current revision together | Requests serialize | One result is accepted, one is stale, and there is no lost update or duplicate next revision | public HTTP/PostgreSQL |
| Restart durability | Browser/headless/race state is correlated | Python host restarts without seed flags | Current profile, bounded history, export, exact replay, row correlations, and public meaning remain stable | restart/API/PostgreSQL |
| Privacy and authority | Preference journey runs | Unrelated state fingerprints and responses are inspected | No source learning fact changes and no private, inferred, evidence, policy, provider, or financial meaning appears | runner/security/architecture |
| Accessible flexibility | Duplicate text, keyboard, focus, 320px reflow, themes, forced colors, reduced motion | Chromium uses the page | Equivalent content/actions remain reachable without unique wording, fixed count/order, or pixel assumptions | Chromium/component/design |
| Closed evidence | Capture has an extra/private/mismatched field or invalid digest/time/race outcome | Runner loads it | Qualification fails before partial comparison or mutation | pure pytest |
| Cleanup | Qualification succeeds or fails | Runner exits | Only its named application, database container/network, captures, browser artifacts, and bounded temporary root are cleaned | runner/finally |

## Verification Commands

Run packet validation, implementation gate, and planning integrity; focused
runner tests; the complete learner-preference contract/domain/application/
PostgreSQL/API suite; OpenAPI and generated-client reproduction; full web tests,
typecheck, zero-warning lint, and build; focused live Chromium; and the complete
isolated approved-lesson workflow.

Also run architecture/import and persistence-ownership checks; security and
privacy checks; learner-language and design-system checks; documentation,
planning, dependency, Python compilation, and whitespace checks; controller-
selected exact-candidate verification; proportionate independent technical
review; deterministic slice closure; and `python dev-tools/agent/check_ready.py`.
Use repository-pinned Python, Node 24, npm 10.8.2, Playwright Chromium, and the
runner-owned disposable PostgreSQL 18.4 topology. Never claim a command or
environment that did not pass, and always execute exact cleanup.

## Documentation and Evidence Update

Record the exact candidate and qualifying receipt; browser/headless/API parity;
complete public journey; canonical digest/history/export correlations; exact
replay and all three simultaneous race outcomes; PostgreSQL row evidence;
restart durability; source-state non-interference; privacy and containment;
accessibility and anti-rigidity cases; cleanup; focused/live/security/
architecture/aggregate checks; changed files; assumptions; unsupported
profiles; and remaining gaps. Keep approval and reviewer records only in the
ignored local ledger.

## Stop Conditions

Stop for a required product implementation, contract, migration, OpenAPI,
generated-client, browser-feature, fixture-meaning, identity, or dependency
change; inconsistent browser/headless behavior; non-serialized or ambiguous
race results; retained-data loss; private-data leakage; preference use as
evidence, competency, eligibility, permission, recommendation, suitability, or
irreversible external action; direct cross-module persistence mutation;
unisolated infrastructure; provider/model/external execution; managed-cloud,
tenancy, recovery, licensing, legal, or commercial decision; active write
collision; stale CAP package; or material CAP-0018/SLI-0074 drift. Route a true
product defect to separately bounded corrective work instead of widening this
qualification packet.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, generated values, fixture count/order, or another
inconsequential qualification correction.

## Required Handoff

Report `CAP-0018.SLI-0074.WRK-0150`; exact candidate and receipt; browser/
headless parity; complete learner journey; exact replay and simultaneous race
matrix; digest/history/export correlation; PostgreSQL restart; unrelated-state
non-interference; privacy, accessibility, containment, cleanup; focused/live/
security/architecture/aggregate checks; changed files; documentation impact;
assumptions; unsupported profiles; and residual gaps. Confirm no product
implementation, contract, generated client, identity, provider, model,
separate AI authority, external action, or financial behavior changed, then
leave SLI-0074 closure-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0149 completed. The packet is the
  smallest final qualification seam that closes SLI-0074 through the existing
  disposable local topology while preserving one protected API for browser and
  future headless clients. No durable decision or lower-level approval is
  required.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  public-API, race-matrix, closed-capture, exact write-scope, documentation,
  and planning validation passed without material CAP or slice drift.
