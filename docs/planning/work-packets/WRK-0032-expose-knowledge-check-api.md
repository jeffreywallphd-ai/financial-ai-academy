---
id: WRK-0032
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-cap-0001
updated: 2026-10-15
parent: SLI-0015
capability: CAP-0001
depends_on: ["WRK-0031"]
decision_gates: []
parallel_safe_with: []
write_scope: ["backend/README.md", "backend/src/financial_ai_academy/hosts/api", "backend/src/financial_ai_academy/bootstrap", "backend/src/financial_ai_academy/platform/security/single_profile_policy.py", "backend/tests/integration/api", "backend/tests/unit/identity/test_single_profile_policy.py", "contracts/api/openapi.json", "apps/web/README.md", "apps/web/src/generated/api-client", "docs/security/local-identity-architecture.md", "docs/architecture/assurance/architecture-verification.md", "docs/assurance/known-verification-gaps.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0015-submit-deterministic-knowledge-check.md", "docs/planning/work-packets/WRK-0032-expose-knowledge-check-api.md"]
generated_artifacts: ["contracts/api/openapi.json", "apps/web/src/generated/api-client"]
base_revision: 515c2e16e4458b1305a89acd594085c828fe49ec
claim_id: WRK-0032:0b044c69-a35f-48be-8955-17782c4ab7ec
claimed_by: codex-cap-0001
claimed_at: 2026-10-15T16:29:05Z
---

# Agent Work Packet: Expose the Knowledge-Check API

## Objective and Deliverable

Expose the exact check definition and idempotent submission result through the
protected API and regenerate the reviewed OpenAPI snapshot and TypeScript
client, using only server-resolved learner context.

## Required Context

Read AGENTS.md, the routed repository/planning sources, CAP-0001, SLI-0015,
WRK-0031, ADR-0005 through ADR-0009, the public Assessment and Identity
facades, current API models/error policy, generator, client generator, security
tests, and nearest READMEs before editing.

## Decisions and Assumptions

The existing opaque cookie remains the only learner selector. The API may
return safe presentation and deterministic results but never answer keys,
storage identifiers, provider payloads, or another learner's evidence.

## In Scope

Add strict request/response models, error mapping, permission checks, tests for
missing/tampered context, stale versions, duplicate/conflict behavior, redacted
unexpected failures, and deterministic generated outputs. Do not add UI,
identity selectors, broad assessment types, or a hand-written client.

## Out of Scope

Browser interaction, history/projection, new identity modes, generalized
assessment search, external event delivery, and changes to scoring semantics.

## Contracts and Interfaces

Expose one exact presentation read and one state-changing submission operation
under the placement/assessment resource. Require same-origin policy for the
write, resolve learner context server-side, map domain errors deterministically,
and regenerate OpenAPI and the TypeScript client from validated models.

## Dependencies and Parallel Safety

WRK-0031 is complete. This packet changes shared host/generator surfaces and is
serial with the UI packet.

## Acceptance Scenarios

- An authorized learner reads a presentation without answer-key leakage and
  submits an exact response for deterministic feedback.
- Missing permission/context fails before Assessment is called; client-supplied
  identity fields are schema-rejected.
- Exact retry returns the original result; conflicting key reuse and stale
  definition return stable conflicts with no private detail.
- Unexpected errors are redacted and correlated.
- Two generations produce byte-identical OpenAPI and client outputs.

## Verification

Run focused host integration, OpenAPI/client generation currency, typecheck,
security, architecture, documentation, and planning checks.

## Stop Conditions

Stop for any client-selected identity, answer-key/provider leakage, a new
authorization model, a non-generated client, or change outside SLI-0015.

## Required Handoff

Report endpoints and permissions, generated outputs, denial/redaction tests,
checks, documentation impact, and readiness of WRK-0033.

## Verification Progress

- Reused the existing Assessment endpoint/models implementation, then added
  focused host tests for answer-key non-disclosure, server-resolved learner
  context, strict rejection of client identity fields, stable conflict mapping,
  and unavailable-service denial.
- OpenAPI and the generated TypeScript client are byte-current. The focused API
  and Identity suite passed 39 tests, TypeScript typecheck passed, and the full
  PostgreSQL-backed backend suite passed 162 tests.
- Architecture passed 8 functions, security passed 10 control groups, and
  documentation and planning validation passed. The security policy now names
  identity and result-authority header sets separately while denying their
  union.

## Planning History

- 2026-10-15: Captured as the second serial packet for SLI-0015.
- 2026-10-15: Refined immediately before start after WRK-0031 completed; no
  material CAP change or decision gate was found.
- 2026-10-15: Protected API/client delivery completed with generated-contract,
  denial, redaction, cross-boundary, and cumulative backend evidence.
