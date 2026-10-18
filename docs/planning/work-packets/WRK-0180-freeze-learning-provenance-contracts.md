---
id: WRK-0180
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0106
capability: CAP-0026
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/adapters/__init__.py", "backend/src/financial_ai_academy/modules/audit/adapters/provenance_contract.py", "backend/src/financial_ai_academy/modules/audit/domain/__init__.py", "backend/src/financial_ai_academy/modules/audit/domain/provenance.py", "backend/tests/contract/provenance", "backend/tests/unit/audit/test_provenance_contract.py", "contracts/README.md", "contracts/compatibility/README.md", "contracts/compatibility/provenance/v1", "contracts/provenance/v1", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/contract-architecture.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0106-trace-learning-content-and-evidence-lineage.md", "docs/planning/work-packets/WRK-0180-freeze-learning-provenance-contracts.md"]
generated_artifacts: []
base_revision: ef7ae20c509556fd4c9c94f1ed4025524ce33fd6
claim_id: WRK-0180:73d80fff-428c-4b9e-9bdd-078d35f749d5
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T07:40:44Z
---

# Agent Work Packet: Freeze Learning Provenance Contracts

## Objective and Deliverable

Freeze an additive, language-neutral `provenance-envelope/v1` contract family
and pure Audit contract boundary for exact published-lesson and knowledge-check
completion lineage. Deliver executable schemas, canonicalization vectors,
approved/denial compatibility fixtures, pure validated values, a contract
adapter, conformance tests, and canonical ownership documentation that later
packets can implement without copying Content or Assessment business state.

This packet must leave a coherent pure contract result. It does not add
persistence queries, application composition, protected HTTP, generated
clients, UI, or live topology behavior.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered context routing,
change impact, decision readiness, delivery planning, architecture/contracts,
security, testing, CAP-0026, SLI-0106, Content/Assessment/Audit public seams,
existing Audit domain/application/PostgreSQL behavior, lesson-package and
Assessment contracts, module/data architecture, consumers, tests, and nearest
READMEs.

Before any implementation file changes, repeat and report the applicable
`AGENTS.md` and repository-root `docs/README.md` startup gate, then revalidate
the current CAP package, parent slice, canonical sources, existing contracts,
consumers, tests, and nearest READMEs.

## Decisions and Assumptions

- CAP-0026 authority is current, SLI-0106 is in its exact manifest, and no
  unresolved decision applies to this pure additive local/shared-core contract.
- Content owns published lesson/source/publication facts. Assessment owns
  knowledge-check completion evidence. Audit owns only validated append-oriented
  integrity/accountability references and the bounded lineage projection.
- The first contract admits only closed `published_lesson` and
  `knowledge_check_completion` roots. Cross-domain roots remain SLI-0107 work.
- The contract records references and validation facts, not lesson body,
  answers, feedback, raw learner identity, provider payload, storage location,
  credentials, permissions, or another module's business state.
- Exact shapes use Draft 2020-12 schemas and deterministic UTF-8 sorted-key
  canonicalization. Meaning changes require an additive contract version.

## In Scope

- Add `contracts/provenance/v1` schemas and contributor documentation for:
  exact typed references and provenance envelopes; the two closed root
  selectors; bounded lineage nodes/edges and incomplete links; request/view
  shapes; closed owner/resource/relation/validation/status vocabularies; and
  canonical digest rules.
- Add compatibility fixtures for exact published-lesson and knowledge-check
  envelopes, one complete bounded lineage view, incomplete-link behavior,
  varied valid Unicode/count/order inputs, canonicalization, and representative
  malformed/private/oversized/conflicting inputs.
- Add pure immutable Audit domain values for validated references, envelopes,
  nodes, edges, incomplete links, and views with deterministic ordering and
  digest derivation.
- Add a pure contract adapter that validates closed schema/semantics, maps
  approved fixture bytes to values, projects exact public bytes, and rejects a
  partial or ambiguous graph before exposure.
- Define explicit v1 node, edge, depth, string, collection, timestamp, semantic-
  version, digest, and diagnostic bounds.
- Update canonical contract architecture, module ownership, Audit instructions,
  architecture-verification mapping, and contract catalogs.
- Add focused conformance, property, compatibility, safe-diagnostic, and anti-
  rigidity tests.

## Out of Scope

- Content/Assessment gateway implementation, Audit repository reads,
  reconciliation changes, application services, migrations, or composition.
- FastAPI routes/models, sessions/permissions, OpenAPI, generated TypeScript,
  browser code, UI, export, or live topology.
- Project, practice, learner-model, financial, market-data, portfolio, dataset,
  model, recommendation, provider/job, or administrative lineage.
- New tenancy, retention, recovery, legal/commercial, encryption, queue,
  provider, signing, blockchain, AI/model, external retrieval, or execution
  decisions.
- Generic arbitrary owners, relations, payload bags, URLs, file paths, SQL
  details, active content, or dynamically registered code.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Audit pure boundary | existing domain/adapters/README and unit patterns | exact listed provenance values, adapter exports, README, focused unit tests | implement contract meaning without application or persistence effects |
| Executable contracts | lesson/Assessment schema and compatibility conventions | new provenance v1 schemas, fixtures, vectors, READMEs, top-level catalogs | freeze external shape and deterministic behavior |
| Architecture | module map, contract architecture, verification map | new provenance contract plus exact related rows/sections | state ownership, non-authority, and evidence honestly |
| Planning | SLI-0106, this packet, register | lifecycle and evidence sections only | maintain governed public planning state |

