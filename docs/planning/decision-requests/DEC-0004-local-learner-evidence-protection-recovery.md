---
id: DEC-0004
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-08-04
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md
---

# Decision Request: Set the Local Learner-Evidence Protection and Recovery Baseline

## Decision Needed

Choose the bounded protection, key-management, backup, restore, and recovery posture required before CAP-0001 may retain learner attempts and completion evidence in the community deployment profile.

## Why Now

Candidate C promises that an individual learner can close and reopen a lesson without losing evidence. That requires durable storage behavior and honest recovery expectations. Implementing persistence first would silently choose how learner data is protected, where keys or credentials live, what backup includes, and whether any recovery objective is claimed.

## Current Authority and Constraints

- The [local profile](../../architecture/deployment/local-open-source-profile.md) places local data under a documented application data root and includes it in backup/export workflows.
- The [data architecture](../../architecture/data/data-architecture.md) uses PostgreSQL for transactional evidence and projections, with learner data receiving explicit classification, access, and retention policy.
- [Security and privacy standards](../../standards/security-and-privacy-standards.md) require least privilege, data minimization, explicit trust boundaries, safe diagnostics, retention, rollback, and an accepted decision for encryption.
- [Operations guidance](../../operations/README.md) treats exact backup, restore, recovery, and qualification procedures as gaps until decisions and executable evidence exist.
- The community baseline cannot depend on a commercial service. Managed-cloud key management, backup automation, availability, and recovery targets may differ operationally but cannot change learning-evidence semantics.
- CAP-0001 excludes comprehensive backup products and recovery guarantees; this decision should authorize only the minimum honest baseline for the first local slice.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| Community data-at-rest and backup posture | ready | A. Host/volume protection plus tested manual backup and no recovery guarantee; B. Application-managed encryption for evidence and backups; C. Required external key service | Accepted: Option A | None - ADR-0008 |
| Cross-store backup coordination | ready | B1. Enter maintenance mode and create one coordinated PostgreSQL/object-store backup set; B2. Keep writes online and implement a cross-store snapshot protocol | Accepted: Option B1 | None - ADR-0008 |
| Backup confidentiality boundary | ready | P1. Require a user-controlled encrypted host volume or encrypted backup medium without application-held keys; P2. Encrypt the backup archive in the application with a user-managed passphrase/key | Accepted: Option P1 | None - ADR-0008 |
| Backup trigger and recovery claim | ready | F1. User-invoked backup, optionally scheduled by host tooling, with no community RPO/RTO; F2. Application-scheduled backups with a stated recovery objective | Accepted: Option F1 | None - ADR-0008 |
| Restore target and rollback | ready | R1. Restore only into an empty inactive target, validate before activation, and never merge; R2. Restore in place with application-managed rollback | Accepted: Option R1 | None - ADR-0008 |
| Identity/session treatment on restore | ready | I1. Restore installation identity and bindings but revoke sessions and recovery credentials before startup; I2. Preserve all backed-up session and recovery state | Accepted: Option I1 | None - ADR-0008 |
| Local retention and deletion | ready | L1. Retain live evidence until explicit installation-data deletion and leave backup-copy retention user-controlled with clear disclosure; L2. Add application-managed time-based retention and backup pruning | Accepted: Option L1 | None - ADR-0008 |
| Transactional and object stores | ready | PostgreSQL owns transactional evidence/projections and the object-storage port owns content/artifacts | Preserve ADR-0003 data responsibilities | None - ADR-0003 |
| Learner and installation identity | constrained | Preserve ADR-0006 installation, actor, learner, mode, and binding meaning; secrets remain outside portable configuration | Use the accepted identity boundary | None - ADR-0006 |
| Local/cloud domain meaning | ready | Evidence and package semantics remain identical; operational protection may differ by profile | Preserve ADR-0004 shared-core parity | None - ADR-0004 |
| Managed-cloud protection and recovery | constrained | Defer cloud encryption, key custody, automated backup, availability, RPO, and RTO to a separate decision with cloud operational authority | Do not broaden this local decision | None - managed-cloud profile scope |

Canonical authority for the nonblocking rows:

