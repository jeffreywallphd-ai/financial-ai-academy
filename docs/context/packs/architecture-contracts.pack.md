# Context Pack: Architecture and Contracts

## Use When

Work affects repository placement, modules, dependencies, APIs, events, portable records, providers, plugins, or generated bindings.

## Preserve

- Domain points inward and does not depend on frameworks/providers.
- Modules communicate through public application operations or versioned events.
- Exact external shapes live in executable schemas.
- Provider-specific payloads stay in adapters.
- Generated artifacts are reproducible and not hand-edited.

## Canonical Sources

- `docs/architecture/README.md`
- `docs/architecture/modules/module-dependency-rules.md`
- `docs/architecture/contracts/contract-architecture.md`
- `docs/architecture/contracts/provider-and-plugin-contracts.md`
- `docs/architecture/contracts/compatibility-and-versioning.md`

## Stop When

Work reverses dependency direction, introduces an unreviewed execution boundary, or makes a breaking contract change without a decision.

