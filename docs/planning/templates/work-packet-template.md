---
id: WRK-0000
kind: work-packet
planning_status: captured
authority: noncanonical
owner: unassigned
updated: YYYY-MM-DD
parent: SLI-0000
capability: CAP-0000
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: []
generated_artifacts: []
base_revision: null
claim_id: null
claimed_by: null
claimed_at: null
---

# Agent Work Packet: Short Objective

## Objective and Deliverable

Give one implementation objective and the observable result the agent must hand back.

## Required Context

Prominently require the implementing agent to read and follow every applicable `AGENTS.md` and repository-root `docs/README.md` before changing files. List the baseline pack, one primary pack, any necessary adjacent pack, and the exact canonical sources, contracts, consumers, tests, and nearest README to inspect.

## Decisions and Assumptions

List accepted decisions that authorize the approach. Record bounded assumptions that do not select durable policy. Every unresolved material choice belongs under Stop Conditions and blocks readiness.

## In Scope

- Exact behavior and boundaries the agent may change

## Out of Scope

- Adjacent behavior, cleanup, refactoring, publication, deployment, or policy choices not authorized

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |

Include public contracts, owning module, consumers, persistence, clients, interface, tests, canonical docs, and derived context when applicable. File lists guide inspection and do not override discovered impact.

## Contracts and Interfaces

Name exact inputs produced for later packets and exact accepted contracts consumed from earlier packets.

## Dependencies and Parallel Safety

Name prerequisite packets or accepted contracts. Explain why concurrent packets cannot race on decisions, schemas, generated artifacts, migrations, or files.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Success |  |  |  |  |
| Relevant denial or failure |  |  |  |  |

Include only applicable malformed-input, unauthorized, replay, stale-version, degraded-provider, local/cloud, provenance, accessibility, responsive, and light/dark scenarios.

## Verification Commands

List exact focused checks first, then applicable contract, architecture, documentation, security, design-system, build, and full-suite gates. Identify external qualification that cannot run locally.

## Documentation and Evidence Update

List canonical sources, ADR/readiness entries, derived packs, register state, and completion evidence that must remain synchronized.

## Stop Conditions

Stop and return the packet to `shaping` or `decision-blocked` when canonical sources conflict, a decision is not ready, provider or data permission is unclear, implementation requires a breaking contract or new policy, write scope materially overlaps another active packet, verification exposes an architecture gap, or external authority is missing.

## Required Handoff

Report the outcome, affected boundaries, exact checks and results, documentation impact, assumptions, residual risks, unresolved decisions, and any work deliberately left out.

## Planning History

Record public packet state and claim changes. Planning, implementation, and scoped-authority evidence remains only in the ignored local ledger.
