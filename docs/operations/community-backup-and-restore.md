# Community Backup and Restore

- Status: accepted design; implementation and qualification pending
- Canonical for: community-profile recovery workflow and support-claim boundary
- Decision: [ADR-0008](../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)

## Operational Promise

The community profile is designed for a user-invoked, maintenance-mode recovery backup and an empty-target restore. Host scheduling may invoke the eventual backup operation, but the application does not promise that a schedule ran, that a particular recovery point exists, or that recovery will complete within a particular time.

A disaster-recovery set restores the same installation. It is not a portable learner export and is not a migration mechanism between populated installations.

## Recovery Set

A finalized set must be self-contained for its declared scope and include:

- one internally consistent logical PostgreSQL backup;
- the closed application-controlled object set needed to interpret retained learner evidence;
- nonsecret installation configuration;
- a versioned manifest describing installation and identity mode, application/schema/migration/contract versions, normalized entries, byte sizes, digests, exclusions, required external secret references, quiescence evidence, validation results, and finalization state; and
- an unambiguous finalization marker written only after validation succeeds.

The set may contain credential verifiers and identity bindings required for same-installation recovery. It must never contain plaintext credentials, provider or API secrets, client cookies, raw recovery codes, or application-held encryption keys.

## Backup Workflow Contract

1. Authenticate local operator authority and acquire an exclusive operation lock.
2. Preflight destination separation, permissions, available space, version support, and acknowledgement that the destination is on a user-controlled encrypted volume or medium outside the active data root.
3. Enter a visible maintenance state, reject new mutations, and drain or safely cancel bounded application and worker activity. Abort if quiescence cannot be proven.
4. Create a logical PostgreSQL backup with a bounded backup role while the maintenance boundary remains active.
5. Copy the exact object set needed for evidence and content-version resolution.
6. Write nonsecret configuration and the manifest into a newly created staging set.
7. Validate manifest closure, paths, sizes, digests, versions, database metadata, content/package provenance, and cross-store references.
8. Atomically finalize the set only after validation passes, then leave maintenance mode and report a redacted result.

An interrupted or failed operation must leave the running source unchanged and must not present its staging output as a valid recovery set. Direct copies of a running database or application data root are unsupported.

## Restore Workflow Contract

1. Require an empty inactive target, explicit operator confirmation, exclusive operation lock, required external secret references, and a trusted recovery-set source.
2. Preflight finalization state, format and application compatibility, normalized paths, manifest closure, resource limits, digests, required space, and target emptiness before database mutation.
3. Restore into isolated staging with network listeners, scheduled jobs, providers, and ordinary workers disabled.
4. Restore PostgreSQL and objects, then run bounded schema and contract migrations only when the declared compatibility policy permits them.
5. Validate installation identity and mode, learner bindings, append-oriented evidence, exact lesson and assessment versions, object references, package digests and provenance, audit continuity, and projection reconciliation.
6. Revoke every restored session and recovery credential; confirm excluded secret values are absent and require fresh authentication.
7. Activate the restored target only after all qualification checks pass. On failure, keep it inactive, preserve diagnostic evidence, and leave any existing installation unchanged.

Restore never merges data, restores in place over a populated target, silently changes identity mode, or substitutes newer content for the versions referenced by retained evidence.

## User Responsibilities and Limitations

- Choose and protect the host/volume encryption and backup-medium key.
- Invoke or independently schedule backups and verify their completion.
- Keep enough copies, separation, and retention for the user's risk tolerance.
- Protect, rotate, and resupply excluded external secrets.
- Test recovery after material version, platform, configuration, or storage changes.
- Explicitly delete obsolete backup copies when retention is no longer desired.

The community profile makes no RPO, RTO, availability, offsite, immutability, authenticity, or ransomware-resilience claim. Restoring an older set can roll back changes and reintroduce data deleted after the set was created.

## Qualification Required Before Support Claims

Executable evidence must cover:

- restrictive data-root permissions and least-privileged database roles on every supported platform;
- coordinated quiescence and rejection of concurrent writes/jobs;
- representative cross-store restore and projection reconciliation;
- exact content, assessment, provenance, and identity continuity;
- session and recovery-credential revocation plus external-secret exclusion;
- corruption, incompleteness, malicious paths, resource exhaustion, incompatible versions, cross-installation input, and unfinalized sets;
- disk-full, permission, interruption, destination-loss, database, and object-store failures;
- diagnostic redaction and actionable bounded failure reporting; and
- controlled end-to-end restore drills across every supported community deployment shape.

Until this evidence exists and is reviewed, the workflow is an accepted design contract, not an implemented or supported backup product.
