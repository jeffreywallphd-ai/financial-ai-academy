---
name: guide-next-planning-action
description: Recommend the next governed planning action and route to the compatible planning skill. Use for broad prompts such as "what would you suggest we do next?", "what is ready?", "how should we proceed?", "what is blocking us?", or "which planning skill should we use?" Default to read-only guidance and never infer implementation authority.
---

# Guide Next Planning Action

## Repository Guidance Gate

Before inspecting or changing repository planning state:

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their authority, context-routing, decision, and planning instructions.
4. Read the planning guide/register, decision readiness, active roadmaps, relevant artifacts, and current repository status.

**Before this skill or any routed skill changes a file, repeat this as a mandatory file-change gate and report completion.** Stop on missing or conflicting authority.

## Default Behavior

Treat general requests for advice, prioritization, status, or "what next" as read-only. Recommend one next action; do not create artifacts, record approvals, or start implementation unless the user explicitly asks for that additional action.

## Deterministic Routing

Use this precedence:

1. `verify-and-close-slice`: a slice is verifying or awaiting completion acceptance.
2. `implement-vertical-slice`: authorized work is already active and not blocked.
3. `review-decision-gates`: any artifact is decision-blocked or one or more related unresolved DEC requests block progress; route the related set to one consolidated decision table and response.
4. `shape-capability`: a capability is captured, shaping, or needs requested changes.
5. `approve-planned-work`: the next stage is waiting for an explicit human decision; group a closed related `DEC-*` set or one slice's closed `WRK-*` set when eligible.
6. `select-vertical-slice`: an approved capability needs a slice, or slice selection needs revision.
7. `author-agent-work-packet`: an approved slice needs packets, or packet planning needs revision.
8. `approve-planned-work`: the closed slice packet set is plan-approved but still needs one separate slice-wide implementation response.
9. `implement-vertical-slice`: packets are fully approved and ready; recommend implementation but do not start it without a current explicit instruction.
10. `shape-capability`: no planned artifacts exist.

Within one precedence level, choose the lowest stable artifact ID unless repository priority authority specifies another order. When multiple related decisions share one planning boundary, or multiple packets share one selected slice and approval stage, return the complete deterministic member list rather than one arbitrary member. Never use model preference, novelty, or estimated excitement as a tie-breaker.

## Workflow

1. Inspect planning state without modifying it.
2. Run `python scripts/recommend_next.py <planning-root>` when the repository uses compatible frontmatter. The router reads approval state from the ignored local ledger and public lifecycle state from tracked artifacts.
3. Reconcile the script result with accepted roadmap priority, explicit user priority, current decisions, and active work. Canonical authority may invalidate a mechanically eligible action.
4. Select one primary skill and list any prerequisite skill.
5. If the selected skill is installed, invoke it only to the extent authorized by the user. If unavailable, name it and provide the next input it requires; do not silently emulate an implementation workflow.
6. Return [the next-action report](assets/next-action-report.md) fields.

## Compatibility Contract

This router recognizes:

- `CAP-*` capability artifacts;
- `DEC-*` decision requests;
- `SLI-*` vertical slices;
- `WRK-*` work packets;
- the common public planning states and six local ledger stages used by the companion skills.

The companion skills are soft dependencies: this folder remains valid when zipped alone, but routed execution requires the named skill to be installed.

## Required Output

Return current state, recommended next action, selected skill, subject artifact, exact bundle members when applicable, reason, prerequisites, approval required, blockers, and what follows. State explicitly whether the response is advice only.

## Stop Conditions

Stop and ask for direction when priority authority conflicts, multiple artifacts are equally authoritative and consequential, the register disagrees with artifacts, decisions are stale, or the next action would require implementation/external authority not present in the request.
