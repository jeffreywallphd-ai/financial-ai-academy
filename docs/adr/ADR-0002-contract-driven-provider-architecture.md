# ADR-0002: Contract-Driven Provider Architecture

- Status: accepted
- Date: 2026-08-03

## Context

Market data, AI models, content, identity, storage, and job systems will vary across local and cloud deployments and over the life of the product.

## Decision

Define platform-owned, versioned contracts for APIs, events, portable records, providers, and plugin manifests. Providers translate external shapes into canonical platform contracts and pass reusable conformance suites.

REST OpenAPI is generated from validated API models and committed for review. JSON Schema is canonical for events, portable records, and provider/plugin manifests.

## Consequences

- Provider-specific payloads do not leak into domain behavior.
- Generated clients and bindings are reproducible artifacts.
- Compatibility is classified and tested.
- Installable extensions require manifests, capability declarations, trust review, and explicit execution boundaries.

## Rejected Alternatives

- Direct provider SDK calls from domain/application code
- Informal dictionary-shaped integrations
- One universal unversioned plugin interface

