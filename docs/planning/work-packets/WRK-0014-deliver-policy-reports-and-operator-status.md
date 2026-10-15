---
id: WRK-0014
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0006
capability: CAP-0002
depends_on: ["WRK-0013"]
decision_gates: []
parallel_safe_with: []
write_scope: [".github/workflows/agent-readiness.yml", "dev-tools/agent/README.md", "dev-tools/agent/check_ci_workflow.py", "dev-tools/agent/check_ready.py", "dev-tools/control-plane", "dev-tools/planning/README.md", "docs/assurance/known-verification-gaps.md", "docs/context/packs/testing-quality.pack.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0006-enforce-policy-and-project-operator-status.md", "docs/planning/work-packets/WRK-0014-deliver-policy-reports-and-operator-status.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: ["artifacts/control-plane"]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0014:bc0d75ad-f363-4f5b-9ca7-99fd726aa7f4
claimed_by: codex-control-plane
claimed_at: 2026-10-15T12:52:20Z
---

# Agent Work Packet: Deliver Policy Reports and Operator Status

## Objective and Deliverable

Deliver a reusable policy/report and operator-projection layer, integrate all
control-plane tests and privacy-minimized reports into local/CI readiness, retain
CI reports, update documentation, and prove parity plus anti-rigidity.

## Required Context

Read `AGENTS.md`, `docs/README.md`, routed context packs, CAP-0002, SLI-0006,
predecessor contracts, planning/testing guidance, current readiness runner, CI
workflow and checker, assurance gaps, affected code/tests, and nearest READMEs
before edits.

## Decisions and Assumptions

- Policy rules are shared code; profile differences describe evidence
  availability, not different safety semantics.
- Reports and status are derived, privacy-minimized, and non-authoritative.
- CI remains read-only and never reconstructs missing local authority or review
  records.
- Workflow artifact upload is evidence retention, not publication/release.

## In Scope

Rule/report schemas, local/CI evaluator, operator projection, atomic report
writer, CLI, readiness allowlist integration, workflow report retention, CI
contract checker changes, assurance/docs, tests, and anti-rigidity assertions.

## Out of Scope

Hosted services, remote workers, branch-protection mutation, dashboards, product
UI, credentials, push/merge/release/deploy, maintenance bypass, or telemetry.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable control plane | Lifecycle, receipts, reviews, adapters | `dev-tools/control-plane/` | Add policy, report, projection, CLI, tests |
| Readiness/CI | Runner, workflow checker, workflow | Named agent/workflow files | Run focused suites and retain machine report consistently |
| Guidance/assurance | Named docs | Exact `write_scope` | Document parity, privacy, retention, next actions, and remaining host gap |
| Planning | SLI/WRK/register | Named planning files | Synchronize lifecycle and evidence |

## Contracts and Interfaces

Stable `control-policy-report-v1` and `operator-status-v1`, stable rule and
remediation IDs, deterministic overall exit mapping, report-output confinement,
and CI artifact name/path contract.

## Dependencies and Parallel Safety

WRK-0013 is complete. This packet is serial because it integrates every prior
control-plane projection into shared readiness and CI surfaces.

## Acceptance Scenarios

The SLI-0006 table is normative. Tests also assert report rule order is stable,
report output uses hashes/counts instead of raw subprocess or review text,
status is read-only, and a narrow local failure does not prescribe unrelated
full-suite work.

## Verification Commands

- `python dev-tools/control-plane/test_policy.py`
- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/agent/check_ci_workflow.py`
- `python dev-tools/agent/check_ready.py`
- `python dev-tools/agent/check_ready.py --profile ci`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`

## Documentation and Evidence Update

Update reusable/operator references, readiness and CI documentation, testing
guidance, assurance gaps, packet/slice evidence, and register. Generated reports
remain untracked runtime outputs and may be uploaded by CI.

## Stop Conditions

Stop for local/CI policy divergence, lifecycle mutation in CI, sensitive report
content, reviewer disclosure, unconfined output, hosted dependency, or material
CAP drift.

## Required Handoff

Report schemas/rules, status behavior, exact focused/local/CI checks, report
retention and privacy evidence, anti-rigidity results, documentation/assurance
impact, remaining external configuration gaps, and next slice action.

## Planning History

- 2026-10-15: Authored just in time as the single SLI-0006 integration packet
  after SLI-0005 and WRK-0013 completed.
- 2026-10-15: Delivered the reusable policy/report and operator-status cores,
  Financial AI Academy adapters, readiness/CI integration, retained sanitized
  reports, and focused anti-rigidity tests. All four control-plane suites,
  workflow contract, planning, documentation, and local/CI readiness passed.
