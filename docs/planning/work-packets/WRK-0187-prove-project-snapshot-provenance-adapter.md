---
id: WRK-0187
kind: work-packet
planning_status: ready
authority: noncanonical
owner: codex-cap-0026
updated: 2026-10-18
parent: SLI-0107
capability: CAP-0026
depends_on: [WRK-0186]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/audit/README.md", "backend/src/financial_ai_academy/modules/audit/adapters/__init__.py", "backend/src/financial_ai_academy/modules/audit/adapters/project_snapshot_reference.py", "backend/src/financial_ai_academy/modules/project/README.md", "backend/tests/architecture/test_module_boundaries.py", "backend/tests/unit/audit/test_project_snapshot_reference.py", "docs/architecture/assurance/architecture-verification.md", "docs/architecture/contracts/provenance-and-lineage-contract.md", "docs/architecture/modules/module-map.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0107-extend-provenance-across-domain-owners.md", "docs/planning/work-packets/WRK-0187-prove-project-snapshot-provenance-adapter.md"]
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Prove the Project Snapshot Provenance Adapter

## Objective

Deliver the first real cross-domain v2 owner adapter by reading one exact,
learner-bound immutable Project snapshot through Project's stable public
operation and issuing the minimal validated `project_snapshot` provenance
envelope. Prove both learning-started and independent Projects can use the seam
without exposing learner identity, project content, storage details, or new
runtime authority.

## Required Context

Revalidate `AGENTS.md`, repository startup and routed context, change impact,
decision readiness, CAP-0026, active SLI-0107, completed WRK-0184 through
WRK-0186, the v2 provenance contracts and pure conformance service, Audit and
Project contributor guidance, Project's public snapshot operation and immutable
snapshot model, architecture verification, module ownership, and affected
tests.

## Decisions and Assumptions

- CAP-0026 and SLI-0107 authority remain current, WRK-0186 is complete, and no
  unresolved decision applies to a local read of an existing Project snapshot.
- The adapter calls only `financial_ai_academy.modules.project.public` and uses
  `OpenProjectSnapshotRequest`, so the provenance seam covers both accepted
  Project origins. It does not inspect Project internals or repositories.
- Learner identity is required only to authorize Project's existing public read
  and never enters the v2 envelope, digest, result, exception, or documentation.
- The root reference contains only the frozen Project identity, snapshot digest,
  close time, observed label, validated status, and fixed adapter producer.
  Project notes, source URLs, artifact bytes or paths, domain-link data, origin,
  and mutable workspace state remain private.
- Project resources are not coerced into unrelated v2 profiles. This first real
  adapter emits no source links; later owner-issued typed references may add
  only contract-valid sources through separately bounded work.
- This packet adds no public HTTP operation, persistence, migration, background
  delivery, provider/model call, export, UI, or new authorization policy.

## Exact Scope

1. Add one frozen Audit outer adapter that implements the existing typed
   conformance port for `PROJECT_SNAPSHOT` and depends only on Project's public
   operation protocol.
2. Bind one caller-supplied learner/project/snapshot request, validate the
   returned exact IDs and revisions, and map only immutable safe facts into the
   frozen v2 domain envelope.
3. Prove valid learning-started and independent snapshot results, exact request
   delegation, canonical conformance success, mismatch denial, Project failure
   isolation, and absence of learner/content/storage fields.
4. Extend architecture evidence so the real cross-module dependency remains
   public-only and Audit gains no Project persistence or internal import.
5. Update contributor, contract, module, verification, slice, packet, and
   register documentation with exact evidence.

## Exclusions

- No change to Project's public operation, domain model, repository, schema,
  migration, API, generated client, browser flow, or permission policy.
- No retained Audit cross-domain row, graph, request operation, export,
  redaction workflow, or background delivery.
- No real Market-data, Portfolio, AI-orchestration, Adaptation, or Audit owner
  adapter and no synthetic fixture reinterpretation.
- No provider, network, filesystem, subprocess, model, execution, financial
  calculation/action, tenant, administrator, commercial, or external effect.

## Acceptance Scenarios

| Scenario | Expected observable result |
| --- | --- |
| Exact immutable snapshot | The adapter calls Project's public `open_snapshot` once with the bound learner/project/snapshot IDs and issues one valid canonical Project envelope |
| Both Project origins | Learning-started and independent snapshots with the same public immutable shape conform without origin-specific branching |
| Confidential boundary | The envelope and conformance result contain no learner ID, note/source/artifact/link content, path, URL, bytes, origin payload, or storage detail |
| Correlated identity | Returned project and snapshot IDs plus positive project/workspace revisions bind exactly to the request and snapshot digest |
| Mismatched or malformed snapshot | The adapter fails closed with a bounded platform-owned reference and retains no returned record |
| Project failure isolation | A Project error yields only the conformance service's stable adapter-failure result; its message/reference cannot leak |
| Public-only architecture | Audit imports Project only through `project.public` and has no Project repository/schema dependency |
| Existing compatibility | Frozen v1/v2 contract suites and the synthetic conformance kit remain unchanged and passing |

## Verification Commands

- `backend/.venv/Scripts/python.exe -m pytest backend/tests/unit/audit/test_project_snapshot_reference.py backend/tests/unit/audit/test_cross_domain_conformance.py backend/tests/unit/audit/test_cross_domain_provenance.py backend/tests/contract/provenance backend/tests/contract/provenance_v2 backend/tests/architecture/test_module_boundaries.py -q`
- `python dev-tools/architecture/check_architecture.py`
- `python dev-tools/security/check_slice_security.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/planning/check_planning.py`
- `git diff --check`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update Audit and Project contributor guidance, the provenance contract guide,
module map, architecture verification, this packet, SLI-0107, and the planning
register. Completion evidence records the exact candidate and qualifying
receipt; Project request and mapping results; origin flexibility;
confidentiality, mismatch, failure-isolation, public-only architecture,
compatibility, security, documentation/planning, and aggregate readiness.

## Stop Conditions

Stop for a required Project contract reinterpretation or operation change;
retained state; public API/UI; resource-to-profile invention; provider/model or
external effects; financial/administrative authority; identity, tenancy,
licensing, recovery, legal/commercial, retention/export, or external-action
decision; scope collision; or material CAP/SLI drift.

Do not stop or reopen broad review for harmless whitespace, optional wording,
fixture count/order, or nonfunctional styling. Fix bounded local defects or
defer polish to CAP-0031.

## Required Handoff

Report `CAP-0026.SLI-0107.WRK-0187`; exact candidate and receipt; public Project
operation and safe mapping; both Project origins; confidentiality and mismatch
denial; Project failure isolation; public-only architecture; v1/v2 and
conformance compatibility; security/documentation/readiness evidence;
assumptions, residual gaps, rollback posture, CAP conformance, and unresolved
decisions. Confirm no Project contract, persistence, API/client, UI, provider,
model, tenant/admin, external-action, or financial authority changed.

## Planning History

- 2026-10-18: Authored just in time after WRK-0186 completion. The packet uses
  Project's existing origin-neutral public snapshot read and the frozen Audit
  port to prove one real owner without expanding transport, persistence, or
  authority. WRK-0188 remains the cumulative slice-qualification boundary; no
  lower-level approval exists or is required.
