---
id: SLI-0106
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: CAP-0026
depends_on: []
decision_gates: []
---

# Vertical Slice: Trace Learning Content and Evidence Lineage

## Outcome and User Scenario

An authorized consumer can request one exact published lesson or retained
knowledge-check completion and receive a versioned, provider-neutral provenance
envelope plus a bounded lineage view. The view identifies the owning modules,
exact content and evidence versions, validation and integrity facts, source and
transformation relationships, and any missing link without copying lesson,
answer, learner, or persistence payloads into Audit. Browser, command-line,
service, and future headless clients use the same protected public operation;
the learner-facing history interface remains a later slice.

## Scope Boundaries

### In Scope

- An additive `provenance-envelope/v1` family for exact typed resource
  references, source and transformation references, validation status,
  integrity facts, lineage nodes/edges, bounded incomplete-link facts, and a
  canonical view digest.
- Two closed initial root kinds: an exact Content-owned published lesson and an
  Assessment-owned knowledge-check completion already represented by an
  append-only Audit integrity reference.
- Content and Assessment/Audit adapters that translate existing public values
  into the common envelope without provider payloads, table access, or a new
  cross-module business aggregate.
- An Audit-owned read application that composes a bounded lineage from owner
  public operations and Audit's own append-only references, preserves stable
  ordering and exact identity, and reports missing or unavailable links
  explicitly rather than inventing continuity.
- Read support over the existing Audit records; no mutation of retained
  completion evidence and no second copy of Content or Assessment state.
- Protected public HTTP operations, reviewed OpenAPI, and generated TypeScript
  client shapes shared by ordinary headless and future browser consumers.
- Focused and live qualification for exact replay, idempotent reconciliation,
  tamper/conflict detection, incomplete links, bounded traversal, confidential
  denial, restart stability, browser-client/headless contract parity, and
  database containment.
- Anti-rigidity evidence for variable educational-source counts, valid Unicode,
  additional non-root nodes and edges within bounds, reordered owner input,
  absent optional facts, and incomplete chains that do not affect unrelated
  records.

### Out of Scope

- Learner-facing lineage or accountable-history pages, visualization, export,
  retention controls, or administrative history; SLI-0108 owns those views.
- Project, practice, financial, market-data, portfolio, dataset, model,
  simulation, recommendation, job, provider, or administrative lineage;
  SLI-0107 owns the cross-domain extension seam.
- Cumulative projection-rebuild, scale, local/cloud, retention-hook, or
  cross-domain conformance closure; SLI-0109 owns final qualification.
- A central mutable provenance aggregate, cross-module database joins, copied
  lesson/evidence payloads, answer or feedback content, raw learner identity,
  provider payloads, storage locators, secrets, or unrestricted audit access.
- Tenancy, organization policy, managed-cloud retention, legal hold,
  compliance guarantees, immutable infrastructure, blockchain, signing,
  external timestamping, or provider selection.
- AI-generated lineage, semantic inference, automatic repair, external
  retrieval, notification, or execution.
- Nonfunctional visual styling; no learner-facing interface is introduced in
  this slice, and optional presentation work remains CAP-0031 scope.

## Canonical Context and Decisions

- [CAP-0026](../capabilities/CAP-0026-preserve-provenance-and-accountable-history.md)
  defines the approved four-slice outcome and selects existing learning content
  and evidence as the first provider-neutral lineage increment.
- [Module Map](../../architecture/modules/module-map.md) and
  [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  keep Content authoritative for published package/source facts, Assessment
  authoritative for completion evidence, and Audit authoritative only for
  append-oriented integrity and accountable-history references.
- [Content-Package Contract](../../architecture/contracts/content-package-contract.md)
  governs exact package identity, educational sources, publication provenance,
  and immutability. The
  [Assessment Contract](../../architecture/contracts/assessment-contract.md)
  governs answer-safe deterministic completion evidence and replay.
- [Data Architecture](../../architecture/data/data-architecture.md) permits
  transactional Audit references in PostgreSQL while prohibiting Audit from
  becoming a copy of owner records.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md),
  [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md),
  and the existing Audit public seam fix the first-loop owners and exact
  source-event integrity boundary.
