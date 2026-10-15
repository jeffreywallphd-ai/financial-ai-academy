---
id: WRK-0047
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0004
updated: 2026-10-15
parent: SLI-0003
capability: CAP-0002
depends_on: ["WRK-0011"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/control_plane.py", "dev-tools/control-plane/test_control_plane.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0003-resume-submit-interrupted-work-packet.md", "docs/planning/work-packets/WRK-0047-correct-submit-cli-input-routing.md"]
generated_artifacts: []
base_revision: ea4091d1b61c838569dbd5e1b62341d9cea941d0
claim_id: WRK-0047:e0b13d03-56cf-4c8e-b52d-fed24a8431a5
claimed_by: codex-cap-0004
claimed_at: 2026-10-15T17:27:17Z
---

# Agent Work Packet: Correct Submit CLI Input Routing

## Objective and Deliverable

Restore the documented `submit` command by routing its repeatable `--input`
arguments to the control-plane engine's `declared_inputs` parameter. Prove the
real CLI can submit an authorized clean candidate without a Python keyword
error, while preserving every lifecycle, scope, and exact-candidate check.

## Required Context

Before changing files, read and follow every applicable `AGENTS.md` and the
repository-root `docs/README.md`. Read the baseline and delivery-planning
context packs, CAP-0002, SLI-0003, WRK-0011, the bounded correction route for
`control-plane.cli-submit-input-mismatch`, the planning and control-plane
READMEs, the CLI parser/dispatcher, engine submission signature, candidate
adapter, and focused lifecycle tests.

## Decisions and Assumptions

The completed-work correction router confined the observed defect to the two
listed control-plane files. CAP-0002 already established `declared_inputs` as
the engine contract and `--input` as the public CLI spelling. Correcting the
argument destination is compatibility repair, not a new lifecycle, authority,
provider, or product decision. Completed WRK-0011 and SLI-0003 history remains
terminal; this packet records a bounded descendant correction.

## In Scope

- Map `submit --input` to the engine's `declared_inputs` keyword, matching the
  already-correct `resubmit` parser contract.
- Add a regression that invokes the real CLI against a clean fixture and proves
  submission succeeds through the parser/dispatcher/engine path.
- Run focused control-plane, planning, documentation, and aggregate readiness
  checks required for a shared control-plane correction.

## Out of Scope

Lifecycle changes, engine signature changes, broader CLI refactoring, new
approval or review stages, maintenance action expansion, product code, remote
execution, publication, deployment, push, and unrelated cleanup.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| CLI adapter | Parser, dispatcher, engine signature | `control_plane.py` | Align public flag destination with the stable engine contract |
| Regression evidence | Existing reusable fixture and submission tests | `test_control_plane.py` | Exercise the real command boundary that exposed the defect |
| Planning lineage | Completed parent slice, descendant packet, register | Listed planning files | Preserve bounded correction history without reopening terminal artifacts |

## Contracts and Interfaces

The public CLI remains `submit WORK_ID --owner ... --claim-id ... [--input
PATH]`; the internal call remains `ControlPlane.submit(...,
declared_inputs=[...])`. Result schema, refusal codes, state transitions,
candidate binding, scope checks, and local approval behavior remain unchanged.

## Dependencies and Parallel Safety

WRK-0011 is complete. The correction route digest
`sha256:2065952fce79982e84f0a873ec2fdc495a15fc6cec2a5c23afb2bf7d17c11b27`
confines implementation to the two control-plane files. This packet is not
parallel-safe because it changes the shared command entry point and aggregate
readiness evidence used by other active work.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| CLI submission | An authorized claimed packet and clean in-scope candidate | The real `submit` CLI runs | The exact candidate is submitted and the result is `submission.recorded` | CLI integration regression |
| Optional input mapping | Zero or more public `--input` flags | Arguments are parsed | The engine receives `declared_inputs` without an unexpected `input` keyword | Parser/CLI regression |
| Safety preservation | A submitted candidate is evaluated | Existing focused suite runs | Dirty, stale, forked, and out-of-scope candidates remain refused | Existing lifecycle tests |
| Bounded correction | The tracked diff is inspected | Qualification completes | No path outside the routed implementation and planning lineage changed | scope/diff checks |

## Verification Commands

Run `python -m unittest dev-tools/control-plane/test_control_plane.py`, the
control-plane focused suite, `python dev-tools/planning/check_planning.py`,
`python dev-tools/documentation/check_docs.py`, `python
dev-tools/agent/check_ready.py --base-ref <packet-base>`, and `git diff
--check`. Submit and verify the exact committed candidate through the repaired
controller and obtain independent technical review before deterministic
completion.

## Documentation and Evidence Update

Update only this packet, the SLI-0003 correction history, and the planning
register. The public CLI contract and existing README remain accurate, so no
canonical behavior documentation changes are expected. Keep all approval and
review records only in ignored local storage.

## Stop Conditions

Stop if the repair requires an engine/lifecycle contract change, weakens
candidate or scope validation, expands the public CLI, escapes the routed
paths, conflicts with another live file lease, introduces a durable decision,
or cannot be qualified through a clean exact candidate.

## Required Handoff

Report the corrected mapping, regression coverage, exact focused and aggregate
results, independent review disposition, documentation impact, and whether the
interrupted CAP-0004 packet can be replayed on the repaired base.

## Verification Progress

- The public `submit --input` parser now emits the engine's existing
  `declared_inputs` keyword; no engine, lifecycle, result, or refusal contract
  changed.
- The new regression drives the real CLI through a fixture claim and committed
  candidate, then confirms `submission.recorded` and the requested declared
  input. The focused lifecycle file passed 11 tests and the complete
  control-plane suite passed 110 tests using a repository-confined Windows
  temporary directory.
- Planning integrity passed for 74 artifacts, documentation validation passed
  for 198 Markdown files plus both catalogs, `git diff --check` passed, and the
  aggregate readiness gate passed all 27 checks against the packet base.
- Exact-candidate affected verification selected four checks—control-plane
  lifecycle, planning-tool behavior, planning integrity, and documentation
  integrity—and recorded a qualifying receipt with no errors. All required
  local completion gates are satisfied; authority and review records remain
  only in ignored local storage.
- Residual qualification is limited to explicit zero/multiple optional-input
  variants and non-Windows execution. The shared `argparse` append/default
  behavior, engine tests, and existing portability boundary remain unchanged.

## Planning History

- 2026-10-15: Authored from the bounded completed-work correction route after
  WRK-0043 submission exposed an unexpected `input` keyword passed by the CLI
  adapter. No CAP package, decision, or authority change is required.
- 2026-10-15: Implementation and pre-submission qualification passed; the
  packet moved to `verifying` for exact-candidate verification and independent
  technical review.
- 2026-10-15: Exact-candidate affected verification and all required local
  completion gates passed; WRK-0047 moved to `complete` without reopening
  WRK-0011 or SLI-0003.
