# Lesson Package Contract v1

This folder contains the executable JSON Schema Draft 2020-12 shapes for the
read-only lesson-package boundary introduced by SLI-0001.

- `manifest.schema.json` is the package entry contract.
- `file.schema.json` defines a declared lesson or generic package file.
- `source.schema.json` defines reviewable HTTPS educational-source provenance.
- `assessment-file.schema.json` closes an opaque Assessment-owned file into the
  package without assigning scoring meaning to Content.
- `image-asset.schema.json` permits only declared passive PNG, JPEG, and WebP
  assets with accessibility text.
- `package-index.schema.json` fixes the language-neutral logical-index shape.

The package digest is publication metadata computed over canonical logical-index
bytes. It is deliberately absent from `manifest.json` to avoid a circular digest.
Semantic, path, media, resource, markup, and integrity rules are exercised by the
compatibility corpus and Python conformance runner.
