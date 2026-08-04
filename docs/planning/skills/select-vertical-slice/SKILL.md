---
name: select-vertical-slice
description: Compare candidate increments and select one small end-to-end vertical slice for an approved capability. Use for vertical selection, slice scoring, SLI-* creation, sequencing the next observable increment, or deciding which capability slice should be planned next; do not use for implementation.
---

# Select Vertical Slice

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions.
4. Read the planning guide/register, parent capability, decision readiness, affected canonical sources, and nearest README.
5. Report completion of the gate. Stop on missing or conflicting authority.

Never select a slice from vision alone. Require a bounded capability and current decision review.

## Eligibility Gate

A candidate is eligible only when it:

- produces observable user or operator value;
- crosses the minimum necessary boundaries end to end;
- has no unresolved proposed or decision-required choice;
- has identifiable contracts, inputs, outputs, and owning modules;
- can be verified independently;
- is small enough for bounded work packets;
- does not require unauthorized external, destructive, credentialed, or production action.

Route an ineligible candidate to `review-decision-gates` or `shape-capability` as appropriate.

## Deterministic Selection

Score each eligible candidate from 0 to 2 on:

1. observable value;
2. end-to-end completeness;
3. decision readiness;
4. contract clarity;
5. dependency independence;
6. verification observability;
7. reversibility and bounded risk.

Recommend the highest total. Break ties by fewer dependencies, then lower irreversible risk, then stable candidate ID. Preserve the full score table and explain every score; never manipulate criteria to favor a preferred solution.

## Workflow

1. Confirm the parent capability has explicit capability-framing approval.
2. Enumerate at least two candidates when materially different increments exist. State when only one viable candidate exists.
3. Apply the eligibility gate before scoring.
4. Score eligible candidates and identify dependencies that must precede selection.
5. Create or revise one `SLI-####-short-name.md` from [the bundled template](assets/vertical-slice-template.md), or the repository-owned template when canonical.
6. Define the boundary path, affected contracts/data, acceptance scenarios, rollback needs, and proposed work-packet seams.
7. Run `python scripts/validate_vertical_slice.py <artifact>`.
8. Update the planning register when required.
9. Request explicit slice-selection approval. Do not record approval from agent recommendation alone and do not begin packet authoring or implementation.

## Compatibility Contract

- Consume an approved `CAP-*` parent and resolved `decision_gates`.
- Produce one `SLI-*` artifact with `selection_approval` and `completion_approval` metadata.
- Use `decision-blocked` whenever a required DEC item is unresolved.
- Move to `ready` only after authorized `selection_approval: approved`.
- Selection approval does not approve work packets or implementation.

## Required Output

Return candidate eligibility, score table, recommended slice, rejected alternatives, dependencies, decision gates, validation result, and the exact selection approval requested.

## Stop Conditions

Stop when the capability is unapproved, candidates cannot produce independent value, scoring depends on missing evidence, ownership or contracts are ambiguous, a decision gate is unresolved, or the proposed slice is actually a horizontal layer or multi-slice program.
