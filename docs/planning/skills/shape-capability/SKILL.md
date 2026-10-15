---
name: shape-capability
description: Shape or revise one complete CAP planning package from accepted product intent, including the coarse plan and sequence for every intended slice. Use before the single CAP approval; do not implement code.
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
7. Enumerate and reserve every intended `SLI-*` in `slice_ids`. Give each slice a coarse observable outcome, dependency/order constraint, and stop boundary; leave detailed slice and packet planning until that work is about to start.
8. Run `python scripts/validate_capability.py <artifact>` from this skill folder.
9. Update the repository planning register in the same change when required.
10. Present the complete package for the single CAP planning approval. Route an explicit human decision to `approve-planned-work`, which records it only in the ignored local ledger and binds it to the package digest and slice manifest.

## State and Approval Contract

- Start new artifacts at `captured` or `shaping`.
- Use `decision-blocked` when any named gate is unresolved.
- Keep approval and reviewer evidence out of the tracked artifact.
- Move to `ready` only when decision gates are resolved and the ignored local ledger contains a current approved CAP package.
- CAP approval authorizes deterministic incremental planning and delivery for every listed slice. It does not authorize material CAP drift or external/destructive action.

## Required Output

Return the artifact path, outcome, scope boundary, complete slice manifest and sequence, decision gates, validation result, register impact, and the one CAP approval requested. If no file change was authorized, return a proposal without editing.

## Stop Conditions

Stop when canonical sources conflict, the outcome combines independent capabilities, product meaning is missing, a regulated or commercial boundary would be selected, provider or data permission is unclear, or approval authority is absent.
