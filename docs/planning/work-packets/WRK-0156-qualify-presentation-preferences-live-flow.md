---
id: WRK-0156
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: SLI-0075
capability: CAP-0018
depends_on: [WRK-0155]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "apps/web/tests/browser/approved-lesson/presentation-preferences.e2e.ts", "backend/src/financial_ai_academy/modules/learner_model/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0075-set-accessible-display-preferences.md", "docs/planning/work-packets/WRK-0156-qualify-presentation-preferences-live-flow.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: a2fe0df6dcc8341f93523bc01b175a31af6345f7
claim_id: WRK-0156:b3c35c5a-7bca-457a-89c7-3ce10eb50e0d
claimed_by: codex-cap-0018
claimed_at: 2026-10-17T22:45:26Z
---

# Agent Work Packet: Qualify the Presentation Preferences Live Flow

## Objective and Deliverable

Close SLI-0075 with one cumulative local qualification of the delivered
learner-presentation-preference contracts, protected public API, PostgreSQL
persistence, generated browser client, global presentation adapter, and
ordinary headless HTTP path. Prove browser/headless parity, all sixteen valid
choice combinations, exact replay and concurrency semantics, restart
durability, protective browser behavior, privacy/isolation, source-state
noninterference, and exact cleanup in the established disposable
approved-lesson topology.

This packet adds qualification and direct assurance evidence only. It does not
change product behavior or contracts, add a browser-only authority, infer a
medical or accessibility trait, or make managed-cloud, recovery, or production
availability claims.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Route through the architecture-contracts,
API/security, testing-quality, deployment-operations, interface-design, and
delivery-planning context; apply the change-impact matrix and decision
readiness. Inspect CAP-0018, SLI-0075, completed WRK-0153 through WRK-0155,
ADR-0005, ADR-0006, ADR-0009, the presentation-preference schemas and vectors,
generated client, browser route and platform adapter, Learner-model application
and PostgreSQL adapters, protected host, approved-lesson runner and browser
journeys, runner tests, nearest READMEs, assurance map, known gaps, and static
build behavior.

No identity, tenancy, provider, model-authority, licensing, encryption,
recovery, legal, commercial, or external-execution decision is open for this
bounded local qualification. Canonical sources govern over this packet.

## Decisions and Assumptions

- WRK-0153 through WRK-0155 supply the frozen contract, implementation,
  protected API, generated client, global runtime adapter, and browser flow.
  This packet may observe them but may not redefine them.
- The established loopback Python host, tracked static build, disposable
  PostgreSQL 18.4 container, server-owned single-profile session, and
  runner-owned temporary root are sufficient for local evidence.
- Browser and ordinary non-browser clients use the same four public operations
  and the same server-owned learner identity, permission, validation,
  idempotency, optimistic revision, and persistence policy.
- The sixteen valid combinations are the Cartesian product of the two closed
  values for text size, text spacing, reading width, and motion. Generated IDs,
  revisions, digests, and canonical times are variable evidence, not fixtures.
- Theme remains local `system|light|dark` browser state and is excluded from
  the learner profile, history, export, headless API, and PostgreSQL rows.
- Device/browser zoom, text scaling, forced colors, and reduced-motion signals
  retain precedence whenever they are more protective. Qualification checks
  usable content/actions and root semantics, not pixel identity.
- Same-key/same-payload concurrency converges on one accepted revision;
  same-key/changed-payload yields one accepted result and one confidential
  conflict; different-key/same-revision yields one accepted result and one
  stale denial, with no duplicate or lost durable change.
- Captures contain only bounded public documents, requests, and expected
  correlations. They exclude cookies, credentials, connection strings,
  private storage locators, inferred traits, evidence, and learner-selected
  identity.
- Harmless whitespace, optional wording, styling, generated values, and
  fixture order do not reopen delivery. Fix them locally when safe or defer
  optional polish to CAP-0031.

## In Scope

- Add one approved-lesson Chromium journey for baseline open, complete preview,
  save, cancel/restore, reset, history, technical record, export, navigation,
  and persistence across routes through the reviewed generated client.
- Exercise all sixteen valid profiles, theme separation, keyboard and named
  controls, focus, narrow reflow, 200-percent text, forced colors, reduced
  motion, equivalent content/actions across themes, malformed/unavailable safe
  fallback, and no unsafe or partial root attributes.
- Capture a closed public profile/history/export, exact accepted request/result,
  root-attribute observations, and privacy-safe expected correlations for
  headless and restart comparison.
- Extend the Python runner with strict presentation capture validation,
  cookie-backed headless reads/mutations/reset/export, exact replay,
  changed-key and stale denials, and simultaneous PostgreSQL race cases through
  public HTTP.
- Correlate current profile, bounded change summaries, and accepted mutation
  rows in `learner_model.presentation_preference_profiles`,
  `presentation_preference_changes`, and
  `presentation_preference_mutations` without using SQL as mutation authority.
