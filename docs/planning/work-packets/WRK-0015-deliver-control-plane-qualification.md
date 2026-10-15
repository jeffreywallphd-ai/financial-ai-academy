---
id: WRK-0015
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0008
capability: CAP-0002
depends_on: ["WRK-0014"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/agent/README.md", "dev-tools/agent/check_ready.py", "dev-tools/control-plane", "dev-tools/planning/README.md", "docs/architecture/assurance/testing-architecture.md", "docs/assurance/known-verification-gaps.md", "docs/context/packs/ai-ml.pack.md", "docs/context/packs/delivery-planning.pack.md", "docs/context/packs/testing-quality.pack.md", "docs/planning/capabilities/CAP-0002-operate-ai-development-control-plane.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0008-qualify-control-plane-safety-and-friction.md", "docs/planning/work-packets/WRK-0015-deliver-control-plane-qualification.md", "docs/standards/ai-agent-development-standards.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: [".local-codex/control-plane/telemetry", "artifacts/control-plane"]
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0015:34f64c2e-e1e5-4242-8717-4403bb451e96
claimed_by: codex-control-plane
claimed_at: 2026-10-15T13:03:01Z
---

# Agent Work Packet: Deliver Control-Plane Qualification

## Objective and Deliverable

Deliver reusable command/path capability grants, output provenance, anonymous
local telemetry and metrics, a deterministic multi-turn regression corpus and
evaluator, readiness integration, documentation, and cumulative CAP closure
evidence without creating a new authority or routine barrier.

## Required Context

Read `AGENTS.md`, `docs/README.md`, routed planning/testing/AI context, CAP-0002,
SLI-0008, every predecessor contract, AI/testing standards and architecture,
the check catalog/executor, readiness runner, affected tests, and nearest
READMEs.

## Decisions and Assumptions

- Capability grants enforce already-authorized local effects; they do not grant
  planning, Git, external, or destructive authority.
- Telemetry is best-effort, local, anonymous, and advisory.
- Deterministic fixtures and hard safety assertions qualify the harness; no
  model or metric can trade away an invariant.
- Generic cores own schemas/algorithms; Financial AI Academy owns catalogs,
  scenario content, thresholds, and adapter mappings.

## In Scope

Grant/provenance/event/report schemas, exact confinement, verification
integration, CLI result provenance and telemetry, metrics/report commands,
scenario corpus/evaluator, fixed readiness checks, docs/assurance, tests, final
slice/CAP evidence, and anti-rigidity/privacy denials.

## Out of Scope

Remote collection/enforcement, dashboards, free-form model graders, prompts or
source capture, identity data, credentials, automatic optimization, external
actions, or new security/approval boundaries.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Reusable control plane | All services/tests | `dev-tools/control-plane/` | Add grants, provenance, telemetry, evaluator, fixtures, tests; integrate verification/CLI |
| Readiness | Fixed runner and guide | Named agent files | Execute corpus and qualification tests |
| Guidance/assurance | Named docs/context | Exact `write_scope` | Document privacy, hard constraints, portability, residual gaps |
| Planning | CAP/SLI/WRK/register | Named artifacts | Synchronize final lifecycle and cumulative evidence |

## Contracts and Interfaces

Versioned contracts named by SLI-0008; stable grant/effect/refusal IDs;
append-only event store; deterministic metric and evaluator ordering; report
confinement; additive receipt/result provenance; explicit forbidden fields.

## Dependencies and Parallel Safety

WRK-0014 is complete. This packet is serial because it wraps shared execution
and qualifies the complete control plane.

## Acceptance Scenarios

The SLI-0008 table is normative. Tests also cover expired/malformed grants,
catalog mismatch, output-digest stability, malformed telemetry isolation,
empty/partial event windows, scenario schema errors, threshold failure, fixture
privacy scanning, and telemetry/report failure not blocking ordinary commands.

## Verification Commands

- `python dev-tools/control-plane/test_qualification.py`
- `python dev-tools/control-plane/evaluate_harness.py`
- `python dev-tools/control-plane/test_operations.py`
- `python dev-tools/control-plane/test_policy.py`
- `python dev-tools/control-plane/test_review.py`
- `python dev-tools/control-plane/test_verification.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/agent/check_ready.py`
- `python dev-tools/agent/check_ready.py --profile ci`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `git diff --check`

## Documentation and Evidence Update

Update the reusable/adapters map, commands, readiness coverage, AI/testing
rules, architecture/assurance/context guidance, planning artifacts, and
cumulative CAP evidence. Generated telemetry/reports remain ignored.

## Stop Conditions

Stop for sensitive event fields, remote transfer, arbitrary grant effects,
nondeterministic authority, safety/metric tradeoff, external/destructive action,
or material CAP drift.

## Required Handoff

Report grant/provenance/event/evaluation contracts, adapter seams, corpus and
thresholds, exact checks, privacy/confinement/anti-rigidity evidence,
documentation/assurance impact, residual gaps, and CAP closure state.

## Planning History

- 2026-10-15: Authored just in time as the final conforming CAP-0002 packet
  after SLI-0007 and WRK-0014 completed.
- 2026-10-15: Delivered exact command/effect/path grants, receipt and CLI
  provenance, anonymous append-only telemetry/metrics, seven tracked multi-turn
  scenarios, evaluator/readiness integration, documentation, and privacy,
  confinement, failure-isolation, and anti-rigidity tests.
