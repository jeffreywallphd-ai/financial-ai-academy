---
id: WRK-0186
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0107
capability: CAP-0026
depends_on: [WRK-0185]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/application/__init__.py", "backend/src/financial_ai_academy/modules/audit/application/cross_domain_conformance.py", "backend/src/financial_ai_academy/modules/audit/ports/__init__.py", "backend/src/financial_ai_academy/modules/audit/ports/cross_domain_provenance.py", "backend/tests/contract/provenance_v2/synthetic_adapters.py", "backend/tests/contract/provenance_v2/test_conformance_kit.py", "backend/tests/unit/audit/test_cross_domain_conformance.py", "contracts/provenance/v2/README.md", "contracts/compatibility/provenance/v2/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0107-extend-provenance-across-domain-owners.md", "docs/planning/work-packets/WRK-0186-build-cross-domain-provenance-conformance-kit.md"]
generated_artifacts: []
base_revision: 20d531334514c15cae4af0cb416594529e43d1cf
claim_id: WRK-0186:66fb3525-4e4c-47de-a926-4e18c31e37bc
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T09:31:00Z
---

# Agent Work Packet: Build the Cross-Domain Provenance Conformance Kit

## Objective and Deliverable

Build a reusable, pure conformance seam that future domain owners can run
against one candidate v2 reference adapter before integration. Deliver one
closed adapter port, immutable per-profile results, deterministic suite
ordering, isolated bounded failures, synthetic adapters for all future-owner
profiles, varied-input evidence, and contributor instructions. The kit consumes
the exact WRK-0184 contract and WRK-0185 core without changing either meaning.

## Required Context

Revalidate `AGENTS.md`, repository startup and routing guidance, change impact,
decision readiness, CAP-0026, active SLI-0107, completed WRK-0184 and WRK-0185,
the provenance contract guide and catalog, Audit's nearest README, the v2 domain
and mapping core, standalone contract runner, approved and denial corpus,
architecture verification, module ownership, and affected tests.

## Decisions and Assumptions

- CAP-0026 and SLI-0107 authority remain current; WRK-0185 is complete; no
  unresolved decision gate applies to a pure local validation seam.
- The adapter port issues one typed owner reference and declares one exact
  closed profile. An outer owner adapter may use the shared v2 mapper, while the
  application conformance service depends only inward on typed domain values.
  The port grants no persistence, runtime discovery, registration, network,
  provider, model, financial, administrative, or external authority.
- A conformance run is per-call immutable evidence. The kit owns no global
  registry, cached result, filesystem read, retained history, or production
  readiness claim.
- Synthetic adapters are contract test doubles only. Their deterministic
  records prove profile compatibility but do not make any future owner real.
- The standalone language-neutral runner remains independent of product imports
  and remains authoritative for schema/catalog corpus qualification.

## In Scope

- A narrow `CrossDomainReferenceAdapter` protocol with an exact profile and one
  side-effect-free typed-reference issue operation.
- Immutable case and suite results with profile, validity, canonical digest on
  success, and bounded code/reference on failure; no raw payload or exception
  text appears in results.
- One pure single-adapter evaluator and a suite evaluator that rejects duplicate
  declared profiles, orders results deterministically, and continues after one
  adapter fails or returns malformed data.
- Exact declared-profile versus emitted-profile validation, closed profile
  coverage helpers, and compatibility with the WRK-0185 mapper and digest.
- Deterministic synthetic adapters for all profiles other than the future real
  Project proof, plus a synthetic Project fixture used only for complete-kit
  contract qualification.
- Parameterized/property-style evidence varying valid identity values, Unicode,
  time offsets, source order and count, optional allowed labels, occurrences,
  adapter order, omissions, failures, malformed output, and duplicates.
- Contributor instructions that distinguish contract qualification, synthetic
  evidence, and the later real owner-adapter proof.

## Out of Scope

- A real Project adapter, Project imports, public operation, persistence,
  migration, graph, history view, HTTP/OpenAPI/client surface, UI, export,
  retention, recovery, signing, or tamper diagnostics.
- Live provider, market-data, dataset, model, execution, simulation,
  recommendation, financial calculation, tenant, administrator, job, network,
  filesystem, subprocess, or external-action behavior.
- Dynamic plugins, runtime registration, entry-point discovery, mutable global
  catalogs, arbitrary profiles, copied business payloads, or a production
  readiness certification.
- V1 changes or changes to frozen v2 schemas, profile catalog, approved corpus,
  denial cases, canonical vectors, or standalone-runner semantics.

## Expected File and Boundary Impact

Audit application owns pure conformance orchestration and depends inward on the
Audit adapter port plus the existing v2 mapping/domain core. The port expresses
only what a future owner must supply. Test-only synthetic adapters live beside
the v2 contract tests and must not be imported by product code. Documentation
explains adoption without presenting synthetic owners as implemented.

No generated artifact, database, deployment file, dependency, API, client,
design token, browser resource, or provider configuration changes.

## Contracts and Interfaces

1. The adapter declaration and emitted resource must name the same exact closed
   profile; disagreement is a bounded invalid result.
2. Each adapter is evaluated independently. A thrown exception or invalid
   typed envelope affects only that profile result. Outer mapping failures are
   reduced to the same fixed adapter-reference diagnostic.
3. Successful results expose the exact profile and canonical envelope digest,
   never the full record. Failure exposes only a stable bounded code and safe
   reference, never raw exception or payload text.
4. Suite input order cannot alter result order or digest. Duplicate declared
   profiles fail closed without choosing one adapter.
