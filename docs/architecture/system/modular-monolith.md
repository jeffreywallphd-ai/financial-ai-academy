# Modular Monolith

- Status: accepted
- Canonical for: module ownership and internal layering
- Related docs: `../modules/module-map.md`, `../modules/module-dependency-rules.md`

## Model

The backend is one versioned Python application with multiple hosts. It is organized module-first and layer-second so each business capability owns its vocabulary, use cases, ports, adapters, and tests.

```text
module/
|-- domain/
|-- application/
|-- ports/
|-- adapters/
`-- tests/
```

## Layer Responsibilities

| Layer | Owns | Must not own |
| --- | --- | --- |
| Domain | Entities, value objects, invariants, domain services, domain events | Frameworks, transport, persistence, provider SDKs |
| Application | Commands, queries, workflows, policy coordination | HTTP, SQL, vendor payloads, UI state |
| Ports | Capabilities required by application behavior | Concrete provider selection |
| Adapters | Translation to databases, providers, queues, files, and transports | New domain policy |
| Hosts | Configuration, composition, lifecycle, authentication context, transport startup | Feature business rules |

## Module Communication

- Synchronous coordination uses a published application operation with a typed request and result.
- Asynchronous coordination uses a versioned event and idempotent consumer.
- A module may retain a stable identifier owned by another module, but it may not load or mutate the other module's persistence representation directly.
- Cross-module database joins are prohibited in application behavior. Read-optimized projections may be created by an explicitly owning reporting or projection component.

## Extraction Rule

A module may become a separately deployed service only when there is evidence for materially different scaling, stronger isolation, independent availability/release needs, independent ownership, or an external protocol boundary that already exists.

Extraction must preserve the public application/event contract and add explicit operational ownership, failure, compatibility, and migration decisions.

