---
id: SLI-0038
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0009
updated: 2026-10-18
parent: CAP-0009
depends_on: []
decision_gates: []
---

# Vertical Slice: Review Rebuildable Learning Progress

## Outcome and User Scenario

An authorized learner opens one chronological progress view of saved knowledge-
check completions, practice attempts, and accepted learning-project submissions.
Each item explains the observable result, time, source family, exact source
reference, and version. The view rebuilds from Assessment-owned append-oriented
evidence, remains usable when one evidence family is temporarily unavailable,
and never presents completion or a score as competency, mastery, a credential,
or financial ability. The same protected API serves generated browser and
ordinary headless clients.

## Scope Boundaries

### In Scope

- An additive, closed `learner-progress/v1` contract owned by Learner model for
  one projection identity, deterministic revision and digest, evidence cutoff,
  source-family freshness, stable newest-first timeline order, bounded pages,
  and opaque continuation bound to one exact projection revision.
- Typed timeline entries for accepted Assessment knowledge-check, practice, and
  learning-project evidence. Entries retain exact event/evidence, placement or
  Project, package/definition/snapshot, policy, score where applicable, and UTC
  occurrence references without answers, feedback text, artifact content, or
  another module's business record.
- Assessment public source operations that enumerate safe learner-scoped facts
  separately for the three evidence families. Learner identity comes only from
  the server context; the Learner-model adapter never reads Assessment tables.
- Learner-model deterministic normalization, exact duplicate replay, immutable-
  identity conflict handling, source-set digesting, and family-isolated rebuild.
  A successful family replaces only its derived family rows. An unavailable or
  inconsistent family preserves its last valid rows as explicitly stale, or is
  explicitly unavailable when no prior successful snapshot exists.
- Learner-model-owned PostgreSQL projection root, source-family checkpoints,
  and ordered derived entries with one transaction, advisory serialization,
  exact restart replay, interruption rollback, and no cross-schema foreign key.
- A protected read/rebuild API with `learner_progress.read`, server-owned learner
  context, reviewed OpenAPI, and one generated TypeScript client shared by the
  browser, command-line, service, and future headless-AI callers.
- An accessible `Your learning progress` browser route that leads with saved
  results and safe next actions, visibly distinguishes partial or stale source
  families, supports bounded continuation, and puts IDs, versions, policies,
  digests, and source timestamps in an accessible `Technical record`.
- Focused and isolated live qualification for empty and mixed evidence, family
  degradation, replay, conflict, stale continuation, restart, persistence,
  authorization, confidentiality, generated-client/headless parity,
  accessibility, source noninterference, and bounded cleanup.
- Anti-rigidity evidence for zero through many valid entries, all three family
  combinations, equal timestamps, Unicode-safe display context, additional
  valid source records, optional score meaning, and one family failing without
  disabling unrelated valid progress.

### Out of Scope

- Competency estimates or `insufficient`, `developing`, `demonstrated`, and
  `review_due` publication; those begin in SLI-0039 under ADR-0014.
- Adaptive ranking, next-step selection, recommendation records, adaptive item
  selection, experiments, instructor overlays, cohort analytics, credentials,
  accreditation, employability, financial suitability, or personalized advice.
- AI/ML models, model providers, feature pipelines, training datasets,
  calibration thresholds, promotion, shadow operation, or learner experiments.
- Mutating, correcting, deleting, or copying Assessment, Project, Curriculum,
  Content, or Audit source records; raw responses, answer keys, feedback text,
  project files, workspace state, or private owner payloads.
- Curriculum-wide progress percentages, prerequisite/eligibility conclusions,
  comparison and advanced filters, review-link navigation, or optional reviewer
  evidence. Those remain for SLI-0039 and SLI-0040.
- Organization tenancy, managed-cloud recovery, new provider/licensing policy,
  external execution, notifications, destructive repair, or public sharing.
- Styling-only polish that does not impair function, meaning, accessibility,
  responsive use, or theme parity; optional polish remains CAP-0031 work.

## Canonical Context and Decisions

- [CAP-0009](../capabilities/CAP-0009-track-progress-and-competency-evidence.md)
  defines the four-slice approved package and this evidence-first increment.
- [ADR-0014](../../adr/ADR-0014-governed-adaptive-learning-research-plane.md)
  requires evidence-centered provenance, deterministic replay, uncertainty and
  abstention before learner-facing competency publication, and a permanent
  evidence-only fallback. This slice establishes that fallback and no model.
