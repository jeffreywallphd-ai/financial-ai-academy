# Contract Governance

- Status: accepted
- Canonical for: contract catalog and conformance documentation

Executable OpenAPI, JSON Schema, examples, and compatibility fixtures belong under top-level `contracts/`. This directory documents contract ownership, semantics, evolution, and conformance.

Start with:

- `docs/architecture/contracts/contract-architecture.md`
- `docs/architecture/contracts/provider-and-plugin-contracts.md`
- `docs/architecture/contracts/compatibility-and-versioning.md`
- `docs/architecture/contracts/content-package-contract.md`
- `docs/standards/contract-compatibility-standards.md`

Add a detailed catalog when the first executable contract family is introduced. Do not create placeholder schemas that imply unsettled domain meaning.

Current learning contract families are cataloged in
[`contracts/learning/README.md`](../../contracts/learning/README.md). They now
include additive Assessment practice draft/retry shapes, Curriculum exact
practice-review targets, and Learner-model practice-history projections. Each
has executable Draft 2020-12 schemas, synthetic compatibility fixtures, and a
dependency-light conformance runner. These records do not authorize
persistence, public APIs, browser behavior, mastery, adaptive ranking, or AI
authority.

ADR-0007 accepts the semantic boundary for versioned lesson packages. Exact manifest and assessment schemas, fixtures, canonicalization vectors, and conformance commands remain delivery artifacts and must not be added outside an approved vertical slice.