- [Decision Readiness](../../adr/decision-readiness.md) exposes no unresolved
  decision for this local shared-core, read-only, existing-owner boundary.
  Tenancy, managed-cloud retention/recovery, provider, legal, and external
  execution choices are not exercised.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Compose one bounded Audit lineage read from owner-issued envelopes and existing integrity references, then expose it through the protected public API | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Let each owner expose unrelated provenance responses and require every client to assemble lineage | yes, but it omits one stable chain and duplicates correlation policy in clients | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 9 |
| C. Copy complete Content and Assessment records into a generic Audit lineage database | no; it violates module ownership and turns Audit into a second business database | - | - | - | - | - | - | - |
| D. Build a browser-only provenance graph over existing API responses | no; it makes the client authoritative, omits headless parity, and enters SLI-0108 presentation scope | - | - | - | - | - | - | - |

## Selection Rationale

Candidate A is eligible and scores 14 of 14. It provides the smallest complete
SLI-0106 result: owner modules keep their facts, Audit validates and correlates
only bounded references, and all clients share one safe public meaning.
Candidate B preserves ownership but provides no interoperable chain and would
force later financial, AI, and project consumers to duplicate correlation.
Candidates C and D cross explicit ownership or slice boundaries.

The refinement preserves CAP-0026's outcome, four-slice manifest, sequence,
decision posture, and non-goals. It narrows the first increment to published
lesson and knowledge-check completion lineage; later manifest slices retain
cross-domain extension, human inspection/export, and cumulative qualification.
No slice-level approval exists or is required.

## Boundary Path

1. Closed `provenance-envelope/v1` schemas define exact resource references,
   typed source/transformation references, validation and integrity facts,
   bounded lineage nodes/edges, incomplete-link facts, and canonical digests.
2. Pure values validate stable owner/kind identities, semantic versions,
   lowercase SHA-256 digests, UTC times, closed statuses and relation kinds,
   root correlation, unique node/edge identity, bounds, and deterministic order.
3. A Content gateway maps one exact `PublishedLesson` and its educational
   sources/publication facts to owner-issued nodes without copying lesson body,
   object paths, or private authoring state.
4. The existing Assessment replay gateway and Audit reconciliation preserve one
   exact knowledge-check event reference. Audit repository reads return only
   Audit-owned append-only reference facts; they never query Assessment tables.
5. Audit's application service composes the requested root and bounded owner
   references, marks missing/unavailable links explicitly, rejects changed same-
   identity facts, and computes one canonical view digest.
6. Protected FastAPI reads derive learner and permission context on the server,
   accept only the two closed root selectors, map safe failures, publish reviewed
   OpenAPI, and regenerate the shared TypeScript client.
7. Focused and isolated live qualification compares generated-client and
   ordinary HTTP documents before and after normal restart, verifies exact
   PostgreSQL correlations and read-only owner-state containment, and removes
   only bounded disposable resources.

## Contracts, Data, and Provenance

The additive contract family separates an owner-issued `ProvenanceEnvelope`
from an Audit-composed `LineageView`. An envelope identifies its schema,
owner module, closed resource kind, stable resource ID, applicable semantic
version or occurrence, integrity digest, producer/policy reference, observed or
recorded time, validation status, and typed source/transformation references.
It contains no domain payload and grants no read permission to the referenced
record.

A lineage view has one exact root selector, bounded nodes, bounded directed
edges, explicit incomplete links, a truncation indicator, and a canonical view
digest. Initial node kinds cover educational source, published lesson,
assessment definition, knowledge-check event, completion evidence, and Audit
integrity reference. Initial relation kinds are closed and descriptive, such as
`published_from`, `defined_by`, `produced`, and `recorded_as`; they confer no
causal, grading, mastery, permission, legal, or financial conclusion.