- [ADR-0003](../../adr/ADR-0003-transactional-analytical-data-separation.md) and the [data architecture](../../architecture/data/data-architecture.md) assign transactional evidence to PostgreSQL and content/artifacts to object storage.
- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md) requires stable installation and learner meaning, fail-closed mode matching, server-owned sessions, and external secret resolution.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md) fixes shared domain and contract meaning while allowing different infrastructure and operational services.
- The [managed-cloud profile](../../architecture/deployment/managed-cloud-profile.md) leaves cloud platform, key, backup, and recovery choices decision-required; this request cannot supply that authority.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Local-host protection with documented manual backup and no service-level recovery guarantee | Stores evidence in PostgreSQL under the documented application data root, uses least-privileged service access, relies on host/filesystem or volume protection for data at rest, keeps secrets outside portable configuration, and provides a tested user-invoked backup/restore path. States that backup freshness is user-controlled and makes no community RPO/RTO guarantee. | Data is not protected from a compromised or improperly shared host. Users may fail to make backups. Restore tooling and documentation must be tested, and the product must communicate the boundary clearly. Cloud production protection remains blocked by a separate qualification decision. | Data classification, filesystem/volume permissions, database configuration, secret resolution, backup/export manifest, restore validation, retention/deletion documentation, diagnostics. | High. Application-managed encryption or managed key adapters can be added later if storage and export contracts preserve opaque identifiers and versioning. |
| B. Application-managed encryption for learner evidence and backups | Can protect selected fields and exports independently of storage infrastructure and supports an explicit local passphrase or key. | Creates key creation, storage, rotation, loss, recovery, migration, search/indexing, and support obligations. Lost keys may make evidence unrecoverable. | Encryption envelope/version, key store, startup/unlock flow, migrations, encrypted backup/export, recovery and support procedures. | Medium. Encryption formats and key lifecycle become durable compatibility contracts. |
| C. Require an external or managed key service for every profile | Centralizes key policy, rotation, access logging, and separation of duties. | Conflicts with a simple offline community baseline unless a local key service is bundled; adds operational complexity and provider dependence before CAP-0001. | Key-provider port, credentials, availability/fallback behavior, deployment tooling, audit and incident response. | Medium to high when provider-neutral contracts are used, but the operational dependency remains. |
| D. Use non-durable or disposable evidence for the first slice | Avoids immediate protection and recovery design. | Fails CAP-0001's retained-evidence outcome and makes completion state misleading after restart. | Temporary storage only; no honest resumption or recovery contract. | High technically, but not viable for the approved capability. |

## Accepted Recommendation

**Option A is the accepted narrowly scoped community baseline, subject to the documented learner-data threat model and executable backup/restore evidence.**

- **Verified:** local data has an accepted application-root boundary, PostgreSQL is the transactional system of record, community operation cannot require a commercial service, and recovery claims require evidence.
- **Assumption to validate:** the initial supported local environment is a private, adequately protected host and the stored lesson evidence is not treated as suitable for hostile multi-user environments.
- **Inference:** relying on documented host protection with tested manual backup is the smallest reversible posture that supports retained evidence without prematurely creating an application key-management product.
- **Explicit limitation:** this recommendation does not choose managed-cloud encryption, key custody, automated backup, availability, RPO, or RTO targets.

## Canonical Direction

**Option A with B1, P1, F1, R1, I1, and L1** is canonical for the community profile through [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md). Executable backup/restore qualification remains a mandatory delivery acceptance gate and is not claimed by this planning artifact; managed-cloud protection and recovery targets remain unresolved.

## Evidence Package

This is a planning-level security and recovery design. No backup command, restore command, storage mutation, encryption feature, retention job, or recovery guarantee has been implemented or qualified.

### Data Classification and Recovery Scope

