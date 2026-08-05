---
id: DEC-0003
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-08-04
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0007-platform-owned-versioned-lesson-package.md
---

# Decision Request: Choose the Initial Versioned Lesson Package

## Decision Needed

Choose the minimum durable, portable representation for an approved lesson, its sources and assets, and one structured deterministic knowledge check in CAP-0001.

## Why Now

Candidate A needs a lesson with a stable identity, version, objectives, content, and source provenance. Candidate B needs a machine-validated assessment definition that can be scored deterministically. Without an accepted package boundary, a seed file or database shape could become an accidental public content standard and make local/cloud portability or future authoring unnecessarily difficult.

## Current Authority and Constraints

- The [contract architecture](../../architecture/contracts/contract-architecture.md) makes JSON Schema canonical for portable records and requires explicit versioning, ownership, examples, and conformance tests.
- [ADR-0002](../../adr/ADR-0002-contract-driven-provider-architecture.md) requires content providers to translate through platform-owned contracts.
- The [data architecture](../../architecture/data/data-architecture.md) assigns content and published artifacts to object storage while transactional state remains in PostgreSQL.
- The [local profile](../../architecture/deployment/local-open-source-profile.md) requires portable backup/export and an explicitly documented data root.
- The same lesson meaning and contract version must work in local and cloud profiles.
- Content authoring UI, full publication workflows, localization, external learning standards, and complex assessment types are outside CAP-0001.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| Initial package representation | ready | A. Platform-owned JSON manifest, constrained Markdown content, structured assessment data, and assets | Use Option A as accepted by ADR-0007 | None - ADR-0007 |
| Logical package container | constrained | A1. Directory is the logical model, with a deterministic archive allowed only as transport | Use Option A1 as accepted by ADR-0007 | None - ADR-0007 |
| Package version and immutability | constrained | V1. Semantic package version plus immutable content digest | Use Option V1 as accepted by ADR-0007 | None - ADR-0007 |
| Lesson markup profile | constrained | M1. Constrained CommonMark with raw HTML and active embeds disabled | Use Option M1 as accepted by ADR-0007 | None - ADR-0007 |
| Asset addressing | constrained | H1. Normalized package-relative paths plus declared media type, size, and SHA-256 digest | Use Option H1 as accepted by ADR-0007 | None - ADR-0007 |
| Portable-record schema dialect | constrained | JSON Schema Draft 2020-12 under the platform-owned learning contract family | Use the accepted JSON Schema path | None - contract architecture |
| Assessment semantic ownership | constrained | The package transports versioned assessment definitions, while Assessment alone owns item meaning, response validation, attempts, and deterministic scoring | Preserve the ADR-0005 Assessment boundary | None - ADR-0005 |
| Local and cloud interpretation | ready | The same package identity, version, digest, and semantics in both deployment profiles | Preserve shared-core parity | None - ADR-0004 |

Canonical authority for the nonblocking rows:

- The [contract architecture](../../architecture/contracts/contract-architecture.md) makes JSON Schema canonical for portable learning records and assigns one owner, version, compatibility policy, examples, and conformance tests.
- [ADR-0005](../../adr/ADR-0005-first-learning-loop-module-ownership.md) assigns assessment item definitions, attempts, responses, and deterministic scoring evidence to Assessment; a content package cannot become a second scoring authority.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md) requires the same core semantics and public contract versions in local and managed-cloud profiles.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Platform-owned package with JSON manifest, Markdown content, structured assessment data, and assets | Creates an explicit portable contract with schema validation, readable content, deterministic assessment fields, provenance, checksums, and immutable versions. Works in source control, local files, object storage, imports, and provider adapters. | Requires an initial schema, package validator, canonicalization rules, and later authoring tools. Markdown capabilities and asset references must be constrained safely. | Content-package JSON Schema, assessment-item schema, package validator, content-provider port, object keys, import/export, provenance and compatibility tests. | High. New fields and content renderers can evolve through versioned contracts; external formats can map through adapters. |
| B. Markdown files with frontmatter only | Very easy to author and inspect manually; minimal initial tooling. | Complex assessment structures, citations, localization, assets, validation, and compatibility become ad hoc. Frontmatter may become an underspecified public API. | Markdown/frontmatter parser, local file layout, renderer security, implicit assessment conventions. | Medium. Migration requires parsing every historical convention into a formal schema. |
| C. Database-first normalized content model | Supports rich querying and future authoring workflows. | Couples the first content contract to persistence, weakens portable local packages, and still requires an import/export representation. | PostgreSQL schema, migrations, authoring APIs, publication snapshots, export format. | Low to medium. Published content must later be separated from mutable authoring state. |
| D. Adopt an external learning-package standard as canonical | May improve interoperability and access to third-party tooling. | The required interoperability scope is undecided; standards may carry broad semantics and assessment models not needed by CAP-0001. Provider-specific or standard-specific meaning could leak into the domain. | Standard parser/exporter, conformance suite, content and assessment mappings, licensing and compatibility review. | Medium. Adapters can be retained, but removing canonical standard semantics from domain contracts may be costly. |