No host, API, generated client, migration, persistence, other module, Web,
deployment, dependency, or unrelated documentation path is writable.

## Contracts and Interfaces

1. `ProvenanceEnvelopeV1` identifies schema version, closed owner module and
   resource kind, stable ID, exact version/occurrence, integrity digest,
   producer/policy reference, observed/recorded UTC time, validation status,
   and typed source/transformation references without a domain payload.
2. `LineageRootV1` is a tagged union for exact `published_lesson` and server-
   scoped `knowledge_check_completion`; no arbitrary owner/resource selector is
   accepted.
3. `LineageViewV1` contains the exact root, bounded nodes, bounded directed
   edges, explicit incomplete links, a truncation flag, and canonical digest.
4. Closed node kinds initially cover educational source, published lesson,
   assessment definition, completion event/evidence, and Audit integrity
   reference. Closed relations describe provenance only and confer no grading,
   mastery, causal, authorization, compliance, or financial meaning.
5. Canonicalization binds all public meaning with UTF-8 JSON, sorted object keys,
   compact separators, unescaped Unicode, UTC `Z` timestamps, normalized closed
   values, and deterministic node/edge ordering independent of input order.
6. Validation rejects unknown keys/enums, active content, arbitrary URLs/paths,
   private fields, invalid IDs/versions/digests/times, uncorrelated roots,
   duplicate changed identities, forbidden cycles, and exceeded bounds before
   returning a partial value. Diagnostics expose only stable code and bounded
   field/reference.
7. The pure boundary imports no framework, database, filesystem, network,
   provider, identity, time source, or another module's implementation.

## Dependencies and Parallel Safety

This is the first SLI-0106 packet and depends only on completed CAP-0001 and the
current CAP-0026/SLI-0106 contracts. It owns the schemas and pure values that
WRK-0181 will consume. It is not parallel-safe with another SLI-0106 packet
because downstream implementation must use the frozen exact contract and the
planning/register files overlap.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Published lesson envelope | Exact package/source/publication facts | The adapter parses and projects the approved document | Stable owner/kind/version/digest/time/reference meaning round-trips exactly without lesson content | schema/compatibility/unit |
| Completion envelope | Exact knowledge-check event/evidence and Audit reference facts | The approved document is admitted | Exact Assessment/Audit identities and integrity facts are retained without answer, feedback, or learner payload | schema/compatibility/unit |
| Complete lineage | Valid envelopes form one bounded chain | A view is composed and projected | Root, nodes, edges, order, and canonical digest are deterministic | domain/property/vector |
| Input order variation | Equivalent valid nodes/edges/sources arrive in another order | Canonicalization runs | Public order and digest are identical | property/vector |
| Valid extension within bounds | Unicode, source counts, optional facts, and additional non-root references vary | Validation runs | Valid documents pass without fixed fixture count or prose assumptions | property/anti-rigidity |
| Incomplete link | One optional owner reference is unavailable | An incomplete-link view is admitted | The missing relation is explicit and no source fact is fabricated | schema/domain |
| Changed duplicate | One identity appears with changed version or digest | Validation runs | The whole view fails with a bounded conflict diagnostic | domain/compatibility |
| Unsafe or private input | Unknown fields, payload bags, responses, feedback, learner ID, path, URL, secret-like key, active content, or provider data appears | Validation runs | The document fails before a partial value or raw input is exposed | schema/security |
| Bound violation | Node, edge, depth, string, or reference limits are exceeded | Validation runs | The document fails with a stable bounded diagnostic | schema/domain |
| Layer isolation | Pure contract/core imports are inspected | Architecture checks run | No framework, persistence, provider, host, or foreign module implementation dependency exists | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/contract/provenance backend/tests/unit/audit/test_provenance_contract.py -q`
- `python backend/tests/architecture/test_module_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Run the tracked affected-check plan and exact-candidate verification after the
implementation candidate is frozen, followed by one independent technical
disposition. Broader API, Web, PostgreSQL, and live checks are deferred because
this packet introduces none of those effects.

## Documentation and Evidence Update

Record exact contract identities, bounds, canonicalization, owner/non-authority
rules, compatibility fixtures, focused and affected checks, candidate/receipt,
technical finding status, rollback/migration impact, residual gaps, and CAP/
slice conformance in this packet and its direct canonical/README sources. Keep
all approval and reviewer records only in ignored local state.

## Stop Conditions

Stop for conflicting canonical ownership; stale CAP authority; a requirement
for arbitrary owners/relations or copied domain payloads; cross-module table
access; a public breaking change; unresolved tenancy, retention/recovery,
legal/commercial, encryption, provider, queue, signing, model, or execution
authority; a write-scope/ownership collision; or material CAP/SLI drift.

Do not stop or reopen review solely for harmless whitespace, optional prose,
valid fixture count/order, nonfunctional styling, or another inconsequential
issue. Fix bounded documentation locally or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0106.WRK-0180`; exact candidate and qualifying receipt;
schemas and contract identities; bounds and canonicalization; approved and
denial corpus; deterministic/anti-rigidity results; architecture/security
isolation; documentation impact; migration/rollback status; assumptions;
residual gaps; CAP conformance; and any unresolved decision. Confirm no
persistence, public API, client, UI, owner-state, identity, provider/model,
external-action, or financial authority changed.

## Planning History

- 2026-10-18: Authored just in time after SLI-0106 refinement. The packet
  freezes one additive pure learning-provenance contract boundary for the first
  two closed roots and leaves application/API/live delivery to its dependent
  packets without adding a lower-level approval.
