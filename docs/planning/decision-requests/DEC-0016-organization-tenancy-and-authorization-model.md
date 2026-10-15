---
id: DEC-0016
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: []
decision_gates: []
decision_record: null
---

# Decision Request: Choose the Organization Tenancy and Authorization Model

## Decision Needed

Choose the organization/tenant identity, membership and role model, transactional
and object-storage placement/isolation strategy, lifecycle, and application
authorization inputs for managed profiles.

## Why Now

Instructor review, cohorts, organization administration, managed cloud, and
health/usage views all require a tenant boundary. A database or request shape
must not accidentally become the policy.

## Current Authority and Constraints

ADR-0006 fixes provider-neutral actor/learner context and server-owned sessions
for local modes. Local/cloud profiles share application semantics. Tenant context
must be explicit in cloud transactional and object keys, and clients/providers
cannot choose authoritative membership, role, or permission state.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Shared service with explicit tenant keys and enforced database/object policies | Efficient operations and scaling; supports shared infrastructure with one application core. | Highest policy/testing burden and blast radius for isolation defects. | Identity/membership contracts, request context, every tenant-owned table/object/job, migrations, RLS/policy, backup/export. | Low-medium; later physical isolation is a migration. |
| B. Stronger per-tenant database/schema and object partition boundary | Smaller isolation blast radius and simpler some compliance/recovery operations. | Higher provisioning, migration, pooling, cost, and cross-tenant operations complexity. | Tenant control plane, routing, database/object lifecycle, jobs, migrations, recovery and telemetry. | Medium; consolidation is difficult. |

## Recommendation

Defer until a threat model, expected tenant scale, recovery/portability needs,
and operational prototype compare both. Preserve explicit tenant context and
provider-neutral authorization regardless of physical placement.

## Evidence Required

- Tenant lifecycle, membership/role, invitation, suspension/removal, and data
  ownership journeys.
- Threat model and authorization matrix including confused-deputy and support access.
- Database/object/job isolation prototypes and negative tests.
- Migration, backup/restore, export/deletion, cost, scale, and incident analysis.

## Required Authority

Product/organization authority with identity/security, data architecture,
privacy, operations, recovery, commercial, and accessibility review.

## Decision Record and Promotion

Promote the selected model to an ADR, identity/tenancy/security/data/deployment
architecture, contract policy, and decision readiness.

## Dependent Planning Updates

Reconcile CAP-0022, CAP-0023, CAP-0025, CAP-0028, and CAP-0029.

## Planning History

- 2026-10-15: Captured as the shared organization and managed-service gate.
