# Security Architecture

- Status: proposed
- Canonical for: security-document routing and initial trust boundaries

## Initial Trust Boundaries

- Browser to authenticated API
- API/worker hosts to PostgreSQL and object storage
- Platform to market-data and model providers
- Raw input to canonical normalized data
- Local host to installable extensions
- Organization/tenant context across request, job, persistence, and storage
- Model input/output and retrieved content
- Imports, exports, generated artifacts, and analytical notebooks

Threat models should be added for learner data, provider/plugin execution, AI data flow, and local/cloud deployment when implementation or a durable decision introduces the boundary.

Baseline behavior is defined in `docs/standards/security-and-privacy-standards.md`. Missing threat models are recorded as gaps, not treated as evidence of safety.

