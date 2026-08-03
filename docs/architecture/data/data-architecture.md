# Data Architecture

- Status: accepted
- Canonical for: transactional, analytical, object, and provenance boundaries

## Stores

| Store | Intended use | Not intended for |
| --- | --- | --- |
| PostgreSQL | Transactional state, relationships, job metadata, projections, audit references | Large immutable analytical history |
| Parquet | Versioned market history, features, experiment datasets, backtest outputs | Mutable transactional workflows |
| DuckDB | In-process analysis over Parquet and bounded local analytical data | Multi-user transactional source of truth |
| Object storage | Content, imports, exports, generated artifacts, dataset objects | Unindexed business state |

## Data Zones

- **Raw:** provider response or source artifact retained only when licensing, privacy, and retention permit.
- **Canonical:** normalized platform-owned records with validation and provenance.
- **Derived:** features, projections, aggregates, learner state, valuations, and experiment datasets.
- **Published:** immutable/versioned datasets or artifacts approved for reuse.

## Rules

- Every externally sourced record retains provider and retrieval provenance.
- Market observations distinguish source time, effective market time, retrieval time, adjustment policy, currency, calendar, and quality flags.
- Learner data and market datasets have separate classification, access, and retention policies.
- Tenant/organization context is explicit in cloud-owned transactional and object keys.
- Raw provider data never bypasses normalization into portfolio, learning, or adaptation behavior.
- Derived datasets identify inputs, transformations, code/version, creation time, and intended use.
- Database abstraction does not promise portability between behaviorally different databases; PostgreSQL is used in both supported deployment profiles.

