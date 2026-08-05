# Context Pack: Deployment and Operations

## Use When

Work affects local/cloud composition, configuration, storage, jobs, secrets, migrations, backup, recovery, readiness, or outages.

## Preserve

- Same domain/application artifacts and contracts in local and cloud profiles
- Same ADR-0009 static React/TypeScript browser artifacts in local and cloud; Python is the production application runtime and Node is build/test tooling only
- Local setup selects exactly one single-profile, built-in, or OIDC identity adapter; populated installations cannot switch without an approved migration
- PostgreSQL transactional behavior in both profiles
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
- `docs/architecture/contracts/identity-provider-contract.md`
- `docs/architecture/deployment/managed-cloud-profile.md`
- `docs/architecture/deployment/local-cloud-capability-parity.md`
- `docs/operations/README.md`
- `docs/operations/community-backup-and-restore.md`

## Stop When

Tenant placement, identity, queue delivery, managed-cloud encryption/recovery objectives, or cloud provider remains unresolved.
