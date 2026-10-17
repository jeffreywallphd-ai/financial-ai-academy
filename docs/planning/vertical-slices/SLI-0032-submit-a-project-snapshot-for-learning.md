---
id: SLI-0032
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: CAP-0007
depends_on: [SLI-0031]
decision_gates: []
---

# Vertical Slice: Submit a Project Snapshot for Learning

## Outcome and User Scenario

A learner with a learning-started Project selects one immutable snapshot,
maps each exact learning-project milestone to evidence already closed inside
that snapshot, and submits it through the protected public API. Deterministic
validation identifies missing, duplicate, unknown, stale, or non-snapshot
evidence without grading quality or inventing mastery. An accepted submission
becomes immutable Assessment evidence, can be reopened with its exact Project,
Content, Curriculum, requirement, and validation provenance, and produces a
bounded completion projection and Audit reference. The live Project remains
independent and later snapshots or submissions never rewrite earlier evidence.

The generated browser is one client of the same API used by supported
non-browser and future headless clients. Identity, authorization, validation,
completion, supersession, and durable state changes remain server-owned and
deterministic.

## Scope Boundaries

### In Scope

- Define an additive Assessment project-submission contract that references one
  exact Project snapshot and its digest, the learning-started Project origin,
  approved Content brief, Curriculum placement, ordered milestone set, and one
  bounded evidence mapping per milestone.
- Require every milestone from the exact approved brief exactly once. Each
  submitted evidence reference must identify a note, safe source, inert
  artifact version, or admitted domain-resource link that is already included
  in the immutable snapshot. Unknown, duplicate, omitted, live-only, stale, or
  cross-project references fail closed.
- Keep validation structural and deterministic: complete milestone-to-snapshot
  closure can produce bounded project-completion evidence, but it does not
  judge quality, truth, code safety, independent reproducibility, mastery,
  competency, suitability, or financial performance.
- Resolve learner identity and permission from the server session; resolve the
  exact snapshot through Project's public operation and the exact learning
  origin, placement, and brief through public Project, Curriculum, and Content
  operations. No module reads another module's tables.
- Persist immutable Assessment-owned submission, validation, completion-
  evidence, and outbox records atomically with server IDs, canonical UTC time,
  request fingerprint, accepted sequence, and full exact-version provenance.
- Make exact replay idempotent and changed reuse conflicting. A later accepted
  snapshot receives a new immutable submission with a forward
  `supersedes_submission_id` reference; it does not update or delete prior
  evidence. Stable history preserves every accepted occurrence.
- Add a typed Assessment completion event and read-only replay/history surface.
  Learner model derives project-activity completion from that public evidence;
  Audit appends integrity/provenance references. Neither consumer becomes the
  source of the submission or snapshot.
- Expose protected submit, validation-result, exact evidence, and ordered
  history operations through reviewed OpenAPI and the generated TypeScript
  client for browser and headless consumers.
- Deliver an accessible learner flow to choose an eligible snapshot, associate
  its closed records with milestones, correct bounded validation problems,
  submit, and reopen retained evidence and derived completion in plain English.
- Prove interruption, concurrency, replay, later-live-work, later-snapshot,
  later-submission, restart, source-version drift, authorization, privacy,
  accessibility, and no-execution behavior end to end.

### Out of Scope

- Submitting an independent Project, treating all Project activity as learning,
  or changing a Project's immutable origin after creation.
- Instructor, peer, or AI grading; qualitative review; revision requests;
  manual override; rubrics with judgment; partial credit; certification; or
  competency/mastery estimation. Those require later capabilities and, where
  applicable, their own authority decisions.
- Mutating, copying, deleting, or locking the live Project workspace; rewriting
  a Project snapshot; or storing Project-owned artifact bytes in Assessment.
- Executing, rendering actively, expanding, installing, scanning through an
  external provider, reproducing, or calling back from any submitted artifact.
- Live Portfolio validation or calculations, provider-backed data, licensed
  market-data use, financial advice, suitability, brokerage, or real actions.
- Organization tenancy, collaboration, public sharing, managed-cloud
  composition, production recovery, external queues, notifications, or a
  separate AI/headless mode.
- Instructor-facing review and feedback. This slice only retains learner-
  visible deterministic validation and immutable source evidence for a later
  reviewer capability.

## Canonical Context and Decisions

- [CAP-0007](../capabilities/CAP-0007-complete-applied-projects.md) fixes this
  as the third manifest slice after the reusable Project and snapshot seams.
