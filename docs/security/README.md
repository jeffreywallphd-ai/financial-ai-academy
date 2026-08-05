# Security Architecture

- Status: partially accepted
- Canonical for: security-document routing, accepted identity security, and remaining trust-boundary hypotheses

## Accepted Boundaries

- [Local Learner Identity Security Architecture](local-identity-architecture.md)
- [Community Learner-Evidence Protection](community-learner-evidence-protection.md)

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

Baseline behavior is defined in `docs/standards/security-and-privacy-standards.md`. Missing threat models are recorded as gaps, not treated as evidence of safety.
