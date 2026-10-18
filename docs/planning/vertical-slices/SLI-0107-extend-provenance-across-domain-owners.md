---
id: SLI-0107
kind: vertical-slice
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: CAP-0026
depends_on: ["SLI-0106"]
decision_gates: []
---

# Vertical Slice: Extend Provenance Across Domain Owners

## Outcome and User Scenario

A domain owner or contributor can issue one versioned, typed provenance
reference and verify it with a shared conformance kit before that reference is
accepted into a bounded lineage chain. Project provides the first real
cross-domain owner adapter; synthetic contract fixtures prove the extension
rules for financial observations, datasets, models, executions, simulations,
recommendations, and administrative actions without claiming that their owning
modules or providers already exist. Audit correlates only validated references
and never copies the owners' business payloads.

## Scope Boundaries

### In Scope

- An additive cross-domain provenance contract family that preserves
  `provenance-envelope/v1` unchanged while introducing closed owner/resource
  profiles with exact identity variants.
- Typed profiles for projects, financial and market observations, datasets,
  models and model executions, simulations, recommendations, and local
  administrative actions. Each profile defines its owner, required identity,
  provenance labels, allowed reference relations, and forbidden private data.
- A provider-neutral profile catalog and pure conformance kit that validates
  owner-issued references, rejects unsupported profiles narrowly, and prevents
  one failing adapter from disabling unrelated profiles or v1 learning lineage.
- A real read-only Project adapter using Project's public operation and exact
  snapshot identity rather than Project persistence or private fields.
- Deterministic synthetic fixtures for profiles whose owning modules are not
  implemented. These fixtures prove contracts only and do not create product
  records, provider integrations, model execution, financial calculations, or
  administrative authority.
- Compatibility, architecture, security, isolation, and anti-rigidity evidence
  across varied valid identities, reference counts and order, optional facts,
  and Unicode values.

### Out of Scope

- Changing, reinterpreting, or broadening `provenance-envelope/v1`; existing
  learning-lineage operations and documents remain byte-compatible where their
  inputs are unchanged.
- A public HTTP operation, learner-facing history page, export, retention
  control, or tamper-diagnostic interface; SLI-0108 owns human inspection and
  purpose-limited output.
- Live market-data or other provider calls, provider-specific payloads,
  portfolio calculations, advice or suitability, model inference or training,
  dataset acquisition, sandbox execution, jobs, notifications, or external
  actions.
- Organization or tenant identity, administrator authorization, managed-cloud
  policy, legal hold, compliance guarantees, encryption selection, signing,
  recovery, or immutable-infrastructure claims.
- A dynamic plugin registry, arbitrary profile registration, central mutable
  provenance aggregate, cross-module database joins, new shared tables, or
  copied domain payloads.
- Nonfunctional styling or broad UI cleanup, which remains CAP-0031 scope.

## Canonical Context and Decisions

- [CAP-0026](../capabilities/CAP-0026-preserve-provenance-and-accountable-history.md)
  authorizes cross-domain, conformance-tested typed references after the
  learning-lineage foundation in SLI-0106.
- [Provenance and Lineage Contract](../../architecture/contracts/provenance-and-lineage-contract.md)
  freezes the closed v1 learning contract and requires additive versioning for
  new owner/resource meaning.
- [Module Map](../../architecture/modules/module-map.md),
  [Contract Architecture](../../architecture/contracts/contract-architecture.md),
  and [Data Architecture](../../architecture/data/data-architecture.md) keep
  business facts with their owners and prevent Audit from becoming a second
  domain database.
- [Project Workspace Contract](../../architecture/contracts/project-workspace-contract.md) provides
  an implemented public snapshot seam suitable for the real adapter proof.
- [Financial Method and Simulation Architecture](../../architecture/finance/financial-method-and-simulation-architecture.md),
  [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md),
  and [Experiment Boundary](../../architecture/ai-ml/experiment-execution-boundary.md)
  constrain future financial, dataset, model, execution, simulation, and
  recommendation profiles without authorizing those capabilities here.
- Accepted ADRs 0012, 0014, 0015, 0016, 0018, and 0020 govern project links,
  method identity, evidence labels, deterministic financial authority, model
  boundaries, and adaptive recommendations where applicable.
- [Decision Readiness](../../adr/decision-readiness.md) exposes no unresolved
  decision for an additive local contract, pure conformance kit, and read-only
  Project adapter. Any requirement for live providers, tenant or administrator
  authority, concrete model execution, external action, or retention/export
  policy returns to its named decision gate.

## Candidate Evaluation

| Candidate | Eligible | Value | End-to-end | Decisions | Contracts | Independence | Verification | Reversibility | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A. Add one closed cross-domain contract family, shared conformance kit, and real Project adapter with synthetic future-owner profiles | yes | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |
| B. Let each domain invent a separate envelope now and map them into shared provenance later | yes, but it duplicates identity and validation policy | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 10 |
| C. Add a dynamic registry that accepts arbitrary owner and resource kinds | no; it defeats closed trust, deterministic validation, and explicit ownership | - | - | - | - | - | - | - |
| D. Defer all extension work until every future owner CAP is implemented | yes, but it withholds the reusable contract and conformance seam those CAPs need | 1 | 0 | 2 | 1 | 0 | 1 | 2 | 7 |