- [ADR-0012](../../adr/ADR-0012-reusable-project-workspace.md) assigns mutable
  work and immutable snapshots to Project, immutable learning submissions and
  deterministic validation to Assessment, projections to Learner model, and
  integrity references to Audit.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md)
  preserves the Content, Curriculum, Assessment, Learner-model, and Audit
  dependency direction and public-operation/event collaboration rule.
- [ADR-0011](../../adr/ADR-0011-inert-applied-project-artifacts.md) keeps every
  submitted dataset, notebook, code file, environment, and result inert and
  prohibits execution or claims of independent reproduction.
- [Project Workspace Contract](../../architecture/contracts/project-workspace-contract.md)
  governs the exact immutable snapshot and evidence-export meaning already
  delivered by SLI-0031.
- [Deterministic Assessment Contract](../../architecture/contracts/assessment-contract.md)
  supplies the established append-only evidence, idempotency, safe event,
  replay, generated-client, and public-consumer patterns without extending its
  current knowledge-check or practice shapes.
- The decision-readiness register marks applied-project ownership ready and
  execution constrained. Organization tenancy, managed cloud, providers, and
  commercial or external-action boundaries remain unavailable here.

## Candidate Evaluation

Only candidates that deliver the complete manifest increment are eligible for
selection. Scores use the repository's zero-through-two criteria.

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A — Exact snapshot submission through retained evidence, projection, Audit, shared API, and browser | yes | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 13 |
| B — Stop after Assessment persistence and a headless submit API | no: omits retained learner history, projection, Audit, and browser value fixed by the CAP slice | — | — | — | — | — | — | — | — |
| C — Build the browser form before freezing server validation and evidence contracts | no: creates client-owned requirement meaning and no independently valid durable evidence | — | — | — | — | — | — | — | — |

## Selection Rationale

Candidate A is the only eligible refinement because it crosses the minimum
complete boundary promised by CAP-0007.SLI-0032: one exact snapshot becomes
immutable Assessment evidence, its deterministic problems are actionable, and
the learner can reopen the resulting completion history. Its one-point
dependency-independence score reflects deliberate use of four existing module
public seams, not ambiguous ownership. The work remains reversible and bounded
because all contracts and persistence are additive, history is append-only,
and the browser consumes the shared API.

Candidate B is a valid internal delivery checkpoint but not a completed
vertical slice; it is retained as a work-packet seam inside Candidate A.
Candidate C is rejected because UI-first validation could diverge from the
authoritative contract and would block supported headless consumers.

## Boundary Path

1. Project returns one learner-authorized immutable snapshot through its public
   application surface. It exposes no repository, object key, host path, or
   mutable workspace authority.
2. Curriculum resolves the exact project-brief placement and Content resolves
   the exact approved brief. Assessment compares those public facts with the
   Project's immutable learning origin and snapshot.
3. Assessment parses the closed intent, validates complete ordered milestone
   coverage and snapshot membership, and produces either bounded issue records
   or one immutable accepted submission/evidence/event aggregate.
4. Assessment-owned PostgreSQL commits accepted submission, milestone-evidence
   bindings, completion evidence, and outbox event atomically. Project,
   Content, and Curriculum persistence remain untouched.
5. Learner model consumes the typed Assessment event/replay surface and derives
   bounded project-activity completion without mastery. Audit consumes the same
   public evidence reference and appends integrity facts.
6. The protected FastAPI host supplies learner context, same-origin and
   authorization policy, then exposes the same reviewed OpenAPI operations to
   the generated browser client and supported headless clients.
7. The browser presents snapshot and milestone facts, bounded validation
   issues, immutable evidence history, supersession links, and derived
   completion without revalidating, grading, or mutating source evidence.

## Contracts, Data, and Provenance

Create a separate additive Project-submission contract family under Assessment
rather than expanding knowledge-check or practice v1. The family should close:

- a learner-safe snapshot candidate containing exact Project/snapshot,
  learning-origin, brief, placement, milestone, revision, and digest facts;
- a submission intent with an opaque idempotency/submission identity and one
  ordered milestone-to-snapshot-resource mapping, but no learner identity,
  server time, score, completion, or authorization fact;
- bounded validation issues with stable codes and safe milestone/resource
  references, never artifact bytes, answers, private paths, database facts, or
  stack traces;
- an immutable accepted submission and completion-evidence record containing
  server IDs/time, exact request fingerprint, occurrence order, optional prior
  submission reference, source versions/digests, snapshot digest, validation-
  policy version, and the accepted mapping;
