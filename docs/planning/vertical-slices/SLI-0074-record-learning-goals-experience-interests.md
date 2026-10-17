---
id: SLI-0074
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0018
updated: 2026-10-17
parent: CAP-0018
depends_on: []
decision_gates: []
---

# Vertical Slice: Record Learning Goals, Experience, and Interests

## Outcome and User Scenario

An authorized learner records learning goals, self-described experience, and
interests; reviews what is stored and why; revises or resets those choices; and
exports a portable versioned record with bounded change history. The same
protected public API serves the generated browser client and supported non-
browser clients. The platform does not infer sensitive traits, treat a stated
preference as evidence, or convert it into permission, eligibility, mastery,
financial suitability, or an irreversible action.

## Scope Boundaries

### In Scope

- A Learner-model-owned, additive `learner-preferences/v1` family for explicit
  learning goals, self-described experience, interests, profile revision,
  purpose and scope disclosures, bounded history, reset, and export.
- Learner-authored goals with stable server-owned identity, bounded plain-text
  title and optional detail, active/archived lifecycle, and learner-controlled
  order. Goals are intentions, not Curriculum requirements or evidence.
- Explicit experience selections and interest labels that preserve the
  learner's own statement and declared scope without inferring proficiency,
  demographics, health, disability, suitability, or protected traits.
- Deterministic create/revise/archive/restore/reorder/reset operations with an
  idempotency key, exact expected revision, server-owned learner context,
  canonical UTC time, bounded quotas, and confidential learner-safe failures.
- Module-owned PostgreSQL persistence for the current profile, accepted
  mutation replay, and bounded append-only change summaries without cross-
  module foreign keys or direct access to Curriculum, Assessment, Adaptation,
  Identity, or Personal-workspace storage.
- Protected API operations, reviewed OpenAPI, and generated TypeScript client
  behavior for browser, command-line, service, and future headless-AI callers
  under the same identity, authorization, validation, and mutation policy.
- An accessible, responsive `Learning preferences` browser flow that uses the
  generated client, leads with learner tasks and purpose, and places exact
  versions, identifiers, revisions, and digests in a `Technical record`.
- Focused and isolated live evidence for persistence, restart, exact replay,
  changed-key and stale-revision denial, reset/export, history bounds, learner
  isolation, privacy, accessibility, API/headless parity, and cleanup.
- Anti-rigidity evidence for varied valid wording, Unicode, empty and populated
  sections, different valid counts and ordering, optional detail, generated
  identities/times, and presentation changes that preserve behavior.

### Out of Scope

- Accessibility, theme, presentation, AI-assistance, or notification choices;
  those belong to SLI-0075 and SLI-0076.
- Automatic goal creation or revision, inferred experience or interests,
  behavioral profiling, embeddings, semantic classification, recommendation,
  adaptive ranking, experimentation, or model/provider calls.
- Curriculum prerequisites or competency definitions, Assessment evidence,
  Learner-model competency/mastery estimates, Adaptation eligibility, grades,
  credentials, completion, certification, financial advice, or suitability.
- Organization policy, tenancy, enterprise administration, guardian controls,
  collaboration, shared profiles, marketing consent, billing, managed-cloud
  retention/recovery, or cross-device synchronization claims.
- Medical or diagnostic information, hidden sensitive-trait fields, free-form
  attachment upload, arbitrary URLs, files, executable content, credentials,
  provider payloads, external notifications, or public profile publishing.
- A separate AI mode, agent-specific authority, autonomous durable mutation,
  or browser-local state as the source of truth.
- Styling-only polish that does not impair meaning, accessibility, responsive
  use, or theme parity; optional polish remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0018](../capabilities/CAP-0018-set-learning-goals-and-preferences.md)
  defines the four-slice outcome and this first preference increment.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) and the
  [Module Map](../../architecture/modules/module-map.md) assign learner
  preferences to Learner model while source evidence and policy remain with
  their owners.
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  keeps eligibility and policy deterministic and prevents preferences from
  becoming evidence or authority.
- [Identity Provider Contract](../../architecture/contracts/identity-provider-contract.md)
  and local identity guidance require server-owned learner context and
  protected operations.
