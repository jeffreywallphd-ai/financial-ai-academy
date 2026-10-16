---
id: SLI-0024
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: CAP-0005
depends_on: ["SLI-0023"]
decision_gates: []
---

# Vertical Slice: Open and Return to an Eligible Activity

## Outcome and User Scenario

A learner viewing one exact approved learning-path version can choose an
available lesson that the current deterministic navigation state says is ready,
open that exact lesson through a server-checked curriculum launch, and return to
the same learning-path version and activity. The refreshed path shows the
learner's current position and exact completion state without hiding optional
branches, selecting a next activity automatically, or treating completion as
mastery.

When a newer curriculum version changes requirements, the old exact-version
route and its evidence remain intelligible. Completion is reused only when the
new graph intentionally references the same exact placed resource; a different
placement or package does not inherit completion by title or activity ID.

## Scope Boundaries

### In Scope

- An Adaptation-owned deterministic launch-resolution operation for one exact
  curriculum ID, curriculum version, and activity ID.
- A protected API and generated TypeScript client that recompute current
  navigation state and return one closed, same-origin exact lesson destination
  only when the activity exists, is a supported lesson, remains available, and
  is eligible to open.
- Use of the existing server-issued navigation and lesson-read permissions;
  callers cannot select a learner identity, destination, placement, package,
  completion state, or eligibility result.
- Learner-facing `Start lesson` and `Review lesson` actions on both equivalent
  list and map presentations, with no open action for locked, unavailable, or
  unsupported assessment activities.
- Validated URL-backed return context that identifies the exact curriculum
  version and selected activity for presentation only. It never grants access
  or changes server policy.
- A lesson-page return action and exact activity marker when the learner comes
  back, followed by a fresh graph/navigation read so newly accepted completion
  evidence is visible.
- Exact-version tests covering changed curriculum requirements, unchanged exact
  placed resources, optional branches, direct/tampered launch attempts, and
  interruption or refresh.
- Focused component and browser evidence for keyboard order, focus, non-color
  position state, accessible action names, responsive reflow, forced colors,
  reduced motion, and light/dark/system themes.

### Out of Scope

- Ranking, recommending, automatically selecting, or automatically opening a
  next activity; mastery or competency estimation; engagement optimization; or
  model-generated explanations.
- Standalone execution of assessment activities or a new Assessment completion
  meaning. Unsupported activity kinds remain visibly unavailable for launch.
- Enrollment, waivers, instructor overrides, organization policy, cross-
  curriculum credit, authoring, certification, or external learning standards.
- A durable current-position, navigation-history, recommendation, or launch-
  grant table; browser return context is not learner evidence.
- A `latest` curriculum alias, automatic version migration, or completion
  transfer based on labels, titles, activity IDs, or inferred equivalence.
- Changing the existing lesson-package, curriculum-graph, navigation-state,
  Assessment evidence, or Learner-model completion semantics.

## Canonical Context and Decisions

- [CAP-0005](../capabilities/CAP-0005-navigate-competency-based-curriculum.md)
  includes learner-controlled exact activity opening, return context, current
  position, and version-safe completion meaning after deterministic state.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  keeps graph and placement meaning in Curriculum, completion in Learner model,
  evidence in Assessment, and host policy out of transport code.
