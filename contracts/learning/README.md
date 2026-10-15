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

## Assessment v1

[`assessment/v1/`](assessment/v1/README.md) defines the private single-select
definition, answer-safe learner presentation, exact-version submission, and
retained result/evidence shapes. The paired corpus in
[`../compatibility/assessment/v1/`](../compatibility/assessment/v1/README.md)
fixes correct and incorrect outcomes, denial behavior, definition/package
digests, and cross-record consistency.

```powershell
uv run --project backend pytest backend/tests/contract/assessment
```

This is direct contract evidence only; application scoring and persistence are
introduced separately.

## Learning Discovery v1

[`discovery/v1/`](discovery/v1/README.md) defines the portable approved
learning-opportunity record and stable browse projection. The compatibility
corpus in [`../compatibility/discovery/v1/`](../compatibility/discovery/v1/README.md)
fixes exact lesson provenance, canonical source/generation digests, stable
ordering, and bounded denial behavior.

```powershell
uv run --project backend pytest backend/tests/contract/discovery
```

The current profile qualifies exact approved lesson records only. Persistence,
API authorization, generated clients, browser behavior, search/filter queries,
and non-lesson destinations require their owning implementation evidence.
