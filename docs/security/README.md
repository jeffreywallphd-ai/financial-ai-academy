# Security Architecture

- Status: partially accepted
- Canonical for: security-document routing, accepted identity security, and remaining trust-boundary hypotheses

## Accepted Boundaries

- [Local Learner Identity Security Architecture](local-identity-architecture.md)
- [Community Learner-Evidence Protection](community-learner-evidence-protection.md)
- [Inert Applied-Project Artifacts](../adr/ADR-0011-inert-applied-project-artifacts.md)
- [Reusable Project Workspace](../adr/ADR-0012-reusable-project-workspace.md)

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

ADR-0012 places learning-initiated and independent mutable work in a bounded
Project workspace. Immutable Project snapshots and Assessment submissions retain
their own authorization and retention boundaries. Project links to portfolios
or other domain resources carry stable references and provenance only; they do
not grant Project access to another module's persistence, provider credentials,
or privileged operations.

Baseline behavior is defined in `docs/standards/security-and-privacy-standards.md`. Missing threat models are recorded as gaps, not treated as evidence of safety.