## Recommendation

**Recommend Option A: a small platform-owned, versioned package with a JSON manifest, constrained Markdown lesson body, structured assessment data, and referenced assets.**

- **Verified:** the platform requires explicit portable contracts, replaceable content providers, versioning, provenance, local/cloud parity, and deterministic assessment data.
- **Assumption to validate:** the first lesson can be represented without a full external learning standard or authoring database.
- **Inference:** a small package provides the best reversible foundation because richer authoring systems and external standards can import to or export from it later.

## Canonical Direction

[ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [content-package contract](../../architecture/contracts/content-package-contract.md) record **Options A, A1, V1, M1, and H1**, including the documented version 1 scope limits, as canonical. Exact executable schemas and implementation remain subject to later planning and local approvals.

## Evidence Package

This evidence is a planning-level contract sketch. It is intentionally not an executable schema, accepted wire contract, storage layout, authoring format, or implementation authorization. Exact schemas, fixtures, limits, validators, generated bindings, and renderer choices belong to approved vertical-slice work.

### Representative Logical Package

Option A1 treats a directory as the logical package. A deterministic archive may later transport the directory, but extraction cannot change identity, paths, bytes, digests, or semantics.

```text
lesson.intro-risk-return/
  manifest.json
  content/
    lesson.md
  assessments/
    knowledge-check.json
  assets/
    risk-return-frontier.png
```

| Manifest field or object | Representative value | Required meaning |
| --- | --- | --- |
| Schema identity | Content-package contract family and schema version 1.0.0 | Selects the exact platform-owned validation contract |
| Package identity | `lesson.intro-risk-return` | Stable identity independent of filename, storage key, locale, or provider |
| Package version | `1.0.0` | Immutable semantic version of this published package |
| Package digest | Lowercase SHA-256 over the deterministic logical package index | Detects altered bytes independently of archive or storage metadata |
| Publication | Published timestamp and status | Distinguishes a reusable published artifact from mutable authoring work |
| Display metadata | Title, summary, `en-US` locale | Learner-facing metadata without defining localization workflows |
| Objectives | Stable objective identifiers and text | Supports one introductory lesson without defining competency mastery |
| Educational sources | Stable source ID, title, locator, publisher, access date, and attribution or license note | Preserves human-reviewable source provenance without treating remote content as trusted package content |
| Lesson body | `content/lesson.md`, `text/markdown`, byte size, SHA-256 | Identifies and integrity-checks the constrained CommonMark body |
| Assessment reference | Stable assessment ID, `1.0.0`, path, media type, byte size, SHA-256 | Transports the exact Assessment-owned definition used by the lesson |
| Asset reference | Stable asset ID, package-relative path, media type, byte size, SHA-256, accessibility text | Allows declared passive media without arbitrary embeds |
| Package provenance | Producer, creation time, source revision, and optional imported-from reference | Distinguishes platform production from provider or import origin |

The representative lesson body uses headings, paragraphs, emphasis, ordered and unordered lists, block quotations, fenced code where the profile permits it, declared asset images, and links to approved `https` source locators. It does not contain raw HTML, scripts, styles, forms, inline SVG markup, iframes, object/embed elements, data URLs, or executable extensions.

The representative `knowledge-check.json` contains one `single_choice` item with a stable item ID and version, prompt, at least two uniquely identified options, exactly one correct option, bounded explanatory feedback, and an explicit deterministic scoring-policy identifier. The package transports that definition; Assessment validates its semantics, owns attempts and responses, and produces score and completion evidence.

### Draft Contract Shape

The eventual executable contract should use JSON Schema Draft 2020-12 and split the manifest and assessment definitions into platform-owned schemas. The following is the proposed minimum shape, not the final field spelling:

| Record | Required fields | Key constraints |
| --- | --- | --- |
| Content-package manifest | schema identity/version; package ID/version; publication; locale; title; objectives; sources; content; assessments; assets; provenance | Closed known object for version 1; stable unique IDs; semantic versions; normalized package-relative paths; declared media types; nonnegative byte sizes; lowercase SHA-256; no duplicate paths or case-fold collisions |
| Knowledge-check definition | schema identity/version; assessment ID/version; item list; scoring-policy ID | Versioned closed object; unique item and option IDs; initially only `single_choice`; exactly one correct option; correct option must exist; scoring meaning enforced by Assessment |
| File reference | stable ID where applicable; relative path; media type; byte size; SHA-256 | Path is beneath package root after normalization; referenced file exists exactly once; measured bytes and digest match; media type is allowlisted and content-sniff checked |
| Educational source | stable source ID; title; locator; publisher; accessed date; attribution or license note | Locator uses an allowed scheme; identifiers are unique; required attribution survives export and rendering |
| Provenance | producer; created time; source revision; optional import origin | Provider/import data remains labeled and cannot overwrite platform package identity |

Cross-field requirements that JSON Schema cannot reliably express alone remain deterministic semantic validation. They include unique normalized paths, case-fold collision detection, referenced-file existence, byte and digest equality, assessment correct-option membership, package-wide identifier uniqueness, archive extraction safety, and supported-version policy.

Planning draft for the manifest schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:financial-ai-academy:learning:content-package-manifest:1.0.0",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "package_id", "package_version", "package_digest", "published_at",
    "locale", "title", "objectives", "sources", "content",
    "assessments", "assets", "provenance"
  ],
  "properties": {
    "schema_version": { "const": "1.0.0" },
    "package_id": { "$ref": "#/$defs/stableId" },
    "package_version": { "$ref": "#/$defs/semver" },
    "package_digest": { "$ref": "#/$defs/sha256" },
    "published_at": { "type": "string", "format": "date-time" },
    "locale": { "type": "string", "minLength": 2, "maxLength": 35 },
    "title": { "type": "string", "minLength": 1, "maxLength": 200 },
    "objectives": {
      "type": "array", "minItems": 1,
      "items": { "$ref": "#/$defs/objective" }
    },
    "sources": {
      "type": "array", "minItems": 1,
      "items": { "$ref": "#/$defs/source" }
    },
    "content": { "$ref": "#/$defs/fileReference" },
    "assessments": {
      "type": "array", "minItems": 1,
      "items": { "$ref": "#/$defs/versionedFileReference" }
    },
    "assets": {
      "type": "array",
      "items": { "$ref": "#/$defs/assetReference" }
    },
    "provenance": {
      "type": "object", "additionalProperties": false,
      "required": ["producer", "created_at", "source_revision"],
      "properties": {
        "producer": { "type": "string", "minLength": 1 },
        "created_at": { "type": "string", "format": "date-time" },
        "source_revision": { "type": "string", "minLength": 1 },
        "imported_from": { "type": "string", "format": "uri" }
      }
    }
  },
  "$defs": {
    "stableId": { "type": "string", "pattern": "^[a-z0-9]+(?:[._-][a-z0-9]+)*$" },
    "semver": { "type": "string", "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$" },
    "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
    "relativePath": { "type": "string", "minLength": 1 },
    "fileReference": {
      "type": "object", "additionalProperties": false,
      "required": ["path", "media_type", "byte_size", "sha256"],
      "properties": {
        "path": { "$ref": "#/$defs/relativePath" },
        "media_type": { "type": "string", "minLength": 1 },
        "byte_size": { "type": "integer", "minimum": 0 },
        "sha256": { "$ref": "#/$defs/sha256" }
      }
    },
    "versionedFileReference": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "version", "path", "media_type", "byte_size", "sha256"],
      "properties": {
        "id": { "$ref": "#/$defs/stableId" },
        "version": { "$ref": "#/$defs/semver" },
        "path": { "$ref": "#/$defs/relativePath" },
        "media_type": { "type": "string", "minLength": 1 },
        "byte_size": { "type": "integer", "minimum": 0 },
        "sha256": { "$ref": "#/$defs/sha256" }
      }
    },
    "objective": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "text"],
      "properties": {
        "id": { "$ref": "#/$defs/stableId" },
        "text": { "type": "string", "minLength": 1, "maxLength": 500 }
      }
    },
    "source": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "title", "locator", "publisher", "accessed_on", "attribution"],
      "properties": {
        "id": { "$ref": "#/$defs/stableId" },
        "title": { "type": "string", "minLength": 1 },
        "locator": { "type": "string", "format": "uri" },
        "publisher": { "type": "string", "minLength": 1 },
        "accessed_on": { "type": "string", "format": "date" },
        "attribution": { "type": "string", "minLength": 1 }
      }
    },
    "assetReference": {
      "type": "object", "additionalProperties": false,
      "required": ["id", "path", "media_type", "byte_size", "sha256", "alt_text"],
      "properties": {
        "id": { "$ref": "#/$defs/stableId" },
        "path": { "$ref": "#/$defs/relativePath" },
        "media_type": { "type": "string", "minLength": 1 },
        "byte_size": { "type": "integer", "minimum": 0 },
        "sha256": { "$ref": "#/$defs/sha256" },
        "alt_text": { "type": "string", "minLength": 1, "maxLength": 500 }
      }
    }
  }
}
```

Planning draft for the initially supported assessment item:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:financial-ai-academy:learning:knowledge-check:1.0.0",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "assessment_id", "assessment_version", "scoring_policy_id", "items"],
  "properties": {
    "schema_version": { "const": "1.0.0" },
    "assessment_id": { "type": "string", "minLength": 1 },
    "assessment_version": { "type": "string", "minLength": 1 },
    "scoring_policy_id": { "const": "single-choice-exact-match.v1" },
    "items": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["id", "version", "type", "prompt", "options", "correct_option_id", "feedback"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "version": { "type": "string", "minLength": 1 },
          "type": { "const": "single_choice" },
          "prompt": { "type": "string", "minLength": 1 },
          "options": {
            "type": "array", "minItems": 2,
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["id", "text"],
              "properties": {
                "id": { "type": "string", "minLength": 1 },
                "text": { "type": "string", "minLength": 1 }
              }
            }
          },
          "correct_option_id": { "type": "string", "minLength": 1 },
          "feedback": { "type": "string", "minLength": 1 }
        }
      }
    }
  }
}
```

