---
id: WRK-0022
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0003
updated: 2026-10-15
parent: SLI-0014
capability: CAP-0003
depends_on: ["WRK-0017", "WRK-0018", "WRK-0019", "WRK-0020", "WRK-0021"]
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane/portfolio_harness.py", "dev-tools/control-plane/evaluate_portfolio.py", "dev-tools/control-plane/evals/portfolio-scenarios.json", "dev-tools/control-plane/evals/scenarios.json", "dev-tools/control-plane/financial_academy_portfolio.py", "dev-tools/control-plane/test_portfolio_qualification.py", "dev-tools/control-plane/test_portfolio_allocation.py", "dev-tools/control-plane/test_portfolio_conflicts.py", "dev-tools/control-plane/test_qualification.py", "dev-tools/control-plane/test_file_leases.py", "dev-tools/control-plane/telemetry.py", "dev-tools/control-plane/README.md", "dev-tools/agent/check_ready.py", "docs/standards/testing-and-verification-standards.md", "docs/standards/ai-agent-development-standards.md", "docs/architecture/assurance/testing-architecture.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/context/packs/testing-quality.pack.md", "docs/context/packs/delivery-planning.pack.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/capabilities/CAP-0003-plan-and-orchestrate-capability-portfolios.md", "docs/planning/vertical-slices/SLI-0014-qualify-portfolio-control-plane.md", "docs/planning/work-packets/WRK-0022-deliver-portfolio-control-plane-qualification.md"]
generated_artifacts: ["artifacts/control-plane/portfolio-harness.json"]
base_revision: b1d035252e5a1df2c67d7c3d5360444db9456f0a
claim_id: WRK-0022:9cbf488b-4125-43de-8ef3-52dfdb0764bd
claimed_by: codex-cap-0003
claimed_at: 2026-10-15T14:16:15Z
---

# Agent Work Packet: Deliver Portfolio Control-Plane Qualification

## Objective and Deliverable

Deliver a reusable real-core portfolio evaluator, cumulative repository tests,
privacy-minimized telemetry/readiness integration, adapter/reuse evidence, and
synchronized assurance documentation that closes CAP-0003.

## Required Context

Read and follow `AGENTS.md`, `docs/README.md`, routed planning/testing context,
CAP-0003 and every completed slice/packet, CAP-0002 qualification/harness/
telemetry/provenance code, current portfolio and lease contracts/tests, testing
and AI-agent standards, assurance maps/gaps, readiness runner/CI, concurrent-
work rules, and the nearest README.

## Decisions and Assumptions

- The tracked portfolio corpus executes real project-neutral code; static
  multi-turn flows continue to own command-sequence friction and authority.
- Safety violations fail independently of and before utilization budgets.
- Reports and telemetry retain stable categories, counts, timings, and digests,
  never source/identity payloads.
- Local/CI fixed gates qualify supported repository behavior; hosted and
  multi-host enforcement remains an explicit external gap.

## In Scope

Corpus/evaluator/contracts, cumulative tests, telemetry aggregates, fixed gate
integration, current-repository catalog checks, generic adapter conformance,
multi-turn scenarios, docs/context/assurance reconciliation, and CAP closure.

## Out of Scope

Hosted qualification, cross-host leases, remote telemetry, automatic execution,
branch protection changes, product functionality, or unrelated assurance gaps.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Generic evaluation | Portfolio cores and CAP-0002 harness | New harness/corpus/runner/tests | Exercise actual generic behavior and budgets |
| Telemetry/readiness | Anonymous metrics and fixed checks | Named files | Make portfolio controls continuously qualified |
| Repository qualification | Adapter/catalog/CLI/provenance | Focused tests | Prove current and reusable seams |
| Assurance/docs | Standards, maps, gaps, packs, guides | Named docs | Keep claims and limits accurate |
| Planning | CAP/SLI/WRK/register | Named artifacts | Close slice and capability with evidence |

## Contracts and Interfaces

`portfolio-harness-corpus-v1`, `portfolio-harness-report-v1`, existing portfolio
and file-edit contracts, categorical `control-telemetry-report-v1` extensions,
fixed readiness check IDs, existing provenance validation, and privacy field
deny lists.

## Dependencies and Parallel Safety

WRK-0017 through WRK-0021 are complete. Qualification touches shared harness,
readiness, standards, and planning surfaces and is serial in this branch.

## Acceptance Scenarios

The SLI-0014 table is normative. Tests also cover malformed/duplicate corpus
IDs, safety-over-friction precedence, deterministic report digests, empty and
mixed portfolio states, branch/lease observations, stale prior contracts,
telemetry sink failure, report confinement, generic-module import direction,
and no new approval or broad-lock step.

## Verification Commands

- `python dev-tools/control-plane/test_portfolio_qualification.py`
- `python dev-tools/control-plane/evaluate_portfolio.py`
- `python dev-tools/control-plane/test_portfolio_allocation.py`
- `python dev-tools/control-plane/test_portfolio_conflicts.py`
- `python dev-tools/control-plane/test_portfolio_ordering.py`
- `python dev-tools/control-plane/test_portfolio.py`
- `python dev-tools/control-plane/test_file_leases.py`
- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/control-plane/test_qualification.py`
- `python dev-tools/control-plane/evaluate_harness.py`
- `python dev-tools/planning/check_planning.py`
- `python dev-tools/documentation/check_docs.py`
- `python dev-tools/design/check_design_system.py`
- `python dev-tools/agent/check_ready.py --profile local`
- `python dev-tools/agent/check_ready.py --profile ci`
- `git check-ignore -v .local-codex/control-plane/file-leases.json`
- `git diff --check`

## Documentation and Evidence Update

Record direct evidence, friction budgets, adapter contract/reuse path, fixed
gate inventory, telemetry privacy, local/CI parity, and explicit hosted/multi-
host gaps without copying local approval or reviewer evidence.

## Stop Conditions

Stop for safety-budget tradeoffs, fabricated coverage, sensitive fixtures or
reports, blocking telemetry, repository imports in generic modules, authority
expansion, remote effects, unresolved decisions, or work outside this packet.

## Required Handoff

Report corpus/contracts, direct evidence, budgets, fixed gates, docs/context,
local and CI results, external limits, residual risks, CAP acceptance mapping,
and capability closure.

## Planning History

- 2026-10-15: Authored just in time for final conforming CAP-0003 qualification.
- 2026-10-15: Added allocation/conflict regression assertions to scope after
  final slice refinement changed their expected active and completeness facts;
  no contract or CAP boundary changed.
- 2026-10-15: Added the repository portfolio adapter to scope after terminal-
  state qualification showed descendant aggregation dropping a container's own
  active checkout-branch observation.
- 2026-10-15: Delivered the seven-scenario real-core corpus/evaluator, thirteen
  multi-turn flows, cumulative qualification, telemetry and readiness
  integration, reusable-adapter evidence, and synchronized assurance docs; all
  packet verification commands passed in local and CI profiles.
