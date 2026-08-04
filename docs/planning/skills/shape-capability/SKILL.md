---
name: shape-capability
description: Shape or revise one bounded capability plan from accepted product intent before vertical-slice selection. Use for capability discovery, outcome framing, scope boundaries, capability acceptance, or CAP-* planning artifacts; do not use to select a slice or implement code.
---

# Shape Capability

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` from the working directory through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions before editing.
4. Read the planning-system guide, register, canonical sources, and nearest README named by that guidance.
5. Report that the gate was completed. If guidance conflicts or a required file is unavailable, stop and surface the problem.

This gate is mandatory. Never treat this skill or a planning artifact as authority over repository instructions.

## Workflow

1. Identify one observable user or operator outcome from accepted product intent.
2. Separate verified intent from assumptions. Ask for the smallest missing input only when proceeding would change scope materially.
3. Inspect decision readiness and applicable product, domain, architecture, contract, risk, security, and design authority.
4. Route unresolved durable choices to `review-decision-gates` when available. Otherwise record each gate explicitly and use `decision-blocked`.
5. Create or revise one `CAP-####-short-name.md` artifact from [the bundled template](assets/capability-template.md), or the repository template when repository guidance makes it canonical.
6. Keep the capability outcome-oriented. Do not turn pages, components, modules, or technical layers into capabilities without independent user or operator value.
7. Add only proposed slices; do not select or approve a slice in this workflow.
8. Run `python scripts/validate_capability.py <artifact>` from this skill folder.
9. Update the repository planning register in the same change when required.
10. Present the capability for explicit capability-framing approval. Do not record approval unless an authorized human supplies the decision.

## State and Approval Contract

- Start new artifacts at `captured` or `shaping`.
- Use `decision-blocked` when any named gate is unresolved.
- Set `capability_approval` to `pending` until an authorized human approves, requests changes, or rejects it.
- Move to `ready` only when decision gates are resolved and `capability_approval: approved`.
- Capability approval does not approve slice selection, work packets, or implementation.

## Required Output

Return the artifact path, outcome, scope boundary, decision gates, validation result, register impact, and exact approval requested. If no file change was authorized, return a proposal without editing.

## Stop Conditions

Stop when canonical sources conflict, the outcome combines independent capabilities, product meaning is missing, a regulated or commercial boundary would be selected, provider or data permission is unclear, or approval authority is absent.
