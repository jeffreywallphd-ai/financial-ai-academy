---
id: WRK-0066
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0023
capability: CAP-0005
depends_on: ["WRK-0065"]
decision_gates: []
parallel_safe_with: []
write_scope: ["apps/web/README.md", "apps/web/tests/browser/approved-lesson/approved-lesson.e2e.ts", "apps/web/tests/browser/approved-lesson/curriculum-graph.e2e.ts", "backend/src/financial_ai_academy/modules/adaptation/README.md", "deployments/local/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/adaptive-navigation-state-contract.md", "tests/e2e/approved-lesson/run.py", "docs/planning/work-packets/WRK-0066-qualify-live-curriculum-navigation-state.md", "docs/planning/vertical-slices/SLI-0023-explain-deterministic-curriculum-state.md", "docs/planning/register.md"]
generated_artifacts: []
base_revision: ef4ca5aed16b68af76a11a1f7cb1b02182a99c46
claim_id: WRK-0066:cddf5dc3-73b8-43a6-9818-ce10ef67cca5
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T01:12:55Z
---

# Agent Work Packet: Qualify Live Curriculum Navigation State

## Objective and Deliverable

Complete SLI-0023 by extending the existing isolated cross-system qualification
so real PostgreSQL repositories, the Python application, same-origin static
browser assets, the generated client, and pinned Chromium prove the complete
server-evaluated navigation-state path. The live evidence must connect retained
lesson completion to the exact navigation projection, compare API facts with
both peer browser views, exercise protected and missing-version failures, and
leave the reusable runner's bounded cleanup behavior intact.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the learning-adaptation, interface-design,
testing-quality, architecture-contract, and delivery-planning packs. Read the
change-impact matrix, decision readiness, CAP-0005, SLI-0023, WRK-0062,
WRK-0063, WRK-0065, ADR-0005, ADR-0009, ADR-0014, the adaptive-pathway and
navigation-state contracts, web and deployment READMEs, the local composition
fixture, the cross-system runner, both live browser specifications, and the
affected API/UI implementation and tests.

## Decisions and Assumptions

- The existing clean-start runner is the qualification harness. This packet
  extends its assertions and report; it does not create another database,
  server, fixture, or browser orchestration path.
- One run starts from an empty isolated database and single-profile learner.
  The first live lesson scenario may capture navigation state before and after
  its own exact retained completion, so the transition does not depend on test
  order, cached browser state, or preexisting evidence.
- The live graph scenario compares the protected navigation API with the
  rendered page only after establishing the opaque session. It treats the
  returned state, reason order, policy identity, evaluation time, and digests
  as server facts and does not reproduce policy or canonicalization in tests.
- Assessment completion and eligibility remain unavailable when the accepted
  live source reports that bounded limitation. The test records it rather than
  inventing a completion or changing product behavior.
- Existing `postgres:18.4`, loopback-only Python host, static build, pinned
  Chromium, external-isolated-database acknowledgement, redaction, and exact
  teardown safeguards remain authoritative.

## In Scope

- Capture the exact protected navigation response before and after the live
  lesson's retained completion in the same learner context and prove that the
  lesson completion and ordered reasons change only as the server reports.
- Qualify the live navigation API envelope, graph identity/digest, policy and
  source/projection provenance, complete graph-ordered activity closure,
  orthogonal state dimensions, multiple reasons/references, and bounded
  assessment-source limitation.
- Compare every live activity's state labels, explanation text, and references
  with the rendered list and peer map while retaining no-launch and no-mastery
  boundaries.
- Extend unauthorized, unsupported-query, missing-exact-version, narrow,
  keyboard, theme, axe, forced-color, reduced-motion, and 200-percent text
  checks across the live navigation path.
- Add direct anti-rigidity assertions for the fixture's shared optional branch,
  unbranched activity, multiple ordered reasons, variable reference counts,
  and complete activity set without hard-coding one specialized card layout.
- Update the runner report and deployment/web documentation to state the exact
  newly qualified boundary and remaining gaps.