## Selection Rationale

Candidate A scores 14 of 14 because it delivers a usable extension seam without
pretending future domains are implemented. It preserves explicit owners, gives
Project a real end-to-end proof, and lets later capabilities adopt a stable
conformance kit incrementally. Candidate B preserves ownership but creates
avoidable vocabulary and validation drift. Candidate C is ineligible because
arbitrary registration would make provenance meaning runtime-configurable and
hard to secure. Candidate D is reversible but blocks the contract dependency
and provides no present cross-domain proof.

The selection preserves CAP-0026's approved outcome, four-slice manifest,
sequence, decision posture, risks, and non-goals. It does not require or create
a slice-level approval.

## Boundary Path

1. Additive schemas define the closed cross-domain envelope and one exact
   identity variant per owner/resource profile; v1 schemas do not change.
2. Pure values validate profile identity, provenance label, digest, time,
   producer or policy reference, allowed relations, field bounds, and canonical
   order before any owner adapter result can be correlated.
3. A closed profile catalog and conformance kit exercise valid, invalid,
   conflicting, reordered, incomplete, and unknown-profile documents without
   importing product adapters.
4. A Project adapter calls only the Project public snapshot operation and maps
   its exact project, revision, resource-link, and submission identities into
   the shared contract without copying project content.
5. Synthetic reference adapters prove the contract shapes for future financial,
   dataset, model, execution, simulation, recommendation, and local
   administrative owners. They cannot call providers, models, or persistence.
6. Compatibility, architecture, security, isolation, and anti-rigidity checks
   prove that v1 learning lineage remains stable and one invalid profile does
   not affect unrelated profiles.
7. Public transport, user inspection, purpose-limited redaction/export, and
   cumulative runtime qualification are intentionally absent until SLI-0108
   and SLI-0109.

## Contracts, Data, and Provenance

The additive contract uses a closed discriminated profile rather than a bag of
optional identity fields. A project snapshot identifies the Project owner,
project ID, exact revision, snapshot digest, and applicable resource or
submission references. Financial observations identify the future owner,
instrument identity, observation or as-of time, method or source-set identity,
unit and currency where applicable, and integrity digest without carrying
licensed provider payloads. Dataset, model, execution, simulation,
recommendation, and administrative profiles similarly require their exact
version, run, policy, occurrence, or snapshot identity rather than overloading
one generic version string.

Every profile retains an observed, calculated, simulated, predicted, generated,
or administrative label appropriate to its semantics. Labels describe origin;
they do not confer correctness, mastery, eligibility, investment suitability,
permission, regulatory status, or authority. Relations remain closed and
descriptive. Unknown owners, kinds, versions, labels, relations, private fields,
provider payloads, unstable locators, ambiguous identity combinations, and
conflicting duplicate identities fail before correlation.

The conformance kit publishes reusable valid and invalid documents plus a
provider-neutral runner. Owners keep their authoritative records and issue
references through public operations. Audit may retain a bounded integrity
reference later, but this slice introduces no cross-owner table, migration, or
new durable business state.

## Acceptance Scenarios

| Scenario | Expected observable result | Owning verification layer |
| --- | --- | --- |
| Real Project snapshot | The adapter reads an exact Project snapshot through its public operation | A valid typed project reference retains exact project/revision/digest facts and no project content or storage fields | contract/application |
| Synthetic owner profiles | Deterministic fixtures represent financial, dataset, model, execution, simulation, recommendation, and administrative identities | Every supported profile passes the same reusable conformance runner without claiming a live owner implementation | contract/conformance |
| v1 compatibility | Existing lesson and completion documents run against their unchanged schemas and compatibility corpus | Existing documents and canonical meaning remain accepted without cross-domain fields | compatibility |
| Unknown or malformed profile | A document uses an unsupported profile/version, ambiguous identity, bad digest, forbidden relation, private field, or oversized value | Only that document fails with a bounded safe error; unrelated profiles and v1 remain usable | domain/security |
| Conflicting identity | Two references reuse one exact identity with changed meaning or digest | Conformance rejects the conflict rather than selecting one value or mutating prior meaning | domain/conformance |
| Adapter isolation | One synthetic adapter is absent, fails, or returns an invalid document | Other owner profiles and the Project adapter still validate independently | application/architecture |
| Variable valid input | Reference counts and order, optional facts, Unicode values, and profile-specific identity variants change within bounds | Canonical results remain deterministic without fixed fixture counts or whole-document snapshots | property/anti-rigidity |
| No external authority | The complete focused suite runs | No network/provider/model call, financial action, tenant decision, persistence migration, or external side effect occurs | architecture/security |

## Agent Work Packets

Detailed packet files are authored one at a time immediately before work starts.
The dependency-ordered seams are:

| Packet ID | Objective | Dependencies | Parallel-safe with | Planning status |
| --- | --- | --- | --- | --- |
| [WRK-0184](../work-packets/WRK-0184-freeze-cross-domain-provenance-contracts.md) | Freeze the additive cross-domain provenance schemas, profile catalog, compatibility corpus, ownership rules, and contract tests | none | none | complete |
| [WRK-0185](../work-packets/WRK-0185-extend-cross-domain-provenance-core.md) | Extend the pure provenance core for closed typed owner profiles, exact identities, deterministic canonicalization, and isolated failures | WRK-0184 | none | complete |
| [WRK-0186](../work-packets/WRK-0186-build-cross-domain-provenance-conformance-kit.md) | Build the reusable cross-domain conformance kit, synthetic reference adapters, property evidence, and contributor instructions | WRK-0185 | none | ready |
| WRK-0187 | Prove the real Project owner adapter through Project's public snapshot seam and focused architecture/security evidence | WRK-0186 | none | captured |
| WRK-0188 | Qualify v1 compatibility, cross-domain isolation, anti-rigidity, documentation, and slice completion | WRK-0187 | none | captured |

Sequential delivery is required because each packet freezes the meaning consumed
by the next. No safe parallel packet is identified inside this small shared
contract boundary. A bounded correction may add a dependent packet without
changing the approved CAP or slice outcome.

## Verification and Qualification

Run additive schema and compatibility conformance; closed-profile and exact-
identity tests; canonicalization, relation, bound, conflict, and property tests;
conformance-runner self-tests; synthetic-adapter isolation; real Project public-
operation integration; v1 regression; provider/private-field and module-boundary
security checks; documentation and planning checks; whitespace integrity; and
aggregate agent readiness. Tests must vary valid counts, ordering, profile
variants, optional facts, and Unicode inputs and must not depend on fixed whole-
document snapshots when focused invariant assertions are sufficient.

## Rollback and Migration

The new contract family and pure conformance assets are additive. No migration,
retained-state rewrite, provider change, or feature exposure applies. Before a
downstream owner publishes the new family, it can be removed without touching
v1 learning lineage. After adoption, meaning changes through a later additive
version rather than in-place reinterpretation.

## Stop Conditions

Stop for conflicting owner authority; stale CAP authority; a requirement for
tenant, organization, or administrator authorization; live provider or licensed
data; a concrete model or execution environment; financial calculation or
action; external effects; public export or retention policy; provider-specific
semantics; a mutable shared aggregate; cross-owner persistence; a v1 contract
break; or a public API/UI expansion. Return to CAP shaping only for a material
outcome, manifest, sequence, risk, or decision-posture change.

Do not stop or reopen review solely for harmless whitespace, optional wording,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or route optional polish to CAP-0031.

## Documentation Impact and Completion Evidence

Update the provenance contract guide, contract catalog, Audit and Project
contributor instructions, module ownership documentation, conformance-kit
instructions, architecture verification, packet artifacts, this slice, and the
planning register. Completion evidence must record exact candidates and
qualifying receipts, v1 compatibility, profile/conformance/core/Project adapter
results, isolation and anti-rigidity results, security and architecture gates,
aggregate readiness, migration status, residual gaps, and CAP conformance.

## Planning History

- 2026-10-18: Refined immediately after SLI-0106 completion. Candidate A scores
  14 of 14 and selects an additive closed profile family, reusable conformance
  kit, one real Project adapter, and synthetic contract proofs for future domain
  owners. The refinement preserves CAP-0026's approved outcome, manifest,
  sequence, decision posture, risks, and non-goals; no lower-level approval
  exists or is required.
- 2026-10-18: Authored dependency-first WRK-0184 with an exact pure-contract,
  compatibility-corpus, architecture, documentation, and test scope. Later
  packets remain captured until the frozen cross-domain contract exists.
- 2026-10-18: Activated WRK-0184 from clean base `cfc0db4` after confirming
  current CAP authority, completed SLI-0106, resolved decision posture, bounded
  contract-only scope, and no active file-ownership collision.
- 2026-10-18: Reclaimed WRK-0184 from base `e7e5dce` after the aggregate gate
  identified the exact derived Guidance source bindings affected by the
  canonical contract-architecture update. The bounded scope reconciliation
  changes no packet outcome, product meaning, or approval posture.
- 2026-10-18: Rebound WRK-0184 once more from base `e7e5dce` after focused
  compatibility verification exposed the directly derived contextual-help
  vector and assertion. The complete bounded reconciliation scope is now fixed.
- 2026-10-18: Completed WRK-0184 and authored dependency-ready WRK-0185 with a
  separate additive v2 type/mapping core, exact frozen identity semantics, and
  focused isolation evidence. V1, product adapters, conformance-kit integration,
  persistence, and public operations remain outside this packet.
- 2026-10-18: Completed WRK-0185 at exact candidate `406fbc1`. The separate
  pure v2 core now enforces closed exact types, immutable profile rules,
  deterministic canonicalization, bounded denial, and frozen-runner digest
  parity. WRK-0186 is the next dependency-ready conformance seam.
- 2026-10-18: Authored WRK-0186 with a pure profile-bound adapter port,
  per-adapter isolation, partial-suite support, deterministic synthetic owner
  proofs, varied-input evidence, and no real owner or runtime authority.
