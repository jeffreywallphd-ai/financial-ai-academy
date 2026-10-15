---
name: verify-and-close-slice
description: Verify completed WRK-* packets, reconcile documentation and evidence, and deterministically close an SLI-* within its approved CAP package. No completion approval is requested.
---

# Verify and Close Slice

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions.
4. Read the planning guide/register, slice, packets, canonical sources, contracts, implementation, tests, evidence, and nearest README.
5. Report completion of the gate. Stop on missing or conflicting authority.

Never infer completion from code presence, an agent claim, a passing subset, or exhausted time.

## Workflow

1. Confirm the slice is `verifying`, every required packet is `complete`, and packet claim/base-revision evidence is retained.
2. Run `python scripts/check_completion_gate.py <slice> <packet> [<packet> ...]`.
3. Re-run the focused checks named by every packet, `python dev-tools/agent/check_ready.py`, and all other applicable repository gates. Record the exact command, exit result, relevant output, and any qualification not performed.
4. Compare delivered behavior with capability acceptance, slice scenarios, contracts, decision authority, risk/security posture, and local/cloud or interface parity requirements.
5. Inspect failure and denial evidence, not only success paths. Keep model-quality evaluation separate from deterministic correctness.
6. Reconcile canonical documentation, ADR/readiness entries, derived context, planning register, roadmap state, migrations, and operational instructions made stale by the change.
7. Complete [the evidence checklist](assets/completion-evidence.md) in the slice's Documentation Impact and Completion Evidence section.
8. Report gaps honestly. Return to implementation, packet shaping, or decision review when evidence is incomplete.
9. When every required check and evidence item passes, move the slice to `complete` and update the register. Do not request or record completion approval.
10. If this is the last CAP slice, verify the cumulative CAP acceptance contract and close the CAP deterministically; otherwise route to just-in-time refinement of the next manifest slice.

## Evidence Contract

Completion evidence must identify:

- delivered outcome and affected boundaries;
- packet IDs and acceptance scenarios;
- exact checks and results;
- contract/schema compatibility;
- documentation and migration impact;
- environment or external qualification not performed;
- assumptions, residual risk, known gaps, and follow-up work;
- CAP package conformance and any material-drift assessment.

Do not rewrite expected results after observing failures. Do not claim a check passed unless it ran successfully.

## Required Output

Return a completion decision of `complete` or `not-ready`, with evidence, failures, documentation impact, remaining work, and the next CAP-manifest action.

## Stop Conditions

Stop closure when any packet is incomplete, required verification failed or did not run, canonical sources conflict, a decision is unresolved, documentation is stale, migration/rollback evidence is absent when relevant, residual risk exceeds approved CAP scope, or material CAP drift is detected.