- [Adaptive Pathway Architecture](../../architecture/learning/adaptive-pathway-architecture.md)
  assigns source evidence to Assessment and derived progress to Learner model.
- [Module Map](../../architecture/modules/module-map.md) and
  [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  prohibit direct cross-module storage access and keep completion distinct from
  mastery.
- Completed CAP-0001, CAP-0006, and CAP-0007 supply exact knowledge-check,
  practice, and learning-project Assessment evidence and existing rebuildable
  source-specific Learner-model projections. CAP-0026 supplies shared
  provenance and accountable-history references without becoming the source.
- [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  [Interface Design System](../../design/README.md),
  [Content Style Guide](../../design/content-style-guide.md), and
  [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern additive contracts, generated-client boundaries, plain learner
  language, progressive technical disclosure, and flexible semantic tests.
- DEC-0009 is complete through ADR-0014. No unresolved model, provider,
  identity, tenancy, licensing, recovery, or experiment choice is required for
  this deterministic evidence-only slice.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Build one Learner-model timeline over all three current Assessment evidence families with family-isolated freshness, PostgreSQL, protected API, generated client, and accessible browser flow | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Build the same vertical path for knowledge checks and practice only, deferring accepted learning-project evidence | yes | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 13 |
| C. Compose only whichever exact-resource projections have already been opened | no - it cannot enumerate complete source evidence, distinguish never-read from empty, or truthfully rebuild the learner timeline | - | - | - | - | - | - | - |
| D. Add probabilistic competency labels while building the timeline | no - it crosses SLI-0039 and requires concrete estimator, calibration, applicability, and publication qualification not selected by this increment | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is the smallest complete approved SLI-0038 path and scores 14 of
14. All three Assessment evidence families already exist behind public module
operations and are required by CAP-0009's learner-progress outcome. Including
them now prevents a misleading partial definition of “progress,” while family-
isolated checkpoints prevent an unavailable Project or practice source from
blocking valid knowledge-check history. Candidate B is bounded but leaves the
first public timeline knowingly incomplete for an already delivered evidence
family. Candidate C makes incidental prior reads authoritative. Candidate D
would materially cross the manifest boundary. Candidate A wins without a tie.

## Boundary Path

1. Closed `learner-progress/v1` schemas and compatibility fixtures define the
   projection, source-family checkpoints, typed evidence entries, page query,
   opaque continuation, and bounded errors without learner identity or private
   payload in the response.
2. Assessment exposes separate safe learner-scoped replay operations for
   knowledge-check, practice, and accepted learning-project evidence. Each
   validates retained rows and returns typed public facts without mutation.
3. A Learner-model source adapter consumes only those operations. The pure
   Learner-model core canonicalizes identities/times, deduplicates exact replay,
   rejects changed reuse, computes family and total source digests, and produces
   a deterministic newest-first timeline with explicit current/stale/
   unavailable source state.
4. A Learner-model PostgreSQL adapter atomically replaces successful family
   rows, carries forward only a prior valid failed-family snapshot as stale,
   updates one projection root and family checkpoints, and leaves the prior
   complete projection intact on interruption or conflict.
5. The application accepts only server learner context, rebuilds then reads one
   exact page, binds continuation to projection revision/digest/page size, and
   maps source failure to explicit partial meaning instead of false success or
   a whole-page outage.
6. Protected FastAPI operations enforce `learner_progress.read`, expose no
   caller-selected learner, publish reviewed OpenAPI, and regenerate the shared
   TypeScript client used by browser and ordinary headless clients.
7. The browser renders saved results, dates, source availability, score context,
   and safe navigation in plain language; exact technical evidence remains
   selectable in a native disclosure. It never calculates progress or
   competency.
8. Focused and disposable live evidence proves exact replay, family isolation,
   stale-cursor refusal, restart, database/source containment, accessibility,
   browser/headless parity, and cleanup.

## Contracts, Data, and Provenance

The additive contract has one projection version, positive revision, canonical
source digest, rebuild time, evidence cutoff, ordered source-family checkpoints,
total entry count, current page, and opaque continuation. A checkpoint names
only `knowledge_check`, `practice`, or `learning_project`; carries its public
source-contract version, state (`current`, `stale`, or `unavailable`), last
successful evidence cutoff and digest when known, and a bounded learner-safe
reason when it is not current.

Timeline entries form a closed discriminated union. Common fields include an
entry kind, event/evidence identity, occurred-at time, source-family state,
source contract and policy versions, and the exact owner reference needed for
replay. Knowledge-check and practice entries may expose bounded score/max-score
facts with explicit completion or attempt meaning. Project entries expose
accepted submission/snapshot and placement references with no qualitative
score. Raw answers, correct answers, feedback, workspace data, artifact bytes,
learner identity, storage locators, provider fields, recommendation state, and
competency claims are forbidden.

Ordering is newest occurrence first, then stable entry-kind and event identity
tie-breakers. Exact duplicates are idempotent. Reuse of an immutable event or
evidence identity for changed meaning fails that source family closed. A
successful rebuild advances the projection revision only when its canonical
meaning changes; an exact replay may refresh observation metadata without
inventing a new learning event. Continuations bind to revision, digest, offset,
and page size; any changed projection refuses the stale continuation rather
than mixing histories.

Learner model owns only the rebuildable root, checkpoints, and derived entries.
Assessment retains source truth. Audit retains integrity references. No foreign
key crosses module schemas. A source-family failure cannot silently erase its
last valid rows or mark them current; it cannot block current unrelated family
rows. No output becomes model-training truth or a competency estimate merely by
appearing in the timeline.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Empty learner | An authorized learner sees no saved progress, all configured source families current, the evidence-only limitation, and a safe route to learning | contract/domain/API/browser |
| Mixed timeline | Knowledge-check, varied practice attempts, and multiple accepted Project submissions appear in stable newest-first order with exact source/version references | contract/domain/PostgreSQL/API/browser/live |
| Exact replay | Rebuilding unchanged Assessment facts preserves entry identities, digest, order, and learner-visible meaning without duplicate rows | domain/PostgreSQL/live |
| Changed identity reuse | One event or evidence identity with different meaning fails its family closed and cannot overwrite valid current or last-good rows | contract/domain/PostgreSQL/security |
| Family unavailable with prior data | Current families rebuild, prior valid failed-family rows remain visibly stale with their last successful cutoff, and no page claims completeness | application/PostgreSQL/API/browser/live |
| Family unavailable without prior data | Other current progress remains usable and the unavailable family is explicit with no invented empty-success meaning | application/API/browser/anti-rigidity |
| Malformed or cross-learner evidence | Invalid source facts are not published; public errors and family diagnostics reveal no learner, answer, storage, or private owner data | source adapter/application/security |
| Interruption and serialization | A simulated mid-rebuild failure or concurrent rebuild leaves one coherent prior or next projection, never a mixed root/checkpoint/entry set | PostgreSQL/integration |
| Stable pagination | Pages have no duplicates or gaps for one revision; a continuation used after a changed rebuild is refused with a safe restart action | contract/application/API/browser |
| Authorization | Missing session/permission, caller learner selectors, guessed cursors, and cross-context access fail closed and confidentially | API/Identity/security/live |
| Evidence-only meaning | UI and recursively inspected responses never label progress as competency, mastery, credential, eligibility, advice, or financial suitability | contract/component/language/architecture |
| Headless parity | Generated browser and ordinary HTTP clients receive the same projection revision, entries, source states, and continuation behavior | API/client/live |
| Flexible valid shapes | Zero through many entries, equal times, all family combinations, different scores, extra valid events, and Unicode-safe public context remain valid | property/contract/UI anti-rigidity |
| Accessible parity | Heading, timeline, family warnings, continuation, errors, technical record, keyboard/focus, reflow, zoom, forced colors, reduced motion, and light/dark/system themes preserve equivalent meaning and actions | component/Chromium/design |
| Restart, containment, cleanup | The exact projection survives normal host restart, Assessment/Project source rows remain unchanged, and qualification removes only its isolated topology | PostgreSQL/live/operations |

## Agent Work Packets

Packet identifiers are reserved and authored one at a time immediately before
each packet starts. The dependency-ordered seams are:

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0195 | [Freeze Learning Progress Contracts](../work-packets/WRK-0195-freeze-learning-progress-contracts.md) | none | none | active |
| JIT-B | Compose family-isolated Learner-model source adapters, application behavior, PostgreSQL migration/repository, replay/conflict/interruption evidence, and contributor documentation | JIT-A | none | captured |
| JIT-C | Expose the protected progress API, confidential failure mapping, reviewed OpenAPI, and generated TypeScript client for browser and headless callers | JIT-B | none | captured |
| JIT-D | Deliver the plain-language accessible `Your learning progress` browser flow through only the generated client | JIT-C | none | captured |
| JIT-E | Qualify mixed/partial evidence, replay, stale continuation, authorization, restart, source containment, browser/headless parity, accessibility, cleanup, and slice boundaries | JIT-D | none | captured |

Dependent packet IDs are not reserved, authored, or claimed until their
concrete predecessor is complete. Corrections remain inside the active packet
when bounded; a new source authority or competency meaning returns to CAP
shaping or decision review.

## Verification and Qualification

Run JSON Schema and compatibility fixtures; Assessment family replay; Learner-
model domain, adapter, application, and repository suites; real-PostgreSQL
migration, atomicity, replay, concurrency, carry-forward, and restart evidence;
protected API authorization/confidentiality tests; reviewed OpenAPI and
generated-client reproduction; Web model/component tests; focused Chromium in
both themes and required accessibility modes; and one ordinary headless client.

Run architecture/import and storage-ownership checks, security/privacy checks,
learner-language and design-system checks, documentation and planning checks,
whitespace, Python quality, typecheck, zero-warning lint, build, exact-candidate
affected verification, local technical review, deterministic completion
structure, and `python dev-tools/agent/check_ready.py`. The final packet extends
the existing disposable PostgreSQL/Chromium topology rather than creating a
second runner. Tests protect contracts and learner meaning, not exact prose,
fixture counts, incidental order outside the contract, styling, or wall-clock
microbenchmarks.

## Rollback and Migration

Contracts, public operations, routes, and Learner-model tables are additive and
versioned. The migration requires forward, idempotent reapply, and development-
down evidence against real PostgreSQL. Down migration is allowed only when the
new projection tables are empty; retained derived data may be rebuilt from
Assessment after an explicit safe empty-target rollback, but the migration must
not delete source evidence or imply backup/recovery authority.

Code rollback may remove an unreferenced route/UI and empty projection schema.
It cannot change, delete, or reinterpret Assessment facts. Contract removal or
semantic change follows compatibility governance. Isolated qualification data
may be deleted only inside the exact disposable topology.

## Stop Conditions

Stop for a stale CAP approval; unresolved evidence, model, provider, identity,
tenancy, licensing, recovery, experiment, or legal decision; competency,
mastery, credential, eligibility, recommendation, or financial meaning entering
this slice; direct cross-module table access; raw answer, feedback, project-file,
private owner, session, or storage leakage; source mutation; a public breaking
change; destructive migration; external action; active file collision; or
material CAP-0009/SLI-0038 drift.

Do not stop or reopen broad review solely for harmless whitespace, optional
wording, nonfunctional styling, valid fixture count/order, or another
inconsequential issue. Fix bounded functional/evidence defects locally or defer
optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will update the learner-state/evidence contract guide, Assessment and
Learner-model contributor guidance, API/client documentation, Identity
permission catalog, module/data/migration maps, architecture verification,
browser guidance, this slice, its packets, and the planning register. It will
not imply a competency model, complete Curriculum percentage, adaptive choice,
provider, or managed-cloud guarantee.

Completion evidence must name exact candidates and local receipts; affected
boundaries; contract compatibility; mixed and partial-family results; replay,
conflict, stale continuation, interruption, concurrency, restart, containment,
source noninterference, browser/headless parity, accessibility, and cleanup;
exact focused and aggregate commands/results; migration/rollback evidence;
documentation impact; assumptions and residual gaps; and CAP conformance.

## Planning History

- 2026-10-18: Refined immediately after CAP-0026 completion from the approved
  CAP-0009 manifest. Candidate A scores 14 of 14 and selects one evidence-only,
  API-first Learner-model timeline over all three delivered Assessment evidence
  families with explicit partial-source freshness and a generated-client
  browser consumer. DEC-0009 remains satisfied by ADR-0014; no slice approval,
  model/provider authority, or material CAP change is introduced.
- 2026-10-18: Activated with dependency-free WRK-0195 after the implementation
  gate confirmed current CAP authority, exact manifest membership, resolved
  decision readiness, validated bounded scope, and no active ownership overlap.
