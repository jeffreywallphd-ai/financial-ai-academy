# Python Backend

This directory will contain the Python modular monolith and its API, worker, and CLI hosts.

Planned structure:

```text
src/financial_ai_academy/
|-- modules/             module-first domain/application/ports/adapters
|-- platform/            database, storage, events, jobs, security, observability
|-- hosts/               API, worker, and CLI entry points
|-- bootstrap/           validated adapter selection and composition
`-- generated/           generated contract bindings
tests/
|-- unit/
|-- contract/
|-- integration/
|-- architecture/
`-- fixtures/
```

Do not add framework or provider dependencies to domain code. See `docs/architecture/system/modular-monolith.md` and the module dependency rules before implementation.

