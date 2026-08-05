# Local Open-Source Deployment Profile

- Status: accepted
- Canonical for: supported local system shape

## Components

- React 19/TypeScript 7 static web application built with React Router 8 Data Mode and Vite 8
- CPython 3.14 API host using FastAPI 0.141 and Pydantic 2.13
- Python worker host
- PostgreSQL
- One setup-selected identity adapter: single profile, built-in credentials, or external OIDC
- Local filesystem through the object-storage port
- DuckDB and Parquet for analytical work
- Local or externally configured market-data and model providers

The initial distribution target is a reproducible container-based installation with a small launcher or CLI. Local data remains under an explicitly documented application data root and is included in backup/export workflows.

Node.js 24 LTS is required to reproduce web generation, builds, and tests but is not a production application server. The local runtime serves the same static browser artifacts used by managed cloud and routes application calls to the Python API through the generated client.

## Requirements

- Setup explicitly selects exactly one identity mode. Single-profile mode is loopback-default and supported only for documented private-host use.
- Built-in and OIDC modes follow the shared [identity-provider and learner-context contract](../contracts/identity-provider-contract.md).
- Once identity bindings or learner evidence exist, mode mismatch fails closed and changing modes requires a separately approved migration.
- No commercial service is required for core learning, assessment, portfolio simulation, or backup/export behavior.
- External API credentials are user-supplied and stored outside portable configuration.
- Network-dependent capabilities expose quota, availability, and offline limitations.
- Approved lessons use the shared [versioned lesson content-package contract](../contracts/content-package-contract.md) through the local filesystem object-storage adapter; backup/export preserves exact package versions, digests, and provenance.
- Retained learner evidence follows [ADR-0008](../../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) and the [community protection boundary](../../security/community-learner-evidence-protection.md): private adequately protected host, restrictive application-data-root access, user-controlled encrypted host/backup media, and no protection claim against a compromised host or privileged administrator.
- Recovery uses a user-invoked, maintenance-mode coordinated PostgreSQL/object recovery set and an empty inactive restore target. Restored sessions and recovery credentials are revoked before activation; external secrets remain excluded.
- The community profile makes no RPO, RTO, availability, offsite, immutability, authenticity, or ransomware-resilience guarantee. Tooling and supported-platform qualification must exist before backup or restore is presented as operationally supported.
- Unsupported cloud-only administrative capabilities are absent or explicitly identified; core domain semantics remain consistent.

## Qualified Approved-Lesson Seam

The first directly qualified local seam is deliberately narrower than the
complete profile. `deployments/local/serve.py` composes the accepted
`single_profile` Identity path, Content/Curriculum public operations,
PostgreSQL 18.4, restrictive filesystem objects, the reviewed OpenAPI client,
and the exact static Vite output on one loopback Python application origin.
`tests/e2e/approved-lesson/run.py` starts an isolated PostgreSQL container and
filesystem root, admits the synthetic approved fixture, exercises success plus
missing-context and stale-placement denial in pinned Chromium, and tears down
only its named resources. Node is used to build and test those static bytes,
not to serve the application.

This evidence does not qualify built-in/OIDC identity, passive-asset delivery,
workers, analytics, backup/restore, remote/public operation, production
distribution, managed cloud, non-Chromium browsers, or recovery objectives.
Use [the local qualification guide](../../../deployments/local/README.md) for
the exact topology and commands.
