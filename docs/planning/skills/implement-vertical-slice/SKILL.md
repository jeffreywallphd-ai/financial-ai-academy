---
name: implement-vertical-slice
description: Implement or resume one SLI-* vertical slice included in a current approved CAP package through incrementally planned and claimed WRK-* packets. No slice, packet, implementation, or completion approval is required.
---

# Implement Vertical Slice

## MANDATORY FILE-CHANGE GATE - COMPLETE BEFORE ANY EDIT

**Stop before changing any repository file:**

1. Find and read every applicable `AGENTS.md` from the working directory through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Execute their required startup: context routing, authority review, decision readiness, impact analysis, nearest README inspection, and required checks.
4. Read the approved slice, every in-scope packet, canonical sources, contracts, consumers, implementation, tests, and current repository status.
5. Report that this gate is complete. If any source is missing, stale, or conflicting, do not edit.

This skill and its plans are subordinate to repository guidance, the approved CAP package, and separate authority required for external or destructive actions.

## Authorization Gate

Require all of the following:

- a current approved CAP package whose slice manifest contains the target slice;
- a refined slice and next packet that pass deterministic validation;
- no `decision-blocked` artifact or newly unresolved decision;
- dependencies satisfied and no uncoordinated overlapping active write scope.

The CAP approval authorizes conforming delivery of every listed slice. Claim only one packet at a time with `python dev-tools/planning/claim_packet.py claim <packet> --owner <owner> --apply`. The helper verifies the current CAP binding, manifest membership, dependencies, and active-scope safety. Update the planning register in the same change and run the repository planning integrity check with local approvals enabled.

Run `python scripts/check_implementation_gate.py <slice> <packet> [<packet> ...]` before editing. Advice-only requests still do not authorize repository changes; the CAP approval governs delivery only after the user has asked to execute the capability.

## Workflow

1. Complete the mandatory repository gate and authorization gate.
2. Revalidate every packet against current canonical sources and repository state. Return stale packets to `shaping`; never implement through drift.
3. Confirm the current packet and dependency order. Execute one packet at a time unless reciprocal non-overlapping scopes make a set deterministically parallel-safe.
4. Claim the first packet, move the slice to `active`, and update the planning register in the same change.
5. Implement narrowly in dependency order:
   1. decision and domain meaning already accepted;
   2. public contracts or events;
   3. application behavior;
   4. adapters and persistence;
   5. hosts, APIs, jobs, or clients;
   6. interface behavior;
   7. documentation and derived context;
   8. end-to-end and operational qualification.
6. For each packet, run the focused verification and applicable repository gates specified in the packet. Verify relevant denial, malformed, timeout, degraded, replay, stale-version, provenance, parity, accessibility, and theme paths.
7. Record exact evidence and documentation impact. Move the active packet to `verifying`, then finalize it as `complete` only when its required handoff is satisfied. Refine and claim the next packet without an approval prompt after revalidating CAP conformance and dependencies.
8. If a check exposes a missing decision or material CAP change, stop, record the blocker, and route to `review-decision-gates` or CAP reshaping. Bounded packet refinement stays in this workflow.
9. When all packets are complete, move the slice to `verifying` and invoke `verify-and-close-slice` when available.

## Change Controls

- Preserve unrelated user changes and inspect a dirty worktree before editing.
- Do not commit, push, publish, deploy, migrate destructively, access credentials, or mutate production unless separately requested and authorized.
- Do not weaken a guardrail or change an acceptance criterion to make verification pass.
- Do not let AI output become authoritative for protected state without owned deterministic validation.
- Keep contracts, tests, canonical docs, derived context, and evidence synchronized with behavior.

## Required Handoff

Report completed packets, affected boundaries, exact checks and results, documentation impact, assumptions, residual risk, blockers, omitted work, and the next deterministic slice action.

## Stop Conditions

Stop immediately when CAP approval is missing or stale, repository instructions were not read, canonical sources conflict, a decision becomes unresolved, material CAP drift appears, provider/data permission is unclear, active work overlaps, verification fails without a local bounded fix, or external/destructive authority is absent.
