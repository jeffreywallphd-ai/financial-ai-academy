---
id: WRK-0015
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0007
capability: CAP-0002
depends_on: ["WRK-0014"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/agent/check_ready.py", "dev-tools/control-plane", "dev-tools/planning/README.md", "docs/context/packs/delivery-planning.pack.md", "docs/context/packs/testing-quality.pack.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0007-close-packet-start-and-bound-recovery-routes.md", "docs/planning/work-packets/WRK-0015-deliver-start-correction-and-maintenance-routes.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: [".local-codex/control-plane/starts", ".local-codex/control-plane/corrections", ".local-codex/control-plane/maintenance"]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0015:0d1555ba-7614-47c7-80cb-839a7651a49c
claimed_by: codex-control-plane
claimed_at: 2026-10-15T12:58:17Z
---

# Agent Work Packet: Deliver Start, Correction, and Maintenance Routes

## Objective and Deliverable

Deliver reusable packet-start, correction-route, and bounded-maintenance cores;
Financial AI Academy adapters; mutation blocking and CLI commands; readiness,
documentation, and comprehensive anti-rigidity/anti-bypass tests.

## Required Context

Read `AGENTS.md`, `docs/README.md`, routed planning/testing context, CAP-0002,
SLI-0007, all predecessor contracts, concurrent-work and testing standards,
affected control-plane code/tests, readiness runner, and nearest READMEs.

## Decisions and Assumptions

- Start closure is deterministic evidence, not another approval.
- Corrections preserve terminal history and route to a new bounded WRK rather
  than reopening or mutating the completed packet.
- Maintenance is a local allowlisted repair session, not a general bypass.
- Project vocabulary, acceptance extraction, risk mapping, and concrete repair
  actions remain adapters outside the reusable cores.

## In Scope

Versioned contracts, confined append-only stores, idempotence/drift checks,
risk route selection, corrective routing, maintenance action registry and
health-gated exit, active-session mutation blocking, CLI/status integration,
readiness allowlist, docs, and focused denial/anti-rigidity tests.

## Out of Scope

Automatic corrective artifact creation, tracked-history rewrite, arbitrary
shell or file editing, remote repair, external/destructive actions, telemetry,
or confinement tokens beyond the registered action boundary.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable control plane | All prior contracts/services/tests | `dev-tools/control-plane/` | Add start/correction/maintenance cores and adapters |
| Readiness | Fixed check inventory | `dev-tools/agent/check_ready.py` | Add operations suite |
| Guidance | Named planning/testing/context files | Exact `write_scope` | Document short path and bounded exceptional routes |
| Planning | SLI/WRK/register | Named artifacts | Synchronize lifecycle and evidence |

## Contracts and Interfaces

Stable `packet-start-manifest-v1`, `correction-route-v1`, and
`maintenance-session-v1`; adapter ports for start context, completed scope, risk,
maintenance handlers, and health; stable refusal codes and one remediation.

## Dependencies and Parallel Safety

WRK-0014 is complete. This packet is serial because it adds exceptional-route
guards to the shared CLI entry point.

## Acceptance Scenarios

The SLI-0007 table is normative. Tests also assert append-only evidence,
concurrent maintenance denial, no command strings, no tracked mutations, health
validation, Windows-safe filenames, and no requirement for approval/full suite
on a low-risk start or in-scope correction route.

## Verification Commands

- `python dev-tools/control-plane/test_operations.py`
- `python dev-tools/control-plane/test_policy.py`
- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/agent/check_ready.py`
- `python dev-tools/agent/check_ready.py --profile ci`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`

## Documentation and Evidence Update

Update the reusable/adapters map, operator commands, short-path and exceptional
route guidance, testing/context requirements, planning lifecycle evidence, and
register. Keep runtime audit records ignored.

## Stop Conditions

Stop for arbitrary repair authority, external/destructive effects, public or
approval/review history mutation, implicit scope widening, new approval layers,
or material CAP drift.

## Required Handoff

Report contracts, adapter boundaries, start/correction/maintenance behavior,
history and mutation-block evidence, exact checks, documentation impact,
remaining gaps, and the next slice action.

## Planning History

- 2026-10-15: Authored just in time as the single conforming SLI-0007 packet
  after SLI-0006 and WRK-0014 completed.
- 2026-10-15: Delivered reusable start, correction, and maintenance cores;
  Financial AI Academy adapters; CLI mutation blocking; readiness integration;
  operational documentation; and focused anti-rigidity/anti-bypass coverage.
  All focused suites plus planning, docs, and both readiness profiles passed.