| Data class | Representative records | Required treatment in the accepted baseline |
| --- | --- | --- |
| Confidential learner data | Opaque learner/actor references, lesson activity, attempts, responses, scores, completion evidence, timestamps, and learner-state projections | Least-privileged PostgreSQL access; protected local data root; included in recovery backup; never written to ordinary diagnostics |
| Confidential identity/security data | Installation identity, identity mode, provider bindings, password and recovery verifiers, session records, and security audit evidence | Included where required to preserve evidence ownership; backup treated as sensitive; all sessions and recovery credentials revoked before restored service starts |
| Integrity-sensitive published content | Exact lesson packages, assessments, curriculum references, sources, provenance, versions, and digests | Included or deterministically referenced in the backup set; package integrity and exact-version availability revalidated during restore |
| Operational metadata | Application, database, schema, migration, contract, backup-format, and provider-capability versions | Included in a self-describing manifest used for preflight compatibility and diagnostics |
| External secrets | Database passwords, OIDC client secrets, API/provider credentials, plaintext passwords, raw recovery codes, encryption keys, and client session cookies | Never copied into the backup set; manifest records only required secret-reference names or capability requirements |
| Runtime diagnostics | Logs, traces, caches, temporary exports, and incomplete staging data | Excluded by default; security/audit records required for domain or recovery integrity remain in their owning store |

A disaster-recovery backup is not a portable learner export. It restores the same installation identity, mode, bindings, evidence, content versions, and audit continuity into an empty target. A future portable export must minimize or omit private identity and authentication material and requires its own contract.

### Local Threat Model

Protected assets are learner/evidence confidentiality and integrity, identity-to-evidence ownership, published content provenance, restore availability, authentication verifier confidentiality, external secrets, and trustworthy backup status.

| Threat or failure | Required outcome | Residual boundary |
| --- | --- | --- |
| Host administrator, malware, or process compromise | Document that Option A does not protect data from a compromised running host; use least privilege and host/volume encryption as defense in depth | Local host administrators remain trusted |
| Shared machine or remotely exposed service | Retain ADR-0006's private-host and authentication boundaries; do not claim the data root is safe from another privileged local user | Host isolation and user account security remain operator responsibilities |
| World-readable files, broad container mounts, or exposed database port | Create restrictive supported-platform permissions, private container/network paths, distinct service credentials, and preflight diagnostics; never publish PostgreSQL by default | Exact permission enforcement is platform-specific and requires qualification |
| Backup copied to an unprotected destination | Classify the set as sensitive; require an operator-selected encrypted volume or medium outside the active data root and an explicit acknowledgement | The application does not hold or recover the external encryption key under P1 |
| Backup theft, tampering, or malicious replacement | External encryption protects confidentiality; file hashes and manifest closure detect accidental alteration; untrusted restore input is validated before mutation | Unsigned hashes do not authenticate a backup against an attacker who can replace the whole set |
| Mixed PostgreSQL and object-store points in time | Acquire one backup lock, enter maintenance mode, stop new writes/jobs, drain or cancel bounded work, then capture both stores | Availability is intentionally reduced during backup |
| Direct copy of a running database or data root | Document as unsupported; use the governed backup operation | A raw copy has no consistency or recovery claim |
| Disk full, permission denial, interrupted process, or destination disconnect | Fail the operation, preserve the running source, never finalize the staging set, and report a bounded actionable diagnostic | Operator must remediate storage or permission failure |
| Corrupt, incomplete, path-escaping, or version-incompatible restore set | Reject during preflight or isolated restore; do not change an existing installation | Recovery may be impossible without another valid backup |
| Restore over populated installation or silent merge | Refuse; restore only to an empty inactive target after explicit operator confirmation | Intentional replacement remains a separate destructive action |
| Old backup resurrects deleted data, sessions, or recovery credentials | Show backup time and rollback warning; revoke all restored sessions and recovery credentials before startup; disclose that old backups retain deleted data | Live deletion cannot erase copies outside application control |
| Missing external secret after restore | Keep the restored service unavailable or affected provider explicitly degraded until the operator supplies the named secret reference | Secrets are not recoverable from the backup |
| Logs expose evidence, credentials, paths, or backup content | Emit allowlisted event codes, backup ID, phase, timestamps, counts, and redacted target label; exclude responses, hashes, secrets, and raw paths | Host-level tooling may have its own logs and requires operator review |
| Ransomware or loss of the active host and attached backup | Recommend offline/separate encrypted copies and restore testing; make no ransomware-resilience claim | One user-managed local backup is not a managed resilience service |

### Application Data Root and Access Boundary

