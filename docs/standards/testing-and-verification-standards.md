# Testing and Verification Standards

- Status: accepted
- Canonical for: evidence expected from repository changes

## General Rules

- Test the invariant at the layer that owns it.
- Add regression evidence for meaningful defects.
- Verify failure, denial, timeout, malformed input, and degraded-provider behavior where relevant.
- Use deterministic fixtures for financial calculations and independent expected results.
- Separate schema validation, business invariants, authorization, and model-quality evaluation.
- Do not substitute end-to-end tests for focused domain or contract evidence.
- Do not substitute model evaluation for deterministic application tests.

## Change Completion

A change reports:

- focused checks run during implementation,
- applicable architecture, contract, documentation, security, and full-suite gates,
- environment or external qualifications not performed,
- raw failures separately from normalized repository-runner output.

Run `python dev-tools/agent/check_ready.py` as the common repository-support gate. Its command set is a fixed allowlist covering planning integrity, planning-tool behavior, skill compatibility and behavior, prompt-level planning evaluations, documentation integrity, and design-system integrity. Do not replace an affected boundary's focused tests with this aggregate result.

Control-plane changes also require anti-rigidity evidence. Test the shortest
ordinary path and assert that it does not add repeated planning approvals,
mandatory unrelated full-suite runs, manual lifecycle edits, or speculative
recovery artifacts. Denial tests must verify a specific invariant and the
narrowest safe remediation. Risk-selected escalation is correct only when a
fixture demonstrates the triggering impact; safety controls are not removed to
reduce command count.

Routine automated verification uses the tracked affected-check catalog. A fresh
receipt binds the exact submitted candidate, selected command IDs and reasons,
declared input and environment fingerprints, attempt outcomes and timings, and
output digests. Receipts report execution facts; they do not approve work or
decide whether evidence proves an acceptance criterion. Failed, timed-out,
partial, drifted, or stale attempts remain non-qualifying evidence. Result reuse
is disabled while installed executable closure or trusted producer provenance is
unknown.

Independent technical review binds one exact candidate and qualifying receipt.
Self-review is invalid. Adverse findings remain append-only until a later strict
descendant supplies explicit closure evidence; closed unrelated findings are not
reopened merely because another review level begins. A third candidate after two
adverse rounds requires root-cause evidence. Review dispositions are technical
evidence, not a planning, release, merge, or external-action approval.

Control policy uses one stable rule inventory in local and CI profiles. A
profile may change fact availability but not rule meaning: ignored local facts
are reported as `not-evaluated`, never silently passed. Retained machine reports
store stable IDs, dispositions, counts, and digests instead of raw command
output, prompts, absolute local paths, or reviewer content. Read-only operator
status must remain a single command and must not run verification, mutate state,
or introduce an approval.

Packet-start tests must distinguish semantic acceptance/scope drift from routine
history, timestamp, or completion-evidence edits. The low/medium-risk route must
exclude aggregate readiness unless a tracked shared-impact fact selects it.
Completed-work correction tests must preserve terminal history and deny path
escape. Maintenance tests must cover one active session, frozen action IDs,
normal-mutation blocking, failed-action evidence, health-gated exit, and the
absence of arbitrary command execution or manual metadata repair.

Control-plane qualification must deny unknown commands, effects, expired grants,
absolute/traversal paths, and paths outside the exact grant before execution.
Machine provenance binds output digests without embedding payloads. Telemetry
tests scan event keys, isolate malformed records, and prove sink failure is
non-blocking. Multi-turn corpus tests keep hard safety assertions independent of
turn/full-readiness budgets and fail on ambiguous refusals or sensitive fields.

On pull requests, CI supplies the base revision so illegal planning lifecycle transitions are rejected. Required-status enforcement remains a repository hosting configuration and must be verified separately from the workflow file.

## Test Data

Do not commit personal learner information, secrets, provider credentials, restricted datasets, or production payloads. Synthetic and licensed fixtures retain source/creation and permitted-use metadata.
