# ADR-0001: Python/TypeScript Modular Monolith

- Status: accepted
- Date: 2026-08-03

## Context

The platform requires modern learner-facing web UX, financial data processing, AI/ML development, background work, and replaceable integrations while remaining practical to run locally.

## Decision

Use a TypeScript web application and a Python backend organized as a module-first modular monolith. The backend exposes API, worker, and CLI hosts from one domain/application package. FastAPI and Pydantic are the API boundary. [ADR-0009](ADR-0009-initial-application-framework-runtime-baseline.md) establishes the initial executable runtime, framework, routing, and rendering lines.

## Consequences

- Python supports finance, analytics, AI, and ML workflows without a separate core implementation.
- TypeScript provides a strongly typed browser application generated against reviewed API contracts.
- Module and layer boundaries require automated dependency checks as implementation appears.
- Services are extracted only with evidence for independent scaling, isolation, ownership, or release needs.

## Rejected Alternatives

- TypeScript-only application core
- Python-based browser UI
- Microservices as the initial architecture