`format` checks, supported media types, size/count limits, semantic-version policy, and all cross-record invariants must be explicit validator configuration and tests; they cannot be assumed from schema annotations alone.

### Versioning and Immutability Rule

- The schema version and package version are separate. The schema version describes the contract family; the package version describes one lesson artifact.
- A published `(package_id, package_version)` identifies exactly one package digest. Reusing that tuple for different bytes is rejected, even when a provider or operator attempts the change.
- The package digest is SHA-256 over a documented deterministic package index derived from the normalized manifest with its own digest value omitted plus the ordered referenced-file digests and byte sizes. Archive timestamps, entry order, compression, and storage metadata do not affect it. The exact canonicalization algorithm requires executable fixtures before release.
- Any change to lesson meaning, objectives, source metadata, assessment definition, feedback, asset bytes, or declared provenance creates a new package version. Published versions remain retrievable while retained learner evidence refers to them.
- Contract-family versions follow the accepted semantic-version policy. Readers reject unknown major versions. Additive optional minor fields may be accepted only when the compatibility policy and conformance fixtures say they are safe; consumers do not guess at unknown scoring policies, item types, or security-relevant capabilities.
- Curriculum and evidence retain exact package and assessment versions. Resolution never silently substitutes `latest`. A transport conversion is valid only when normalized paths, referenced bytes, versions, and package digest remain unchanged.
- Mutable drafts and authoring histories are outside this package. Publication creates the immutable portable artifact; authoring tools may later produce it through separately governed workflows.

