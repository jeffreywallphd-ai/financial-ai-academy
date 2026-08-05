# Provider and Plugin Contracts

- Status: accepted
- Canonical for: replaceable external capability boundaries

## Provider Families

Initial provider families include market data, AI/model inference, content repositories, object storage, identity, job execution, and notifications.

## Required Manifest Information

Every installable provider declares:

- provider identity and semantic version,
- implemented contract versions,
- capabilities and limitations,
- configuration schema,
- required secrets,
- outbound hosts or other egress,
- data categories received or emitted,
- rate, quota, and payload bounds,
- health and readiness behavior,
- licensing and attribution metadata where applicable.

## Boundary Rules

- Provider payloads are untrusted input.
- Raw responses are not domain objects.
- Normalization records provider, retrieval time, source timestamps, transformations, quality flags, and licensing/attribution references.
- A missing capability is reported explicitly; adapters do not fabricate support.
- Read operations do not silently install, repair, authenticate, or upgrade a provider.
- Secrets are resolved by the host and are never stored in portable provider manifests.

## Execution Model

- Vetted first-party adapters may run in process for local and controlled deployments.
- Untrusted or independently supplied cloud extensions run out of process with restricted credentials, filesystem access, network egress, resource bounds, and explicit capability brokering.
- Inspection and admission never execute plugin code.

## Conformance

Each provider family has reusable conformance tests for successful behavior, missing capabilities, malformed results, timeouts, quota failures, cancellation, safe diagnostics, provenance, and idempotency where applicable.

Identity providers additionally follow the [identity provider and learner-context contract](identity-provider-contract.md). Identity mode, subject mapping, session, recovery, and authorization semantics cannot be replaced by a generic provider payload.

Content providers additionally follow the [versioned lesson content-package contract](content-package-contract.md). Provider packages remain untrusted input; provider identity or signatures do not bypass schema, semantic, path, media, integrity, resource-bound, or renderer validation.
