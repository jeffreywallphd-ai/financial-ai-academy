---
id: WRK-0019
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0011
capability: CAP-0003
depends_on: ["WRK-0017"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/portfolio.py", "dev-tools/control-plane/portfolio_conflicts.py", "dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_portfolio_conflicts.py", "dev-tools/control-plane/test_portfolio_ordering.py", "dev-tools/control-plane/README.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0011-identify-parallel-safe-work.md", "docs/planning/work-packets/WRK-0019-deliver-parallel-compatibility.md"]
generated_artifacts: []
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0019:b8ec60ae-c407-4244-98c9-3e6e20516c3d
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:03:47Z
---

# Agent Work Packet: Deliver Parallel Compatibility

## Objective and Deliverable

Deliver generic pair/set compatibility analysis, repository evidence projection
and aggregation, CLI/docs, and focused safety and anti-rigidity tests.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/testing context,
CAP-0003, SLI-0009/0011, WRK-0017, concurrent-work and scope semantics,
portfolio code/tests, local control state shape, CLI, and nearest README.

## Decisions and Assumptions

- `incompatible` requires affirmative collision/dependency evidence; `unknown`
  records insufficient evidence and narrow remediation.
- WRK compatibility requires reciprocal declarations in addition to disjoint
  exact scope evidence; CAP/SLI compatibility uses aggregated refined evidence.
- Active claim and branch comparisons expose categorical conflict only.
- Scope aggregation never claims completeness while declared descendants are
  absent or unrefined.

## In Scope

Compatibility contract/core, graph evidence fields, repository aggregation,
read-only command, concurrency/README guidance, pair/set tests, and
anti-rigidity assertions.

## Out of Scope

Leases, allocation, agent execution, branch mutation, merge, push, remote
coordination, or lifecycle writes.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generic portfolio | Graph/order cores | `portfolio.py`, `portfolio_conflicts.py`, tests | Carry generic evidence and decide compatibility |
| Repository adapter | Planning artifacts/local state | `financial_academy_portfolio.py` | Project and aggregate repository facts |
| CLI/docs | Command dispatch/readmes | Named files | Expose and explain advisory compatibility |
| Planning | SLI/WRK/register | Named artifacts | Synchronize lifecycle and evidence |

## Contracts and Interfaces

`portfolio-compatibility-v1`; decision values `compatible`, `incompatible`, and
`unknown`; stable evidence/reason codes; deterministic safe sets; existing path
normalization and result envelopes.

## Dependencies and Parallel Safety

WRK-0017 is complete. This packet shares portfolio adapter/CLI surfaces and is
executed serially in the current branch.

## Acceptance Scenarios

The SLI-0011 table is normative. Tests also cover case/separator normalization,
generated-vs-write overlap, empty candidate sets, deterministic repeatability,
unknown incomplete descendants, reciprocal declarations, and every-pair-safe
group invariants.

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Document the decision taxonomy, aggregation confidence, reciprocal WRK rule,
and narrow remediation. Record checks without local owner/approval metadata.

## Stop Conditions

Stop for false safety, blanket unknown-as-conflict, identity leakage, mutation,
unresolved decisions, or scope beyond this packet.

## Required Handoff

Report compatibility contract, evidence aggregation, CLI/tests, docs,
assumptions, residual risks, and CAP conformance.

## Planning History

- 2026-10-15: Authored just in time for conforming SLI-0011 delivery.
- 2026-10-15: Refined the write scope to include the existing ordering adapter
  integration assertion made stale by normal predecessor-slice completion.
- 2026-10-15: Delivered `portfolio-compatibility-v1`, scope/resource/claim/
  branch evidence, safe-set construction, CLI/docs, and seven focused tests;
  all named repository gates passed.