- The active application data root owns installation metadata, the PostgreSQL volume/reference, local object storage, and bounded operation state. Backup destinations are outside that root so they cannot recurse into themselves or be lost with an in-place restore.
- API and worker processes receive only the database/object capabilities they require. PostgreSQL remains on a private local/container network with a least-privileged application role and a separately bounded backup/restore role; exact grants require executable schema review.
- Supported platforms create restrictive file and directory permissions and diagnose material broadening. Container mounts expose only required paths; neither the web client nor content providers receive direct filesystem or database access.
- Secret values resolve through the host secret boundary and portable configuration stores references only. Backup and restore diagnostics never echo resolved values.
- Restore input is untrusted. Path normalization, manifest closure, type/size limits, file hashes, version support, and staging boundaries are validated before activation.

### Representative Recovery Backup Set

```text
financial-ai-academy-backup-<backup-id>/
  backup-manifest.json
  database/
    application.dump
  objects/
    <application-controlled paths and bytes>
  installation/
    nonsecret-configuration.json
  FINALIZED
```

The manifest records backup ID and format version; creation start/completion times; installation identity and identity mode; application, PostgreSQL, schema, migration, and contract versions; source platform profile; maintenance/quiescence evidence; every included entry's normalized path, size, and digest; object/package identities and versions; database dump metadata; exclusions; required external secret references; validation result; and finalization state.

The set contains the PostgreSQL application database, exact object-storage data needed for retained evidence and content-version resolution, and nonsecret installation configuration. It can contain credential verifiers and identity bindings because it is a same-installation recovery artifact. It never contains plaintext credentials, provider/API secrets, client cookies, or raw recovery codes. Every restored server session and recovery credential is revoked before service activation.

### Backup Operation Design

1. Authenticate a local operator through host authority, acquire an exclusive operation lock, and preflight destination separation, permissions, available space, supported encrypted-medium acknowledgement, and tool versions.
2. Enter a visible maintenance state, reject new mutations, and wait for or safely cancel bounded application and worker operations. Abort if quiescence cannot be proven.
3. Create a PostgreSQL logical dump with a dedicated least-privileged backup role. The exact dump format and PostgreSQL version matrix are delivery choices; copying a running PostgreSQL data directory is not supported.
4. Copy the closed set of required objects while writes remain quiesced. Retain exact lesson package versions, digests, provenance, and assessment references required by evidence.
5. Write the nonsecret installation configuration and manifest to a newly created staging directory using application-generated names. Never follow links or accept package-authored output paths.
6. Re-read every staged entry, verify path closure, size, digest, required content, and database archive readability, then atomically create or rename the finalization marker/set where supported.
7. Exit maintenance mode only after source integrity remains healthy. On any failure, leave the live source unchanged, mark no valid backup, safely clean or clearly label incomplete staging, and emit a redacted diagnostic.

The operation is user-invoked. Host schedulers may invoke the same command, but the application makes no schedule, freshness, RPO, RTO, offsite-copy, immutability, or high-availability promise. UI/CLI status may report only observed facts: last attempt, last successful finalized backup, destination label, backup ID, duration, size, and validation result.

### Restore Operation Design

1. Require an empty inactive destination and explicit local operator confirmation. Refuse a target containing installation identity, bindings, learner evidence, or an active service.
2. Preflight the complete manifest, finalization marker, normalized paths, entry closure, sizes/digests, supported backup/application/database/schema/contract versions, required capacity, and external secret-reference requirements before database or object mutation.
3. Restore PostgreSQL and objects into isolated staging resources. Do not merge with a populated database or object root and do not follow backup-provided links.
4. Validate database constraints, migration state, exact content and assessment versions, object/package digests, evidence provenance, identity-mode consistency, and installation identity. Only separately approved forward migrations may run.
5. Rebuild or reconcile derived completion projections from append-oriented Assessment evidence and compare deterministic results with retained references. A projection mismatch fails qualification rather than rewriting source evidence silently.
6. Revoke all restored sessions and recovery credentials, require fresh authentication, and keep providers with missing external secrets explicitly unavailable.
7. Run health and representative evidence queries before making the restored target eligible for activation. Failure preserves the staged diagnostic evidence but never damages another installation.

Activation or deletion of an existing installation is a separate explicit destructive operation. DEC-0004 does not authorize it.

### Qualification Matrix

