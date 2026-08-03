# Context Pack: Deployment and Operations

## Use When

Work affects local/cloud composition, configuration, storage, jobs, secrets, migrations, backup, recovery, readiness, or outages.

## Preserve

- Same domain/application artifacts and contracts in local and cloud profiles
- PostgreSQL transactional behavior in both profiles
- Explicit capability readiness and degraded states
- Portable export and recovery semantics
- No infrastructure-provider assumption without ADR

## Canonical Sources

- `docs/architecture/deployment/local-open-source-profile.md`
- `docs/architecture/deployment/managed-cloud-profile.md`
- `docs/architecture/deployment/local-cloud-capability-parity.md`
- `docs/operations/README.md`

## Stop When

Tenant placement, identity, queue delivery, encryption, recovery objectives, or cloud provider remains unresolved.

