---
id: WRK-0188
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0107
capability: CAP-0026
depends_on: [WRK-0187]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/tests/contract/provenance_v2/test_slice_qualification.py", "contracts/compatibility/provenance/v2/README.md", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0107-extend-provenance-across-domain-owners.md", "docs/planning/work-packets/WRK-0188-qualify-cross-domain-provenance-slice.md"]
generated_artifacts: []
base_revision: 5bd836d548239f20f713a5c17f6f33e05ea2ec8a
claim_id: WRK-0188:04b5670a-6b5e-47ea-a534-35a0b645e84c
claimed_by: codex-cap-0026
claimed_at: 2026-10-18T09:47:56Z
---

# Qualify the Cross-Domain Provenance Slice

## Objective

Qualify the complete SLI-0107 increment by replacing the synthetic Project
fixture with the real public-only Project adapter inside the reusable nine-
profile conformance suite, proving partial adoption and failure isolation remain
flexible, rerunning the unchanged v1/v2 compatibility and safety boundaries,
and reconciling completion evidence without adding another product surface.

## Required Context

Revalidate `AGENTS.md`, repository startup and routed context, change impact,
decision readiness, CAP-0026, active SLI-0107, completed WRK-0184 through
WRK-0187, the frozen v1/v2 contracts and compatibility corpus, the pure core,
conformance kit, real Project adapter, Audit contributor guidance, provenance
contract guide, architecture verification, and affected tests.

## Decisions and Assumptions

- CAP-0026 and SLI-0107 authority remain current, WRK-0187 is complete, and no
  unresolved decision gate applies to cumulative local qualification.
- The cumulative test replaces only the synthetic Project profile with the real
  adapter. The other eight profiles remain explicit test-only forecasts and do
  not claim product owners.
- Complete qualification is intentionally closed to the nine frozen profiles,
  while partial suites exercise zero and varied subsets so incremental owner
  adoption never requires a fixed adapter count or all-or-nothing runtime.
- Failure of the real Project adapter remains local to that case; unrelated
  synthetic profiles continue to validate and report exact missing coverage.
- This packet changes no production behavior, schema, contract meaning,
  transport, persistence, provider/model integration, or authorization.

## Exact Scope

1. Add cumulative conformance tests that combine the real Project adapter with
   the eight synthetic future-owner adapters and prove complete deterministic
   profile coverage.
2. Vary subset size and order without fixed whole-report snapshots; assert only
   set/order/digest invariants that define the contract.
3. Prove a failing or mismatched Project public read does not disable unrelated
   profiles and does not expose rejected values or Project error details.
4. Rerun the complete frozen v1/v2 contract, pure core, conformance, Project
   adapter, Project-origin, module-boundary, architecture, security,
   documentation/planning, whitespace, and aggregate readiness gates.
5. Reconcile Audit/contract/architecture guidance and SLI-0107 completion
   evidence with exact candidate and receipt facts.

## Exclusions

- No new owner adapter, profile, schema field, relation, label, mapper, port,
  domain rule, product operation, persistence, migration, API/client, or UI.
- No retained cross-owner graph, export/redaction workflow, background event,
  provider/model/runtime call, financial or administrative action, tenant,
  external effect, or managed-cloud claim.
- No reinterpretation of v1, no fixture-count assumption beyond the closed v2
  profile catalog, and no broad cleanup or styling work.

## Acceptance Scenarios