## Out of Scope

Product runtime, domain, API, generated client, contract, policy, graph fixture,
completion semantics, persistence schema, migration, activity launch,
return/current-position history, ranking, recommendation, mastery or
competency labels, model output, experiments, new provider/cloud/dependency,
additional browsers, remote binding, production deployment, recovery claims,
or changes to CAP-0005's accepted scope.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Live browser evidence | current approved-lesson and graph live specifications | the two listed `.e2e.ts` files | Connect retained evidence, protected API facts, and peer UI without changing product behavior |
| Qualification runner | isolated PostgreSQL/Python/static/browser orchestration and report | `tests/e2e/approved-lesson/run.py` | Report the navigation boundary already exercised by the single reusable harness |
| Deployment/web guidance | current qualified/unqualified claims | listed web and local deployment READMEs | Keep evidence claims exact and prevent production or recovery overstatement |
| Planning evidence | SLI packet table, history, register | this packet, SLI-0023, register | Complete the final dependency-ordered packet and slice coherently |

No product source, backend module, contract, generated artifact, design-system
asset, package metadata, lockfile, deployment composition, or fixture source may
change.

## Contracts and Interfaces

The live tests consume the generated `NavigationState` and `CurriculumGraph`
types and the two protected exact-version GETs. They establish learner context
through ordinary browser use and never send learner, policy, provider, or
permission selectors. A valid response must name the exact graph identity and
digest and contain one activity state for every graph activity in exact graph
order. UI assertions locate each activity card by reviewed activity identity
or heading and compare the four dimensions plus every returned reason and
reference; they do not duplicate the validator or policy algorithm.

The runner's final JSON report adds a concise navigation-state qualification
claim while retaining the hashed static index, database topology, isolated
filesystem, Python application process, graph/catalog fixture identities, and
same-origin serving facts. It exposes no DSN, cookie, learner identity, answer,
or provider payload.

## Dependencies and Parallel Safety

WRK-0065 is complete and supplies the accepted browser join and annotations.
This packet is the final SLI-0023 seam and overlaps the existing live suite,
runner report, web/deployment guidance, and planning records; it is not
parallel-safe with another packet touching those files. It must preserve the
already qualified discovery, graph, lesson, assessment, completion, security,
and cleanup paths.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Live evidence transition | Empty isolated storage and one established learner context | Exact lesson completion is recorded | A fresh protected navigation read reports the lesson completed with exact retained-evidence reasons while the prior read did not | approved-lesson live browser/API |
| Exact state parity | Published five-activity graph and current navigation projection | Exact graph page opens | Graph/state identity matches and every state dimension, ordered explanation, and reference appears in both list and map | graph live browser/API |
| Bounded assessment source | Assessment activity has no accepted completion projection | Live state is read | Completion/eligibility remain unavailable with bounded reasons and no mastery inference | graph live browser/API |
| Flexible graph shape | Shared optional branches, unbranched activity, multiple reasons, and variable reference counts exist | Live page renders | All compatible facts remain visible without a specialized count/layout assumption | anti-rigidity live assertions |
| Protected exact read | No session, a query selector, or missing exact version is requested | Navigation API/page is used | Standard bounded denial or missing/unavailable page appears with no learner/state leak and no latest substitution | live API/browser |
| Accessible adaptive display | View, theme, viewport, keyboard, forced-color, reduced-motion, or text scale changes | Learner uses the page | Equivalent facts and actions remain axe-clean, operable, and non-overflowing | live browser/design |
| Harness containment | Qualification succeeds or fails | Runner exits | Only its exact process, uniquely named database container, and bounded temporary data root are removed | runner behavior/current controls |

## Verification Commands

Run the updated production build and live runner through an explicitly
acknowledged isolated PostgreSQL service or its own pinned disposable
container. Also run focused live-spec discovery, TypeScript typecheck, lint,
complete Vitest and mocked graph browser suites, architecture, security,
design-system, documentation, planning, packet validation, diff, and aggregate
readiness checks. Prepare one exact candidate, qualifying receipt, and
independent technical review before completion.

