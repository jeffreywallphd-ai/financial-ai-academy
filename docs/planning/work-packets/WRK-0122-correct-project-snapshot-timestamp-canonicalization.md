---
id: WRK-0122
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0007
updated: 2026-10-17
parent: SLI-0031
capability: CAP-0007
depends_on: [WRK-0120]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/src/financial_ai_academy/modules/project/application/service.py", "backend/tests/unit/project/test_project_workspace_service.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0031-save-project-work-and-close-a-snapshot.md", "docs/planning/work-packets/WRK-0122-correct-project-snapshot-timestamp-canonicalization.md"]
generated_artifacts: []
base_revision: b18988789268cddcb0f57ed097431aa5b61bda1f
claim_id: WRK-0122:b42f1bd6-e2eb-40bf-8518-b7c429a053d5
claimed_by: codex-cap-0007
claimed_at: 2026-10-17T02:04:25Z
---

# Agent Work Packet: Correct Project Snapshot Timestamp Canonicalization

## Objective and Deliverable

Remove the intermittent Project checkpoint integrity failure exposed by the
live SLI-0031 qualifier. Make snapshot material use the Project contract's one
canonical timestamp representation, add a deterministic regression for
fractional seconds that end in zero, and return WRK-0121 to qualification
without changing any public contract or authority.

## Required Context

Before editing, follow `AGENTS.md` and `docs/README.md`; route through the
Project, architecture, API/security, and testing-quality context packs; apply
the change-impact matrix and decision-readiness register; inspect CAP-0007,
SLI-0031, WRK-0118 through WRK-0121, the Project snapshot and workspace
contracts, `ContractProjectAdapter`, `ProjectService`, Project application
tests, and nearest READMEs.

## Decisions and Assumptions

- Accepted Project snapshot, digest, PostgreSQL, API-first, and generated-client
  decisions remain sufficient. No new durable decision is required.
- The Project contract adapter is the canonical timestamp authority. The
  application service must not independently choose a different JSON spelling.
- The observed failure is deterministic: an `updated_at` microsecond value such
  as `123450` is hashed with six digits by `ProjectService._timestamp`, then
  validated with trailing zeroes removed by
  `ContractProjectAdapter._format_timestamp`.
- This is a functional integrity correction, not optional styling or copy.

## In Scope

- Reuse the already validated workspace contract document when constructing
  snapshot material so `workspace_created_at` and `workspace_updated_at` are
  hashed in exactly the representation the contract validates.
- Add a deterministic application regression using a clock value with nonzero
  fractional seconds ending in one or more zeroes.
- Prove snapshot closure, digest validation, immutable stored snapshot, and
  export remain stable for that timestamp without relaxing any digest check.
- Run focused Project application/contract tests and the planning, whitespace,
  documentation, security, architecture, and readiness checks appropriate to
  the two-line boundary correction. WRK-0121 owns the resumed live qualifier.

## Out of Scope

Any schema, OpenAPI, generated client, browser behavior, persistence migration,
timestamp precision policy change, digest relaxation, compatibility exception,
identity, tenancy, provider, Portfolio, Assessment, learner-model, financial
action, AI authority, external execution, managed-cloud, recovery, styling, or
remote-push change.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Project application | snapshot material assembly and contract adapter | `service.py` only | Reuse canonical workspace timestamp strings for digest input |
| Regression | existing headless workspace/snapshot service tests | named Project service test | Reproduce trailing-zero fractional precision deterministically |
| Planning | SLI-0031, this packet, register | named planning files | Record correction lifecycle and return to WRK-0121 |
| Contracts/API/storage/UI | all affected consumers | none | Public shapes and authority remain frozen |

## Contracts and Interfaces

No external shape changes. Snapshot material still carries the accepted UTC
timestamp strings and SHA-256 digest. The correction removes a second internal
serialization path; it does not truncate the stored `datetime`, weaken digest
validation, or make clients authoritative for time or evidence.

## Dependencies and Parallel Safety

WRK-0120 supplies the completed Project application/browser flow. WRK-0122 is
the bounded correction prerequisite for WRK-0121. It is not parallel-safe with
WRK-0121 because both reconcile SLI-0031 planning state, so WRK-0121 remains
released until this packet is complete.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Trailing-zero timestamp | accepted workspace time has nonzero microseconds ending in zero | a checkpoint closes | digest creation and contract revalidation use one canonical string and closure succeeds | deterministic unit regression |
| Exact integrity | corrected checkpoint exists | snapshot and export are revalidated | exact material digest and record bindings still pass without a bypass | Project application/contract tests |
| Precision flexibility | valid UTC times have zero, trimmed, or full fractional precision | normal Project flows run | success does not depend on incidental final microsecond digits | anti-rigidity regression and current suites |
| Boundary preservation | correction is applied | imports and public operations are inspected | contract remains authoritative and API/schema/client/storage behavior is unchanged | architecture and diff review |

## Verification Commands

Run the packet validator and planning integrity; focused Project application
service tests; Project contract and API tests affected by snapshot closure;
Python compile and formatting/lint checks available in the repository; Git
whitespace, documentation, architecture, security, planning, exact-candidate,
aggregate readiness, and independent technical review. After completion,
resume WRK-0121 and run its isolated PostgreSQL/API/Chromium/restart qualifier.

## Documentation and Evidence Update

Record the exact failing precision, root cause, corrected canonical source,
regression result, candidate receipt, and review outcome in this packet, the
SLI history, and the register. Do not claim a contract or public behavior
change. Assurance documents remain owned by WRK-0121 unless the correction
changes an existing claim.

## Stop Conditions

Stop for a required contract/schema/API/migration change; evidence that the
contract canonicalizer itself is inconsistent; digest relaxation; retained
snapshot mutation; write collision; unrelated Project behavior; unresolved
identity, tenancy, provider, recovery, legal, commercial, model-authority, or
external-execution choice; or material CAP-0007 drift.

Do not reopen review for formatting-only corrections inside the named files.

## Required Handoff

Report `CAP-0007.SLI-0031.WRK-0122`; exact root cause and fractional timestamp;
changed boundary; regression and cumulative checks; candidate receipt and
independent review; documentation impact; and confirmation that no contract,
API, storage, browser, provider, assessment, learner-model, financial, or AI
authority changed. Then return to WRK-0121.

## Planning History

- 2026-10-17: Authored after WRK-0121 reproduced intermittent checkpoint
  `integrity_failure` and a 1,000-iteration direct service probe identified
  `snapshot_digest` failures whenever valid fractional seconds ended in zero.
  The packet is intentionally limited to canonical timestamp reuse and one
  deterministic regression.
- 2026-10-17: Reclaimed from clean base `b189887` after preserving the
  already-authored WRK-0121 qualifier. Snapshot digest assembly now reuses the
  contract-projected workspace timestamp strings instead of independently
  rendering the same datetimes. The deterministic `123450` microsecond
  regression and the focused Project unit, contract, and API suites passed
  138 tests with one environment-specific skip; exact-candidate verification
  and independent review remain before completion.