- a safe completion event and ordered history record with enough provenance to
  replay Learner-model and Audit consumers without embedding artifact bytes or
  copying Project state.

Canonical request identity must be independent of harmless JSON object order
and must preserve the contract-defined milestone and evidence sequence.
Snapshot resource references bind exact IDs and versions already present in the
closed snapshot. The validation policy is versioned and deterministic. It
checks identity, source agreement, membership, uniqueness, closure, and complete
milestone coverage only. A valid record does not assert that an artifact is
safe, a result is true, code ran correctly, requirements were met
qualitatively, or the learner has mastery.

Assessment persistence is append-oriented and rejects ordinary update/delete.
The exact replay key is learner plus submission ID plus canonical request
fingerprint. A changed fingerprint conflicts. Each distinct accepted snapshot
gets the next locked occurrence order and may point forward from the previous
accepted submission without mutating it. Learner-model current completion is a
rebuildable view over immutable history; Audit stores only public evidence and
integrity references. Project snapshots needed by retained Assessment evidence
cannot be destructively removed by a normal Project archive or cleanup path.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Eligible candidate | A learning-started Project exposes an authorized closed snapshot whose origin still matches the exact placement and brief | Project/Content/Curriculum public-operation tests |
| Complete valid submission | Every exact milestone maps to one or more resources in that snapshot and Assessment commits one immutable evidence/event aggregate | contract/domain/application/PostgreSQL |
| Missing or invalid requirement | Missing, duplicate, unknown, stale, live-only, cross-project, or non-snapshot evidence returns ordered safe issues and creates no completion evidence | contract/domain/API/PostgreSQL |
| Independent Project denial | An independent Project snapshot cannot be submitted and gains no Assessment or Learner-model meaning | application/API/security/live |
| Exact replay and conflict | The same submission ID and canonical request returns the original evidence; changed reuse conflicts without another row or event | domain/PostgreSQL/API |
| Concurrent distinct submission | Concurrent valid submissions serialize occurrence order and preserve one immutable aggregate per distinct accepted request | PostgreSQL concurrency |
| Later live work | Mutating the Project after snapshot closure does not alter validation, evidence, event, history, or completion derived from the submitted snapshot | Project/Assessment integration/live |
| Superseding snapshot | A later valid snapshot creates a new occurrence that references the prior submission; both remain reopenable and byte-for-byte stable | PostgreSQL/API/browser/replay |
| Source drift | Missing, unavailable, or version/digest-mismatched brief, placement, Project origin, or snapshot fails closed without falling forward to a newer source | application/API/integration |
| Projection and Audit | Learner model derives bounded project-activity completion and Audit appends source/integrity references only from the typed Assessment evidence | public-event/unit/PostgreSQL |
| History reopen | Browser and headless clients reopen stable ordered evidence, exact provenance, milestone bindings, completion meaning, and supersession without private fields | API/generated client/component/Chromium/live |
| Authorization and privacy | Missing session, caller-selected learner, cross-learner Project/snapshot/submission guesses, malformed selectors, and forbidden origin fail confidentially | API/security/browser |
| Interruption and restart | Failure before atomic commit leaves no accepted partial aggregate; accepted evidence, projection, and Audit references survive a normal restart and deterministic replay | PostgreSQL/live |
| Flexible valid shape | One through twenty milestones, varied resource kinds/counts/order, Unicode learner text, optional provenance, multiple snapshots, and generated IDs/times do not depend on one fixture | compatibility/unit/component anti-rigidity |
| Accessible parity | Snapshot choice, milestone mapping, validation issues, retained history, focus, keyboard order, zoom/reflow, forced colors, reduced motion, and both themes preserve equivalent meaning | component/Chromium/design |
| No execution or advice | Submission never executes or actively renders artifacts, calls a provider, injects secrets/network, reproduces a result, or presents financial advice/performance assurance | architecture/security/language/live |

## Agent Work Packets

Packet IDs are reserved and packets are authored one at a time immediately
before work starts. These seams define the complete slice plan; exact file
scope is refined just in time.