The v1 service applies explicit node, edge, depth, string, and reference bounds.
Stable ordering is derived from root distance, owner, kind, ID, version, and
digest rather than database or adapter order. Duplicate identities with
different meaning, cycles where the relation kind forbids them, malformed
digests, unsupported versions, uncorrelated roots, and private fields fail
closed. An unavailable optional owner link becomes a bounded incomplete-link
fact; it does not cause another root or unrelated chain to disappear.

The knowledge-check path reuses the existing append-only Audit record and exact
Assessment replay/reconciliation behavior. No new business table is introduced.
Repository changes may add read queries or indexes over Audit-owned columns, but
must not add a Content/Assessment foreign key or copy response, score, feedback,
lesson body, educational-source locator, raw learner ID, or provider data.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Exact published lesson | An authorized caller supplies exact package ID, version, and digest | The view returns the Content root, publication/source references, exact owner/version/integrity facts, and one stable view digest without lesson body | contract/domain/API |
| Exact completion evidence | The server-bound learner requests one exact knowledge-check evidence record | Reconciliation is idempotent and the view correlates Audit reference, Assessment event/evidence, definition, package, and source identities without responses or feedback | application/PostgreSQL/API |
| Browser/headless contract parity | The generated TypeScript client and ordinary HTTP client request the same authorized root | Both receive equivalent validated documents and safe failure meaning | generated client/live |
| Exact replay | The same owner facts are read repeatedly and after a normal restart | Node/edge order and canonical view digest remain identical; no duplicate Audit record appears | domain/PostgreSQL/live |
| Changed same identity | One retained event or owner reference reuses an identity with changed digest/version | The request fails as an integrity conflict and preserves the accepted record | domain/PostgreSQL |
| Incomplete optional link | A referenced owner record is absent or temporarily unavailable | The requested chain reports one bounded incomplete link without fabricating facts or disabling unrelated roots | application/API |
| Malformed or oversized graph | Input or adapter output has an unsupported version, bad digest, duplicate conflict, forbidden cycle, private field, or exceeds a bound | Validation fails before a partial response or write is exposed | contract/domain/security |
| Authorization and ownership | Session, learner scope, or exact resource permission is absent | Access fails confidentially without revealing chain counts, IDs, digests, sources, or existence | API/security |
| Owner isolation | A lineage read runs | Content, Assessment, and learner state are unchanged; Audit reads only its own records and owner public operations | architecture/integration/live |
| Variable valid lineage | Source counts, valid Unicode, node/edge order, optional times, and additional bounded references vary | The same invariants hold without fixed fixture counts, whole-document snapshots, or incidental database order | property/contract anti-rigidity |
| Local restart | The private loopback host restarts without reseeding | The exact chain remains available from retained owner and Audit facts with no external request | live/architecture |
| Cleanup | Focused or live qualification succeeds or fails | Only named temporary captures, database/container resources, and test roots are removed | live/control plane |

## Agent Work Packets

Detailed packet files are authored one at a time immediately before work starts.
The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0180](../work-packets/WRK-0180-freeze-learning-provenance-contracts.md) | Freeze the provider-neutral provenance envelope and bounded learning-lineage contracts, compatibility corpus, ownership rules, and conformance tests | none | none | complete |
| [WRK-0181](../work-packets/WRK-0181-compose-learning-lineage-core.md) | Compose the Audit learning-lineage core, Content/Assessment public adapters, Audit-owned read persistence, idempotent reconciliation, and focused architecture/security evidence | WRK-0180 | none | complete |
| WRK-0182 | Expose protected learning-lineage operations through FastAPI, reviewed OpenAPI, and the generated TypeScript client for browser and headless consumers | WRK-0181 | none | captured |
| WRK-0183 | Qualify exact live learning lineage, restart, containment, anti-rigidity, documentation, and slice completion | WRK-0182 | none | captured |

Sequential delivery is required because each packet stabilizes the contract and
public seam consumed by its successor. A bounded correction may add a dependent
packet without changing the approved CAP or slice outcome.