### Path, Asset, and Archive Profile

- Version 1 paths use forward-slash-separated relative segments from a conservative portable ASCII set. Absolute, drive-qualified, UNC, empty, dot, dot-dot, backslash-containing, NUL-containing, control-character, hidden, reserved-device, or normalization-ambiguous paths are rejected.
- Validation rejects duplicate normalized paths, case-fold collisions, symlinks, hard links, devices, and any resolved path outside the logical package root. Import never follows a link from the package.
- Version 1 assets are limited to passive raster images (`image/png`, `image/jpeg`, and `image/webp`). The validator compares the declared media type with content-sniffed bytes. SVG, HTML, PDF, audio, video, fonts, archives, and executable content require a separately reviewed profile expansion.
- Every referenced file is declared exactly once with measured byte size and SHA-256. Missing, undeclared, extra, mismatched, unsupported, or duplicate files cause rejection. Required accessibility text accompanies learner-visible images.
- Directory validation is the initial logical behavior. If archive transport is later introduced, validation applies entry-count, per-entry, total compressed, total expanded, and expansion-ratio limits before committing files; partial extraction is discarded. Exact safe limits are deployment configuration constrained by tested platform ceilings, not package-authored values.

### Renderer-Security Review

- Version 1 uses CommonMark 0.31.2 syntax with a platform profile. Raw HTML is rejected rather than passed through; extensions are denied unless the profile names and tests them.
- Markdown is treated as untrusted input. Parsing produces a constrained intermediate representation whose node and attribute kinds are allowlisted. Rendering uses context-appropriate encoding and safe DOM sinks; maintained HTML sanitization is defense in depth, not permission to accept arbitrary HTML.
- Links are limited to approved `https` external locators or declared package-relative learner-navigation targets. `javascript`, `data`, `file`, `blob`, protocol-relative, control-character-obfuscated, and other schemes are rejected after normalization. External links receive safe opener/referrer behavior.
- Images resolve only to declared package assets through an application-controlled content handler. Rendering and validation perform no implicit network fetch, file read outside the package, script execution, style injection, or remote embed.
- Browser Content Security Policy and Trusted Types may add defense in depth, but they do not replace validation, encoding, sanitization, safe sinks, or asset isolation.
- Imported packages remain untrusted even when signed or received from an approved provider. Provider identity and integrity evidence do not grant markup, URL, or executable authority.

