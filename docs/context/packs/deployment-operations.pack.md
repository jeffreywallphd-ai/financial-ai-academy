# Context Pack: Deployment and Operations

## Use When

Work affects local/cloud composition, configuration, storage, jobs, secrets, migrations, backup, recovery, readiness, or outages.

## Preserve

- Same domain/application artifacts and contracts in local and cloud profiles
- Same ADR-0009 static React/TypeScript browser artifacts in local and cloud; Python is the production application runtime and Node is build/test tooling only
- Local setup selects exactly one single-profile, built-in, or OIDC identity adapter; populated installations cannot switch without an approved migration
- PostgreSQL transactional behavior in both profiles
- ADR-0018 exact allowlisted packaged adapters and PostgreSQL-backed at-least-
  once jobs preserve idempotency/reconciliation, lease/fencing,
  cancellation/timeout uncertainty, retry, dead-letter, and narrow degradation.
- Community recovery uses a coordinated user-invoked set and empty inactive restore; restored sessions/recovery credentials are revoked and no community RPO/RTO is claimed
- Explicit capability readiness and degraded states
- Portable export and recovery semantics
- No infrastructure-provider assumption without ADR
- The approved-lesson qualification uses one loopback Python API/static process, PostgreSQL 18.4, an isolated filesystem root, deterministic seeding, and exact-resource teardown; Node remains build/test tooling.

## Canonical Sources

- `docs/architecture/deployment/local-open-source-profile.md`
- `docs/adr/ADR-0009-initial-application-framework-runtime-baseline.md`
- `docs/adr/ADR-0008-community-learner-evidence-protection-and-recovery.md`
- `docs/adr/ADR-0006-setup-selectable-learner-identity.md`
- `docs/adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md`
- `docs/architecture/contracts/job-delivery-contract.md`
- `docs/architecture/deployment/provider-admission-and-job-delivery.md`
- `docs/architecture/contracts/identity-provider-contract.md`
- `docs/architecture/deployment/managed-cloud-profile.md`
- `docs/architecture/deployment/local-cloud-capability-parity.md`
- `docs/operations/README.md`
- `docs/operations/community-backup-and-restore.md`
- `docs/operations/provider-and-job-operations.md`

## Stop When

Tenant placement, identity, managed-cloud encryption/recovery objectives, cloud
provider, an external broker, or an out-of-process provider host remains
unresolved.
