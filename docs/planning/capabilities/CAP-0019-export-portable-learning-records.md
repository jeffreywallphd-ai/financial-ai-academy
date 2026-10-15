---
id: CAP-0019
kind: capability
planning_status: shaping
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0009", "CAP-0017", "CAP-0026"]
decision_gates: []
approval_model: cap-package-v1
slice_ids: ["SLI-0078", "SLI-0079", "SLI-0080", "SLI-0081"]
---

# Capability: Export and Retain Portable Learning Records

## Outcome

An individual learner can create, verify, download, retain, and restore or
re-import supported portable records for evidence, progress, preferences, and
saved work under the deployment profile's documented protection and recovery
boundary.

## Users and Value

Learners need control of durable learning history and work. Value is observable
when exports are versioned, complete for their declared scope, integrity-bound,
portable, and honest about excluded data, licensing, and recovery guarantees.

## Scope

### In Scope

- Versioned portable manifests and records for authorized learning evidence,
  progress projections, preferences, workspace metadata, project snapshots, and
  permitted resource artifacts.
- Export selection, manifest preview, integrity, provenance, redaction,
  resumable generation, download, validation, compatibility, and bounded import.
- Community coordinated backup/empty-target restore integration under ADR-0008
  without claiming an RPO or RTO.
- Accessible status, error, limitation, and recovery guidance.

### Out of Scope

- Export of provider secrets, unlicensed data, raw internal database dumps,
  managed-cloud recovery objectives, populated-target merge, or cross-product
  interoperability not established by a contract.
- Treating an export as a credential or authoritative source over live evidence.

## Canonical Context

- [Contract Architecture](../../architecture/contracts/contract-architecture.md)
- [Community Backup and Restore](../../operations/community-backup-and-restore.md)
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
- [CAP-0009](CAP-0009-track-progress-and-competency-evidence.md)
- [CAP-0017](CAP-0017-maintain-personal-learning-workspace.md)
- [CAP-0026](CAP-0026-preserve-provenance-and-accountable-history.md)

## Decision Gates and Constraints

- Exact portable schemas are platform-owned and versioned; owning modules
  provide authorized export views without sharing persistence internals.
- Community restore remains user-invoked, maintenance-mode, coordinated,
  integrity-checked, empty-target, and revokes restored sessions/credentials.
- Managed-cloud protection and recovery remain outside this package until their
  separate decisions are accepted.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0078 | A learner previews and exports a versioned integrity-bound manifest of authorized evidence, progress, preferences, and workspace records. | First after dependencies; establishes portable schemas and export views. | Credentials, provider secrets, raw dumps, or unlicensed data changes the CAP package. | captured |
| SLI-0079 | The learner resumes export generation, downloads records and permitted artifacts, and verifies completeness, integrity, provenance, and limitations. | After SLI-0078. | Unbounded background jobs or hidden omission changes the CAP package. | captured |
| SLI-0080 | A supported empty target validates and imports or restores compatible records while preserving original provenance and refusing conflicts or unsupported versions. | After SLI-0079; integrates ADR-0008 community recovery. | Populated-target merge, managed-cloud recovery, or evidence rewriting changes the CAP package. | captured |
| SLI-0081 | Export/retention is qualified for authorization, redaction, licensing, interruption, compatibility, corruption, recovery, accessibility, and no-RPO/RTO claims. | Last; depends on SLI-0078 through SLI-0080. | Service-level guarantees or external-standard claims changes the CAP package. | captured |

## Capability Acceptance

- Export manifests state scope, versions, source identities, digests, provenance,
  omissions, restrictions, and compatible import/restore behavior.
- Unauthorized, secret, unlicensed, corrupt, conflicting, or unsupported content
  is excluded or refused with bounded diagnostics.
- Interrupted generation is recoverable without duplicate or contradictory
  records; restore preserves original evidence and projection rebuildability.
- Community qualification proves the accepted recovery boundary without
  implying managed-cloud guarantees.

- Every slice includes focused failure and anti-rigidity tests; unsupported
  record classes are reported as bounded omissions rather than blocking every
  otherwise valid export.

## Risks and Non-Goals

Portable records can leak sensitive or licensed content or imply credential
status. This CAP provides controlled portability, not raw data extraction,
universal interoperability, populated-target merge, or service guarantees.

## Documentation Impact

Delivery will add portable schemas and compatibility, export/import operations,
license/redaction policy, backup/restore integration, learner guidance,
accessibility, and qualification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 16 with manifest SLI-0078 through
  SLI-0081. The package awaits one CAP planning approval.

