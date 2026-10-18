---
id: WRK-0164
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-18
parent: SLI-0077
capability: CAP-0018
depends_on: [WRK-0150, WRK-0156, WRK-0161]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/dist", "backend/src/financial_ai_academy/modules/learner_model/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/capabilities/CAP-0018-set-learning-goals-and-preferences.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0077-qualify-complete-learning-preferences.md", "docs/planning/work-packets/WRK-0164-qualify-complete-learning-preferences.md", "tests/e2e/approved-lesson/run.py", "tests/e2e/approved-lesson/test_replay_qualification.py"]
generated_artifacts: ["apps/web/dist"]
base_revision: d727791781679f9ab8cc22c2353e9ee7083bee48
claim_id: WRK-0164:1dd5c894-015b-49c9-9495-c7e137fc06c1
claimed_by: codex-cap-0018
claimed_at: 2026-10-18T01:46:42Z
---

# Agent Work Packet: Qualify Complete Learning Preferences

## Objective and Deliverable

Close SLI-0077 and CAP-0018 with cumulative evidence that the three delivered
learner-owned public preference API families and the two browser-local settings
work together without cross-family state leakage, authority escalation, or
shared-failure coupling. Reuse the complete approved-lesson topology and add
only the missing cross-family storage-isolation assertions and report facts.

The deliverable is qualification and completion evidence, not a new product
endpoint, aggregate settings model, export format, preference, UI, provider,
model execution path, notification system, or managed-cloud deployment.

## Required Context

Before implementation, revalidate `AGENTS.md`, `docs/README.md`, the routed
context sources, change-impact matrix, decision readiness, CAP-0018, SLI-0077,
the completed SLI-0074 through SLI-0076 plans and qualification packets, all
three preference contracts, local/cloud capability parity, the approved-lesson
runner and pure tests, public API and generated-client consumers, persistence
adapters, nearest READMEs, assurance sources, and current planning register.

Stop for a canonical conflict, stale CAP package, incomplete dependency,
unresolved decision, active write collision, or material scope drift. The
required startup has been performed and reported before this planning change.

## Decisions and Assumptions

- The CAP-0018 package remains approved and unchanged; SLI-0074, SLI-0075,
  and SLI-0076 are complete and SLI-0077 is the final enumerated increment.
- WRK-0150, WRK-0156, and WRK-0161 provide independently accepted browser,
  headless API, PostgreSQL, replay, concurrency, restart, privacy,
  accessibility, local-adapter, and cleanup evidence for their families.
- The complete approved-lesson runner already executes all three families in
  one isolated topology. This packet should add a reusable composite snapshot
  and bounded assertions rather than duplicate product journeys or runners.
- The three public families share one opaque authorized learner context but
  remain non-atomic, separately revisioned authorities. Theme and reminder
  state remain local to the browser.
- Local/cloud parity means shared contract, domain, application, and adapter
  semantics here. It does not claim a qualified managed-cloud operation.
- Harmless whitespace, optional wording, nonfunctional style, generated
  values, or fixture order do not reopen review. A bounded evidence correction
  can be fixed in this packet; product defects use a separately bounded route.

## In Scope

- Add one composite preference-family storage snapshot over the three existing
  isolated snapshots and a deterministic assertion that only the named family
  changes during its browser/headless/race phase.
- Prove each family retains its own profile, change, and mutation rows while
  the other two remain byte-for-byte equivalent before and after that phase.
- Prove the three final profiles are bound to one opaque learner context while
  retaining distinct profile identities, schemas, revisions, and exports.
- Compare the complete composite state before and after normal application
  restart and ordinary headless reads.
- Add closed cumulative report facts and pure tests for accepted isolation,
  leaked-family change, unknown family, missing/extra family, distinct learner
  context, and flexible valid contents.
- Run the already complete browser/headless/PostgreSQL/live journey, focused
  suites, exact-candidate verification, independent review, completion gates,
  and repository readiness.
- Reconcile direct runtime, assurance, known-gap, planning, and completion
  documentation from evidence actually observed.

## Out of Scope

