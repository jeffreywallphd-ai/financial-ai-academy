# Guidance Module

Guidance owns safe versioned projections that explain platform concepts,
methods, limitations, and troubleshooting. Canonical product, domain,
architecture, contract, risk, and method sources retain their meaning.

The implemented boundary contains pure immutable `platform-help/v1` values,
contract parsing/projection, exact-version lookup, deterministic literal
search, a checked-in starter corpus, and a transport-neutral application/public
seam. Composition admits every JSON resource as one corpus before the API can
serve it; an invalid, duplicated, stale, or internally inconsistent record
rejects startup rather than exposing a partial result.

The protected API uses the same Guidance operations for browser, command-line,
service, and future headless-AI callers. It has no database, request-time
repository-document read, network, model, provider, grading, eligibility,
learner-state, or financial-action dependency. Provider payloads and authoring
sources remain outside domain values.

Contributions to the immutable corpus follow `resources/README.md`. Published
meaning changes require an exact new version and updated source fingerprint;
runtime code never treats repository Markdown as content storage.
