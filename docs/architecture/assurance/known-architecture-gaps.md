# Known Architecture Gaps

- Status: current
- Canonical for: visible architecture decisions and evidence not yet available

## Decision Gaps

- Organization identity/tenancy administration and identity-mode migration
- Cloud infrastructure provider and deployment tooling
- Job-queue implementation and delivery guarantees
- Exact multi-tenant placement and row-policy design
- Content authoring workflow and tooling
- External learning interoperability scope
- Model-provider admission and local-model support matrix
- Market-data licensing policy by provider and edition
- Experiment governance and consent details
- Managed-cloud encryption, key custody, backup automation, retention, availability, RPO, and RTO

## Evidence Gaps

- Current dependency checks cover the implemented Content, Curriculum,
  Identity, generated-client, browser, and local-composition seams; remaining
  modules, events, providers, workers, and analytical boundaries lack equivalent
  executable fitness functions.
- Python/Node manifests, exact locks, the Windows Node 24 build, dependency
  inventory, and the static/no-Node-server runtime boundary are executable.
  Multi-platform clean-install/build and production-distribution qualification
  remain absent.
- Executable lesson-package schemas, compatibility fixtures, OpenAPI, and the
  generated TypeScript client exist. Event, provider/plugin, finance, and
  external-learning contract families remain unimplemented.
- No provider conformance suite exists yet.
- The loopback private-host approved-lesson composition is directly qualified
  with PostgreSQL 18.4, filesystem objects, Python same-origin static/API
  serving, and pinned Chromium. Complete local distribution, workers,
  analytics, built-in/OIDC identity, passive assets, remote operation, and all
  managed-cloud qualification remain absent.
- No community backup/restore tooling, manifest contract, supported-platform permission profile, compatibility matrix, or controlled restore qualification exists yet.
- No model or adaptive-learning evaluation harness exists yet.

These gaps are not authorization to choose a design silently. Move a gap into an accepted ADR and the applicable architecture/verification documents before relying on it for implementation.
