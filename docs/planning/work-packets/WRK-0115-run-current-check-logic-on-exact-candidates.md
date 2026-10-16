---
id: WRK-0115
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-control-plane-correction
updated: 2026-10-16
parent: SLI-0004
capability: CAP-0002
depends_on: ["WRK-0114"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/financial_academy_checks.py", "dev-tools/control-plane/test_verification.py", "dev-tools/control-plane/verification.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0004-select-affected-checks-and-record-receipts.md", "docs/planning/work-packets/WRK-0115-run-current-check-logic-on-exact-candidates.md"]
generated_artifacts: []
base_revision: 2c03265419a6115427d0371359c42d9b585ffda9
claim_id: WRK-0115:f4f00386-2a67-4ace-b979-9a120a114072
claimed_by: codex-control-plane-correction
claimed_at: 2026-10-16T21:52:55Z
---

# Agent Work Packet: Run Current Check Logic on Exact Candidates

## Objective and Deliverable

Make repository-specific web checks execute the current trusted control-plane
wrapper while targeting the submitted exact-candidate root. This lets a current
catalog add or correct a check for a historical product candidate without
requiring out-of-scope control-plane files in that product packet. Implement the
bounded WRK-0012 correction route with digest
`sha256:90555fb8f500dbc529976d4e0c23ca9e0e0247c7a93426b3ab40d6f132fd2803`.

## Required Context

Read `AGENTS.md`, `docs/README.md`, routed startup sources, CAP-0002, SLI-0004,
WRK-0012, WRK-0067, WRK-0114, the recorded correction route, testing and
concurrent-work guidance, the catalog, executor, verification service, focused
tests, and the nearest control-plane README before editing.

## Decisions and Assumptions

- The control-plane installation that selects a current catalog also owns the
  wrapper implementation for those allowlisted commands.
- Product source, tests, dependencies, Git identity, and build output continue
  to come from the exact candidate root passed explicitly to the wrapper.
- Commands remain fully materialized in the plan and receipt; no arbitrary
  path or untracked command is accepted from the product candidate.
- Normal same-worktree verification remains behaviorally identical.

## In Scope

- Add an explicit repository-root argument to the web-check wrapper.
- Define repository web-check commands with a portable logical wrapper identity
  and the exact candidate working root.
- Materialize a portable logical wrapper identity only at execution time and
  bind the wrapper bytes into the tracked check contract.
- Authenticate those bytes in the reusable executor before launch and after
  completion, failure, or timeout, and retain the observations in the receipt.
- Prove a wrapper outside a historical candidate invokes commands against that
  candidate, including a mode absent from the historical wrapper.
- Preserve current runtime preparation, isolation, catalog digest, and narrow
  affected-selection behavior.

## Out of Scope

Untracked or arbitrary command execution, remote workers, verification result
reuse, dependency installation, weakening candidate stability, copying control
files into product packets, or a new approval stage.

## Expected File and Boundary Impact

| Area | Allowed to change | Reason |
| --- | --- | --- |
| Web-check wrapper | CLI root argument and focused tests | target an explicit exact-candidate repository |
| Repository catalog | resolved current-wrapper command | separate trusted check logic from candidate inputs |
| Verification executor | bounded logical-wrapper materialization | keep the catalog portable while executing trusted current bytes |
| Operator guidance | control-plane README | document the ownership and confinement boundary |
| Planning lineage | this packet, parent slice, register | retain bounded correction provenance |

## Contracts and Interfaces

The internal wrapper CLI gains `--root <repository>` with the current repository
as its default. Catalog commands pass the current wrapper path and `--root .`;
the allowlisted executor already runs with the exact candidate as its working
directory, so `.` resolves to that candidate. Plan and receipt schemas remain
unchanged and record the materialized command.

## Dependencies and Parallel Safety

WRK-0114 is complete and supplies the focused Project browser check that exposed
this seam. The packet changes shared control-plane adapter files and is not
parallel-safe with another control-plane packet. WRK-0111 remains submitted and
must receive fresh verification after this correction completes.

## Acceptance Scenarios

| Scenario | Expected result |
| --- | --- |
| Current catalog checks a historical candidate | current wrapper logic runs against historical candidate inputs |
| Historical wrapper lacks a new mode | current allowlisted mode still executes without product-scope expansion |
| External wrapper changes | executor refuses before launch or after every exit path; the receipt cannot qualify |
| Ordinary same-worktree run | behavior and candidate stability remain unchanged |
| Invalid explicit root | command fails without falling back to another repository |
| Unrelated narrow change | no additional broad suite is selected |

## Verification Commands

- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- affected exact-candidate verification and independent technical review
- `python dev-tools/agent/check_ready.py`
- `git diff --check`

## Documentation and Evidence Update

Update reusable operator guidance, this packet, the parent slice, and register.
Keep exact receipts and review records only in ignored local state; tracked
artifacts contain no reviewer or approval identity, disposition, or history.

## Stop Conditions

Stop if the change executes untracked commands, reads product inputs outside the
submitted candidate, weakens stable-HEAD checks, embeds a machine-specific path
in tracked data, requires product-scope expansion, or materially changes CAP-0002.

## Required Handoff

Report wrapper ownership, candidate-root confinement, historical-candidate and
same-worktree evidence, selected/deferred checks, exact candidate and receipt,
focused and aggregate results, documentation impact, and remaining environment
gaps.

## Planning History

- 2026-10-16: Authored after a current focused browser check could be selected
  for a historical product candidate but its relative command resolved the
  older candidate wrapper. The bounded correction separates current trusted
  check logic from exact candidate inputs without widening the product packet.
- 2026-10-16: Incrementally refined after execution evidence showed that an
  absolute wrapper path was not portable or content-bound. The replacement
  correction route adds the existing reusable verification seam without
  changing product scope or requiring a new approval stage.
- 2026-10-16: Strengthened the reusable executor so wrapper authentication is
  independent of wrapper-controlled code and remains enforced across every
  subprocess outcome.
