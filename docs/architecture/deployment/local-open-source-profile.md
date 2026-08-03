# Local Open-Source Deployment Profile

- Status: accepted
- Canonical for: supported local system shape

## Components

- TypeScript web application
- Python API host
- Python worker host
- PostgreSQL
- Local filesystem through the object-storage port
- DuckDB and Parquet for analytical work
- Local or externally configured market-data and model providers

The initial distribution target is a reproducible container-based installation with a small launcher or CLI. Local data remains under an explicitly documented application data root and is included in backup/export workflows.

## Requirements

- No commercial service is required for core learning, assessment, portfolio simulation, or backup/export behavior.
- External API credentials are user-supplied and stored outside portable configuration.
- Network-dependent capabilities expose quota, availability, and offline limitations.
- Unsupported cloud-only administrative capabilities are absent or explicitly identified; core domain semantics remain consistent.

