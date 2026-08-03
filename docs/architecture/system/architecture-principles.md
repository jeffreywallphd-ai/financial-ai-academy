# Architecture Principles

- Status: accepted
- Canonical for: repository-wide architectural constraints
- Related ADRs: ADR-0001 through ADR-0004

## Principles

1. **One product core.** Local open-source and managed-cloud deployments use the same domain and application code. Infrastructure and entitlements vary through explicit adapters and configuration.
2. **Modular monolith first.** Begin with strong in-repository boundaries and independently runnable API and worker processes. Extract a service only when scaling, isolation, ownership, or release evidence justifies it.
3. **Contracts are explicit.** Public APIs, events, files, providers, and plugin manifests use versioned, language-neutral schemas with compatibility tests.
4. **Modules own behavior and data.** A module does not read another module's tables or import its internals. Coordination uses public application operations or published events.
5. **Providers remain replaceable.** Market-data, model, content, storage, identity, and job providers implement platform-owned ports. Provider-specific shapes do not become domain models.
6. **Deterministic policy surrounds AI.** Models may rank, explain, tutor, or propose. Deterministic application and domain policy owns eligibility, authorization, grading, financial calculations, and durable state transitions.
7. **Evidence and provenance are first-class.** Learning recommendations, assessments, market observations, generated content, model outputs, and portfolio results retain source and version information sufficient for explanation and replay.
8. **Transactional and analytical workloads are separated.** PostgreSQL is the system of record. Parquet and DuckDB support bulk analysis, feature work, and backtesting.
9. **Secure and private by default.** Least privilege, tenant context, data minimization, safe diagnostics, explicit external egress, and fail-closed provider behavior apply at every boundary.
10. **Architecture claims require evidence.** Important constraints should eventually be backed by executable checks. Unverified claims remain visibly recorded as gaps.
11. **Generated artifacts are not hand-edited.** Generated API clients, schema bindings, and contract snapshots identify their source and regeneration command.
12. **No speculative distribution.** Abstractions and deployable units are introduced to protect a current boundary, not to imitate a hypothetical future microservice estate.

