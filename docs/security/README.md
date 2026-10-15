# Security Architecture

- Status: partially accepted
- Canonical for: security-document routing, accepted identity security, and remaining trust-boundary hypotheses

## Accepted Boundaries

- [Local Learner Identity Security Architecture](local-identity-architecture.md)
- [Community Learner-Evidence Protection](community-learner-evidence-protection.md)
- [Inert Applied-Project Artifacts](../adr/ADR-0011-inert-applied-project-artifacts.md)
- [Reusable Project Workspace](../adr/ADR-0012-reusable-project-workspace.md)
- [Learner-Managed Experiment Execution](../adr/ADR-0016-learner-managed-experiment-execution.md)
- [Platform-Native Human-Reviewed Content Authoring](../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
- [Allowlisted Adapters with PostgreSQL At-Least-Once Jobs](../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
- [Append-Only Bounded Learner-Projection Overrides](../adr/ADR-0019-append-only-bounded-projection-overrides.md)

## Initial Trust Boundaries

- Browser to authenticated API
- API/worker hosts to PostgreSQL and object storage
- Platform to market-data and model providers
- Raw input to canonical normalized data
- Local host to installable extensions
- Organization/tenant context across request, job, persistence, and storage
- Model input/output and retrieved content
- Imports, exports, generated artifacts, and analytical notebooks

The community learner-data protection and recovery threat boundary is accepted by ADR-0008. Threat models remain required for managed-cloud protection and recovery, provider/plugin execution, AI data flow, and other deployment boundaries when implementation or a durable decision introduces them.

Applied-project datasets, notebooks, code, environments, and results are
untrusted inert data under ADR-0011. The initial platform may validate bounded
metadata, store, inspect through separately accepted passive renderers,
download, export, and restore those artifacts, but it may not execute them,
grant network or secret access, or send them to an execution provider. Learners
run tools in environments they control. Platform-managed or provider-managed
execution remains a separate decision-required trust boundary.

ADR-0016 applies that inert boundary to financial AI/ML experiments. The
platform may export integrity-bound run bundles and validate imported result
bundles from learner-controlled environments. Provider-neutral run/result
contracts preserve a future optional analytics execution-port seam, but the
current product exposes no execute operation. A sandbox adapter still requires
a new decision and complete isolation, image/package, identity/tenancy, egress,
secret, job, quota, cost, cleanup, monitoring, incident, and provider
qualification.

ADR-0012 places learning-initiated and independent mutable work in a bounded
Project workspace. Immutable Project snapshots and Assessment submissions retain
their own authorization and retention boundaries. Project links to portfolios
or other domain resources carry stable references and provenance only; they do
not grant Project access to another module's persistence, provider credentials,
or privileged operations.

ADR-0017 keeps mutable authoring revisions separate from immutable published
packages. Preview, imports, provider content, AI proposals, and future external-
standard mappings remain untrusted, non-published inputs. Only an authorized
human review bound to the exact validated revision may make it eligible for an
atomic publication operation; any edit invalidates that review authority.
Future interoperability adapters remain optional and cannot bypass native
safety, accessibility, ownership, provenance, or package validation.

ADR-0018 admits only exact allowlisted reviewed packaged adapters in the
initial in-process trust class. Discovery or configuration never authorizes
unknown code, and secrets are resolved only at a permitted invocation boundary.
PostgreSQL job metadata excludes secrets and raw sensitive/provider payloads;
leases and fencing prevent stale workers from publishing authoritative results.
At-least-once delivery requires idempotency or reconciliation, and neither
timeout nor cancellation proves an external effect stopped. Untrusted adapter
hosting, a sandbox, and an external broker remain separate decisions.

ADR-0019 treats instructor access and projection overrides as high-impact,
privacy-sensitive actions. Source evidence and base projections stay immutable;
an override is a time-bounded visible overlay requiring separate proposal and
confirmation by distinct authorized actors, current source/policy checks,
learner-visible reason/history, expiration/reversal, and audit references.
DEC-0016 remains required before implementation because it owns tenant,
membership, role, and exact permission isolation.

Baseline behavior is defined in `docs/standards/security-and-privacy-standards.md`. Missing threat models are recorded as gaps, not treated as evidence of safety.