5. Complete-profile qualification compares exact closed sets; partial suites
   remain valid for incremental owner development and report missing profiles
   without treating them as implemented failures.
6. The kit is stateless and performs no I/O. The language-neutral runner retains
   schema/catalog/corpus responsibility; the kit validates typed owner adapters
   through the production v2 domain core. Test-only outer adapters exercise the
   shared mapping boundary before issuing those typed values.

## Dependencies and Parallel Safety

Depends on completed WRK-0185 and directly shares the v2 Audit boundary and
planning files with later packets. It is not parallel-safe with WRK-0187 or
WRK-0188. Complete and close this packet before claiming its successor.

## Acceptance Scenarios

| Scenario | Expected observable result |
| --- | --- |
| Every synthetic profile | All nine deterministic test adapters produce valid profile-bound digests matching the frozen standalone runner |
| Partial owner adoption | A one-profile or mixed subset runs successfully and reports the exact missing closed profiles without requiring a fixed adapter count |
| Adapter failure isolation | One exception or malformed record yields one bounded invalid case while unrelated adapters still validate |
| Profile mismatch or duplicate | The kit rejects the mismatch or duplicate deterministically without choosing an adapter or leaking its record |
| Variable valid input | Unicode, time offset, source order/count, allowed labels, versions, and occurrences vary within bounds while canonical meaning stays deterministic |
| Confidential malformed input | Provider-like private keys, raw exception text, URLs, and oversized values do not appear in result diagnostics |
| Boundary isolation | Product code imports no synthetic adapters and the kit imports no Project owner, repository, host, provider, model, filesystem, subprocess, or network dependency |
| V1 and frozen-v2 compatibility | Existing v1/v2 contract suites and fingerprints remain exact |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/audit/test_cross_domain_conformance.py backend/tests/unit/audit/test_cross_domain_provenance.py backend/tests/contract/provenance backend/tests/contract/provenance_v2 -q`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `git diff --check`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update Audit contributor guidance, v2 contract and compatibility instructions,
the provenance contract guide, module map, architecture verification, this
packet, SLI-0107, and the planning register. Completion evidence records the
exact candidate and qualifying receipt, synthetic-profile and partial-suite
results, isolation, anti-rigidity, confidentiality, compatibility,
architecture/security, documentation/planning, and aggregate readiness.

## Stop Conditions

Stop for contract reinterpretation; a real owner or Project operation; retained
state; runtime plugin discovery; provider/model/network/filesystem/external
effects; financial or administrative authority; public API/UI; unresolved
identity, tenancy, licensing, model, recovery, legal/commercial, retention, or
external-action decisions; scope collision; or material CAP/SLI drift.

Do not stop or reopen broad review for harmless whitespace, optional wording,
test fixture count/order, naming that preserves the closed contract, or
nonfunctional styling. Fix bounded local defects or defer polish to CAP-0031.

## Completion Evidence

- Exact candidate: `979ce9fc9c5aa2a085f6154bf0c7ab892f5e8f77`.
- Qualifying receipt: `sha256:9a88079424164b3beec919ae852fa8718598b7c5ad36e19779adce2aa2b576f2`.
- The focused Audit and provenance contract suite passed 76 tests, including
  all nine frozen profiles, partial suites, deterministic order and digest,
  duplicate-profile denial, adapter failure isolation, variable valid input,
  and confidential malformed-input handling.
- Architecture verification passed 18 checks, slice security passed 10 checks,
  and aggregate agent readiness passed 30 checks. Documentation, planning, and
  whitespace integrity also passed.
- Existing v1 and frozen-v2 compatibility remained exact. The packet added no
  real owner, retained state, API/client, UI, provider or model call, tenant or
  administrator authority, external action, or financial authority.

## Required Handoff

Report `CAP-0026.SLI-0107.WRK-0186`; exact candidate and qualifying receipt;
port, case/suite, profile coverage, canonical digest, failure-isolation,
synthetic-adapter, varied-input, confidentiality, v1/v2 compatibility,
architecture/security, documentation, and readiness evidence; assumptions;
residual gaps; rollback/migration posture; CAP conformance; and unresolved
decisions. Confirm no real owner, persistence, API/client, UI, provider/model,
tenant/admin, external-action, or financial authority changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0185 completion. This packet
  converts the frozen v2 contract and pure core into an incremental reusable
  owner conformance seam with test-only synthetic profile adapters. The later
  real Project proof remains WRK-0187, and no lower-level approval exists or is
  required.
- 2026-10-18: Activated from clean base `20d5313` after confirming current CAP
  authority, completed WRK-0185, resolved decisions, exact isolated write
  scope, and no active file-ownership collision.
- 2026-10-18: Implemented the pure profile-bound port and per-call conformance
  report, deterministic partial/complete suite evaluation, duplicate and
  failure isolation, all-profile synthetic adapters, independent-runner digest
  parity, and varied valid input evidence without adding a real owner or I/O.
- 2026-10-18: Reconciled the incremental contract to the implemented inward-
  layering seam: owner adapters issue typed envelopes, while outer adapters may
  use the shared mapper. Adapter-raised validation references now collapse to a
  fixed platform-owned field so crafted URLs or secrets cannot enter results.
- 2026-10-18: Verified and completed at exact candidate `979ce9f` with a valid
  qualifying receipt, accepted technical disposition, 76 focused tests, and
  passing architecture, security, documentation, planning, whitespace, and
  aggregate-readiness gates. WRK-0187 is now dependency-ready.