- [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
  requires exact immutable package identity and forbids silent `latest`
  substitution.
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  and [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
  keep eligibility deterministic and authoritative before any later ranking.
- [Curriculum Graph Contract](../../architecture/contracts/curriculum-graph-contract.md)
  owns the exact placed activity reference; the
  [Navigation-State Contract](../../architecture/contracts/adaptive-navigation-state-contract.md)
  owns current server-evaluated completion, availability, requirement, and
  eligibility meaning.
- SLI-0022 and SLI-0023 provide the exact graph, protected current navigation
  projection, generated client, accessible list/map, and live composed-system
  baseline consumed here. SLI-0024 does not revise their v1 contracts.
- Decision readiness permits this deterministic, provider-neutral path. It
  introduces no model authority, identity, tenancy, provider, queue,
  encryption, recovery, legal/commercial, or external-execution decision.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Protected Adaptation launch resolution plus exact URL-backed return context | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. New curriculum-context lesson-read facade that duplicates the existing lesson response | yes | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 12 |
| C. Render a direct browser link from graph references and trust the displayed state | no - the client would become launch-policy authority and stale state could bypass re-evaluation | - | - | - | - | - | - | - |
| D. Persist current position and migrate completion between curriculum versions | no - durable ownership, migration, and equivalence authority are unnecessary and unresolved for this slice | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the highest-scoring eligible increment. It adds one narrow
server-side decision at the Adaptation boundary that already composes exact
Curriculum and Learner-model facts, reuses the existing lesson route and read
contract, and keeps return context explicitly non-authoritative. It is directly
testable through policy, API, generated-client, component, and browser seams and
adds no durable data or migration.

Candidate B can enforce the same policy but creates a second lesson-read
transport and tighter Adaptation-to-Content delivery coupling, so its contract
clarity and independence are lower. Candidate C violates the CAP requirement
that application policy, not browser state, authorize the curriculum launch.
Candidate D introduces state and semantic-transfer authority beyond the
approved outcome instead of preserving history through exact references.

## Boundary Path

1. The browser loads the exact Curriculum graph and current Adaptation
   navigation projection exactly as in SLI-0023; list and map remain peer
   presentations of the same closed data.
2. For an activity that appears openable, the browser submits only curriculum
   ID, curriculum version, and activity ID through the generated public client.
   It does not send a learner, destination, placement, package, or state claim.
3. The API host resolves the learner context and requires the existing
   server-issued navigation and lesson-read permissions before calling the
   public Adaptation operation.
4. Adaptation reloads the exact graph and current completion sources, evaluates
   the deterministic policy, finds the requested activity in the evaluated
   graph, and refuses missing, mismatched, locked, unavailable, or unsupported
   activity kinds without returning a destination.
5. For an eligible or completed available lesson, Adaptation returns a closed
   launch-resolution value containing exact graph/projection and lesson
   placement/package references plus the fixed same-origin lesson destination.
   The host exposes only that value through a versioned response.
6. The browser navigates to the existing lesson route and carries validated
   exact curriculum/activity return context for presentation. The lesson API
   continues to enforce its own exact placement authorization and package
   contract.
7. Returning opens the same exact curriculum version with the selected activity
   identified in the URL. The route reloads graph and navigation data, marks the
   activity in text and non-color styling, and reflects any newly retained
   completion without client-side policy or evidence mutation.
8. Old and new curriculum versions remain separate exact routes. Completion can
   appear in both only when both graph versions intentionally reference the
   same exact placement/package identity and digest.

## Contracts, Data, and Provenance

Add a closed `activity-launch-v1` response under the existing Adaptation
contract family. It identifies schema version, curriculum ID/version/digest,
activity ID, navigation projection digest and evaluation time, exact lesson
placement and package identity/version/digest, and one same-origin destination.
The request is path-bound to the exact curriculum version and activity and
accepts no body, learner selector, destination, policy result, or fallback
version. Exact field names and error mapping are frozen in the first packet.

The launch resolution is a current deterministic decision, not a durable
recommendation, completion event, or access grant. It contains no learner or
provider identity, answer, score, private reason payload, approval data,
storage key, or arbitrary URL. Standard protected denials remain bounded.
Locked, unavailable, unsupported, missing, stale, malformed, and source-
unavailable cases return no destination.

Return context is a validated same-origin presentation locator built from the
already known exact curriculum and activity identifiers. It is safe to refresh,
copy, omit, or tamper with because the server independently rechecks launch
policy and the graph route validates membership before showing a position
marker. No database schema or event changes. Assessment evidence and Learner-
model projections remain immutable/rebuildable sources, and graph versions
remain append-only.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Eligible lesson | The learner sees `Start lesson`; a server-rechecked launch returns the exact placed lesson destination and the lesson opens | Adaptation/API/component/browser |
| Completed lesson | The learner sees `Review lesson`; reopening preserves completion meaning and exact package provenance without creating new evidence | Policy/API/component/live browser |
| Locked prerequisite | No open action is presented, and a direct launch request is refused after current server evaluation with no destination or hidden state | Policy/API/browser denial |
| Unavailable or unsupported activity | The activity and explanation remain visible, but unavailable lessons and assessment-only activities cannot launch | Policy/API/component |
| Stale or tampered request | Unknown activity, wrong curriculum version, changed client state, or a fabricated placement/destination fails closed and never substitutes a version | Contract/API/browser |
| Interrupted navigation | Refreshing the lesson or curriculum route preserves valid exact return context; invalid context is ignored safely and never affects authorization | Unit/component/browser |
| Return after completion | After accepted lesson completion, returning reloads current navigation state and shows the selected activity as complete and current | Live PostgreSQL/Python/browser |
| Optional branch | Optional activities remain visibly optional before, during, and after launch; opening one does not hide siblings or make it a requirement | Policy/component/browser anti-rigidity |
| Curriculum version change | Old and new exact routes coexist; a changed placement/package receives no inherited completion, while a deliberately reused exact resource may reuse its existing evidence | Policy/contract/live integration |
| Multiple and flexible graph shapes | Multiple entries, unbranched activities, shared same-kind branches, absent presentation hints, and sibling reordering need no code or schema special case | Unit/component/browser anti-rigidity |
| Unauthorized request | Missing either required server-issued permission returns the standard protected denial without graph, learner, state, or destination data | API integration |
| Accessible current position | List and map expose the same action and selected-position text with logical focus, non-color meaning, zoom/reflow, forced colors, reduced motion, and theme parity | Component/browser/design-system |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
their work begins. The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0085 | Freeze activity-launch v1, the pure launch decision, bounded errors, and direct anti-rigidity corpus | SLI-0023 | none | complete |
| WRK-0086 | Compose the protected application/API operation through current public gateways and regenerate the client | WRK-0085 | none | complete |
| JIT-C | Add learner actions, validated return context, and equivalent list/map current-position presentation | JIT-B | none | planned |
| JIT-D | Qualify exact launch/return/completion/version behavior in the isolated live stack and reconcile documentation | JIT-C | none | planned |

## Verification and Qualification

Run the launch contract/compatibility corpus; Adaptation domain and application
tests; public-boundary architecture tests; protected API and OpenAPI snapshot
checks; generated-client usage tests; curriculum-graph and lesson unit/component
tests; TypeScript typecheck, lint, and build; focused Chromium tests; design,
language, documentation, planning, architecture, security, and Git whitespace
checks; affected exact-candidate verification; and
`python dev-tools/agent/check_ready.py`.

The final packet must use the existing isolated PostgreSQL 18.4, Python host,
same-origin production assets, and pinned Chromium path to prove server-side
launch denial, exact lesson opening, retained completion on return, two exact
curriculum versions, cleanup, and no destination leakage. Tests must derive
expected paths and state from fixture records rather than hard-code one graph
shape. Whitespace, advisory copy, and nonfunctional styling do not create a
review cycle or select unrelated backend/Docker work.

## Rollback and Migration

The launch contract, pure decision, protected endpoint, generated-client
surface, and UI actions are additive. No database, event, evidence, or
curriculum migration exists. Rollback removes the UI action/return context,
then the API/launch operation and contract; the complete SLI-0023 graph and
navigation experience remains usable. Existing completion evidence and exact
curriculum versions are not rewritten.

## Stop Conditions

Stop for ranking, recommendation, automatic next-step selection, model
inference, mastery or competency claims, a new activity-completion meaning,
standalone assessment execution, durable current-position or launch state,
completion transfer by inferred equivalence, a `latest` alias, caller-selected
learner/destination/state, browser-authoritative eligibility, cross-module
repository access, provider-specific state, graph mutation, organization
policy, managed-cloud dependencies, conflicting canonical guidance, active
file overlap, stale CAP authority, or material CAP-0005 drift.

Do not stop or request another approval for detailed field names, exact files,
packet decomposition, focused tests, harmless whitespace, advisory wording, or
nonfunctional styling that remains inside this slice. Fix bounded functional or
accessibility defects locally; defer optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery updates the Adaptation and host READMEs, activity-launch contract and
compatibility guidance, API/client contract notes, curriculum-graph and lesson
feature documentation, architecture-verification map, affected known gaps, and
this slice/register evidence. Completion must record exact policy/contract/API/
component/browser/live commands and results; positive, refusal, interruption,
version, provenance, accessibility, theme, and anti-rigidity evidence; contract
compatibility; migration non-applicability; assumptions and known gaps; and
confirmation that model, recommendation, mastery, provider, external service,
and durable-state authority did not change.

## Planning History

- 2026-10-16: Refined just in time after SLI-0023 completion. Candidate A
  scored 14/14 because it rechecks deterministic eligibility at the existing
  Adaptation boundary, reuses the exact lesson path, and preserves return and
  version context without durable navigation state. The four packet seams
  conform to the approved CAP-0005 outcome, manifest, dependency order, scope,
  risk posture, and non-goals and add no decision or lower-level approval gate.
- 2026-10-16: Refined JIT-A as WRK-0085 around the closed activity-launch v1
  success contract, pure exact-input decision, stable bounded denials, public
  Adaptation surface, and direct compatibility/anti-rigidity evidence.
- 2026-10-16: Activated WRK-0085 after revalidating the current CAP package,
  completed dependency, exact bounded scope, executable checks, and absence of
  a decision or active ownership collision.
- 2026-10-16: Completed WRK-0085 at accepted candidate
  `e5de843db38a67c00b5527129eaf03198c3c0d42`. The closed schema, pure
  resolver, exact-context denials, compatibility corpus, public exports,
  flexible-graph tests, and architecture evidence passed focused, full
  Adaptation, compilation, planning, documentation, whitespace, affected-
  verification, independent-review, and aggregate-readiness checks. No
  migration, persistence, API, generated-client, browser, evidence, model,
  provider, or external-action boundary changed; composed launch remains JIT-B.
- 2026-10-16: Refined JIT-B as WRK-0086 around one fresh Adaptation
  graph/projection composition, the accepted pure launch resolver, both
  existing read permissions, a bodyless exact-version endpoint, bounded HTTP
  denials, and deterministic OpenAPI/client generation. No decision or
  lower-level approval gate was added.
- 2026-10-16: Activated WRK-0086 after revalidating its completed WRK-0085
  dependency, current CAP package, exact write/generated scope, accepted
  permissions and contracts, and absence of a decision or edit collision.
- 2026-10-16: Completed WRK-0086 at exact candidate
  `9d324b53d040ef6571897719b803d4eebd7692dd`. The single-context application
  composition, dual-permission protected endpoint, bounded denials, OpenAPI
  snapshot, and generated client passed focused and adjacent tests, generation
  checks, TypeScript checks, architecture fitness, affected verification, and
  aggregate readiness. Two nonblocking maintenance observations were deferred
  to CAP-0031 without reopening this functional packet. No persistence,
  migration, UI policy, new permission, model authority, provider, queue,
  cloud, or external-action boundary changed; learner interaction remains JIT-C.
