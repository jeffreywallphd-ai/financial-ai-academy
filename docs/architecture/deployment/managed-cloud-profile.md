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