## Verification and Qualification

Run schema and compatibility conformance; pure canonicalization, graph,
ordering, bound, missing-link, conflict, and property tests; Content/Assessment
adapter and Audit application tests; PostgreSQL reconciliation/read,
immutability, interruption, and migration/reapply checks when affected;
module-boundary and security checks; protected API denial/response tests;
reviewed OpenAPI and generated-client reproduction; ordinary headless and
generated-client parity; normal restart and read-only containment; and the
tracked affected-check plus independent technical-review workflow.

Finish the slice with documentation, planning, whitespace, and aggregate agent
readiness. Tests must vary valid graph shape and ordering and must not make
unrelated full-suite or browser presentation checks routine when the affected
boundary does not require them.

## Rollback and Migration

The contract and public operations are additive. Existing Content, Assessment,
Learner-model, Project, Guidance, and Audit records remain compatible. The
preferred implementation reads existing Audit-owned columns and owner public
operations; any necessary additive index or read projection must have an
empty/test rollback and cannot rewrite accepted evidence. Published envelope
meaning changes through an additive version rather than in-place reinterpretation.

## Stop Conditions

Stop for conflicting canonical ownership; stale CAP authority; an unresolved
tenancy, managed-cloud retention/recovery, legal/commercial, provider, model,
encryption, queue, signing, or external-execution decision; a requirement to
copy owner payloads or read another module's tables; a public contract break;
unbounded traversal/export; answer, learner, secret, path, or provider leakage;
or a scope change into project/financial/AI/admin lineage or learner-facing
history. Return to CAP shaping only for material outcome, manifest, ordering,
risk, or decision-posture drift.

Do not stop or reopen review solely for harmless whitespace, optional copy,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or route optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Update provenance and Audit vocabulary, contract architecture, module ownership,
Audit contributor instructions, API/client documentation, architecture
verification, residual gaps, direct runtime instructions, packet artifacts,
this slice, and the planning register. Completion evidence must record exact
candidates and qualifying receipts, contract/core/PostgreSQL/API/headless/live
results, source and view digests, confidentiality and containment, restart and
cleanup, migration/rollback status, residual gaps, and CAP conformance.

## Planning History

- 2026-10-18: Refined immediately after CAP-0020 completion. Candidate A scores
  14 of 14 and selects one Audit-composed, owner-issued, protected learning-
  lineage seam over existing published lessons and knowledge-check evidence.
  The refinement preserves CAP-0026's approved outcome, four-slice manifest,
  order, decision posture, risks, and non-goals; no lower-level approval exists.
- 2026-10-18: Authored dependency-first WRK-0180 with an exact pure-contract,
  compatibility-corpus, architecture, documentation, and test scope. Later
  packets remain captured until their accepted inputs exist.
- 2026-10-18: Activated WRK-0180 from clean base `ef7ae20` after confirming
  current CAP authority, resolved decisions, dependency readiness, bounded
  pure-contract scope, and no ownership collision.
- 2026-10-18: Completed WRK-0180 at exact candidate `e6129fe` with qualifying
  affected evidence and 26 focused provenance tests; WRK-0181 may now consume
  the frozen provider-neutral contract without reopening lower-level approval.
- 2026-10-18: Authored WRK-0181 just in time with exact shared-core,
  owner-adapter, Audit-read, PostgreSQL, documentation, and test boundaries.
- 2026-10-18: Activated WRK-0181 after dependency, decision, scope, and current
  CAP-package checks; implementation proceeds without lower-level approval.
- 2026-10-18: Submitted WRK-0181 candidate `a369b79` for exact affected
  verification after focused shared-core and PostgreSQL evidence passed.
- 2026-10-18: Completed WRK-0181 at corrected candidate `6010d88` with a
  qualifying receipt, 30 focused tests, passing architecture/security/readiness
  gates, private-locator integrity, bounded request failures, and no open
  technical finding. Protected transport is now eligible for WRK-0182.