### Draft Validation Report

This is the required validation matrix for the later executable schemas and validator. `PASS` means the proposed design has an explicit deterministic expected result; no validator has been implemented or run yet.

| Fixture or mutation | Expected result | Planning review |
| --- | --- | --- |
| Representative directory package with matching schema, files, sizes, and digests | Accept and return normalized identity, versions, digest, references, and provenance | PASS |
| Missing required field, wrong primitive type, invalid semantic version, or unknown top-level field | Reject with stable schema diagnostic and no partial registration | PASS |
| Unknown schema major, assessment item type, scoring policy, or security-relevant capability | Reject as unsupported; never infer or downgrade meaning | PASS |
| Duplicate package-wide ID, item ID, option ID, file path, or case-fold-equivalent path | Reject with collision diagnostic | PASS |
| Absolute, drive, UNC, dot-dot, backslash, NUL, control, reserved, symlink, hard-link, or escaping path | Reject before reading or committing referenced content | PASS |
| Missing, extra, duplicate, size-mismatched, digest-mismatched, corrupted, or unsupported-media file | Reject the entire package without partial publication | PASS |
| Declared media type differs from sniffed bytes, or an active-content type is renamed as an image | Reject as media mismatch or unsupported type | PASS |
| Raw HTML, inline SVG, iframe, form, script, style, event attribute, active embed, or unapproved extension in Markdown | Reject under the version 1 Markdown profile | PASS |
| Obfuscated or direct unsafe URL scheme in Markdown or source metadata | Reject after normalization; renderer performs no fetch | PASS |
| Knowledge-check correct option is absent, option IDs repeat, or more than one correct answer is encoded | Reject in Assessment semantic validation | PASS |
| Same package ID/version arrives with a different digest | Reject as immutable-version conflict and retain the accepted artifact | PASS |
| Archive exceeds entry, compressed, expanded, per-file, or expansion-ratio limits | Reject without retained partial extraction | PASS when archive transport is introduced |
| Diagnostic contains malicious paths, content, URLs, or source text | Return bounded structured codes with untrusted values escaped and secrets absent | PASS |

