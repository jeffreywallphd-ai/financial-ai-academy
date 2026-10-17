---
id: CAP-0027
kind: capability
planning_status: ready
authority: noncanonical
owner: unassigned
updated: 2026-10-16
parent: null
depends_on: ["CAP-0019", "CAP-0024", "CAP-0026"]
decision_gates: ["DEC-0011", "DEC-0012", "DEC-0017"]
approval_model: cap-package-v1
slice_ids: ["SLI-0110", "SLI-0111", "SLI-0112", "SLI-0113"]
---

# Capability: Operate the Community Edition Locally

## Outcome

An individual or contributor can install, configure, start, inspect, upgrade,
back up, restore, and troubleshoot the community edition on a supported private
host with free-data and externally configured provider connections and honest
capability limitations.

## Users and Value

Community users need a dependable path from a clean machine to a recoverable
local service. Value is observable when documented commands are repeatable,
configuration and data locations are clear, upgrades preserve supported data,
and recovery is qualified within ADR-0008 rather than promised abstractly.

## Scope

### In Scope

- Supported local prerequisites, install/start/stop/status, configuration and
  secret resolution, loopback/private-host defaults, data locations, health,
  logs, troubleshooting, and uninstall-with-preservation guidance.
- Deterministic migrations and upgrades with preflight, backup, rollback
  boundaries, compatibility, and failure diagnostics.
- ADR-0008 coordinated backup and empty-target restore qualification.
- Admitted free-data/external model providers under ADR-0013, ADR-0020, and
  ADR-0018 with explicit unavailable/degraded behavior.
- Explicit Alpha Vantage free or verified-education credential setup with
  visible quota and rights-profile limits, no bundled/shared key assumption,
  and a fully usable provider-independent local core when it is absent.

### Out of Scope

- Managed hosting, shared-host security guarantees, automatic backup service,
  RPO/RTO, production SLA, premium licensed providers, arbitrary plugins, or
  protecting against a compromised local host.

## Canonical Context

- [Operations Documentation](../../operations/README.md)
- [Community Backup and Restore](../../operations/community-backup-and-restore.md)
- [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md)
- [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md)
- [Local and Cloud Capability Parity](../../architecture/deployment/local-cloud-capability-parity.md)
- [ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
- [ADR-0020](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md)
- [Provider and Durable-Job Operations](../../operations/provider-and-job-operations.md)
- [CAP-0024](CAP-0024-connect-and-govern-replaceable-providers.md)

## Decision Gates and Constraints

- ADR-0008 fixes private-host, coordinated user-invoked recovery sets,
  maintenance-mode empty-target restore, credential revocation, and no RPO/RTO.
- Provider setup is limited to postures accepted by ADR-0013, ADR-0020, and
  ADR-0018; access does not imply licensed use or safe extension execution.
- ADR-0009 fixes the Python API and static React client runtime shape; Node is
  build/test tooling and no deployment-specific domain fork is permitted.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0110 | A user installs and starts a supported private-host community profile with validated configuration, explicit data locations, health, and safe defaults. | First after provider decisions and dependencies. | Shared-host claims, hidden prerequisites, or cloud-only domain behavior changes the CAP package. | captured |
| SLI-0111 | The user configures the Alpha Vantage-first profile and other admitted data or external/local model providers through secret indirection and sees capability, license, quota, cost, and health limits. | After SLI-0110 and CAP-0024. | Bundled/shared provider keys, unreviewed providers, or secret exposure changes the CAP package. | captured |
| SLI-0112 | The user performs preflighted upgrade, coordinated backup, integrity verification, and empty-target restore with documented failure and rollback boundaries. | After SLI-0110 and CAP-0019. | Automatic RPO/RTO, populated-target merge, or managed-cloud recovery changes the CAP package. | captured |
| SLI-0113 | Local operation is qualified on supported environments for clean install, restart, provider outage, upgrade/migration, backup/restore, troubleshooting, accessibility, and data preservation. | Last; depends on SLI-0110 through SLI-0112. | Production SLA or remote multi-user hosting changes the CAP package. | captured |

## Capability Acceptance

- A supported clean environment reaches healthy local operation through one
  documented path and reports prerequisites, versions, configuration, secrets,
  ports, data locations, and limitations.
- Upgrades and migrations are deterministic and recoverable within documented
  boundaries; backup/restore qualification matches ADR-0008 exactly.
- Provider outage or absence degrades only dependent capabilities and does not
  corrupt local core state.
- A clean local install requires no Alpha Vantage credential; adding or removing
  one changes only the declared market-data capability and never blocks startup,
  imports, lessons, projects, backup, or restore.
- Installation, security, recovery, accessibility, and troubleshooting evidence
  is executable and does not claim unsupported platforms or service levels.

- Every slice includes focused failure and anti-rigidity tests so optional
  provider or platform tooling does not turn a minimal supported local install
  into an all-integrations prerequisite.

## Risks and Non-Goals

Local simplicity can hide security, provider, or recovery limits. This CAP does
not promise shared-host isolation, automatic backups, RPO/RTO, managed service,
premium data rights, or arbitrary extension safety.

## Documentation Impact

Delivery will add supported-environment, install/configuration, provider,
health/logging, migration/upgrade, backup/restore, troubleshooting, security,
and qualification documentation.

## Planning History

- 2026-10-15: Shaped from catalog candidate 24 with manifest SLI-0110 through
  SLI-0113. Provider decisions DEC-0011, DEC-0012, and DEC-0017 block approval.
- 2026-10-15: DEC-0017 was promoted to ADR-0018. Exact allowlisted packaged
  adapters and PostgreSQL at-least-once jobs now constrain local planning;
  DEC-0012 remains unresolved.
- 2026-10-16: DEC-0012 was promoted through ADR-0020. All listed provider
  decision gates are resolved, so this CAP returns to shaping for dependency
  and CAP-package readiness validation.
- 2026-10-16: Revalidated the complete four-slice package against ADR-0020.
  The Alpha Vantage setup is optional, rights-profiled, secret-indirected, and
  degradable; the slice manifest and dependency order are unchanged.

