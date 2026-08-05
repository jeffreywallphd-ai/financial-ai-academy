# System Overview

- Status: accepted
- Canonical for: high-level system shape
- Related docs: `modular-monolith.md`, `../deployment/local-cloud-capability-parity.md`

## System Shape

```mermaid
flowchart LR
    WEB["React/TypeScript static client"] --> API["Python/FastAPI API host"]
    API --> CORE["Modular application core"]
    WORKER["Python worker host"] --> CORE

    CORE --> LEARN["Learning modules"]
    CORE --> FIN["Financial modules"]
    CORE --> ADAPT["Adaptation module"]
    CORE --> AI["AI orchestration module"]

    CORE --> PORTS["Versioned ports and contracts"]
    PORTS --> PROVIDERS["Market data, model, content, identity, storage, and job adapters"]

    CORE --> PG["PostgreSQL system of record"]
    WORKER --> ANALYTICS["Parquet and DuckDB analytics"]
    CORE --> OBJECTS["Object storage port"]
```

## Primary Processes

- **Web application:** React 19 and TypeScript 7 browser experience using React Router 8 Data Mode and Vite 8. It produces static client assets and consumes only the generated API client.
- **API host:** CPython 3.14, FastAPI 0.141, and Pydantic 2.13 composition exposing authenticated application operations and generated OpenAPI.
- **Worker host:** asynchronous ingestion, backtesting, document processing, model evaluation, embeddings, and recommendation projection work.
- **CLI host:** local setup, diagnostics, backup, restore, contract inspection, and administrative operations.

The API, worker, and CLI are entry points into the same Python application package. They do not contain domain policy.

Node.js 24 LTS is build and test tooling, not a production application host. The initial system has no Node server, server-side rendering, React Server Components, server actions, or backend-for-frontend. [ADR-0009](../../adr/ADR-0009-initial-application-framework-runtime-baseline.md) governs this baseline.

## Storage Responsibilities

- PostgreSQL owns transactional state, identifiers, job metadata, learner records, course state, portfolios, and audit references.
- Parquet holds larger immutable or versioned analytical datasets.
- DuckDB queries local or object-backed analytical data without becoming the transactional source of truth.
- Object storage holds content, imports, exports, generated artifacts, and dataset objects behind stable storage keys.

## Deployment Profiles

- The local profile uses containerized PostgreSQL, local filesystem object storage, local DuckDB/Parquet, and local or external model/data adapters.
- The cloud profile uses managed equivalents, tenant-aware identity and authorization, horizontally scalable hosts, and managed operational controls.
- Both profiles expose the same domain semantics and public contract versions.

## Explicit Non-Goals

- Microservices as the initial repository structure
- Provider-specific domain models
- LLM-controlled grading, financial calculation, authorization, or portfolio mutation
- Separate community and cloud domain implementations
- A notebook serving as production application logic
