# Web Application

This directory will contain the TypeScript learner-facing application.

Planned structure:

```text
src/
|-- app/                 routing and composition
|-- features/            module-aligned learner/admin experiences
|-- components/          shared presentational components
|-- design-system/       semantic tokens and production icon assets
|-- platform/            API, auth, configuration, and telemetry clients
`-- generated/api-client/ generated from reviewed OpenAPI
tests/
```

The web application uses public generated clients. It does not import backend internals, own authoritative domain policy, or access databases/providers directly.

## Interface Design System

All interface work must follow:

- [Interface Design System](../../docs/design/README.md)
- [Interface Style Guide](../../docs/design/style-guide.md)
- [Interface Design Standards](../../docs/standards/interface-design-standards.md)
- [Executable tokens](src/design-system/tokens.css)
- [Production iconography](src/design-system/icons/README.md)

Feature code consumes semantic tokens and the reviewed icon pack. It must not introduce a parallel feature-local palette, spacing scale, theme map, shadow system, or icon set.

When shared visual behavior changes, update the design guide, executable assets, consumers, and relevant visual/accessibility tests together. Run:

```powershell
python dev-tools/design/check_design_system.py
python dev-tools/documentation/check_docs.py
```
