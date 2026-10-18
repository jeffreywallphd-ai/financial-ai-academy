# Guidance Module

Guidance owns safe versioned projections that explain platform concepts,
methods, limitations, and troubleshooting. Canonical product, domain,
architecture, contract, risk, and method sources retain their meaning.

The implemented boundary contains pure immutable `platform-help/v1`,
`contextual-help/v1`, and `feature-guidance/v1` values, strict contract
projection, exact-version lookup, deterministic literal topic search,
checked-in source-bound resources, and one transport-neutral application/public
seam. Composition admits the complete topic corpus and then the contextual and
feature-guidance registries before the API can serve them; an invalid,
duplicated, stale, dangling, or internally inconsistent record rejects startup
rather than exposing a partial result.

The protected API uses the same Guidance operations for browser, command-line,
service, and future headless-AI callers. Context reads return one exact routing
document whose ordered references open the existing exact topic operation.
Feature-guidance reads accept only an exact surface, condition, and mapping
version and return the admitted mapping plus its reviewed record without
interpreting feature state or substituting another version. Guidance has no
database, request-time repository-document read, network, model, provider,
grading, eligibility, learner-state, or financial-action dependency. Provider
payloads and authoring sources remain outside domain values.

The disposable local qualification reads every shipped exact context and
referenced topic through both an authenticated browser context and a fresh
ordinary HTTP client. It compares the complete ordered public documents and
digests before and after normal host restart, checks confidential unauthenticated
denial, observes no non-loopback browser request, and fingerprints all
non-Identity database schemas before and after the Guidance-only phase. This is
direct local evidence for the read-only boundary; it is not managed-cloud,
availability, or operating-system network-isolation evidence.

The browser is a generated-client consumer at `/help` and at exact
`/help/topics/{topic_id}/versions/{topic_version}` routes. It validates the
closed public response before rendering inert typed nodes, preserves
server-owned search order and cursors, and keeps exact source facts in a
progressive technical record. It owns no help corpus, ranking, authorization,
latest-version selection, analytics, or separate headless behavior.

Contributions to the immutable corpus and registry follow `resources/README.md`.
Published meaning changes require an exact new version and updated source
fingerprint; runtime code never treats repository Markdown as content storage.
