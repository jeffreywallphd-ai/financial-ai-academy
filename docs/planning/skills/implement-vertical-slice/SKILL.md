---
name: implement-vertical-slice
description: Implement or resume one approved SLI-* vertical slice through its authorized WRK-* packets. Use only when slice selection, packet planning, and separate implementation activation approvals are recorded and the user currently asks to implement; applies to repository file changes, tests, contracts, documentation, and verification. Do not trigger from advice-only or "what next" prompts.
---

# Implement Vertical Slice

## MANDATORY FILE-CHANGE GATE - COMPLETE BEFORE ANY EDIT

**Stop before changing any repository file:**

1. Find and read every applicable `AGENTS.md` from the working directory through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Execute their required startup: context routing, authority review, decision readiness, impact analysis, nearest README inspection, and required checks.
4. Read the approved slice, every in-scope packet, canonical sources, contracts, consumers, implementation, tests, and current repository status.
5. Report that this gate is complete. If any source is missing, stale, or conflicting, do not edit.

This skill and its plans are subordinate to repository guidance and current user authority.

## Authorization Gate

Require all of the following:

- a current explicit user instruction to implement this named slice or packets;
- `selection_approval: approved` on the parent slice;
- `planning_approval: approved` on every packet to execute;
- `implementation_approval: approved` with approver, date, and scoped `implementation_authority`;
- no `decision-blocked` artifact or newly unresolved decision;
- dependencies satisfied and no uncoordinated overlapping active write scope.

Claim each packet with `python dev-tools/planning/claim_packet.py claim <packet> --owner <owner> --authority <implementation_authority> --confirm-current-instruction --apply` before implementation. Update the planning register in the same change and run the repository planning integrity check. The claim records the base revision and exclusive ownership evidence; it does not replace the approval gates above.

A general request for advice, planning, prioritization, review, or "what next" is not implementation authority. Run `python scripts/check_implementation_gate.py <slice> <packet> [<packet> ...]` before editing.

## Workflow

1. Complete the mandatory repository gate and authorization gate.
2. Revalidate every packet against current canonical sources and repository state. Return stale packets to `shaping`; never implement through drift.
3. Confirm the exact packet order. Run packets concurrently only when their accepted interfaces and write scopes are explicitly independent.
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
7. Record exact evidence and documentation impact. Mark a packet `complete` only when its required handoff is satisfied.
8. If a check exposes a missing decision or scope expansion, stop, record the blocker, and route to `review-decision-gates` or packet reshaping.
9. When all packets are complete, move the slice to `verifying` and invoke `verify-and-close-slice` when available.

## Change Controls

- Preserve unrelated user changes and inspect a dirty worktree before editing.
- Do not commit, push, publish, deploy, migrate destructively, access credentials, or mutate production unless separately requested and authorized.
- Do not weaken a guardrail or change an acceptance criterion to make verification pass.
- Do not let AI output become authoritative for protected state without owned deterministic validation.
- Keep contracts, tests, canonical docs, derived context, and evidence synchronized with behavior.

## Required Handoff

Report completed packets, affected boundaries, exact checks and results, documentation impact, assumptions, residual risk, blockers, omitted work, and the completion acceptance still required.

## Stop Conditions

Stop immediately when authorization is incomplete, repository instructions were not read, canonical sources conflict, a decision becomes unresolved, scope or contract meaning drifts, provider/data permission is unclear, active work overlaps, verification fails without a local bounded fix, or external/destructive authority is absent.