- Product contracts, public routes, domain/application behavior, persistence
  schemas or migrations, generated clients, browser features, local adapters,
  dependencies, design-system changes, or deployment composition.
- A combined settings endpoint, aggregate portable export/import, cross-family
  transaction, shared revision, or new source of truth.
- New preference values, inferred traits, adaptive policy, recommendation,
  evidence or grading logic, provider/model execution, reminder delivery,
  background work, cloud operations, or production claims.
- Reimplementing focused evidence already accepted by WRK-0150, WRK-0156, or
  WRK-0161 when the complete runner can compose it directly.

## Expected File and Boundary Impact

| Boundary | Owned change | Evidence target |
| --- | --- | --- |
| Live orchestration | Add composite snapshots, named-family isolation checks, learner-context correlation, restart equality, and report facts | Cross-family containment in one real topology |
| Pure qualification | Add focused helper tests | Fail closed on leakage or malformed aggregate evidence without infrastructure |
| Public product | Inspect only; no product file is writable | Existing browser/headless contracts remain unchanged |
| Direct documentation | Reconcile Web, Learner-model, local runtime, architecture assurance, and known gaps | Claims distinguish qualified shared-core semantics from unqualified cloud operation |
| Planning | Update WRK-0164, SLI-0077, CAP-0018, and register together | Deterministic packet, slice, and CAP completion |

No unlisted product, contract, migration, client, dependency, design-system,
deployment-composition, or planning file may change.

## Contracts and Interfaces

This packet consumes the existing protected routes under
`/api/v1/learner-preferences`,
`/api/v1/learner-presentation-preferences`, and
`/api/v1/learner-assistance-preferences`, including their mutation, history,
reset behavior, and export operations. It creates no fourth or aggregate API.

The composite snapshot is test evidence only. It is a closed mapping from the
three stable family names to their existing profile, change, and mutation row
snapshots. The isolation assertion accepts an exact `changed_family`, requires
that family to change when expected, and requires every other family to remain
equal. The final correlation uses opaque learner IDs only and must not expose
cookies, credentials, connection strings, personal content, prompts, financial
account data, provider data, or private storage locators.

The cumulative report contains closed booleans and counts sufficient to state
what was qualified. It is not a learner record, public API, portable export,
or authorization source.

## Dependencies and Parallel Safety

WRK-0150, WRK-0156, and WRK-0161 are complete and supply the family-level
evidence this packet composes. The packet owns the shared approved-lesson
runner, its pure test module, direct assurance sources, and CAP closure files;
it is not parallel-safe with any writer on those paths.

Claim from a recorded base revision, acquire exact-file leases before edits,
and retain one owner until finalization. Reviewer and approval records remain
only in ignored local control-plane storage.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Learner-family phase | Composite state before one family journey | Browser, headless, replay, and race work completes for that family | Only the named family's rows change; both other families remain exact | live runner/PostgreSQL |
| All families retained | All three family journeys have completed | Composite state is inspected | Each family has its own profile, changes, mutations, revision, and profile ID | live runner/PostgreSQL |
| Shared authorized context | Three final learner-owned profiles exist | Opaque learner identifiers are correlated | Exactly one current learner context is represented without caller selection | live runner/PostgreSQL |
| Distinct authorities | Three final profiles exist | IDs and exported shapes are compared | Profile identities and schema-specific values remain distinct and no aggregate profile exists | runner/contracts |
| Headless read containment | Composite state is captured | Ordinary clients read/history/export/replay exact requests | No family changes outside an accepted named mutation | runner/public HTTP/PostgreSQL |
| Restart containment | Final composite state exists | Production Python host restarts without reseeding | Every family remains exactly equivalent and separate | restart/API/PostgreSQL |
| Browser-local exclusion | Theme and reminder journeys run | Public API captures and database rows are inspected | Neither local setting appears in learner-owned API or storage | Chromium/contract/PostgreSQL |
| No downstream authority | Full preference journey runs | Unrelated state fingerprint is compared | Evidence, competency, grading, eligibility, financial, provider/model, and notification state remain unchanged | runner/security/architecture |
| Leakage rejection | A non-named family changes in a pure fixture | Isolation helper evaluates it | Qualification fails with the leaked family named | pure pytest |
| Malformed aggregate rejection | A family is missing, extra, or unknown | Helper validates it | Qualification fails before a misleading report is produced | pure pytest |
| Flexible valid contents | IDs, times, revisions, and row counts vary within existing contracts | Isolation helper compares before/after | Qualification depends on family identity and equality, not fixture count or ordering | pure pytest |
| Existing cumulative journey | Valid delivered interfaces are exercised | Complete workflow runs | Browser/headless parity, accessibility, privacy, races, restart, recovery, and cleanup all still pass | existing full-stack suites |
| Exact cleanup | Qualification succeeds or fails | Runner exits | Only its named disposable topology and bounded artifacts are removed | runner/finally |

