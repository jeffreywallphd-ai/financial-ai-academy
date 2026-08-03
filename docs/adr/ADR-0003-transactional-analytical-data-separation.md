# ADR-0003: Transactional and Analytical Data Separation

- Status: accepted
- Date: 2026-08-03

## Context

Learner/course/portfolio state needs transactional integrity, while price history, features, experiments, and backtests need efficient analytical processing and portable datasets.

## Decision

Use PostgreSQL as the transactional system of record in both local and cloud profiles. Use Parquet for larger immutable or versioned analytical data and DuckDB for in-process analysis. Use an object-storage port for content, imports, exports, datasets, and generated artifacts.

## Consequences

- Local installation includes PostgreSQL rather than a behaviorally different transactional database.
- Analytical storage is not used as mutable application state.
- Data lineage, timestamps, adjustment policy, and licensing metadata are first-class.
- Storage adapters may differ by deployment while keys and semantics remain stable.

## Rejected Alternatives

- SQLite locally with PostgreSQL only in cloud
- A separate distributed warehouse at project inception
- A time-series or vector database before evidence requires it

