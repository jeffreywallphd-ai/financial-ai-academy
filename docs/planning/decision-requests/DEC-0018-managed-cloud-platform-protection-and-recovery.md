---
id: DEC-0018
kind: decision-request
planning_status: captured
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["DEC-0016", "DEC-0017"]
decision_gates: []
decision_record: null
---

# Decision Request: Choose the Managed-Cloud Reference Protection and Recovery Profile

## Decision Needed

Choose the first managed-cloud reference platform and its network, compute,
database, object, encryption/key, backup, availability, recovery, region, and
service-objective baseline.

## Why Now

CAP-0028 cannot qualify a managed service or state RPO/RTO and availability
without a concrete platform profile. Community recovery intentionally supplies
no cloud authority.

## Current Authority and Constraints

The shared core, Python API/static client, PostgreSQL plus object/analytical
store responsibilities, and provider ports are fixed. Managed-cloud platform,
encryption/keys, backups, availability, RPO/RTO, and recovery are
decision-required and need controlled evidence.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Single-region multi-zone managed services baseline | Lower operational complexity while supporting managed database/object storage, KMS, zone resilience, backups, and bounded recovery objectives. | Region-level disaster recovery is manual or slower; provider coupling and egress remain. | Deployment adapters, keys/secrets, network, storage, backup/restore, failover, observability and support. | Medium; a second region can be added, but platform migrations are costly. |
| B. Multi-region managed baseline | Stronger regional resilience and potentially tighter recovery objectives. | Much higher data consistency, residency, cost, failover, test, and operational complexity. | Global routing, replicated stores, keys, migrations, conflict/failover, backup and incident operations. | Low-medium; commitments and data placement persist. |

## Recommendation

Defer the final platform/profile until tenant scale, data residency, target
objectives, support capacity, and total-cost evidence are reviewed. Option A is
the default hypothesis for qualification, not implementation authority.

## Evidence Required

- Candidate platform/service comparison and current support constraints.
- Threat model, encryption/key rotation, network and admin-access design.
- Backup/restore and zone/region failure prototypes with measured recovery.
- Availability/RPO/RTO, residency, cost, capacity, incident, and exit/portability analysis.

## Required Authority

Product/service authority with cloud architecture, security/privacy, operations,
recovery, data, cost, legal/residency, and support review.

## Decision Record and Promotion

Promote the accepted reference profile and measured objectives to an ADR,
deployment/security/operations architecture, runbooks, and decision readiness.

## Dependent Planning Updates

Reconcile CAP-0028 and cloud portions of CAP-0025, CAP-0027, and CAP-0029.

## Planning History

- 2026-10-15: Captured while shaping the managed-cloud capability.