| Scenario | Expected observable result |
| --- | --- |
| Real-plus-synthetic complete suite | Replacing the synthetic Project profile with the real adapter still yields one valid case for every frozen profile and a complete report |
| Varied partial adoption | Empty and varied profile subsets run independently, preserve deterministic profile order, and report the exact missing set without treating absence as an adapter failure |
| Input reordering | Reversing or interleaving adapters cannot change per-profile codes or digests |
| Real Project failure | A Project exception or mismatched snapshot invalidates only the Project case and exposes no Project message, learner ID, URL, path, token, or payload |
| V1 compatibility | Every frozen v1 schema, approved document, canonical vector, and recorded fingerprint remains unchanged and passing |
| V2 compatibility | Frozen catalog, schemas, approved/denial corpus, canonical vectors, pure core, mapper, and language-neutral runner remain exact |
| Boundary containment | Product code imports no synthetic adapter; Audit uses only `project.public`; no repository/schema, API/UI, provider/model, filesystem/network, or external-effect boundary appears |
| Anti-rigidity | Valid Unicode, time offsets, source order/count, identity variants, zero sources, and partial profile sets remain accepted within frozen semantic bounds |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/contract/provenance backend/tests/contract/provenance_v2 backend/tests/unit/audit/test_cross_domain_provenance.py backend/tests/unit/audit/test_cross_domain_conformance.py backend/tests/unit/audit/test_project_snapshot_reference.py backend/tests/unit/project/test_project_workspace_service.py backend/tests/unit/project/test_project_learning_snapshot.py backend/tests/architecture/test_module_boundaries.py -q`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `git diff --check`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update Audit contributor and v2 compatibility guidance, the provenance contract
guide, architecture verification, this packet, SLI-0107, and the planning
register. Completion evidence records the exact candidate and receipt; mixed
real/synthetic, partial-set, order, isolation, confidentiality, v1/v2,
anti-rigidity, architecture/security, documentation/planning, and readiness
results; and explicit residual future-owner/runtime gaps.

## Stop Conditions

Stop for contract reinterpretation; a new real owner or profile; production
behavior; retained state; public API/UI; provider/model/external effects;
financial/administrative authority; unresolved identity, tenancy, licensing,
recovery, legal/commercial, retention/export, or external-action decision;
scope collision; or material CAP/SLI drift.

Do not stop or reopen broad review for harmless whitespace, optional wording,
test count/order, or nonfunctional styling. Fix bounded local defects or defer
polish to CAP-0031.

## Completion Evidence

- Exact candidate: `c07207f3648cf74d6a64bf8b200e3f40e73d1c14`.
- Qualifying receipt: `sha256:7bc09c4d3d975d19d02e34a0b65dfeaabec9741634ab40f6801ae03388a4d239`.
- The complete focused command passed 112 tests. The mixed suite replaces only
  the synthetic Project profile with the real public-only adapter, validates
  all nine frozen profiles, preserves exact v1/v2 compatibility, and proves
  variable partial-set adoption and input-order invariance.
- A crafted Project failure produces only the bounded Project case while
  unrelated profiles remain valid; rejected URL, token, message, learner, and
  payload details do not enter the report.
- Architecture passed 18 checks, security passed 10 control groups, and all 30
  aggregate-readiness checks passed. Documentation, planning, and whitespace
  integrity also passed.
- This test-and-documentation packet changes no production contract, code,
  retained state, migration, API/client, UI, provider/model, tenant or
  administrator authority, external action, or financial behavior.

## Required Handoff

Report `CAP-0026.SLI-0107.WRK-0188`; exact candidate and receipt; mixed real and
synthetic coverage; partial/order/failure isolation; v1/v2 compatibility;
anti-rigidity and confidentiality; architecture/security/documentation and
readiness evidence; assumptions, residual gaps, rollback posture, CAP
conformance, and unresolved decisions. Confirm no production contract,
persistence, API/client, UI, provider/model, tenant/admin, external-action, or
financial authority changed, and close SLI-0107 when all acceptance evidence is
current.

## Planning History

- 2026-10-18: Authored just in time after WRK-0187 completion. The packet adds
  cumulative mixed-adapter and flexible partial-suite evidence, not a new
  product feature, then closes SLI-0107 if the frozen contracts and all gates
  remain current. No lower-level approval exists or is required.
- 2026-10-18: Activated from clean base `5bd836d` after confirming current CAP
  authority, completed WRK-0187, resolved decisions, exact isolated write
  scope, and no active file-ownership collision.
- 2026-10-18: Added cumulative mixed-adapter qualification, varied partial-set
  and order evidence, and confidential Project-failure isolation without any
  production behavior or contract change.
- 2026-10-18: Verified and completed at exact candidate `c07207f` with a valid
  qualifying receipt, accepted technical disposition, 112 focused tests, and
  passing architecture, security, documentation, planning, whitespace, and
  aggregate-readiness gates. SLI-0107 is complete.