## Verification Commands

Run packet and planning validation, implementation gate, focused pure replay
tests, the complete preference contract/domain/application/PostgreSQL/API
suites selected from the actual diff, full Web tests, TypeScript typecheck,
zero-warning lint, production build, and the focused Chromium preference
journeys. Run the complete isolated approved-lesson workflow to collect the
cumulative browser/headless/PostgreSQL/restart/cleanup evidence.

Also run architecture/import and persistence-ownership checks; security,
privacy, learner-language, design-system, documentation, planning, dependency,
Python compilation, and whitespace checks; controller-selected exact-candidate
verification; one independent technical review; deterministic slice and CAP
completion structure; and `python dev-tools/agent/check_ready.py`. Record only
commands that pass and do not inflate a harmless style issue into a functional
blocker.

## Documentation and Evidence Update

Record the exact candidate and receipt; three-family isolation matrix; one
opaque learner context with distinct family authorities; browser/headless API
parity; local theme and reminder exclusion; exact replay and concurrency;
normal restart; unrelated-state noninterference; accessibility, privacy,
containment, cleanup; focused, live, architecture, security, and aggregate
checks; assumptions; unsupported deployment profiles; and remaining gaps.

Update only the direct sources in `write_scope`. Approval identities, reviewer
records, and review histories remain absent from tracked artifacts.

## Stop Conditions

Stop for a required product, contract, schema, migration, OpenAPI, generated-
client, browser-feature, local-adapter, dependency, or deployment-composition
change; ambiguous family ownership; a combined API or transaction; inconsistent
browser/headless meaning; retained-data loss; private-data leak; caller-selected
learner identity; preference use as evidence, competency, authorization,
grading, eligibility, recommendation, financial suitability, provider/model
permission, notification authority, or irreversible action; provider/model or
external execution; managed-cloud, tenancy, licensing, recovery, legal, or
commercial expansion; stale CAP authority; active write collision; or material
CAP-0018/SLI-0077 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, generated values, fixture count or order, or an
advisory readability signal. Fix bounded inconsequential evidence issues in
scope or defer optional polish to CAP-0031.

## Required Handoff

Report `CAP-0018.SLI-0077.WRK-0164`; exact candidate and receipt; cross-family
isolation matrix; shared opaque learner context and distinct profile identities;
browser/headless parity; browser-local exclusion; replay, concurrency, restart,
privacy, accessibility, containment, cleanup, focused/live/architecture/
security/aggregate checks; changed files; documentation impact; assumptions;
unsupported cloud profiles; and residual gaps. Confirm that no product contract,
combined API, generated client, preference meaning, identity, provider, model,
notification, external action, or financial behavior changed, then close
SLI-0077 and CAP-0018 deterministically.

## Planning History

- 2026-10-18: Authored just in time after the three delivering slices and their
  final qualification packets completed. The packet reuses one established
  topology and adds only missing composite isolation evidence. It preserves the
  approved CAP-0018 package and requires no lower-level approval.
- 2026-10-18: Activated from recorded base `d727791` after validating current
  CAP authority, all three complete dependencies, the exact write scope, and no
  active coordination collision. The packet-start manifest selected affected
  verification and one independent technical review.
- 2026-10-18: Added the exact regenerated static browser directory to the
  bounded generated scope after the production build refreshed its content
  hash. This is derived candidate evidence only and changes no product source,
  contract, behavior, or CAP boundary.
