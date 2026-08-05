# Learning Contracts

Portable learning-activity, competency, assessment, and evidence schemas live here when introduced through approved delivery work.

The semantic package boundary is accepted by [ADR-0007](../../docs/adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [versioned lesson content-package contract](../../docs/architecture/contracts/content-package-contract.md).

## Lesson Package v1

The executable Draft 2020-12 schemas are in [`lesson-package/v1/`](lesson-package/v1/README.md). The compatibility corpus in [`../compatibility/lesson-package/v1/`](../compatibility/lesson-package/v1/README.md) fixes:

- one approved synthetic lesson package;
- safe path, file-closure, integrity, media, markup, and resource-limit denials;
- canonical package-index bytes and the expected SHA-256 package digest;
- immutable package identity/version conflict behavior.

Run the contract evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/lesson_package
```

These contracts establish portable admission behavior only. They do not establish Content persistence, Assessment scoring, API, browser rendering, or local/cloud storage conformance.
