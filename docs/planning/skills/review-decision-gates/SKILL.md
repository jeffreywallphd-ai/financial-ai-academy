---
name: review-decision-gates
description: Review planned work for unresolved durable decisions, classify decision readiness, and create or revise DEC-* decision requests. Use before capability approval, vertical-slice selection, work-packet approval, or implementation when architecture, identity, tenancy, licensing, AI authority, provider, security, recovery, commercial, or external-action choices may be unresolved.
---

# Review Decision Gates

## Mandatory Repository Entry Gate

**Before changing any repository file, stop and complete this gate:**

1. Find and read every applicable `AGENTS.md` through the repository root.
2. Read the repository-root `docs/README.md` when it exists.
3. Follow their startup, authority, routing, editing, decision, and verification instructions.
4. Read the decision-readiness register, planning guide, affected canonical sources, and nearest README before editing.
5. Report completion of the gate. Stop on missing or conflicting authority.

This skill identifies and routes decisions. It never supplies human or organizational approval.

## Deterministic Classification

Classify each material choice as:

- `ready`: accepted authority fully determines the choice within scope;
- `constrained`: accepted authority permits only a named bounded path;
- `proposed`: direction exists but cannot authorize implementation;
- `decision-required`: materially different viable choices remain.

Treat constrained work outside its accepted boundary as decision-required. Treat missing provider terms, legal review, security posture, or external authority as decision-required.

## Workflow

1. Identify the planned outcome, affected boundaries, contracts, data, users, and external effects.
2. Compare every material choice with current ADRs, readiness records, product/domain authority, risk/security rules, provider terms, and non-goals.
3. Record ready and constrained decisions with their exact authority.
4. For each proposed or decision-required item, block dependent artifacts and create or revise one focused `DEC-####-short-name.md` from [the bundled template](assets/decision-request-template.md).
5. Present viable options, verified constraints, trade-offs, reversibility, affected contracts, and required approvers. Separate facts, assumptions, and inference.
6. Run `python scripts/validate_decision_request.py <artifact>`.
7. Update planning artifacts and the planning register in the same change when required.
8. Request an authorized decision. Do not set `decision_approval: approved` from agent judgment or another planning artifact.
9. After approval, require promotion into the owning canonical document or ADR and update decision readiness before marking the request complete.

## Compatibility Contract

- Other planning skills consume `decision_gates` as a list of DEC IDs or canonical readiness identifiers.
- Unresolved DEC items require dependent artifacts to use `planning_status: decision-blocked`.
- A decision is resolved only when `decision_approval: approved`, approver and date are present, and `decision_record` points to canonical authority.
- Approval of a decision does not approve capability framing, slice selection, work packets, or implementation.

## Required Output

Return the classification table, blocking DEC IDs, canonical authority for nonblocking decisions, validation results, affected artifacts, and exact approval requested.

## Stop Conditions

Stop when options cannot be compared with verified evidence, qualified review is required, canonical sources conflict, an approver is unidentified, or the choice would silently broaden regulated, commercial, security, privacy, licensing, financial, or AI authority.
