# Versioned Lesson Content-Package Contract

- Status: accepted
- Canonical for: semantic package boundary, ownership, versioning, integrity, and safe rendering
- Decision: [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md)
- Exact shapes: [lesson-package v1 JSON Schemas](../../../contracts/learning/lesson-package/v1/README.md)
- Executable evidence: [lesson-package v1 compatibility corpus](../../../contracts/compatibility/lesson-package/v1/README.md)

## Purpose

The content package is the portable published representation of one approved lesson and its bounded assessment references. It is independent of provider payloads, storage keys, database layouts, archive metadata, and mutable authoring state.

## Logical Package

The logical model is a directory containing:

- one JSON manifest;
- one constrained CommonMark lesson body;
- one or more structured JSON assessment-definition files;
- zero or more declared passive assets.

An archive may transport this directory only after its format and extraction controls are separately approved. Transport must preserve normalized paths, bytes, semantic versions, file digests, and package digest.

## Ownership

| Concern | Owner | Rule |
| --- | --- | --- |
| Package identity, version, publication, body, sources, provenance, and storage references | Content | Content validates and publishes immutable package versions |
| Curriculum placement | Curriculum | Curriculum retains exact package and assessment version references without reading Content persistence |
| Assessment definition semantics, responses, attempts, scoring, and completion evidence | Assessment | Package transport never grades or becomes assessment authority |
| Learner completion projection | Learner model | Projection retains exact source-evidence and package-version references |
| Provider translation | Content adapter | External formats normalize to this contract and retain provider/import provenance |

## Identity, Versioning, and Immutability

- `schema_version` identifies the portable-record contract family version.
- `package_id` is stable across storage locations and providers.
- `package_version` is a semantic version of the published lesson artifact.
- `package_digest` is lowercase SHA-256 over a deterministic logical package index whose exact canonicalization is fixed by executable compatibility vectors.
- A published `(package_id, package_version)` maps to one digest. A conflicting digest is rejected without replacing the accepted artifact.
- Changes to lesson meaning, objectives, educational-source metadata, assessment definitions, feedback, assets, or declared provenance require a new package version.
- Consumers resolve exact versions and reject unsupported major versions or unrecognized security-relevant capabilities. They never silently substitute `latest`.

## References and Integrity

Every referenced file declares a normalized package-relative path, media type, measured byte size, and SHA-256 digest. Stable IDs and versions are also required where semantics cross module boundaries.

Version 1 paths use forward-slash-separated relative segments from a conservative portable profile. Validation rejects absolute, drive, UNC, empty, dot, dot-dot, backslash, control, NUL, hidden, reserved-device, case-colliding, normalization-ambiguous, linked, or root-escaping paths. Referenced files must exist exactly once; undeclared extras and integrity or media mismatches fail the entire package.

## Content and Renderer Trust Profile

- CommonMark is parsed through a platform profile; raw HTML and unapproved extensions are rejected.
- Allowed document nodes and attributes form a constrained intermediate representation before rendering.
- External links use approved HTTPS locators. Active, local-file, data, blob, protocol-relative, obfuscated, and unknown schemes are rejected after normalization.
- Images resolve only through declared package assets and an application-controlled content handler.
- Version 1 assets are limited to passive PNG, JPEG, and WebP images with required accessibility text. SVG, HTML, PDF, audio, video, fonts, archives, and executable content require a reviewed profile expansion.
- Validation and rendering do not implicitly fetch remote content, access files outside the package, execute code, inject styles, or create active embeds.
- Context-aware encoding, safe DOM sinks, maintained sanitization, Content Security Policy, and Trusted Types are layered controls; no one control expands accepted package authority.

## Validation Boundary

Admission is atomic and validates:

1. supported schema and package versions;
2. JSON Schema shape;
3. package-wide semantic invariants and unique identifiers;
4. normalized paths and file-set closure;
5. measured size, digest, and sniffed media type;
6. assessment types, option membership, and scoring-policy identity through Assessment;
7. markup nodes, links, and assets through the versioned renderer profile;
8. configured entry, per-file, total-size, and processing limits;
9. immutable identity/version/digest conflicts;
10. bounded structured diagnostics that safely encode untrusted values.

Provider identity, signatures, or prior storage do not bypass validation. Failed admission creates no partial publication or assessment registration.

### Executable Version 1 Profile

The executable profile uses schema version `1.0.0` and permits only these declared capabilities:

- `lesson.commonmark.v1`;
- `asset.raster.v1`;
- `assessment.reference.v1`.

The manifest schema delegates source, lesson-file, assessment-file, passive-image, and package-index records to stable Draft 2020-12 schema identifiers under `contracts/learning/lesson-package/v1/`. The assessment record is deliberately closure-only: it assigns no answer, scoring, attempt, or completion authority to Content.

Admission enforces these initial measured limits:

| Resource | Limit |
| --- | ---: |
| Package files | 128 |
| Total package bytes | 32 MiB |
| Individual file bytes | 8 MiB |
| Manifest bytes | 256 KiB |
| Lesson CommonMark bytes | 1 MiB |
| Raster image pixels | 16,000,000 |
| CommonMark nesting level | 32 |

Diagnostics expose a stable code, a reference truncated to 120 characters with control line breaks removed, and a bounded platform-authored message. They do not return untrusted file bytes, raw markup, external filesystem paths, stack traces, or accepted/conflicting digests.

### Canonical Index and Digest

The logical index contains every measured package file, including `manifest.json`, exactly once. Each index entry contains exactly `path`, `media_type`, `size_bytes`, and lowercase `sha256`. Entries sort by the UTF-8 bytes of normalized logical paths. The array is serialized as UTF-8 JSON with object keys sorted lexicographically, separators `,` and `:`, Unicode unescaped, and no trailing newline. `package_digest` is lowercase SHA-256 over those bytes.

The approved fixture fixes the package digest as `576d543b404a7f70f2e5bebee55c32a3f945d8e8da73654c43ef92e656aee008`; the committed vector also carries the full canonical-byte hexadecimal value and each file measurement. The digest is publication metadata and is deliberately absent from `manifest.json`, preventing a circular digest.

## Compatibility and Conformance

The contract family follows [compatibility and versioning](compatibility-and-versioning.md). Additive optional fields are accepted only when documented compatibility and fixtures demonstrate safety. Unknown item types, scoring policies, markup extensions, media classes, or other security-relevant capabilities fail closed.

The version 1 schemas, representative and malicious fixtures, deterministic
digest vectors, semantic-validator tests, parser-profile security tests, and
immutable-version conflict tests are executable. The approved-lesson seam also
directly qualifies PostgreSQL Content metadata, restrictive local filesystem
objects, exact-version Curriculum placement/read behavior, the closed safe
body-node representation, the reviewed API/generated client, and browser
rendering for the approved no-asset fixture. Managed object storage, real
passive-asset delivery, archive transport, authoring, and complete local/cloud
adapter parity remain future evidence and must not be inferred.

## Explicit Non-Scope

Mutable authoring projects, authoring UI, publication workflow, localization workflow, content signing, remote embeds, rich simulations, additional assessment types, external learning standards, and archive selection are not accepted by this contract.