| Packet seam | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| WRK-0124 | Freeze additive Assessment project-submission, validation-issue, evidence, event, and history contracts plus pure deterministic policy | SLI-0031 | none | complete |
| WRK-0125 | Deliver safe Project snapshot facts, Assessment-owned application/persistence, public adapters, atomic evidence/event storage, replay, and supersession | WRK-0124 | none | complete |
| WRK-0126 | Expose protected candidate, validation/submission, exact-evidence, and history operations through reviewed OpenAPI and the generated TypeScript client | WRK-0125 | none | complete |
| WRK-0127 | Deliver Learner-model project-completion projection and Audit evidence-reference consumption through Assessment's typed public replay surface | WRK-0126 | none | verifying |
| JIT-D | Deliver the accessible generated-client snapshot submission, correction, retained-evidence, and completion-history browser flow | JIT-C | none | captured |
| JIT-E | Qualify contract, persistence, public API/headless, browser, projection, Audit, restart, denial, accessibility, and no-execution behavior and close the slice | JIT-D | none | captured |

## Verification and Qualification

Run closed-schema and semantic compatibility over valid, reordered, boundary,
stale, expanded, and malicious documents; pure milestone-coverage and snapshot-
membership policy tests; Assessment application and atomic PostgreSQL tests for
replay, conflict, concurrency, ordering, supersession, rollback, mutation
denial, source drift, and restart; Project/Content/Curriculum public-adapter and
cross-schema isolation checks; typed event/replay, Learner-model rebuild, and
Audit append/idempotency tests; protected API success/denial/privacy tests;
reviewed OpenAPI and generated-client reproduction; browser model/component and
focused Chromium tests; and the isolated PostgreSQL/Python/static generated-
client/headless/Chromium workflow.

Also run architecture, security, dependency, learner-language, accessibility,
design-system, documentation, planning, whitespace, exact-candidate control,
aggregate readiness, and independent technical-review gates. Anti-rigidity
coverage must vary valid milestone and evidence counts, resource kinds and
ordering, Unicode, optional provenance, IDs, timestamps, later snapshots, and
history length. Optional wording or nonfunctional early-stage styling cannot
block functional completion.

## Rollback and Migration

Contracts, Assessment tables, Learner-model projections, and Audit references
are additive and versioned. Empty-development rollback is permitted only when
no retained submission/evidence/event rows exist. A production rollback may
remove feature exposure while preserving immutable accepted Assessment records,
Project snapshots they reference, typed events, and compatible read/replay
operations. It cannot delete, renumber, rewrite, or detach prior evidence.

Learner-model projection rows remain rebuildable from Assessment evidence;
Audit integrity references remain append-oriented. A failed migration or
interrupted submission must roll back the entire Assessment aggregate and leave
Project state unchanged. Contract retirement requires a later compatible
migration and explicit retained-evidence analysis.

## Stop Conditions

Stop for ambiguous owner authority; cross-module table/object access; mutation
or copying of Project-owned workspace state; destructive retained-evidence
migration; client-selected learner, authorization, validation, completion,
supersession, or time; qualitative/instructor/AI grading; mastery or competency
claims; executable or active-render artifact behavior; external provider or
financial action; live Portfolio dependency; organization tenancy; managed-
cloud protection/recovery; external queue/notification; unresolved retention
or legal/commercial choice; private-data leak; stale CAP package; active file
collision; or material expansion beyond CAP-0007.

Do not stop or reopen review solely for harmless whitespace, optional copy, or
nonfunctional styling. Correct it locally when in scope or defer optional
cleanup to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery must reconcile the Project, Assessment, Learner-model, Audit, Content,
and Curriculum module READMEs; new executable contracts and compatibility
corpus; Project workspace and Assessment contract architecture; API/generated-
client documentation; migrations and local operations; module map; community
evidence protection; learner language; architecture verification; known gaps;
this slice; its packets; and the planning register.

Completion evidence must name exact candidates and receipts, focused and
cumulative checks, supported environments, contract and migration
compatibility, deterministic validation policy, atomic persistence, Project
snapshot immutability, idempotency/concurrency/supersession behavior,
Learner-model and Audit replay, API/browser/headless parity, authorization and
privacy denials, restart and cleanup, accessibility, assumptions, residual
risks, and unqualified profiles. It must explicitly state that no artifact was
executed or actively rendered, no result was independently reproduced, no
quality/mastery/competency or advice claim was made, no live Portfolio/provider
integration was added, and no managed-cloud or production-recovery profile was
qualified.

## Planning History

- 2026-10-17: Refined the third CAP-0007 manifest increment after SLI-0031
  completed. Candidate A scores 13/14 and is the only eligible cut because it
  preserves the complete exact-snapshot-to-Assessment-evidence-to-projection
  path for both generated-browser and headless clients. The five packet seams
  remain additive, deterministic, API-first, and inside ADR-0012 and ADR-0011;
  no new decision gate or CAP material change was exposed.