- Compare privacy-safe before/after fingerprints for unrelated Curriculum,
  Content, Assessment, Project, Personal workspace, Audit, completion,
  practice, and other Learner-model facts so display choices cannot become
  evidence, mastery, eligibility, permission, recommendation, or suitability.
- Restart the normal Python host without reseeding and prove profile, history,
  export, root semantics, exact replay, and PostgreSQL correlations retain
  meaning.
- Extend pure runner tests for closed capture shape, all-combination coverage,
  digest/chronology correlation, concurrency matrices, confidentiality scans,
  theme exclusion, restart equality, source-state noninterference, and
  finally-path cleanup.
- Regenerate the tracked static browser from accepted sources and synchronize
  direct Web, Learner-model, local-deployment, assurance, known-gap, slice,
  packet, and register evidence.

## Out of Scope

Product contract, domain, application, repository, migration, API, OpenAPI,
generated-client, browser-feature, presentation-adapter, identity, permission,
or session changes; new product-meaning fixtures; multiple real learners or
organizations; OIDC or built-in credentials; remote/public binding; inferred
or medical traits; assistive-technology detection; arbitrary CSS or scales;
competency, evidence, grading, eligibility, recommendation, experimentation,
financial suitability or advice; provider/model calls; separate AI mode;
external notifications or execution; background jobs; analytics; managed
cloud; backup/restore tooling; RPO/RTO; production load; multi-browser
certification; dependency or lockfile changes; shared token/icon changes; pixel
baselines; or styling redesign.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live Chromium | delivered route, global adapter, generated client, browser support | one approved-lesson presentation-preference journey | Exercise the exact learner-visible public-API path and root semantics |
| Live orchestration | runner startup, sessions, snapshots, restart, cleanup | approved-lesson runner | Correlate browser, headless HTTP, races, PostgreSQL, restart, and cleanup |
| Pure qualification | existing capture, denial, restart, and anti-rigidity tests | runner test module | Prove fail-closed evidence logic without relying only on infrastructure |
| Static browser | accepted TypeScript source and exact lockfile | `apps/web/dist` as generated output | Serve the candidate qualified by the Python host |
| Product implementation | contracts, core, persistence, host, client, route, adapter | none | Qualification may not silently fix or widen product behavior |
| Direct guidance | Web/module/local READMEs, assurance, known gaps | listed Markdown sources | Keep qualified and intentionally unqualified claims exact |
| Planning | SLI-0075, this packet, register | listed planning files | Close the final packet and slice evidence together |

No unlisted product, contract, migration, dependency, shared design-system, or
deployment-composition file may change.

## Contracts and Interfaces

Browser and headless clients consume only:

```text
POST /api/v1/session/single-profile
GET  /api/v1/learner-presentation-preferences
POST /api/v1/learner-presentation-preferences/mutations
GET  /api/v1/learner-presentation-preferences/history
GET  /api/v1/learner-presentation-preferences/export
```

The capture must contain a closed version marker; current public profile,
history, and export; exact replayable request; all-combination/root-attribute
observations; concurrency requests and expected outcome classes; and safe
correlation summaries. It must not contain session material, caller-selected
learner identity, permission state, database keys, connection details,
provider/model data, inferred or medical traits, evidence, scores,
recommendations, or arbitrary diagnostics.

The runner may inspect only the isolated three presentation-preference tables
for exact correlation, plus privacy-safe counts or hashes for unrelated
schemas. All durable writes enter through the protected public mutation API.

## Dependencies and Parallel Safety