## Documentation and Evidence Update

Record the live before/after completion facts, API/UI parity, exact state and
reason matrix, graph/policy/source/projection provenance, authorization and
missing-version behavior, anti-rigidity shapes, accessibility/theme/reflow,
database/application/static/browser topology, teardown, exact test counts,
assumptions, and remaining gaps in this packet and SLI-0023. Reconcile the web
and local deployment claims without implying production, recovery, multi-user,
model, recommendation, mastery, or cross-browser qualification. Keep approval
and reviewer records only in ignored local stores.

## Stop Conditions

Stop for a runtime, graph, contract, generated client, policy, fixture meaning,
completion meaning, migration, persistence, activity-launch, return-history,
model/ranking/recommendation/mastery, provider/cloud, dependency, design-system,
multi-browser, remote-host, production/recovery, or external-action change;
failed containment or cleanup; active scope collision; conflicting canonical
authority; material CAP/SLI drift; stale CAP approval; or evidence that cannot
be obtained through the current isolated harness.

## Required Handoff

Report the exact candidate; before/after completion navigation facts; complete
graph/state closure and provenance; state/reason UI parity; assessment-source,
denial, query, and missing-version results; anti-rigidity, theme,
accessibility, responsive, security, architecture, focused, aggregate,
receipt, review, and cleanup evidence; changed paths; assumptions and known
gaps; and confirmation that no product runtime, launch, client policy, model,
ranking, recommendation, mastery, persistence, migration, or new authority was
added. Leave SLI-0023 ready for deterministic closure or return a bounded
blocker.

## Completion Evidence

- Exact implementation candidate `f9e4e68` passed the affected verification
  selected for its planning, documentation, and architecture boundaries. Its
  retained qualifying receipt records a stable post-run tree and no failed
  command.
- The same exact candidate passed the isolated PostgreSQL 18.4, Python,
  same-origin static-client, and pinned-Chromium runner. All eight live
  scenarios passed, including the retained-completion transition, protected
  navigation API and list/map parity, accessibility and responsive variants,
  denial paths, and exact cleanup.
- The missing exact-version response was checked directly for absence of the
  curriculum title, learner or activity state, completion and eligibility
  fields, reason references, and graph, source-set, or projection digests.
  Unsupported queries and missing sessions remained bounded failures.
- Canonical Adaptation and navigation-contract guidance now describes the
  delivered server-evaluated projection and browser presentation boundary.
  Architecture verification records deterministic eligibility before ranking
  while retaining unavailable assessment completion as an explicit gap.
- TypeScript typecheck and lint, the focused web and browser checks, 15
  architecture checks, documentation and planning integrity, Git whitespace,
  and the aggregate readiness gate passed. The aggregate gate reported all 27
  checks ready when its temporary fixtures were confined to the ignored local
  workspace.
- No product runtime, transport contract, generated client, policy, fixture,
  persistence schema, migration, dependency, activity-launch authority,
  model, ranking, recommendation, or mastery behavior changed. Non-Chromium
  browsers, real assistive-technology sessions, managed-cloud composition,
  production recovery, and supported assessment completion remain outside the
  qualified boundary.

## Planning History

- 2026-10-16: Authored just in time after WRK-0065 completion. The packet
  reuses the existing isolated cross-system harness to connect exact retained
  lesson evidence, protected navigation API facts, and the accepted peer
  browser views. It adds no product behavior or decision gate and remains
  within the approved CAP-0005 package.
- 2026-10-16: Resumed the same bounded packet to reconcile three stale
  architecture/module qualification statements, assert missing-version
  response confidentiality, and rerun exact-candidate affected verification
  after the repository selector correction. No product or contract meaning
  changes.
- 2026-10-16: Completed the packet after exact-candidate affected and live
  composed-system verification passed, objective documentation matched the
  delivered boundary, cleanup remained exact, and no open technical finding
  remained.
