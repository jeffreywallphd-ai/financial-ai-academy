---
id: SLI-0109
kind: vertical-slice
planning_status: ready
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: CAP-0026
depends_on: [SLI-0106, SLI-0107, SLI-0108]
decision_gates: []
---

# Vertical Slice: Qualify Complete Provenance and History

## Outcome and User Scenario

An authorized learner or ordinary headless client can inspect the complete
delivered provenance and accountable-history system and trust that exact replay,
projection rebuild, conflicts, missing links, redaction, bounded export, owner
isolation, and maximum supported shapes preserve the same meaning. Local and
future cloud profiles can reuse the shared contracts and core without turning
Audit into a copy of owner data or choosing a tenant, legal, or infrastructure
retention policy.

## Scope Boundaries

### In Scope

- Cumulative qualification of learning-lineage v1, cross-domain owner-reference
  v2, the real Project snapshot adapter, accountable-history inspection, and
  ephemeral portable-evidence export delivered by SLI-0106 through SLI-0108.
- Exact replay, idempotency, changed-input conflict, source-set identity,
  projection rebuild, tamper/integrity diagnostics, missing-link isolation, and
  deterministic canonical digests at the documented contract bounds.
- Browser and ordinary headless use of the protected generated public APIs,
  with the server remaining authoritative for identity, purpose, authorization,
  redaction, and disclosed meaning.
- Cross-owner conformance and failure containment, including the real Project
  adapter and explicitly synthetic future-owner forecasts without claiming that
  the forecast owners are implemented.
- A policy-neutral retention seam: authoritative owner records retain their own
  lifecycle, Audit retains only bounded integrity/accountability references,
  and accountable-history export remains an unretained response. Later storage
  adapters may apply a selected retention class without changing provenance
  identity or copying protected owner payloads.
- Deployment-neutral contracts and shared-core behavior suitable for local and
  future cloud adapters; operational managed-cloud qualification is excluded.
- Cumulative accessibility, plain-language, privacy, security, restart,
  containment, cleanup, and anti-rigidity evidence.

### Out of Scope

- Selecting retention periods, deletion schedules, legal holds, tenant policy,
  immutable storage, signing, encryption keys, recovery objectives, or a cloud
  provider.
- Managed-cloud operation, public hosting, organization or administrator access,
  multi-tenant isolation, or a claim that local qualification proves cloud
  infrastructure behavior.
- A centralized provenance database, owner-payload copies, dynamic plugin
  registry, unlimited graphs or exports, blockchain, compliance guarantees, or
  public disclosure.
- Implementing the eight future v2 owner forecasts, provider/model execution,
  financial calculations, recommendations, external actions, or new domain
  records merely to increase conformance coverage.
- New browser-only policy, visual polish, or another human approval stage for
  conforming slice, packet, verification, review, or completion work.

## Canonical Context and Decisions

- [CAP-0026](../capabilities/CAP-0026-preserve-provenance-and-accountable-history.md)
  defines the approved four-slice outcome and makes this the cumulative final
  increment.
- [SLI-0106](SLI-0106-trace-learning-content-and-evidence-lineage.md),
  [SLI-0107](SLI-0107-extend-provenance-across-domain-owners.md), and
  [SLI-0108](SLI-0108-inspect-accountable-history.md) define the delivered
  contracts, public operations, clients, adapters, and focused evidence.
- The [Provenance and Lineage Contract](../../architecture/contracts/provenance-and-lineage-contract.md)
  governs exact references, graphs, canonicalization, conformance, history,
  redaction, diagnostics, and ephemeral export.
- The [Data Architecture](../../architecture/data/data-architecture.md) and
  [Contract Architecture](../../architecture/contracts/contract-architecture.md)
  keep business records with their owners and deployment details behind ports.
- [Local and Cloud Deployment Parity](../../architecture/deployment/local-cloud-capability-parity.md)
  requires one shared core while leaving operational profile differences to
  adapters.
- [Decision Readiness](../../adr/decision-readiness.md) permits shared-core and
  local qualification. Managed-cloud retention, tenancy, encryption, recovery,
  and provider choices remain decision-gated and outside this slice.
- [Interface Design Standards](../../standards/interface-design-standards.md)
  and [User-Facing Language Standards](../../standards/user-facing-language-standards.md)
  govern cumulative browser evidence without turning style heuristics into
  brittle functional gates.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cumulative qualification plus the minimum missing policy-neutral retention and deployment seams | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| Introduce a managed retention scheduler and legal classification policy | no; periods, deletion, legal hold, tenancy, recovery, and infrastructure choices are outside CAP-0026 | - | - | - | - | - | - | - | - |
| Qualify a managed-cloud deployment as equivalent to local operation | no; cloud, tenant, security, provider, and recovery decisions remain unresolved or owned elsewhere | - | - | - | - | - | - | - | - |
| Close from prior isolated slice evidence only | no; it omits cumulative bounds, cross-owner isolation, projection-rebuild, and deployment-seam evidence | - | - | - | - | - | - | - | - |

