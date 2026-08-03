# Financial AI Academy

Financial AI Academy is a planned open-source and commercializable platform for adaptive learning about financial investing, financial AI, and machine learning.

The platform is being designed around:

- individualized learning pathways driven by explicit learner evidence,
- deterministic policy surrounding AI-assisted tutoring and recommendations,
- provider-neutral contracts for market data, models, content, storage, identity, and jobs,
- a Python modular-monolith backend with independently runnable API and worker hosts,
- a TypeScript web application,
- PostgreSQL transactional storage and Parquet/DuckDB analytical storage,
- one shared application core for local open-source and managed-cloud profiles.

## Current Status

The repository is in its architecture and documentation foundation stage. Application implementation has not started.

## Start Here

- Contributors and automated agents: read [AGENTS.md](AGENTS.md).
- Documentation governance: read [docs/README.md](docs/README.md).
- Architecture: begin with [architecture principles](docs/architecture/system/architecture-principles.md) and the [system overview](docs/architecture/system/system-overview.md).
- Decisions: use the [ADR index](docs/adr/README.md) and [decision-readiness register](docs/adr/decision-readiness.md).
- Contracts: use the [contract architecture](docs/architecture/contracts/contract-architecture.md) and top-level [contracts map](contracts/README.md).

## License

This repository is currently licensed under the GNU General Public License v3.0. Commercial packaging, hosted services, separately distributed extensions, and any additional licensing model require explicit legal and product decisions; the existing license must not be silently reinterpreted.

## Documentation Validation

```text
python dev-tools/documentation/check_docs.py
```
