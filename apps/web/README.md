# Web Application

This directory will contain the TypeScript learner-facing application.

Planned structure:

```text
src/
|-- app/                 routing and composition
|-- features/            module-aligned learner/admin experiences
|-- components/          shared presentational components
|-- platform/            API, auth, configuration, and telemetry clients
`-- generated/api-client/ generated from reviewed OpenAPI
tests/
```

The web application uses public generated clients. It does not import backend internals, own authoritative domain policy, or access databases/providers directly.