- 2026-10-17: Refined JIT-A as WRK-0124. The packet freezes the complete
  transport-neutral Assessment Project submission/evidence family and pure
  milestone-to-snapshot validation policy while persistence, API, projections,
  Audit consumption, browser behavior, and live qualification remain deferred.
- 2026-10-17: Activated the slice and WRK-0124 after the CAP authority,
  implementation gate, dependency state, bounded scope, and durable packet
  claim were revalidated against the current repository revision.
- 2026-10-17: WRK-0124 completed at exact corrected candidate `97d316a` after
  qualifying verification and bounded contract hardening. The additive
  transport-neutral contract and pure deterministic policy now bound every
  later stateful and client packet without adding runtime authority.
- 2026-10-17: Refined the former combined JIT-B seam as WRK-0125 for the
  independently reviewable transport-neutral Assessment application,
  cross-module public gateways, PostgreSQL evidence/outbox aggregate, replay,
  ordering, and supersession boundary. Protected API/OpenAPI/generated-client
  delivery remains the dependent JIT-B2 increment; the approved CAP/SLI
  outcome and decision boundaries are unchanged.
- 2026-10-17: Activated WRK-0125 after the implementation gate confirmed the
  current CAP package, completed dependency, decision readiness, bounded scope,
  and absence of active ownership collisions. No lower-level approval was
  added.
- 2026-10-17: Returned WRK-0125 to `ready` before implementation and refined
  its boundary to include a Project-owned safe snapshot-facts operation. The
  current snapshot projection lacks a domain link's exact target version/as-of,
  while the retained snapshot workspace contains it; Project will expose only
  those immutable safe facts so Assessment neither guesses nor reads Project
  persistence.
- 2026-10-17: Reactivated the refined WRK-0125 boundary from base `bb6f531`
  after packet validation, implementation authority, dependency readiness, and
  exact edit ownership passed again.
- 2026-10-17: Refined WRK-0125's test-only write scope to include the existing
  Assessment migration inventory assertions affected mechanically by the new
  additive `assessment_0004` migration. No behavior or approval boundary
  changed.
- 2026-10-17: Reactivated the fully bounded implementation and migration-
  regression scope from base `f66a0df` after all deterministic gates passed.
- 2026-10-17: WRK-0125 completed at corrected candidate `31bf760` after a
  qualifying affected-check receipt and bounded history-integrity hardening.
  Assessment now assembles candidates only through public operations, persists
  immutable evidence and its safe event atomically, preserves exact replay and
  supersession, serializes non-regressing occurrence time, and refuses storage
  beyond the canonical 100-item complete-history bound. The protected HTTP/
  OpenAPI/generated-client seam remains JIT-B2.
- 2026-10-17: Refined JIT-B2 as WRK-0126. The bounded packet composes the
  completed submission core, exposes four protected Project-scoped HTTP
  operations, and regenerates the reviewed OpenAPI/client seam for browser and
  headless consumers. Projection, Audit, browser behavior, and live
  qualification remain dependent packets; no new decision or CAP drift arose.
- 2026-10-17: Activated WRK-0126 after the implementation gate confirmed the
  current CAP authority, completed dependency, exact bounded scope, and lack of
  unresolved decisions or active ownership collisions.
- 2026-10-17: Entered WRK-0126 exact-candidate verification and hardened
  domain-resource timestamp rejection, generated exact-selector types, and the
  focused API authorization and resource-shape matrix without changing the
  packet, slice, or CAP boundary.
- 2026-10-17: WRK-0126 completed at exact candidate `b512386` with qualifying
  affected-check receipt `sha256:7cb5488057b82cdca5221cdb8ccf7ae9ad1d6bd19bc625674f7c74890206976a`.
  The protected shared API now covers candidate, submit, exact evidence, and
  history; generated clients preserve exact domain-resource selectors; and
  focused verification proves refusal without persistence, read-only and valid
  cross-learner denial, independent-Project denial, replay, privacy, and note,
  source, and artifact shapes. Projection, Audit, browser, and slice-wide live
  qualification remain in the dependent JIT-C through JIT-E packets.
- 2026-10-17: WRK-0127 completed at exact candidate `2248e16`. Assessment
  Project completion replay is correlated and flattened to safe provenance;
  Learner model deterministically rebuilds bounded Project activity completion;
  and Audit appends deterministic integrity references. Learner-scoped
  submission identity and canonical Project identifier boundaries are proven
  across unit and PostgreSQL checks. Browser delivery and slice-wide live
  qualification remain in the dependent JIT-D and JIT-E packets.
