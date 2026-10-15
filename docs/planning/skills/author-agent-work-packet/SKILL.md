---
name: author-agent-work-packet
description: Create or revise a bounded WRK-* packet immediately before that work starts, within a refined SLI-* and current approved CAP package. Define exact scope, dependencies, contracts, checks, and stop conditions without requesting packet approval.
---

# Author Agent Work Packet

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions.
4. Read the planning guide/register, CAP-authorized parent slice, canonical sources, contracts, consumers, tests, and nearest README.
5. Report completion of the gate. Stop on missing or conflicting authority.

No packet may outsource a product, architecture, risk, or approval decision to its implementing agent.

## Packet Boundary

Define one packet as the smallest change that:

- produces one observable technical or user-facing result;
- has its own focused verification cycle;
- can receive an independent review decision;
- has one owner and a bounded write scope;
- leaves the repository coherent if completed before later packets.

Fold scaffolding, documentation, and configuration into the packet whose deliverable needs them. Split work only when a reviewer could accept one result and reject the other.

## Workflow

1. Confirm the parent `SLI-*` is in a current approved CAP package, is deterministically ready, and has no unresolved decision gate.
2. Map the boundary path from domain and contract through application, adapters, hosts/clients, interface, documentation, and verification.
3. Identify accepted inputs and outputs between packets before declaring parallel work.
4. Create each `WRK-####-short-name.md` from [the bundled template](assets/work-packet-template.md), or the repository-owned template when canonical.
5. Specify exact in-scope and out-of-scope behavior, files to inspect, repository-relative `write_scope`, generated artifacts, contract impact, dependencies, relevant failure scenarios, executable checks, documentation impact, and stop conditions.
6. Mark packets parallel-safe only when they do not overlap decisions, schemas, migrations, generated artifacts, write scopes, or ownership. Declare reciprocal `parallel_safe_with` references.
7. Run `python scripts/validate_work_packet.py <artifact>` for every packet.
8. Update the parent slice and planning register in the same change when required.
9. Mark a packet `ready` after validation. Author later packets just in time as dependencies become concrete; do not request a planning or implementation approval.

## Authority and State Contract

- New packets use `planning_status: shaping`.
- `ready` requires deterministic validation, resolved decision gates, and conformance to the current approved CAP package.
- `active` requires a successful bounded claim against the current CAP package, satisfied dependencies, and no ownership collision.
- Activation records `base_revision`, `claim_id`, `claimed_by`, and `claimed_at`; authoring leaves those claim fields null.
- Packet decomposition, exact write scope, and implementation tactics may be refined without approval when they remain within the CAP and slice contracts.
- Material CAP drift returns the CAP package to shaping. External or destructive actions retain separate action authority.

## Required Output

Return packet paths, dependency order, parallel-safe groups, contracts between packets, validation results, remaining deterministic gates, and CAP conformance.

## Stop Conditions

Stop when the CAP package is unapproved or stale, the slice is outside its manifest, a packet spans unrelated outcomes, expected interfaces are unknown, checks are not executable, write scopes overlap active work, a durable choice remains unresolved, material CAP drift appears, or the plan would authorize external/destructive action implicitly.
