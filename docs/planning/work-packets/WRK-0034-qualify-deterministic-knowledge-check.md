---
id: WRK-0034
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0015
capability: CAP-0001
depends_on: ["WRK-0033"]
decision_gates: []
parallel_safe_with: []
write_scope: ["tests/e2e/approved-lesson", "deployments/local", "apps/web/tests/browser/approved-lesson", "backend/src/financial_ai_academy/modules/assessment/README.md", "apps/web/README.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0015-submit-deterministic-knowledge-check.md", "docs/planning/work-packets/WRK-0034-qualify-deterministic-knowledge-check.md"]
generated_artifacts: []
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0034:ae4a3ab8-8d5d-461e-9bd6-f3b1359f27d0
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:35:35Z
---

# Agent Work Packet: Qualify the Deterministic Knowledge Check

## Objective and Deliverable

Qualify the complete SLI-0015 path on disposable PostgreSQL and a real browser,
reconcile documentation/evidence, and close the slice only when every owning
layer passes.

## Required Context

Read AGENTS.md, routed deployment/testing/security context, CAP-0001,
SLI-0015, WRK-0031 through WRK-0033, the local composition and runner, live
browser suite, module/web/local READMEs, and every gate invoked by setup.

## Decisions and Assumptions

Only PostgreSQL 18.4, loopback single-profile identity, filesystem objects,
same-origin Python static serving, and pinned Chromium are qualified. The
runner must remove its exact disposable container and data root on every path.

## In Scope

Extend the approved-lesson E2E and local qualification for exact definition,
correct/incorrect feedback, retry/idempotency, denial, stale/malformed input,
transaction failure, accessibility, provenance, advisory, architecture,
security, docs, planning, and aggregate readiness. Unsupported deployment
profiles remain explicitly unqualified.

## Out of Scope

Cloud/remote identity, recovery guarantees, projection/history, multiple
assessments, hosted CI enforcement, and any weakening of a failed gate.

## Acceptance Scenarios

- The same-origin app seeds and opens the exact 1.1.0 successor package and its
  immutable Assessment placement, then records and displays correct feedback.
- Context-free access and client-selected authority fail closed; no newer or
  missing version is substituted.
- All focused and cumulative suites, contract generators, static build,
  browser, architecture, security, design, docs, planning, advisory, and
  aggregate readiness gates pass on current inputs.
- Disposable database/container and filesystem state are removed even after a
  failure.

## Verification

Run the live E2E directly, then `npm --prefix apps/web run setup:dev --
--verify-only`, `python dev-tools/agent/check_ready.py`, planning validation,
and diff/status review.

## Stop Conditions

Do not mask raw failures, fabricate cloud/recovery qualification, or weaken an
invariant to reduce friction. Route bounded defects to owning packets/slices.

## Required Handoff

Report exact environment, test counts, generated/current checks, cleanup,
documentation impact, unsupported profiles, residual gaps, and slice closure.

## Verification Progress

- The live same-origin path passed two Chromium scenarios against isolated
  PostgreSQL 18.4 and a temporary filesystem root. The seeded fixture was
  `intro-risk-return@1.1.0` with `risk-return-check-1@1.0.0`; the browser
  submitted the exact immutable reference tuple and displayed the retained,
  deterministic result.
- The complete local workflow passed 162 backend tests, 21 Vitest tests, seven
  focused Chromium scenarios, and two live Chromium/PostgreSQL scenarios.
  OpenAPI and the generated TypeScript client were current, and the production
  web build transformed 98 modules.
- Architecture passed eight fitness functions, security passed ten control
  groups, design validation verified 125 tokens and 56 icons, documentation
  verified 187 Markdown files and catalogs, planning verified 63 artifacts,
  aggregate readiness passed 27 checks, and npm reported zero vulnerabilities.
- The qualification runner removed its exact PostgreSQL container, Compose
  network, and temporary data root after the run. Only the local single-profile
  deployment is qualified; cloud identity, hosted recovery, projection/history,
  and multiple-assessment behavior remain outside this packet.

## Planning History

- 2026-10-15: Captured as the final serial qualification packet for SLI-0015.
- 2026-10-15: Refined immediately before start after UI completion. No new
  durable decision or CAP drift was found.
- 2026-10-15: Full Docker-backed qualification passed and cleaned up all
  disposable state; the packet is ready for deterministic finalization.