## Selection Rationale

The cumulative qualification candidate is the only decision-ready final
increment and scores 14 of 14. It proves the existing public APIs, generated
client, pure cores, conformance adapters, and local host together while adding
only the minimum missing test or harness support needed to demonstrate the
approved retention and deployment seams. A policy-neutral seam does not select
how long anything is kept: it proves that owner records, bounded Audit
references, and unretained exports remain distinct so a later authorized policy
can be applied without changing provenance meaning.

A managed retention service or cloud qualification would cross named durable
decision gates. Prior isolated evidence is necessary but cannot by itself prove
the CAP's cumulative acceptance. The three dependencies are complete, the CAP
approval remains current, and this refinement preserves its outcome, manifest,
order, risks, and non-goals. No slice-level approval exists or is required.

## Boundary Path

1. An authorized learner session or ordinary headless caller selects one exact
   lesson or completion root through the protected public contract.
2. The host resolves owner operations through public ports, and Audit composes
   the same bounded canonical lineage without reading owner persistence.
3. Replaying the same owner facts produces the same references, source set,
   graph, disclosed history, and digests; a changed same-identity fact fails as
   an explicit conflict without partial publication.
4. Rebuilding the disposable projection from exact owner facts reproduces the
   accepted source-set identity and view while missing or invalid references
   remain bounded diagnostics isolated to their chain.
5. The v2 conformance service evaluates the real Project adapter and synthetic
   future-owner forecasts independently, preserving exact coverage and local
   failure containment under reorder and maximum supported shapes.
6. Browser and headless consumers receive the same authorized history meaning;
   the browser adds no policy and exposes technical detail progressively.
7. Export is generated from the authorized disclosed view and returned without
   a retained download record; owner lifecycle and future adapter retention
   remain outside provenance identity.
8. Restart, adapter substitution, maximum-bound cases, and exact cleanup prove
   shared-core semantics without claiming managed-cloud infrastructure parity.

## Contracts, Data, and Provenance

No new business aggregate or cross-module store is introduced. Existing
provenance v1/v2 and accountable-history v1 schemas remain authoritative. Their
closed owners, kinds, labels, relations, exact identities, bounds,
canonicalization, digests, diagnostics, redaction categories, and export meaning
cannot be weakened for qualification.

The retention hook is a separation contract, not a duration policy. Owner
modules retain authoritative records under their own lifecycle. Audit may retain
only the bounded integrity/accountability references already accepted by the
contract. Accountable-history export remains an ephemeral response with no path,
locator, retained-download identity, runtime-clock claim, or business payload.
Any later persistence adapter or job can attach an authorized retention class
outside the provenance identity while preserving exact source references and
digests; selecting such classes and behavior is later work.

Qualification evidence identifies exact revisions, contract fingerprints,
selected checks, runtime topology, and bounded pass/fail results without copying
private learner content into tracked artifacts.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Exact replay | Equivalent owner facts are reconciled and requested repeatedly | Canonical references, source sets, graphs, histories, and digests remain exact with no duplicate retained Audit reference | core/application/live runner |
| Same-identity conflict | A source reuses an exact identity with changed integrity or meaning | The operation fails with a closed conflict and publishes no partial view or unrelated-chain change | contract/application |
| Projection rebuild | The disposable Audit projection is removed and rebuilt from exact owner facts | The rebuilt source set and public view match the accepted canonical identity | PostgreSQL/integration |
| Broken or invalid link | One chain contains a missing, unavailable, unsupported, mismatched, or invalid reference | The exact bounded gap or safe diagnostic is visible without raw rejected data; unrelated chains remain usable | contract/security/isolation |
| Maximum supported shape | Graphs, sources, transformations, facts, diagnostics, and redaction counts reach documented limits | Valid maximum shapes remain deterministic and over-limit shapes fail closed without timing- or fixture-count assumptions | property/performance bound |
| Cross-owner conformance | The real Project adapter and synthetic future-owner forecasts run together under varied order | Each profile is evaluated once, exact missing coverage is reported, and one failure cannot disable another profile | conformance/architecture |
| Retention separation | Inspection and export run repeatedly before and after restart | Owner records and bounded Audit references keep their documented lifecycle, export creates no retained record, and no unselected duration or deletion policy is implied | architecture/integration/containment |
| Authorization and redaction | An unauthorized or differently purposed caller requests lineage, history, or export | The response remains confidential and disclosed fields/counts stay within the selected purpose | authorization/security |
| Headless/browser parity | Browser and ordinary HTTP/generated clients inspect the same root | The same server-owned meaning and export availability appear; the browser contributes no authority or hidden data | API/generated client/Chromium |
| Accessible responsive use | The history is used by keyboard and screen reader at narrow and wide layouts in both themes | Content, actions, focus, disclosure, contrast, and status meaning remain equivalent | component/Chromium/design |
| Deployment-neutral core | Equivalent in-memory/local adapters invoke the same core contracts | Canonical results and failure meaning remain adapter-independent; no managed-cloud behavior is claimed | architecture/conformance |
| Restart and exact cleanup | The isolated local host restarts and the qualification ends | Results rebuild exactly and only the isolated database, browser, server, and generated runtime artifacts are removed | live runner/operations |