This matrix defines required executable evidence for the later delivery slice. `DEFINED` means the scenario and expected result are reviewable; no command has been implemented or executed.

| Scenario | Required evidence and expected result | Planning state |
| --- | --- | --- |
| Representative learner completes the lesson, backup runs, source is unavailable, and restore targets an empty installation | Exact identity/evidence/content versions return; completion projection rebuilds; sessions/recovery are revoked; fresh authentication succeeds when configured | DEFINED |
| Backup starts while a write or worker job is active | Maintenance drains/cancels safely or backup aborts; no mixed finalized set exists | DEFINED |
| Database dump succeeds but object copy, verification, or finalization fails | Live source remains usable; incomplete set is not listed as restorable | DEFINED |
| Destination is inside active root, is an existing nonempty set, lacks capacity, is disconnected, or denies writes | Preflight or bounded operation failure; no overwrite or valid final marker | DEFINED |
| Manifest, dump, object, package, size, or digest is missing or corrupted | Restore rejects before activation and reports the exact bounded phase/code | DEFINED |
| Restore includes path traversal, link, special file, duplicate path, excessive entry, or oversized content | Preflight rejects without writing outside isolated staging | DEFINED |
| Backup/app/database/schema/contract version is unsupported | Restore fails closed with supported-version guidance; no implicit downgrade or unapproved migration | DEFINED |
| Target already contains installation identity or evidence | Restore refuses merge or overwrite | DEFINED |
| Required OIDC/provider secret is absent | Core restored state remains inactive or the provider is explicitly unavailable; no secret is fabricated or logged | DEFINED |
| Old backup contains a session or recovery verifier that was revoked after backup | Restored service invalidates all such credentials before listening | DEFINED |
| Live learner data was deleted after the backup | Restore warning identifies the backup point and potential resurrection; documentation explains that the external copy must be deleted separately | DEFINED |
| Same fixture is backed up/restored through supported local platforms | Domain IDs, evidence, versions, digests, projection results, and diagnostics are equivalent | DEFINED |
| Redaction sentinels appear in learner responses, secrets, identifiers, filenames, and errors | Logs contain only allowlisted encoded fields and no sentinel values | DEFINED |

Delivery cannot claim backup/restore support until these scenarios run in a controlled environment, include a real restore into an empty target, record tool versions and raw failures, and reconcile any mismatch with this decision.

### Retention, Deletion, and User-Facing Limits

- CAP-0001 live evidence is retained until the local operator explicitly deletes the installation data through a supported operation. Version 1 makes no automatic expiry or per-record deletion claim.
- Backup copies are user-controlled external artifacts. Deleting live evidence or the active data root does not delete older backups; the user must delete each copy according to their needs and applicable obligations.
- A backup set contains confidential learner and identity/security data even though plaintext secrets are excluded. It must be kept on access-restricted encrypted storage, preferably separate/offline from the active host, and disposed of securely.
- The application records backup and restore audit facts without learner responses, credentials, secret values, raw verifier values, or uncontrolled paths. Diagnostic retention must not outlive its supported operational purpose.

Required product language, substantially unchanged in meaning:

> The community edition stores learner evidence on your local host and relies on your operating system, account, filesystem or volume, and backup-medium protections. It does not provide application-managed at-rest encryption, automatic backups, high availability, offsite storage, ransomware protection, or guaranteed recovery times. Backups run only when you or your host scheduler invoke them. A backup is sensitive, may contain data later deleted from the live installation, and must be stored on protected encrypted media. Without a recent verified backup, some or all local data may be unrecoverable.

### Standards Consulted

