---
id: WRK-0185
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0107
capability: CAP-0026
depends_on: [WRK-0184]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/adapters/__init__.py", "backend/src/financial_ai_academy/modules/audit/adapters/cross_domain_provenance_contract.py", "backend/src/financial_ai_academy/modules/audit/domain/__init__.py", "backend/src/financial_ai_academy/modules/audit/domain/cross_domain_provenance.py", "backend/tests/unit/audit/test_cross_domain_provenance.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0107-extend-provenance-across-domain-owners.md", "docs/planning/work-packets/WRK-0185-extend-cross-domain-provenance-core.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Extend the Cross-Domain Provenance Core

## Objective and Deliverable

Implement one pure Python v2 owner-reference core that exactly realizes the
frozen `provenance/v2` contract without changing the v1 learning-lineage core.
Deliver immutable typed identities for every closed profile variant, exact
owner/profile/label/relation validation, deterministic mapping and
canonicalization, bounded confidential failures, and focused unit evidence.

The result is an internal reusable Audit-domain seam. It adds no product owner
adapter, lineage graph, persistence, public operation, generated client, or
browser behavior. WRK-0186 consumes it for the reusable conformance kit and
synthetic adapters; WRK-0187 later adds the first real Project adapter.

## Required Context

Before this planning edit, the repository `AGENTS.md` and `docs/README.md`
Required Startup was completed and reported. The review covered context routing,
change impact, decision readiness, CAP-0026, SLI-0107, completed WRK-0184, the
frozen v2 schemas/catalog/corpus, v1 Audit provenance core and adapters, Audit
ownership, architecture verification, tests, and nearest READMEs.

Before implementation, repeat and report the applicable startup gate. Revalidate
the current CAP package, parent slice, completed dependency, decision posture,
exact packet scope, and claim. Inspect the frozen schemas/catalog/fixtures, the
complete v1 core and mapping adapter, exports, consumers, focused tests, and
canonical provenance/module documentation before editing.

## Decisions and Assumptions

- CAP-0026 authority is current; SLI-0107 is active; WRK-0184 is complete; and
  no durable decision applies to a pure local contract implementation.
- V1 types, validators, mappings, canonical bytes, exports, requests, views,
  consumers, fixtures, and public behavior remain unchanged.
- V2 is a separate additive type family rather than new optional fields on v1.
  The frozen nine-profile catalog and ten identity variants are authoritative.
- Profile identity is represented by immutable profile-specific dataclasses,
  including separate financial account and analysis variants. A generic mutable
  identity mapping is allowed only at the mapping-adapter boundary.
- Market-observation resource identity remains the canonical SHA-256 digest of
  its exact normalized identity tuple. Other resource IDs equal the catalog's
  designated identity field.
- Validation is pure and stateless. One malformed envelope raises one bounded
  v2 error and cannot disable another profile or mutate admitted input.

## In Scope

- Add a separate Audit-domain v2 module with closed enums for owner module,
  profile/resource kind, origin label, relation, and validation status.
- Add immutable typed values for producer, ten exact identity variants, resource
  reference, source reference, and owner-reference envelope.
- Validate exact owner/profile/resource-kind combinations, identity variant,
  allowed label and relation sets, safe identifiers/versions/digests, aware
  times, positive occurrences/revisions, source bounds, resource-ID strategy,
  and duplicate/conflicting exact identities.
- Normalize aware times to UTC, sort sources deterministically, project one
  closed mapping shape, and calculate stable canonical envelope digests.
- Add a closed mapping adapter that admits the approved frozen fixture shape,
  rejects unknown/private keys and bad scalar/container types, and round-trips
  only the normalized contract meaning.
- Add focused unit tests that load every approved v2 profile, exercise both
  financial variants, prove source-order/timezone equivalence, reject changed
  duplicate meaning and independent Market IDs, vary valid Unicode/counts, and
  prove one failing profile does not affect another or v1.
- Update Audit and canonical architecture documentation for the implemented
  pure v2 seam and its explicit non-authority.

## Out of Scope

- Changes to `domain/provenance.py`, `adapters/provenance_contract.py`, the v1
  schemas/corpus/runner, existing learning-lineage behavior, or public exports.
- Changes to the frozen v2 schemas, catalog, compatibility corpus, or standalone
  dependency-light runner except through a later bounded correction if a true
  contradiction is found.
- The reusable conformance-kit integration, synthetic owner adapter library,
  Project public-operation adapter, graph composition, retained Audit reference,
  migration, repository, API, OpenAPI, generated client, or UI.
- Provider calls or payloads, market values, portfolio calculations, advice,
  dataset rows, model input/output, execution, recommendation text, Project
  content, actor/learner/tenant identity, administrator authority, storage
  locator, credential, external action, or dynamic profile registration.
- Unrelated refactoring, dependency changes, formatting cleanup, or styling.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Audit domain | complete v1 provenance and lineage core | new isolated `cross_domain_provenance.py`; additive domain exports | implement pure v2 values without broadening v1 |
| Contract adapter | v1 mapping adapter and frozen v2 documents | new isolated v2 mapping adapter; additive adapter exports | translate closed mappings at the boundary |
| Unit evidence | existing Audit provenance tests and v2 fixtures | one new focused v2 unit file | bind exact variants, normalization, failures, and isolation |
| Audit docs | module README | exact pure-v2 core section | state implemented maturity and non-authority |
| Architecture | provenance contract, module map, verification map | exact v2 core/verification sentences | keep ownership and evidence current |
| Planning | parent slice, this packet, register | lifecycle and evidence only | preserve governed delivery state |

