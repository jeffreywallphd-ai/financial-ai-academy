---
name: review-decision-gates
description: Review planned work for unresolved durable decisions, classify readiness, compare viable options in a deterministic table, recommend a path, and create or revise DEC-* decision requests. Use before capability approval, vertical-slice selection, work-packet approval, or implementation when architecture, identity, tenancy, licensing, AI authority, provider, security, recovery, commercial, or external-action choices may be unresolved.
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

## Decision Table Contract

Use [the bundled classification table](assets/decision-classification-table.md) for every review. Include exactly these columns in this order:

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |

- Include one row for every material choice, including nonblocking ready or constrained decisions when they affect the planned outcome.
- For each `proposed` or `decision-required` row, list at least two materially distinct options that satisfy verified constraints. Do not present an option that canonical authority already prohibits as viable.
- For each `ready` or `constrained` row, state the accepted bounded path as the only viable option and cite its canonical authority after the table.
- Keep option labels stable between this table and the corresponding `DEC-*` request.
- Name the recommended option explicitly, or use `Defer` when evidence or qualified review is insufficient.

## Workflow

1. Identify the planned outcome, affected boundaries, contracts, data, users, and external effects.
2. Compare every material choice with current ADRs, readiness records, product/domain authority, risk/security rules, provider terms, and non-goals.
3. Record ready and constrained decisions with their exact authority and accepted bounded path.
4. For each proposed or decision-required item, block dependent artifacts and create or revise one focused `DEC-####-short-name.md` from [the bundled template](assets/decision-request-template.md).
5. Populate the required decision table. Present at least two viable options for every unresolved choice, plus verified constraints, trade-offs, reversibility, affected contracts, and required approvers. Separate facts, assumptions, and inference.
6. Run `python scripts/validate_decision_request.py <artifact>`.
7. Update planning artifacts and the planning register in the same change when required.
8. Group all related unresolved `DEC-*` requests for the same planning boundary into one closed decision set. Present one consolidated table and request one authorized response that identifies the chosen option for every listed decision. Permit explicit item-specific exceptions in that same response.
9. Route the single explicit response to `approve-planned-work`. It records one local decision per `DEC-*` with a shared bundle identifier and never stores approval evidence in tracked files.
10. Promote each approved choice independently into its owning canonical document or ADR and update decision readiness before marking that request complete.

## Compatibility Contract

- Other planning skills consume `decision_gates` as a list of DEC IDs or canonical readiness identifiers.
- Unresolved DEC items require dependent artifacts to use `planning_status: decision-blocked`.
- A decision is resolved only when the ignored local ledger contains an approved decision and `decision_record` points to canonical authority. Tracked files never contain approval or reviewer evidence.
- Approval of a decision does not approve capability framing, slice selection, work packets, or implementation.
- A consolidated response covers only the exact `DEC-*` IDs and option mappings presented. Later or materially revised decisions require a new response.

## Required Output

Return one consolidated decision table with the exact columns `Decision`, `Readiness`, `Viable options`, `Recommendation`, and `Blocking DEC`; then return canonical authority for nonblocking decisions, validation results, affected artifacts, evidence or review still required, and one exact approval request covering every enumerated `DEC-*`. Never omit the viable-options column, even when one accepted path is the only viable option.

## Stop Conditions

Stop when options cannot be compared with verified evidence, qualified review is required, canonical sources conflict, an approver is unidentified, or the choice would silently broaden regulated, commercial, security, privacy, licensing, financial, or AI authority.