- [PostgreSQL backup and restore documentation](https://www.postgresql.org/docs/current/backup.html) and [SQL dump guidance](https://www.postgresql.org/docs/current/backup-dump.html) support logical backups and describe `pg_dump` as an internally consistent database snapshot. DEC-0004 adds maintenance mode because PostgreSQL consistency alone does not coordinate the separate object store.
- [NIST SP 800-209, Security Guidelines for Storage Infrastructure](https://csrc.nist.gov/pubs/sp/800/209/final) calls for documented backup frequency/retention/protection, coverage of related assets, application-level consistency, restore procedures, integrity verification, and periodic end-to-end restore testing.
- [NIST SP 1800-25, Data Integrity](https://csrc.nist.gov/pubs/sp/1800/25/final) treats secure storage, backups, integrity checking, audit, and protection against accidental or malicious destruction as coordinated controls.
- The [CISA StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide) recommends offline, encrypted backups and regular integrity and disaster-recovery testing. The community baseline can recommend but cannot provide or verify offline separation under user control.
- The [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) makes encryption placement dependent on the threat model and notes the key-lifecycle complexity created by application encryption.
- The [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) supports recording import/export and administrative events while excluding or masking session identifiers, tokens, passwords, connection strings, keys, and sensitive personal data.

### Security Review Criteria

Canonical changes to this threat and recovery posture are evaluated against the following criteria for the community release. Reviewer identity, status, and conclusion remain local-only records and are not copied into tracked artifacts.

- the private, adequately protected local-host assumption and trusted-host-administrator residual risk;
- P1's reliance on user-controlled host/volume/backup-medium encryption instead of application-managed encryption;
- the confidential recovery-backup contents, external-secret exclusions, and mandatory session/recovery revocation;
- maintenance-mode cross-store consistency, least-privileged backup/restore access, isolated staging, and no-merge restore;
- user-controlled backup freshness and retention with no community RPO/RTO;
- the limitation language, deletion/backup-copy disclosure, and absence of managed-cloud authority;
- the qualification matrix as a mandatory implementation and release gate; and
- any additional control, scope reduction, or decision needed before approval.

Future changes to these criteria require the applicable qualified security review; agent standards analysis cannot supply that authority.

## Evidence Required

- **Prepared:** learner-data classification and local threat model covering host compromise, shared machines, browser/API access, database credentials, logs, exports, copied data roots, backup media, rollback, corruption, and ransomware limitations.
- **Prepared:** application-data-root, secret-resolution, least-privilege, maintenance-mode, staging, and destination-protection design.
- **Prepared:** representative backup set, backup/restore workflows, and executable qualification matrix for evidence/projection consistency, versions, corruption, identity/session handling, failure reporting, and local-platform parity.
- **Prepared:** retention, installation-level deletion boundary, diagnostic redaction, and user-facing limitation language.
- **Satisfied for canonical promotion:** ADR-0008 records Options A, B1, P1, F1, R1, I1, and L1 with the documented residual risks and scope limits.
- **Still required before delivery acceptance:** executable controlled backup/restore qualification. Separate managed-cloud security and recovery decisions remain required before production cloud delivery.

## Required Authority

Changes to the threat model, protection boundary, accepted sub-decisions, or residual-risk posture require qualified security review and product/architecture decision authority. Reviewer and decision records remain only in the ignored local ledger. Managed-cloud recovery targets require separate future cloud operational authority.

## Decision Record and Promotion

The scoped community baseline is recorded in [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md), the [community protection boundary](../../security/community-learner-evidence-protection.md), and the [community backup/restore design](../../operations/community-backup-and-restore.md). Security architecture, deployment guidance, known gaps, verification, and decision readiness reflect that boundary. The managed-cloud portion remains unresolved pending separate authority and qualification.

## Dependent Planning Updates

- DEC-0004 has been removed from CAP-0001's unresolved decision gates.
- Refine Candidate C persistence, restart, corruption, backup, restore, retention, and limitation scenarios.
- Keep managed-cloud encryption, key strategy, automated backup, RPO, and RTO as separately blocked operational decisions.

## Planning History

- 2026-08-04: Decision request captured from CAP-0001's learner-evidence protection and recovery gate.
- 2026-08-04: Option A was established as the proposal to shape; required security and recovery evidence was not waived and no cloud posture was selected.
- 2026-08-04: The decision table, learner-data classification, threat model, access boundary, representative recovery set, maintenance-mode backup and empty-target restore designs, qualification matrix, retention/deletion boundary, limitation language, standards review, and security-review criteria were prepared. No executable qualification or cloud posture was claimed.
- 2026-08-04: ADR-0008 and synchronized security, operations, deployment, assurance, readiness, and context guidance established the canonical community boundary; DEC-0004 moved to `complete`. Executable qualification and managed-cloud posture remain unresolved.