No schema/corpus, conformance-runner, production application/service, port,
repository, migration, host, API/client, Web, deployment, dependency, provider,
or unrelated documentation file is writable.

## Contracts and Interfaces

1. The new type family uses distinct `CrossDomain*` names and schema version
   `2.0.0`; no v1 enum or dataclass gains a value or field.
2. Each resource admits exactly one catalog identity variant. Financial result
   variants carry an explicit account/analysis discriminator. Market resource
   ID is recomputed from the normalized exact identity; field-based profiles
   must equal their designated identity ID.
3. Mapping input/output is the exact envelope schema: resource, nested identity,
   producer, and zero to twenty sources. Unknown fields and unsupported enum or
   scalar values fail with a bounded reference and common confidential message.
4. Normalization projects times to UTC `Z` at mapping/canonical output, sorts
   sources by relation and canonical reference, and never mutates caller-owned
   mappings or dataclass instances.
5. Reuse of one exact profile identity with changed integrity/provenance meaning
   is a conflict; identical reuse is a duplicate. A failure is local to the one
   validation call and retains no registry or global state.
6. Canonical envelope digest is lowercase SHA-256 over compact sorted-key UTF-8
   JSON with unescaped Unicode. It matches the frozen runner for every approved
   document and equivalent ordering/timezone representations.
7. The core performs no filesystem, network, persistence, provider, model,
   identity, authorization, clock, randomness, execution, or external action.

## Dependencies and Parallel Safety

This packet depends on completed WRK-0184 and consumes its exact contract
meaning. It is not parallel-safe with WRK-0186 because that packet imports the
new values and mapping adapter, and it overlaps the parent slice and architecture
records. Complete and finalize this packet before claiming WRK-0186.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Closed profiles | Every approved frozen v2 document | The mapping adapter admits and reprojects it | Every profile and exact identity is retained in normalized deterministic form | fixture/unit |
| Financial variants | One analysis result and one valid account variant | Each is admitted | Exactly one explicit variant passes and resource ID equals its selected identity ID | unit/property |
| Market identity | One exact observation tuple | Resource identity is checked | Only the tuple digest is accepted; an independent ID fails | unit/contract |
| Equivalent meaning | Sources reorder and aware offsets represent the same instants | Canonicalization runs | Projected mapping and envelope digest remain exact | property/anti-rigidity |
| Conflicting duplicate | One exact profile identity repeats with changed digest or meaning | The envelope validates | The call fails rather than selecting, merging, or mutating either value | unit/security |
| Confidential denial | Unknown/private keys, unsupported enums, bad types, unsafe IDs, or oversized sources arrive | Mapping or domain validation runs | A bounded reference and generic message are returned without rejected values | unit/security |
| Failure isolation | One malformed profile is validated between valid documents of other profiles | Calls run independently | Only the malformed call fails; both valid calls still pass | unit/anti-rigidity |
| V1 isolation | Existing v1 provenance tests and fingerprints run | The additive v2 module is present | V1 public meaning and accepted documents remain unchanged | regression/architecture |
| Layer isolation | New module imports and effects are inspected | Architecture checks run | No adapter, repository, host, provider, model, clock, filesystem, or network enters the pure core | architecture |

## Verification Commands

- `backend\.venv\Scripts\python.exe -m pytest backend/tests/unit/audit/test_cross_domain_provenance.py backend/tests/unit/audit/test_provenance_contract.py backend/tests/contract/provenance backend/tests/contract/provenance_v2 -q`
- `python tests/architecture/test_approved_lesson_boundaries.py`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

Freeze one exact candidate, run the tracked affected-check plan, and obtain one
independent technical disposition. API, generated-client, PostgreSQL, browser,
Docker, and live-host checks are not routine for this pure internal value seam.

## Documentation and Evidence Update

Record the exact types, profile/identity validation, mapping and digest behavior,
focused/regression/property/architecture/security results, candidate and
qualifying receipt, migration/rollback impact, residual gaps, and slice/CAP
conformance in this packet and its direct canonical sources. Keep all approval
and reviewer records only in ignored local state.

## Stop Conditions

Stop for a contradiction with the frozen v2 schema/catalog/corpus; any v1
meaning or fixture change; a new profile, identity field, label, relation, or
resource-ID strategy; mutable global registry; production owner implementation;
graph, persistence, migration, public API/UI, provider/model/data-license,
tenant/administrator, financial authority, retention/export, external action,
or write-scope collision; or material CAP/SLI drift.

Do not stop or reopen broad review solely for harmless whitespace, optional
prose, implementation naming that preserves the frozen mapping, valid count or
ordering variation, or another inconsequential issue. Fix bounded local items
or defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0107.WRK-0185`; exact candidate and qualifying receipt;
implemented types and identity variants; mapping/canonical/digest equivalence;
financial and Market identity results; duplicate/conflict and confidential
denials; failure and v1 isolation; anti-rigidity, architecture, security,
documentation, and readiness evidence; migration/rollback status; assumptions;
residual gaps; CAP conformance; and unresolved decisions. Confirm no v1,
contract corpus, product owner adapter, persistence, public API/client, UI,
provider/model, identity/tenant/admin, external-action, or financial authority
changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0184 completion. The packet
  implements a separate pure v2 type/mapping family against the frozen contract,
  keeps v1 unchanged, and leaves conformance-kit integration, synthetic owners,
  real Project integration, and cumulative slice qualification to WRK-0186
  through WRK-0188 without adding a lower-level approval.