Executable qualification must turn every row into positive and negative fixtures, prove deterministic results across supported local and cloud adapters, and record the validator/schema/tool versions used.

### Standards and Product Review

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) is the current released schema dialect and supports the platform's portable-record contract choice.
- [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/) supplies a stable parse specification; the platform profile deliberately removes raw HTML and limits extensions and URLs.
- The [OWASP Cross-Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) supports context-aware encoding, maintained sanitization for HTML, and safe sinks rather than treating framework defaults or CSP as the primary defense.
- The [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) supports allowlisted types, generated or mapped storage names, size limits including post-decompression size, least privilege, and defenses against malicious active content and archive bombs.

**Product/content review conclusion:** the representative package can express CAP-0001's one versioned introductory lesson, objectives, educational sources, passive visual asset, deterministic single-choice knowledge check, and explanatory feedback. It intentionally does not define mutable authoring projects, localization workflows, competency mastery, question banks, rich simulations, remote embeds, arbitrary HTML, package signing, external learning-standard interoperability, or additional assessment types.

**Architecture/security review conclusion:** Options A, A1, V1, M1, and H1 fit the accepted platform-owned contract, module-ownership, provenance, and local/cloud-parity constraints and support the canonical direction. Residual implementation risks are parser/sanitizer vulnerabilities, ambiguous canonicalization, denial of service, media-parser flaws, unsafe archive handling, stale dependencies, and incorrectly broadened profiles. Those risks require executable conformance fixtures, dependency maintenance, bounded limits, and later security review; they are not waived by this planning decision.

## Evidence Required

- **Prepared:** representative logical package containing lesson identity, semantic version, digest, objectives, educational sources, content, one knowledge check, feedback, provenance, and a passive asset.
- **Prepared:** planning-level JSON Schema drafts plus a validation matrix covering malformed fields, unsafe paths and links, duplicate identifiers, unsupported versions and capabilities, media mismatches, archive limits, and content integrity.
- **Prepared:** semantic versioning, digest, immutable publication, exact-version resolution, and reader compatibility rules.
- **Prepared:** constrained CommonMark, link, asset, renderer, safe-sink, sanitization, network-fetch, and untrusted-import security review.
- **Prepared:** product/content scope review confirming CAP-0001 expressiveness without claiming future authoring, assessment, localization, or interoperability scope.
- **Satisfied:** ADR-0007 records Options A, A1, V1, M1, and H1 and the documented version 1 scope limits as canonical authority.

## Required Authority

Product and architecture decision authority after product-content and contract review of the representative package and schema. Approval evidence is retained only in the ignored local ledger.

## Decision Record and Promotion

The accepted package decision is recorded in [ADR-0007](../../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [content-package contract](../../architecture/contracts/content-package-contract.md). Decision readiness, contract governance, deployment parity, context guidance, and verification gaps now reflect the accepted boundary. Executable schemas remain restricted to approved delivery work.

## Dependent Planning Updates

- DEC-0003 has been removed from CAP-0001's unresolved decision gates.
- Refine Candidate A package validation, provenance, stale-version, and safe-rendering scenarios.
- Keep authoring workflows and external learning-standard support as separately shaped capabilities and decisions.

## Planning History

- 2026-08-04: Decision request captured from CAP-0001's content-format gate.
- 2026-08-04: The representative package, schema drafts, compatibility rules, path and asset profile, renderer-security review, validation matrix, standards review, and product-scope review were prepared.
- 2026-08-04: ADR-0007, the content-package contract, decision readiness, contract and deployment guidance, context packs, CAP-0001, and the planning register were synchronized; DEC-0003 moved to `complete`.
