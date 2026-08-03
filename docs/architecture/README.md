# Architecture Documentation

- Status: accepted
- Canonical for: architecture documentation routing and authority
- Related ADRs: `docs/adr/README.md`
- Verification: `docs/assurance/architecture-verification.md`

## Purpose

This directory describes the intended structure of Financial AI Academy. It defines system boundaries, module ownership, contract behavior, data responsibilities, deployment profiles, and the evidence expected to keep implementation aligned with the architecture.

Architecture documents describe the current intended design. Accepted ADRs record why significant decisions were made. Executable schemas under `contracts/` define exact external data shapes. If those sources conflict, stop and reconcile the conflict rather than silently selecting one.

## Start Here

1. [Architecture Principles](system/architecture-principles.md)
2. [System Overview](system/system-overview.md)
3. [Modular Monolith](system/modular-monolith.md)
4. [Module Map](modules/module-map.md)
5. [Module Dependency Rules](modules/module-dependency-rules.md)
6. [Contract Architecture](contracts/contract-architecture.md)
7. The task-specific architecture document
8. [Architecture Verification](assurance/architecture-verification.md)

## Areas

| Directory | Responsibility |
| --- | --- |
| `system/` | System shape, guiding principles, process model, and repository structure |
| `modules/` | Domain-module ownership and dependency rules |
| `contracts/` | APIs, events, provider/plugin seams, compatibility, and conformance |
| `learning/` | Learning, assessment, learner-state, and adaptive-pathway components |
| `ai-ml/` | AI/ML boundaries, model gateways, evaluation, and runtime responsibilities |
| `data/` | Transactional, analytical, object, lineage, retention, and migration concerns |
| `deployment/` | Local open-source and managed-cloud profiles |
| `assurance/` | Testing, fitness functions, qualification, and known architecture gaps |

## Update Rule

Update the relevant architecture document, ADR, context pack, executable contract, and verification evidence in the same change when a decision alters module ownership, dependency direction, public contracts, provider capabilities, persistence semantics, AI authority, security boundaries, or deployment behavior.

