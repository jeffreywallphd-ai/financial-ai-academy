# ADR-0007: Platform-Owned Versioned Lesson Package

- Status: accepted
- Date: 2026-08-04
- Decision request: [DEC-0003](../planning/decision-requests/DEC-0003-versioned-lesson-package-format.md)

## Context

CAP-0001 needs a portable approved lesson with stable identity, objectives, educational sources, one deterministic knowledge check, feedback, assets, provenance, and immutable versions. A Markdown convention, persistence model, provider payload, archive type, or external learning standard must not become an accidental public contract. The same meaning must work through local filesystem and managed object-storage adapters.

## Decision

Adopt a small platform-owned lesson package consisting of a JSON manifest, constrained CommonMark lesson content, structured JSON assessment definitions, and declared assets.

- A directory is the logical package model. A deterministic archive may be used only as transport and cannot change normalized paths, referenced bytes, versions, digests, or semantics.
- Portable manifest and assessment records use platform-owned JSON Schema Draft 2020-12 contract families. Exact schemas are introduced only through approved delivery work.
- Published packages use a stable package ID, semantic package version, schema version, and immutable SHA-256 package digest. One `(package_id, package_version)` identifies one digest and cannot be republished with different bytes.
- The package digest is derived from a documented deterministic logical package index, independent of archive ordering, timestamps, compression, and storage metadata. Its exact canonicalization algorithm requires executable fixtures before release.
- Package references use normalized package-relative paths with declared media type, measured byte size, and SHA-256. Unsafe, ambiguous, duplicate, escaping, linked, missing, extra, or integrity-mismatched content is rejected.
- Version 1 lesson markup is constrained CommonMark with raw HTML, active embeds, inline SVG, executable extensions, and implicit network or filesystem access disabled. External links are limited to approved HTTPS locators. Version 1 learner-visible assets are passive raster images with accessibility text.
- Content owns package identity, publication state, lesson body, source provenance, and content storage references. Assessment owns item meaning, response validation, attempts, deterministic scoring, and completion evidence; package transport does not create a second scoring authority.
- Imported and provider-supplied packages are untrusted regardless of source or signature. Schema, semantic, path, media, integrity, resource-bound, and renderer validation applies at every admission boundary.
- Local and managed-cloud profiles interpret the same package identity, version, digest, contract versions, and learning meaning.

## Consequences

- Approved lessons are portable across source control, filesystem storage, object storage, import/export, and provider adapters without coupling their public meaning to persistence.
- Rich authoring systems and external learning standards can map through adapters later without becoming domain authority.
- Published learner evidence can retain exact package and assessment versions without silent `latest` substitution.
- Package validators, canonicalization fixtures, content renderers, media handling, compatibility tests, and resource limits become required executable evidence.
- The initial profile intentionally supports fewer content and assessment features than a general learning-content platform.

## Alternatives Rejected

- **Markdown with frontmatter only.** It leaves structured assessments, provenance, assets, validation, and compatibility underspecified.
- **Database-first normalized content.** It couples the portable lesson boundary to persistence and still requires import/export contracts.
- **An external learning-package standard as canonical.** The interoperability requirement is not yet selected and broader external semantics must not leak into the initial domain contract.
- **A canonical archive format.** Archive mechanics are transport concerns and must not determine logical identity or meaning.
- **A sanitized HTML subset for version 1.** Constrained CommonMark presents a smaller initial renderer attack surface.
- **Digest-only asset references.** Relative declared paths remain author-reviewable while per-file and package digests preserve integrity.

## Boundaries

This decision does not accept exact executable field names, canonicalization bytes, package size/count limits, archive format, parser or sanitizer library, persistence schema, API shape, content signing, authoring workflow, localization workflow, additional media or assessment types, remote embeds, or external learning-standard interoperability. Each requires approved planning and applicable security, compatibility, and product review.

This decision authorizes canonical architecture promotion only. It does not select a vertical slice, approve a work packet, or authorize implementation.

## Verification Implications

- Add positive and negative schemas and fixtures for manifest and assessment records.
- Prove stable package digest calculation across supported platforms and transports.
- Reject malformed schemas, unsupported versions/capabilities, unsafe or colliding paths, media mismatches, integrity failures, active content, unsafe URLs, resource exhaustion, and immutable-version conflicts.
- Prove Assessment remains the sole runtime scoring authority and exact versions remain attached to evidence.
- Run the same conformance corpus through local filesystem and managed object-storage adapters.
- Keep coverage classified as a gap until executable checks own these claims.

## Supersession

None. Changes to the logical package, immutability rule, markup trust profile, asset trust boundary, or module ownership require a superseding ADR and compatibility/migration analysis.
