---
id: CAP-0028
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0025", "CAP-0027", "CAP-0029"]
decision_gates: ["DEC-0016", "DEC-0017", "DEC-0018", "DEC-0019"]
approval_model: cap-package-v1
slice_ids: ["SLI-0114", "SLI-0115", "SLI-0116", "SLI-0117"]
---

# Capability: Operate a Managed Cloud Service

## Outcome

Qualified operators can deploy and operate the shared application core as a
secure, observable, scalable, recoverable, supportable managed service with
accepted tenant, platform, protection, recovery, delivery, and commercial
boundaries and no contradictory cloud-only domain behavior.

## Users and Value

Organizations and learners need reliable managed access while operators need
repeatable deployment and recovery evidence. Value is observable when the cloud
profile passes explicit security, isolation, migration, availability, recovery,
and support qualification against accepted objectives.

## Scope

### In Scope

- The tenant model from DEC-0016, provider/job posture from ADR-0018, cloud
  platform/encryption/key/backup/availability/recovery posture from DEC-0018,
  and commercial/licensing boundary from DEC-0019.
- Repeatable environment provisioning, deployment, secret/key handling,
  migrations, scaling, health, logs, metrics, alerts, backup/restore, disaster
  recovery, rollback, incident and support runbooks.
- Shared core contracts, migrations, provider ports, portable exports, and
  capability discovery with infrastructure adapters only.
- Controlled qualification and accessible operator status.

### Out of Scope

- Selecting a platform before DEC-0018, unsupported compliance claims,
  contradictory cloud domain logic, live brokerage, arbitrary extensions, or
  treating documentation as SLA evidence.

## Canonical Context

- [Local and Cloud Capability Parity](../../architecture/deployment/local-cloud-capability-parity.md)
- [Community and Commercial Editions](../../product/community-and-commercial-editions.md)
- [Security Architecture](../../security/README.md)
- [Operations Documentation](../../operations/README.md)
- [Decision Readiness](../../adr/decision-readiness.md)
- [ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
- [Provider Admission and Job Delivery](../../architecture/deployment/provider-admission-and-job-delivery.md)
- [CAP-0027](CAP-0027-operate-community-edition-locally.md)
- [CAP-0029](CAP-0029-administer-platform-health-and-usage.md)

## Decision Gates and Constraints

- ADR-0018 supplies the initial provider/job baseline. DEC-0016, DEC-0018, and
  DEC-0019 must still be accepted and promoted before this package can be approved.
- Cloud differences are adapters, scale, availability, managed identity,
  entitlements, providers, operations, analytics, and support—not a domain fork.
- RPO/RTO, availability, encryption, recovery, and compliance statements require
  controlled evidence and cannot be inferred from the community profile.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0114 | Operators provision one accepted cloud profile with tenant-aware configuration, network/trust boundaries, secrets/keys, data stores, and shared-core migrations. | First after all decisions and dependencies. | Unaccepted platform, implicit tenant placement, or cloud domain fork changes the CAP package. | captured |
| SLI-0115 | Operators deploy, scale, upgrade, and roll back application/API, static client, workers, and admitted providers with health and delivery guarantees. | After SLI-0114. | New runtime architecture or unaccepted queue semantics changes the CAP package. | captured |
| SLI-0116 | Operators back up, restore, recover, and respond to incidents against accepted availability and recovery objectives with audit and support evidence. | After SLI-0115. | Claims beyond DEC-0018 or untested compliance guarantees changes the CAP package. | captured |
| SLI-0117 | The managed profile is qualified for isolation, security, migrations, scale, failover, recovery, observability, support, portability, accessibility, and shared-core parity. | Last; depends on SLI-0114 through SLI-0116. | Multi-region or regulatory scope outside the accepted posture changes the CAP package. | captured |

## Capability Acceptance

- Repeatable provisioning and deployment produce an isolated profile whose
  shared domain/application behavior, contracts, and migrations match community.
- Security, key/secret, tenant isolation, delivery, scaling, upgrade/rollback,
  backup/restore, and incident paths meet the accepted objectives in controlled
  qualification.
- Failures produce actionable observability and bounded degradation without
  cross-tenant leakage or silent data loss.
- Service, recovery, availability, commercial, and support claims cite current
  qualification rather than design intent.

- Every slice includes focused failure and anti-rigidity tests; optional scale,
  region, and provider features remain capability-discovered rather than
  mandatory for the accepted reference profile.

## Risks and Non-Goals

Cloud operation combines high-impact security, privacy, cost, legal, and
recovery choices. This CAP does not infer a provider, SLA, compliance status,
licensing model, or tenant boundary and does not fork product semantics.

## Documentation Impact

Delivery will add cloud deployment, tenancy, network/security, key/secret,
storage/jobs, scaling, observability, migrations, backup/recovery, incident,
support, qualification, and limitation documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 25 with manifest SLI-0114 through
  SLI-0117. DEC-0016 through the applicable DEC-0019 boundaries block approval.
- 2026-10-15: DEC-0017 was promoted to ADR-0018; external brokers and provider
  hosts remain outside the accepted PostgreSQL/allowlisted baseline.