WRK-0155 is complete and supplies the generated-client browser flow and global
presentation seam. WRK-0156 owns the shared approved-lesson runner, tracked
static build, assurance sources, and SLI-0075 closure paths, so it is not
parallel-safe with another writer on those surfaces. SLI-0075 closes only after
this packet completes.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Baseline live open | Fresh isolated topology and authorized local learner | Chromium opens Display and accessibility | Safe baseline renders without a database write; theme remains local | Chromium/API/PostgreSQL |
| All valid profiles | The four closed two-value settings | Each of sixteen combinations is saved and reopened | Exact accepted values apply as four safe root attributes without losing content/actions | Chromium/capture |
| Preview and cancel | Accepted settings and a changed draft | Learner previews then cancels or navigates away | Draft applies transiently and accepted settings are restored without a write | Chromium/network |
| Reset and theme separation | Non-baseline learner settings and dark theme | Learner resets saved choices | A new baseline learner revision persists while local theme remains dark | Chromium/API/PostgreSQL |
| Browser/headless parity | Closed browser capture | Ordinary cookie-backed client reads, mutates, resets, and exports | Public meaning matches without UI imports or browser authority | runner/public HTTP |
| Exact replay race | Two clients submit the same key and payload together | Both requests finish | Both observe one accepted result and only one next revision/change/replay row exists | public HTTP/PostgreSQL |
| Changed-key race | Two clients submit one key with different values | Requests serialize | One result is accepted, one is a confidential conflict, and only accepted meaning persists | public HTTP/PostgreSQL |
| Stale-revision race | Two fresh keys target one current revision | Requests serialize | One result is accepted, one is stale, and no update is lost or duplicated | public HTTP/PostgreSQL |
| Restart durability | Browser/headless/race state is correlated | Python host restarts without reseeding | Profile, history, export, exact replay, root semantics, and rows remain stable | restart/API/PostgreSQL |
| Protective precedence | Any saved profile is active | 200-percent text, forced colors, or reduced motion is applied | Content/actions stay reachable and the more-protective browser/device behavior wins | Chromium/axe/design |
| Closed safe fallback | Service state is unavailable or malformed | Any route opens | Baseline remains complete; no partial/private setting or unsafe root value renders | Chromium/component |
| Privacy and authority | Display-preference journey runs | Unrelated state fingerprints and responses are inspected | No source learning fact changes and no inferred, evidence, policy, provider, or financial meaning appears | runner/security/architecture |
| Closed evidence | Capture has an extra/private/mismatched field or invalid digest/time/combination | Runner loads it | Qualification fails before comparison or mutation | pure pytest |
| Cleanup | Qualification succeeds or fails | Runner exits | Only its named app, database topology, captures, browser artifacts, build, and bounded temporary root are cleaned | runner/finally |

## Verification Commands

Run packet validation and planning integrity; focused runner tests; the full
presentation-preference contract/domain/application/PostgreSQL/API suite;
OpenAPI and generated-client reproduction; full Web tests, typecheck,
zero-warning lint, and build; the focused approved-lesson presentation journey;
and the complete isolated approved-lesson workflow.

Also run architecture/import and persistence-ownership checks; security and
privacy checks; learner-language and design-system checks; documentation,
planning, dependency, Python compilation, and whitespace checks; controller-
selected exact-candidate verification; proportionate independent technical
review; deterministic slice closure; and
`python dev-tools/agent/check_ready.py`. Use repository-prepared Python, Node
24, npm 10.8.2, Playwright Chromium, and the runner-owned disposable PostgreSQL
18.4 topology. Never claim an environment or command that did not pass, and
always execute exact cleanup.

## Documentation and Evidence Update

Record the exact candidate and qualifying receipt; browser/headless/API parity;
all sixteen profiles and root semantics; exact replay and concurrency matrix;
history/export and PostgreSQL correlations; restart durability; theme
separation; device precedence; invalid/unavailable fallback; unrelated-state
noninterference; privacy, accessibility, containment, cleanup; focused/live/
security/architecture/aggregate checks; changed files; assumptions; unsupported
profiles; and remaining gaps. Keep approval and reviewer records only in
ignored local control-plane storage.

## Stop Conditions

Stop for a required product implementation, contract, migration, OpenAPI,
generated-client, browser-feature, presentation-adapter, fixture-meaning,
identity, or dependency change; inconsistent browser/headless behavior;
non-serialized or ambiguous concurrency; retained-data loss; private-data
leakage; display choices used as inferred traits, evidence, competency,
eligibility, permission, recommendation, suitability, or irreversible external
action; direct cross-module persistence mutation; unisolated infrastructure;
provider/model/external execution; managed-cloud, tenancy, recovery, licensing,
legal, or commercial decision; active write collision; stale CAP package; or
material CAP-0018/SLI-0075 drift. Route a true product defect to separately
bounded corrective work instead of widening this qualification packet.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, generated values, fixture count/order, or another
inconsequential qualification correction.

## Required Handoff

Report `CAP-0018.SLI-0075.WRK-0156`; exact candidate and receipt; browser/
headless parity; all sixteen display profiles; root attributes and safe
fallback; theme separation; exact replay and concurrency matrix; history/
export and PostgreSQL restart correlations; source-state noninterference;
privacy, accessibility, containment, cleanup; focused/live/security/
architecture/aggregate checks; changed files; documentation impact;
assumptions; unsupported profiles; and residual gaps. Confirm no product
implementation, contract, generated client, identity, provider, model,
separate AI authority, inferred trait, external action, or financial behavior
changed, then leave SLI-0075 closure-ready.

## Planning History

- 2026-10-17: Authored just in time after WRK-0155 completed. The packet is
  the smallest final qualification seam that closes SLI-0075 through the
  existing disposable local topology while preserving one protected API for
  browser and headless clients. No durable decision or lower-level approval is
  required.
- 2026-10-17: Marked ready after packet, dependency, decision-readiness,
  public-API, all-combination, concurrency, closed-capture, exact write-scope,
  documentation, and planning validation passed without CAP or slice drift.
- 2026-10-17: Activated from recorded base `a2fe0df` after validating the
  completed dependency, current CAP authority, qualification-only scope,
  exact file ownership, and no active coordination collision.
