# Managed Cloud Deployment Profile

- Status: accepted
- Canonical for: managed multi-tenant system shape

## Components

- The same web, API, and worker application artifacts used by the local profile
- Managed PostgreSQL and object storage
- Managed identity integration and application authorization
- Tenant-aware configuration, entitlements, audit, and administrative controls
- Scalable job execution and provider routing
- Centralized metrics, tracing, logs, backups, recovery, and deployment qualification

## Isolation

- Organization context is established by authenticated request or job context and propagated explicitly.
- Application authorization is authoritative; database row policies and object-key partitioning provide defense in depth.
- Provider credentials, budgets, and data-use permissions are tenant or platform scoped as explicitly configured.
- Premium deployment placement must not create a premium domain-code fork.

Provider-specific hosting, identity, queue, and infrastructure choices remain decision-required until accepted by ADR.

The shared web artifact follows [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md): a React/TypeScript client built as static assets with no required Node production server. A cloud CDN or static host may serve those bytes, but it cannot introduce a cloud-only Node BFF, framework API, or different client contract.

[ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) applies only to the private-host community profile. It does not authorize managed-cloud encryption, key custody, backup automation, retention, availability, RPO, RTO, tenant recovery, or disaster-recovery posture.

Managed identity adapters must produce the same [provider-neutral learner context](../contracts/identity-provider-contract.md) as local modes. Provider claims establish normalized identity inputs; application authorization remains authoritative.

Managed content and object-storage adapters must preserve the same [versioned lesson content-package contract](../contracts/content-package-contract.md) as the local profile. Provider or storage metadata cannot change package identity, version, digest, provenance, assessment ownership, or rendering authority.
