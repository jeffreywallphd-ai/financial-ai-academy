# ADR-0008: Community Learner-Evidence Protection and Recovery

- Status: accepted
- Date: 2026-08-04
- Decision request: [DEC-0004](../planning/decision-requests/DEC-0004-local-learner-evidence-protection-recovery.md)

## Context

CAP-0001 retains learner attempts, responses, scores, completion evidence, identity bindings, and the exact content needed to interpret that evidence. In the community profile, those records span PostgreSQL and object storage on a user-operated host. The platform therefore needs an honest minimum protection and recovery boundary before retained evidence is implemented, without creating an application key-management product or implying managed-service recovery guarantees.

## Decision

Adopt a private-host, user-operated protection and recovery baseline for the community profile.

- The supported community baseline assumes a private, adequately protected host with trusted host administrators. Least-privileged service access and restrictive data-root permissions are required, but the application does not claim protection from a compromised host or privileged local user.
- Data-at-rest confidentiality relies on user-controlled host, filesystem, or volume protection. Recovery sets must be placed on a user-controlled encrypted volume or medium outside the active application data root. The application does not own, escrow, rotate, or recover those encryption keys.
- External secrets remain outside portable configuration and the recovery set. The set may contain credential verifiers and identity bindings needed to recover the same installation, so the entire set is confidential.
- A recovery set is one coordinated, self-describing unit containing a logical PostgreSQL backup, the closed object set needed to interpret retained evidence, nonsecret installation configuration, and a versioned manifest with normalized paths, sizes, digests, compatibility data, exclusions, and finalization state.
- Backup is user-invoked and may be scheduled by host tooling. The application enters maintenance mode, rejects new mutations, proves bounded work is quiescent, captures both stores, validates the staged set, and finalizes it only after success. Copying a running PostgreSQL data directory or an uncoordinated application data root has no recovery claim.
- The community profile makes no recovery-point objective, recovery-time objective, high-availability, offsite-retention, immutability, or ransomware-resilience guarantee. Backup freshness, copy count, physical separation, medium protection, and retention remain user responsibilities.
- Restore accepts only a finalized, compatible set from a trusted source and operator. It validates manifest closure, normalized paths, resource limits, digests, versions, database contents, content provenance, and cross-store evidence references in an empty inactive staging target. It never merges with or restores over a populated installation.
- Restore preserves the installation identity, configured identity mode, learner bindings, evidence ownership, exact lesson and assessment versions, and audit continuity. All restored sessions and recovery credentials are revoked before activation; fresh authentication is required, and excluded external secrets must be supplied separately.
- Live learner evidence remains until the operator explicitly invokes installation-data deletion. Backup-copy retention and deletion remain outside application control and must be disclosed. Restoring an older set can reintroduce data deleted after that set was created.
- File hashes and manifest closure provide internal consistency checks, not cryptographic authenticity against an attacker able to replace the complete set. The initial baseline therefore requires a trusted source and operator.
- Local and managed-cloud profiles preserve the same learner-evidence, identity, content-version, and projection semantics. This ADR does not select managed-cloud encryption, key custody, backup automation, availability, retention, RPO, or RTO.

## Consequences

- CAP-0001 may plan retained evidence against a defined community protection and recovery boundary.
- Community operation remains possible without a commercial key or backup service.
- Maintenance-mode backup intentionally trades availability for simpler cross-store consistency.
- Recovery sets are same-installation disaster-recovery artifacts, not portable learner exports.
- Users must be told that host protection, encrypted backup media, backup freshness, backup-copy deletion, and physical separation are their responsibility.
- Backup and restore tooling, supported-platform permissions, database roles, manifest schemas, compatibility matrices, failure behavior, and user-facing limitations require executable qualification before any support or recovery claim.
- Managed-cloud delivery remains blocked on separate security and operational decisions.

## Alternatives Rejected

- **Application-managed encryption.** It would introduce durable key creation, storage, rotation, loss, recovery, migration, indexing, and support obligations before the first retained-evidence slice.
- **A required external key service.** It would compromise the simple offline community baseline and add provider availability before it is needed.
- **Online cross-store snapshot coordination.** It adds consistency protocol and failure-recovery complexity that the first private-host profile does not require.
- **Application-scheduled backups with stated RPO/RTO.** The community profile cannot prove the necessary scheduling, monitoring, storage, or restore performance.
- **In-place or merge restore.** It risks partial mutation and ambiguous evidence ownership; empty inactive restore keeps the current installation untouched until qualification succeeds.
- **Preserving sessions and recovery credentials.** It could resurrect active or already-used security material after rollback.
- **Application-managed time-based retention and backup pruning.** It broadens the first capability into a retention product while still being unable to control user-held copies.
- **Disposable evidence.** It contradicts CAP-0001's retained-evidence outcome.

## Boundaries

This decision does not accept exact command names, archive formats, manifest fields, database grants, supported operating systems, schedules, migration procedures, portable export semantics, application-managed encryption, signing or remote attestation, automated pruning, managed-cloud controls, or recovery objectives.

This decision authorizes canonical architecture promotion only. It does not select a vertical slice, approve a work packet, authorize implementation, or establish that backup and restore are operationally supported.

## Verification Implications

Before delivery claims the community recovery path:

- prove least-privileged database roles and restrictive data-root behavior on every supported platform;
- prove new writes and jobs are rejected or drained while a coordinated set is captured;
- restore retained attempts, responses, scores, completion evidence, identity bindings, audit continuity, and exact content versions from representative sets;
- recompute projections and reconcile them with append-oriented source evidence;
- reject incomplete, corrupt, malicious, path-escaping, oversized, incompatible, unfinalized, untrusted, or cross-installation sets without changing an existing installation;
- prove sessions and recovery credentials are revoked before activation and excluded secrets remain absent;
- exercise disk-full, permission-denied, interruption, destination-loss, object-mismatch, and database-failure paths;
- confirm diagnostics redact learner responses, credentials, tokens, secrets, raw recovery material, and sensitive paths; and
- run controlled restore drills for each supported community deployment shape and retain versioned evidence.

Until those checks exist, verification coverage remains a gap and recovery remains an accepted design boundary rather than an implemented support claim.

## Supersession

None. Application-managed encryption, recovery-set authentication, online backups, merge restore, application-managed retention, managed-cloud controls, or recovery guarantees require a superseding or profile-specific ADR with migration and qualification analysis.
