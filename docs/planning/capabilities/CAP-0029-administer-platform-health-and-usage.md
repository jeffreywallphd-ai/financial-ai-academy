---
id: CAP-0029
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0024", "CAP-0025", "CAP-0026"]
decision_gates: ["DEC-0016", "DEC-0017"]
approval_model: cap-package-v1
slice_ids: ["SLI-0118", "SLI-0119", "SLI-0120", "SLI-0121"]
---

# Capability: Administer Platform Health and Usage

## Outcome

An authorized operator can inspect provider, job, storage, model, data, failure,
audit, and edition-appropriate usage and service-limit state; diagnose bounded
incidents; and take only explicit safe administrative actions without gaining
product-domain authority or exposing learner content.

## Users and Value

Operators need actionable service visibility while learners and organizations
need privacy and isolation. Value is observable when health and usage signals
are versioned, attributable, tenant/role-filtered, and connected to runbooks
without raw sensitive payloads or silent automated mutation.

## Scope

### In Scope

- Health, dependency, provider, job, storage, model/data usage, quota/limit,
  failure, audit-reference, freshness, and service-status contracts.
- Tenant/role filtering under DEC-0016 and job/provider semantics under
  DEC-0017, with local and managed profile capability differences.
- Dashboards and APIs for diagnosis, bounded drill-down, correlation, retention,
  export, alert handoff, and explicitly allowlisted safe actions.
- Accessible operator views and privacy/redaction controls.

### Out of Scope

- Billing settlement, employee surveillance, raw learner content, arbitrary
  shell/database access, self-healing that mutates business state, or SLA and
  compliance claims not accepted elsewhere.

## Canonical Context

- [Operations Documentation](../../operations/README.md)
- [Security Architecture](../../security/README.md)
- [AI/ML System Boundaries](../../architecture/ai-ml/ai-ml-system-boundaries.md)
- [CAP-0024](CAP-0024-connect-and-govern-replaceable-providers.md)
- [CAP-0025](CAP-0025-manage-identities-organizations-roles-entitlements.md)
- [CAP-0026](CAP-0026-preserve-provenance-and-accountable-history.md)

## Decision Gates and Constraints

- DEC-0016 establishes tenant/role filtering and organization isolation;
  DEC-0017 establishes provider/job states and delivery meaning.
- Observability records operational facts and bounded audit references, not raw
  prompts, learner content, provider secrets, or duplicate business state.
- Any administrative mutation is explicit, authorized, allowlisted, audited,
  reversible where possible, and never inferred from an alert or model output.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0118 | An authorized operator sees versioned component, dependency, provider, job, storage, and freshness health with bounded diagnostics. | First after dependencies and decisions; establishes health contracts. | Arbitrary shell/database access or raw sensitive payloads changes the CAP package. | captured |
| SLI-0119 | The operator inspects tenant/role-filtered model, data, storage, job, quota, and edition-limit usage with provenance and redaction. | After SLI-0118. | Billing settlement, cross-tenant analytics, or surveillance changes the CAP package. | captured |
| SLI-0120 | The operator correlates failures to audit/runbook evidence and invokes only explicit safe disable, retry, or recovery handoffs with authorization and audit. | After SLI-0119. | Autonomous business-state repair or arbitrary execution changes the CAP package. | captured |
| SLI-0121 | Administration is qualified for accuracy, freshness, failure storms, isolation, redaction, retention, accessibility, safe actions, and local/cloud capability honesty. | Last; depends on SLI-0118 through SLI-0120. | SLA/compliance claims or production mutation outside allowlisted actions changes the CAP package. | captured |

## Capability Acceptance

- Health and usage signals have stable meaning, source, time, freshness,
  dimensions, retention class, redaction, and access policy.
- Cross-tenant, unauthorized, stale, malformed, secret-bearing, and high-volume
  cases fail closed or degrade without obscuring unaffected diagnostics.
- Safe administrative handoffs are explicit, authorized, audited, and bounded;
  dashboards do not become command shells or domain mutation surfaces.
- Accuracy, privacy, accessibility, outage, retention, and profile-difference
  evidence covers direct and failure paths.

- Every slice includes focused failure and anti-rigidity tests so unknown or
  unavailable telemetry isolates its named signal and never blocks unrelated
  operations or requires a universal dashboard dependency.

## Risks and Non-Goals

Operational visibility can leak sensitive data or grow into an unsafe control
surface. This CAP excludes raw learner content, arbitrary execution, billing
settlement, surveillance, unapproved self-healing, and unsupported SLA claims.

## Documentation Impact

Delivery will add health/usage/limit contracts, telemetry taxonomy, redaction and
retention, role/tenant policy, safe-action/runbook boundaries, operator UI,
alerts/export, operations, and verification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 26 with manifest SLI-0118 through
  SLI-0121. DEC-0016 and DEC-0017 block CAP approval and delivery.
