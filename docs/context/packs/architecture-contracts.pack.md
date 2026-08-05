# Context Pack: Architecture and Contracts

## Use When

Work affects repository placement, modules, dependencies, APIs, events, portable records, providers, plugins, or generated bindings.

## Preserve

- Domain points inward and does not depend on frameworks/providers.
- Modules communicate through public application operations or versioned events.
- The first learning loop keeps Content, Curriculum, Assessment, Learner model, and Audit as distinct semantic owners.
- Identity providers resolve to one platform-owned learner-context contract; provider payloads stay private to Identity adapters.
- Versioned lessons use the platform-owned ADR-0007 content-package contract; package and provider inputs remain untrusted.
- Exact external shapes live in executable schemas.
- ADR-0009 fixes the initial runtime/framework lines while generated OpenAPI clients remain the browser data authority and Node remains build/test tooling only.
- The qualified approved-lesson seam keeps Content, Curriculum, and Identity behind public operations from PostgreSQL/filesystem through the generated client to the closed browser renderer.
- Provider-specific payloads stay in adapters.
- Generated artifacts are reproducible and not hand-edited.

## Canonical Sources

- `docs/architecture/README.md`
- `docs/adr/ADR-0005-first-learning-loop-module-ownership.md`
- `docs/adr/ADR-0006-setup-selectable-learner-identity.md`
- `docs/adr/ADR-0007-platform-owned-versioned-lesson-package.md`
- `docs/adr/ADR-0009-initial-application-framework-runtime-baseline.md`
- `docs/architecture/modules/module-map.md`
- `docs/architecture/modules/module-dependency-rules.md`
- `docs/architecture/contracts/contract-architecture.md`
- `docs/architecture/contracts/identity-provider-contract.md`
- `docs/architecture/contracts/content-package-contract.md`
- `docs/architecture/contracts/provider-and-plugin-contracts.md`
- `docs/architecture/contracts/compatibility-and-versioning.md`

## Stop When

Work reverses dependency direction, introduces an unreviewed execution boundary, or makes a breaking contract change without a decision.
