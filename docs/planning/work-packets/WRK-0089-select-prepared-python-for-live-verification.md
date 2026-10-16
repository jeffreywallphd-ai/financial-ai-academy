---
id: WRK-0089
kind: work-packet
planning_status: active
authority: noncanonical
owner: codex-cap-0005
updated: 2026-10-16
parent: SLI-0024
capability: CAP-0005
depends_on: ["WRK-0088"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/README.md", "dev-tools/control-plane/check_approved_lesson.py", "dev-tools/control-plane/test_verification.py", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0024-open-and-return-to-an-eligible-activity.md", "docs/planning/work-packets/WRK-0089-select-prepared-python-for-live-verification.md"]
generated_artifacts: []
base_revision: e3a797735a4cfa3e5d9eb5bb853fb9687e57fcd2
claim_id: WRK-0089:266738cf-3c47-47ce-a505-316a7632e245
claimed_by: codex-cap-0005
claimed_at: 2026-10-16T13:20:05Z
---

# Agent Work Packet: Select Prepared Python for Live Verification

## Objective and Deliverable

Make the repository-owned affected-check wrapper select and propagate the
prepared backend Python runtime for isolated live qualification. A clean fork
with the documented backend environment must run the live exact-candidate
check without an ambient `PYTHONPATH` workaround or an unrelated system Python,
while explicit overrides and dependency-free check modes remain supported.

## Required Context

Before editing, read and follow every applicable `AGENTS.md` and the repository
root `docs/README.md`; route through the delivery-planning and testing-quality
packs. Read the change-impact matrix, decision readiness, CAP-0005, SLI-0024,
WRK-0088, concurrent-work rules, the control-plane README, the affected-check
wrapper, verification catalog, verification tests, local development setup,
backend environment layout, and approved-lesson live runner. Inspect the exact
failed and qualifying WRK-0088 receipts locally without copying reviewer or
approval data into tracked files.

## Decisions and Assumptions

- The repository backend virtual environment is the preferred implicit Python
  runtime when its platform-specific executable exists. The invoking Python is
  the portable fallback for check modes and setups without that environment.
- `FINANCIAL_AI_ACADEMY_PYTHON_EXECUTABLE` is a bounded explicit override,
  analogous to the existing Node/npm runtime controls. It selects an
  executable; it does not add dependencies, mutate the environment, or install
  software.
- The resolved Python is exported as `PYTHON` for nested scripts and directly
  invokes the approved-lesson runner. The wrapper does not rely on
  `PYTHONPATH`, copy a virtual environment into the candidate snapshot, or
  loosen exact-candidate isolation.
- This is a test-control portability correction only. It cannot alter product
  APIs, generated clients, learning behavior, fixture meaning, or a future
  headless AI mode.

## In Scope

- Extend the prepared runtime value with one resolved Python executable.
- Resolve an explicit Python override first, then a repository backend virtual
  environment using Windows or POSIX layout, then the invoking interpreter.
- Use that exact executable for the isolated live runner and propagate it to
  nested child processes.
- Add deterministic unit tests for explicit override, prepared-environment
  preference, fallback, child propagation, and live-runner invocation.
- Correct the control-plane README so it describes Node/npm and Python runtime
  selection precisely.
- Record focused, affected, and aggregate evidence and reconcile SLI-0024 and
  the planning register.

## Out of Scope

Product domain, application, API, OpenAPI, generated-client, UI, database,
fixture, Docker, lesson, curriculum, or model behavior; dependency
installation; virtual-environment creation; lockfiles; global environment
mutation; generic runtime management; remote execution; separate AI-mode
planning; or unrelated control-plane refactoring.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Affected-check runtime | wrapper, verification catalog, local setup | `dev-tools/control-plane/check_approved_lesson.py` | Select and use the prepared Python without changing check selection |
| Regression evidence | current runtime and snapshot tests | `dev-tools/control-plane/test_verification.py` | Prove override, discovery, fallback, propagation, and exact live invocation |
| Operator guidance | control-plane runtime section | `dev-tools/control-plane/README.md` | Document the actual portable selection order and override |
| Planning evidence | packet, parent slice, register | listed planning files | Keep packet status and SLI-0024 completion evidence synchronized |

No product source, public contract, generated artifact, dependency manifest,
fixture, deployment composition, or live browser specification may change.

## Contracts and Interfaces

`resolve_runtime(environment, root)` consumes the supplied environment and the
repository root and returns Node, npm, and Python commands. Existing Node/npm
pair validation and version requirements remain unchanged. The new optional
Python override is a single path or command resolved without shell parsing.
`child_environment` publishes that resolved value as `PYTHON`, and
`run_live_in_snapshot` invokes the same value for the tracked candidate's live
runner. All other check modes preserve their current commands and selection.

