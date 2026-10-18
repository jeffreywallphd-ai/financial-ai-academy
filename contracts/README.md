# Executable Contracts

This directory is reserved for reviewed, executable, language-neutral contract artifacts.

```text
api/             generated OpenAPI snapshot
common/          shared structural schemas
guidance/        versioned platform-help and guidance records
events/          versioned event schemas and envelope
providers/       provider and plugin manifests/capabilities
learning/        portable learning records
finance/         portable financial records
compatibility/   fixtures and approved compatibility decisions
```

No placeholder schema should be added before its semantic owner and compatibility policy are accepted. Contract architecture is documented in `docs/architecture/contracts/`.

Implemented contract families include the versioned lesson package and the
initial deterministic Assessment v1 learning/evidence records plus its
Assessment-owned completion event. See `learning/README.md`,
`events/README.md`, and `compatibility/README.md` for executable evidence.

The Guidance-owned `platform-help/v1` family defines inert exact-version help
topics and deterministic literal-search records without making repository
documentation, AI output, or the browser a source of authority.

The additive Guidance-owned `contextual-help/v1` family maps one exact feature
context to ordered exact approved Help topics for shared browser and headless
use without copying feature state or authority.
