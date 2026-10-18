# Guidance Module

Guidance owns safe versioned projections that explain platform concepts,
methods, limitations, and troubleshooting. Canonical product, domain,
architecture, contract, risk, and method sources retain their meaning.

The initial boundary contains only pure immutable `platform-help/v1` values,
contract parsing/projection, exact-version lookup, and deterministic literal
search. It has no database, filesystem, network, FastAPI, browser, model,
provider, grading, eligibility, or financial-action dependency.

Future composition must use the Guidance public/application seam and keep
provider payloads and authoring sources outside domain values. An invalid
corpus is rejected atomically before any topic becomes visible.