## Dependencies and Parallel Safety

WRK-0088 is complete and supplies the exact live scenario that exposed this
clean-host portability seam. This packet touches shared control-plane runtime
and verification-test files and the active slice/register, so it is not
parallel-safe with other work on those paths. It owns no product boundary and
does not reopen WRK-0088's accepted candidate.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Prepared environment | A repository backend virtual-environment executable exists and no override is set | Runtime resolution runs | That executable becomes the child and live-runner Python | unit and live affected check |
| Explicit override | A Python override and prepared environment both exist | Runtime resolution runs | The explicit executable wins without shell parsing | unit |
| Portable fallback | No override or repository environment exists | Runtime resolution runs | The invoking interpreter remains usable for dependency-free modes | unit |
| Exact live invocation | An isolated candidate snapshot is prepared | Live qualification runs | Build uses prepared Node/npm and the runner uses the resolved Python | unit command capture and affected check |
| No product drift | The wrapper correction is applied | Focused and aggregate checks run | Public APIs, generated clients, fixtures, and application behavior remain unchanged | scope diff and readiness |

## Verification Commands

Run:

```text
python dev-tools/control-plane/test_verification.py
python dev-tools/control-plane/check_approved_lesson.py --mode live
python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0089-select-prepared-python-for-live-verification.md
python dev-tools/planning/check_planning.py
python dev-tools/documentation/check_docs.py
git diff --check
python dev-tools/agent/check_ready.py
```

Submit one exact candidate, run fresh affected verification without setting
`PYTHONPATH`, and obtain one independent technical review. The live check may
use the repository's existing isolated Docker/PostgreSQL qualification path;
it must not install or publish anything.

## Documentation and Evidence Update

Update the control-plane README with the Python selection order and explicit
override. Record the exact candidate, focused tests, live result, aggregate
readiness, qualifying receipt, review disposition, assumptions, and remaining
gaps in this packet and SLI-0024. Keep approval and reviewer records only in
the ignored local ledger.

## Stop Conditions

Stop for a required dependency install, product/API/client/fixture change,
shell-parsed executable input, environment mutation outside the child process,
candidate-snapshot weakening, new remote execution, provider/cloud choice,
unresolved decision, active write collision, conflicting canonical guidance,
stale CAP authority, or material CAP-0005/SLI-0024 drift.

Do not stop or request approval for the bounded runtime selection, its tests,
documentation wording, harmless whitespace, or other inconsequential cleanup
inside the declared scope.

## Required Handoff

Report the exact selection order, changed files, focused/live/aggregate results,
affected receipt, independent review, documentation impact, assumptions, and
residual risks. Confirm that no product API, generated client, learning
behavior, durable state, model authority, provider, or separate AI-mode plan
changed, then leave SLI-0024 ready for deterministic closure.

## Implementation Evidence

- The affected-check runtime now resolves one Python command in explicit
  override, repository `backend/.venv`, and invoking-interpreter order. It
  exports that command to child processes and uses the same command for the
  isolated approved-lesson runner; Node/npm resolution is unchanged.
- The focused verification suite passed 28 tests with three platform-bounded
  skips. New coverage proves explicit override priority, prepared-environment
  preference, portable fallback, child propagation, exact live-runner
  invocation, and—on POSIX—a symlinked `.venv/bin/python` remaining the
  exported and invoked path.
- Live qualification ran with no `PYTHONPATH` and passed all eight isolated
  PostgreSQL 18.4/Python/public-API/generated-client/Chromium scenarios. This
  directly reproduces the clean-fork path that previously selected the wrong
  interpreter.
- Python compilation, packet validation, planning integrity, documentation
  integrity, and Git whitespace checks passed. The aggregate readiness gate
  passed all 29 checks.
- No product source, API/OpenAPI/generated client, fixture, database, UI,
  learning behavior, dependency, durable state, model authority, provider, or
  separate AI-mode plan changed. The existing public API remains available to
  UI and non-UI clients.

## Planning History

- 2026-10-16: Authored just in time after WRK-0088 completion isolated a
  clean-host verifier-runtime defect from the already accepted product
  candidate. The bounded wrapper/test/documentation correction remains inside
  SLI-0024 qualification, preserves exact-candidate isolation and public API
  availability, and adds no decision or lower-level approval gate.
- 2026-10-16: Independent R01 identified that canonicalizing a POSIX virtual-
  environment symlink could collapse it to the base interpreter and defeat
  `pyvenv.cfg` discovery. The bounded correction now makes the selected path
  absolute without dereferencing its final symlink and adds POSIX regression
  coverage for resolution, child export, and live-runner invocation.