- [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  [Decision Readiness](../../adr/decision-readiness.md), and the change-impact
  matrix require versioned additive contracts, module-owned persistence,
  generated clients, and local/cloud semantic parity.
- [Interface Design System](../../design/README.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern the learner-facing flow and progressive technical disclosure.
- No unresolved identity, tenancy, provider, model, licensing, execution,
  encryption, recovery, legal, or commercial choice is needed for this bounded
  local learner-owned profile.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Deliver explicit goals, self-described experience, and interests through Learner-model contracts, PostgreSQL, protected API, generated client, and accessible browser flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Deliver contracts, persistence, and API but defer the learner-visible review/revise/reset/export flow | yes | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 12 |
| C. Store the profile only in browser local storage | no - it cannot provide protected API/headless parity, server-owned identity, durable history, or restart recovery | - | - | - | - | - | - | - |
| D. Infer goals, experience, or interests from activity and assessment data | no - it creates hidden profiling and changes evidence, adaptive-authority, consent, privacy, and model-policy boundaries | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the smallest complete approved SLI-0074 path and scores 14/14.
It gives the learner direct control over explicit data, preserves one shared
public API for browser and headless use, and establishes stable contracts that
later CAP-0018 slices may consume without copying tables or redefining learner
ownership. Candidate B is technically bounded but omits the observable learner
outcome. Candidate C creates a browser-only authority. Candidate D is outside
the approved CAP and would require new privacy, adaptive-learning, and model-
authority decisions. Candidate A wins without a tie-break.

## Boundary Path

1. Closed versioned schemas define learner-entered goals, scoped self-
   descriptions of experience, interest labels, current profile, mutation
   intent, bounded change summary, and portable export without inference or
   downstream policy meaning.
2. Pure Learner-model values validate identifiers, text, enumeration, order,
   history bounds, chronology, revision, and canonical digest. A deterministic
   mutation function creates the next profile or reset state.
3. A Learner-model application service obtains learner identity from its
   context port, applies server-owned IDs and time, enforces exact replay and
   optimistic concurrency, and returns current/history/export projections.
4. A module-owned PostgreSQL repository atomically stores the current profile,
   accepted idempotency result, and bounded change summary. It does not query
   another module schema or treat preferences as learning evidence.
5. Protected FastAPI operations derive learner identity and permission only
   from the server session, map bounded failures, publish reviewed OpenAPI, and
   regenerate the shared TypeScript client.
6. The generated client powers an accessible `Learning preferences` route for
   viewing purpose, adding/revising/ordering/archiving data, reset, history,
   export, and reopening after interruption. A supported non-browser caller
   observes the same profile and policy.
7. Focused and isolated live qualification proves restart durability,
   idempotency, concurrency, privacy, isolation, API/headless/browser parity,
   accessibility, provenance, source-state non-interference, and exact cleanup.

## Contracts, Data, and Provenance

The additive `learner-preferences/v1` family has closed schemas for a current
profile, mutation intent, change-history result, and export. A profile has a
schema version, server-owned learner-bound profile ID, positive revision,
ordered goals, ordered experience entries, ordered interests, canonical
creation/update times, and a deterministic document digest.

A goal has a server-owned goal ID, bounded title and optional detail, explicit
active/archived state, and canonical creation/update times. An experience entry
is an explicit learner-selected level (`new`, `some_experience`, or
`experienced`) within a bounded learner-named subject; the value is a self-
description, never verified competency. An interest is a bounded learner-
authored label with stable server-owned identity. The contract preserves the
learner's original text and does not derive classifications, protected traits,
or Curriculum/Assessment meaning.

A mutation intent contains one idempotency key, exact expected revision, and a
closed operation for goal, experience, interest, ordering, archive/restore, or
reset behavior. Learner identity, object IDs, canonical times, next revision,
digest, and persistence facts are server authority. Exact replay returns the
accepted result; changed reuse or a stale revision fails without duplicate or
lost update. Reset creates a new empty revision and a bounded change summary;
it does not erase source evidence or other modules' state.

History contains bounded metadata needed to explain when and how the learner
changed this profile, not snapshots of every prior private value. Export
contains the current profile plus bounded history and purpose/limitation
metadata; it contains no session, permission, database, provider, hidden
profile, recommendation, evidence, score, or inferred field.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Empty open | An authorized learner opens a deterministic empty profile without a write side effect and sees purpose, scope, and a clear next action | domain/application/API/browser |
| Record explicit data | The learner adds varied valid goals, self-described experience, and interests and reopens the exact accepted order and wording | contract/application/PostgreSQL/API/browser/live |
| Revise and archive | The learner edits, orders, archives, restores, and removes only profile-owned values without changing Curriculum, Assessment, or learner evidence | domain/application/API/browser |
| Reset and history | Reset produces a new empty revision and an explanatory bounded change record while unrelated learning state remains unchanged | domain/PostgreSQL/API/live |
| Portable export | The learner downloads a versioned current-profile/history representation with purpose and limitations and no private implementation detail | contract/API/browser/live |
| Headless parity | A supported non-browser HTTP client reads and mutates the same profile through the same session, contract, and deterministic policy | API/live qualification |
| Exact retry and stale write | Repeating one exact mutation returns its accepted result; changed-key reuse or old expected revision fails without duplicate or overwrite | domain/PostgreSQL/API/live |
| Authorization and isolation | Caller-selected learner identity, missing session/permission, guessed IDs, and cross-learner reads fail closed with bounded public errors | application/API/security/live |
| No inferred authority | Profiles and exports are recursively inspected and downstream collaborators are observed | No inferred trait, evidence, mastery, eligibility, permission, recommendation, provider, or financial-suitability meaning is created | contract/architecture/security |
| Bounds and interruption | Text/count/history quotas and simulated write interruption fail atomically while the prior valid profile remains usable | domain/PostgreSQL/anti-rigidity |
| Flexible valid shapes | Empty/populated sections, Unicode and varied valid text, optional detail, different counts/order, and generated IDs/times remain valid | contract/domain/UI anti-rigidity |
| Accessible parity | Labels, purpose, forms, history, reset/export, errors, keyboard/focus, reflow, reduced motion, forced colors, and light/dark/system themes preserve equivalent content and actions | component/Chromium/design |
| Restart and cleanup | Accepted changes survive normal application restart and qualification removes only its isolated topology and ignored artifacts | PostgreSQL/live runner |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0147 | Freeze learner-preference v1 profile, mutation, history/export, compatibility, pure domain, transport-neutral parser/projector, privacy, and anti-rigidity contracts | none | none | complete |
| WRK-0148 | Compose Learner-model application/persistence/migrations, protected API, reviewed OpenAPI, and generated client | WRK-0147 | none | complete |
| JIT-C | Deliver the plain-language accessible `Learning preferences` browser flow exclusively through the generated client | JIT-B | none | captured |
| JIT-D | Qualify contracts, PostgreSQL, API/headless access, browser behavior, restart, accessibility, privacy, containment, and slice boundaries | JIT-C | none | captured |

Dependent packets are not reserved, authored, or claimed until their concrete
predecessor is complete.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; Learner-model preference domain,
application, repository, and API suites; real-PostgreSQL migration, atomicity,
replay, conflict, reset, restart, and isolation evidence; reviewed OpenAPI and
generated-client reproduction; web model/component tests; focused mocked and
isolated live Chromium; and one non-browser public-API observation.

Run architecture/import and persistence-ownership checks, security and privacy
checks, learner-language and design-system checks, documentation and planning
checks, whitespace, typecheck, zero-warning lint, build, affected verification,
independent technical review, completion structure, and
`python dev-tools/agent/check_ready.py`. Every packet includes focused anti-
rigidity evidence appropriate to its layer. Harmless whitespace, optional
wording, styling, fixture count, or ordering must not create a re-review loop.

## Rollback and Migration

Contracts and database changes are additive and versioned. New Learner-model
migrations require forward, reapply, and development-down evidence against real
PostgreSQL. Empty reads remain side-effect free; the first accepted mutation
may create the learner's profile atomically.

A code rollback may remove an unreferenced route and UI, but it cannot silently
reinterpret or transfer stored preferences. Public contract removal or
semantic change follows compatibility governance. Reset is a learner-requested
profile mutation, not a database rollback or deletion of source learning data.
Isolated qualification data may be deleted only inside its exact disposable
topology.

## Stop Conditions

Stop for inferred or hidden profiling; medical/protected-trait meaning;
preferences used as evidence, mastery, eligibility, permission, grading,
recommendation, experiment consent, financial suitability, or irreversible
action; Curriculum/Assessment/Adaptation ownership transfer; cross-module
persistence access; organization/collaborative ownership; provider/model/
network/credential use; external notifications; managed-cloud policy;
breaking contract change; destructive migration; private-data leakage; stale
CAP approval; active write collision; or material CAP-0018 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional styling, incidental fixture count/order, or another
inconsequential issue. Fix it locally within scope or defer optional polish to
CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will document explicit preference meaning and limitations, Learner-
model ownership, versioned contracts, persistence, protected API/headless
parity, purpose and privacy disclosures, reset/export behavior, accessible UI,
and exact qualification evidence. Completion records exact candidates, focused
and affected checks, receipts, privacy and anti-rigidity results, changed
boundaries, assumptions, and residual gaps without tracked reviewer identity or
approval history.

## Planning History

- 2026-10-17: Refined immediately before delivery from the approved CAP-0018
  manifest. Candidate A scored 14/14 and preserves explicit learner control,
  API/headless parity, Learner-model ownership, later-slice boundaries, and the
  CAP's no-inference and no-policy-bypass constraints. No slice approval is
  required.
- 2026-10-17: Activated through dependency-ready WRK-0147 after confirming the
  current CAP package, resolved decision posture, exact bounded write scope,
  and exclusive file-edit ownership. No lower-level approval is required.
- 2026-10-17: Refined dependency-ready JIT-B as WRK-0148 after the exact
  learner-preference contract and pure core completed. The packet keeps one
  protected browser/headless API and adds no new durable decision.
- 2026-10-17: Completed WRK-0148 with one protected API for browser and
  headless clients, module-owned PostgreSQL persistence, exact replay and
  optimistic revision semantics, bounded non-content history, portable
  export, reviewed OpenAPI, and generated TypeScript operations. The next
  dependency-ready increment is the browser flow; simultaneous-writer race
  evidence remains in the final live-qualification seam.
