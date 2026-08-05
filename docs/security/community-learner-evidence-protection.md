# Community Learner-Evidence Protection

- Status: accepted
- Canonical for: community-profile learner-evidence threat and protection boundary
- Decision: [ADR-0008](../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)

## Supported Boundary

The community profile supports retained learner evidence only on a private, adequately protected host whose administrators are trusted. PostgreSQL, object storage, installation metadata, and bounded operation state live under an explicitly documented application data root with restrictive supported-platform permissions and least-privileged process access.

This boundary does not protect data from a compromised host, malware running with sufficient privilege, a hostile administrator, or an improperly shared machine. Single-profile identity remains loopback-default and private-host only; built-in or OIDC identity does not turn the community profile into a qualified public multi-tenant service.

## Protected Assets

| Class | Examples | Required treatment |
| --- | --- | --- |
| Learner evidence | attempts, responses, scores, completion evidence, timestamps, learner-state projections | least-privileged PostgreSQL access; recovery coverage; no ordinary diagnostic payloads |
| Identity and security state | installation identity, identity mode, learner bindings, credential verifiers, sessions, recovery state, security audit evidence | confidential recovery handling; restored sessions and recovery credentials revoked before activation |
| Content integrity | exact lesson and assessment versions, packages, sources, provenance, and digests | closed recovery-set coverage or deterministic reference; revalidation during restore |
| Operational compatibility | application, schema, migration, contract, backup-format, and capability versions | self-describing manifest and fail-closed compatibility checks |
| External secrets | database, OIDC, market-data, and model-provider secrets; plaintext credentials; raw recovery codes | resolve outside portable configuration; never include secret values in a recovery set |

## Required Controls

- Keep PostgreSQL private to the local/container network and use distinct, least-privileged application and backup/restore roles.
- Mount only the required data paths into API and worker processes. Web clients, content packages, and providers receive no direct filesystem or database access.
- Resolve secrets through the host secret boundary; portable configuration and recovery manifests carry references or capability requirements only.
- Treat every recovery set as confidential because it may contain learner evidence, identity bindings, and credential verifiers.
- Require an operator-selected encrypted host volume or encrypted backup medium outside the active data root. The application does not hold or recover its key.
- Treat restore input as untrusted data even when the source is trusted: validate path normalization, manifest closure, file type and size limits, digests, supported versions, database content, and content provenance before activation.
- Allow only empty-target, inactive staging restores. Never silently merge with or overwrite a populated installation.
- Revoke all restored sessions and recovery credentials before startup and require fresh authentication.
- Emit allowlisted operation phase, count, version, and redacted-target diagnostics; never emit responses, credential material, tokens, secrets, raw recovery data, or sensitive filesystem paths.
- Preserve the exact evidence, identity, content-version, projection, and audit semantics defined by the shared core.

## Residual Risks and User Disclosures

- Host administrators and sufficiently privileged processes remain trusted.
- User-controlled encryption is only as strong as the selected host or backup-medium configuration and key handling.
- Manifest hashes detect internal inconsistency but do not authenticate a complete set replaced by an attacker.
- User invocation provides no freshness guarantee; the community profile has no RPO or RTO.
- One attached copy is not an offsite, immutable, or ransomware-resilient backup.
- Application deletion cannot erase recovery copies outside application control, and restoring an older copy can reintroduce deleted records.
- Loss of an excluded external secret can leave a restored provider unavailable.
- Corrupt, incompatible, incomplete, or missing recovery sets can make recovery impossible.

## Status of Evidence

The threat boundary is accepted. No backup or restore tool, permission profile, manifest schema, compatibility matrix, controlled restore drill, or recovery guarantee is qualified merely by this document. Delivery must satisfy the [community backup and restore qualification](../operations/community-backup-and-restore.md) before claiming operational support.

Managed-cloud encryption, key custody, backup automation, availability, retention, RPO, and RTO remain outside this boundary and require separate decisions.