## Agent Work Packets

The single final packet is authored immediately before work starts and reuses
existing complete evidence rather than duplicating it:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0194](../work-packets/WRK-0194-qualify-complete-provenance-and-history.md) | Add only the minimum missing retention-seam, bounds, rebuild, adapter-neutral, or cumulative assertions; run complete browser/headless/live qualification; reconcile evidence; and close CAP-0026 | WRK-0183, WRK-0188, WRK-0193 | none | ready |

Detailed file scope, generated artifacts, selected checks, and stop conditions
are frozen at packet start. The packet must not create redundant runners or new
product behavior merely to produce evidence.

## Verification and Qualification

Run existing provenance v1/v2 schema and compatibility runners, pure-core and
property tests, cross-domain conformance tests, real Project adapter tests,
accountable-history contract/application/API tests, OpenAPI and generated-client
parity, security and architecture checks, component and focused Chromium
accessibility tests, replay/projection-rebuild/PostgreSQL tests, and the
disposable local topology selected from the actual affected files.

Extend evidence only where cumulative retention separation, maximum bounds,
source-set rebuild, adapter neutrality, or cross-slice isolation is not already
observable. Run documentation, planning, migration, dependency, Python,
TypeScript, zero-warning lint, build, exact-candidate affected verification,
one independent technical review, deterministic slice and CAP closure, and
`python dev-tools/agent/check_ready.py`.

Tests assert contracts, ownership, bounded behavior, and required language—not
incidental whitespace, fixed fixture counts, wall-clock microbenchmarks, whole-
page snapshots, styling details, or internal implementation order. A bounded
inconsequential correction does not reopen a full review cycle.

## Rollback and Migration

This slice adds no public schema, migration, retained export, or policy by
default. Minimal harness and conformance assertions are removable without
changing learner or owner data. Existing additive contracts, projections, and
public operations retain the rollback rules established by their delivering
slices.

If qualification exposes a functional defect, route the smallest correction to
WRK-0194 when it remains inside the approved CAP. Do not erase retained facts,
weaken a bound, or reinterpret an owner record to make qualification pass. A
new public meaning, managed policy, infrastructure service, or breaking contract
returns the CAP to shaping or the applicable durable decision gate.

## Stop Conditions

Stop for stale CAP authority; a new owner or centralized business record;
breaking provenance/history meaning; caller-selected learner, purpose, tenant,
or authorization; direct cross-module storage access; retention duration,
deletion, legal hold, tenant policy, encryption, signing, recovery, immutable
storage, or cloud-provider selection; managed-cloud or public-hosting claims;
provider/model execution; external action; destructive migration; active write
collision; or material CAP-0026 drift.

Do not stop or reopen review solely for harmless whitespace, optional wording,
nonfunctional visual polish, fixture count or order, or another inconsequential
issue. Fix bounded issues locally or defer optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Delivery will reconcile the CAP, this slice, WRK-0194, the planning register,
the provenance contract guide, Audit contributor guidance, architecture
verification evidence, and any real gap found in deployment-parity or retention-
seam documentation. It will not create a managed retention contract by
implication.

Completion evidence must name the exact candidate, affected boundaries, checks
and live topology; prove exact replay, conflict, source-set rebuild, bounded
maximum shapes, cross-owner isolation, authorization/redaction, ephemeral
export, browser/headless parity, adapter-neutral shared-core semantics, restart,
accessibility, containment, cleanup, and aggregate readiness; and list residual
gaps honestly. CAP-0026 closes only when all four approved slices cumulatively
satisfy its acceptance scenarios.

## Planning History

- 2026-10-18: Refined the final approved manifest increment after SLI-0106,
  SLI-0107, and SLI-0108 completed. Deterministic selection found cumulative
  qualification plus the minimum policy-neutral retention and deployment seams
  eligible at 14 of 14. Managed retention and cloud qualification remain
  decision-gated, while isolated prior evidence alone is insufficient. The
  refinement preserves CAP-0026 and requires no slice-level approval.
- 2026-10-18: Authored WRK-0194 just in time as one qualification-first packet
  over the completed lineage, cross-domain conformance, and accountable-history
  seams. It adds no product behavior or lower-level approval and stops before
  managed retention, tenancy, legal, recovery, or cloud decisions.
