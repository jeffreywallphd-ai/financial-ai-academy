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

- Exact allowlisted, reviewed packaged adapters in ADR-0018's initial trusted class may run in process for local and controlled deployments.
- Runtime download, arbitrary module paths, editable-source discovery, dependency installation, entry-point scanning, and marketplace-style activation are excluded.
- Untrusted or independently supplied extensions are not admitted by the initial baseline. Any future admission requires a separately accepted out-of-process host with restricted credentials, filesystem access, network egress, resource bounds, and explicit capability brokering.
- Inspection and admission never execute plugin code.

## Conformance

Each provider family has reusable conformance tests for successful behavior, missing capabilities, malformed results, timeouts, quota failures, cancellation, safe diagnostics, provenance, and idempotency where applicable.

Identity providers additionally follow the [identity provider and learner-context contract](identity-provider-contract.md). Identity mode, subject mapping, session, recovery, and authorization semantics cannot be replaced by a generic provider payload.

Content providers additionally follow the [versioned lesson content-package contract](content-package-contract.md). Provider packages remain untrusted input; provider identity or signatures do not bypass schema, semantic, path, media, integrity, resource-bound, or renderer validation.

Content authoring and future interoperability providers additionally follow
[ADR-0017](../../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md)
and the [content-authoring workflow contract](content-authoring-workflow-contract.md).
No external learning-standard profile is currently admitted. Any future adapter
keeps standard payloads private, emits a deterministic mapping report, and
cannot supply human review or bypass native validation and publication policy.

Model providers additionally follow
[ADR-0013](../../adr/ADR-0013-explicit-model-provider-opt-in.md). A manifest must
declare local or external execution, model capability limits, all received and
emitted data classes, outbound hosts, retention/training/secondary-use posture,
redaction, cost/quota signals, and disablement behavior. Admission requires
current evidence; credentials do not enable an adapter. Invocation requires the
selected provider instance and every operation data class to be explicitly
permitted, with a deterministic no-model fallback.

Market-data providers additionally follow
[ADR-0015](../../adr/ADR-0015-market-data-portfolio-method-registry.md) and
[ADR-0020](../../adr/ADR-0020-staged-market-data-sourcing-with-alpha-vantage-first.md).
The platform contract owns instrument and coverage identity, bounded queries,
canonical observations, calendars, corporate actions, adjustments, quality,
times, provenance, attribution, and applicable-use references. Provider SDK
types, endpoint names, identifiers, quota messages, and raw payloads remain
inside adapters. Every configured operation is checked against an exact current
provider/plan/dataset/deployment/audience/use profile; missing or ambiguous
rights deny only that operation. Alpha Vantage is the first adapter target, not
a required provider or contract shape, and conformance also runs against an
independent fake/reference adapter.

An admitted model or job provider is not thereby an experiment executor.
[ADR-0016](../../adr/ADR-0016-learner-managed-experiment-execution.md) admits
only learner-managed execution with validated result import. A future analytics
sandbox or execution-provider adapter requires separate durable authority and
qualification even when it implements the provider-neutral run/result seam.

All provider-triggering asynchronous work follows
[ADR-0018](../../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md)
and the [durable job-delivery contract](job-delivery-contract.md). Delivery is
at least once; handlers require effect-level idempotency or reconciliation, and
timeouts or cancellation do not imply an external provider stopped.
