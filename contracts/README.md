# Executable Contracts

This directory is reserved for reviewed, executable, language-neutral contract artifacts.

```text
api/             generated OpenAPI snapshot
common/          shared structural schemas
guidance/        versioned platform-help and guidance records
provenance/      provider-neutral provenance envelopes and bounded lineage
accountable-history/ purpose-limited history inspection and portable evidence
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

The additive Guidance-owned `feature-guidance/v1` family maps one exact public
surface condition to a reviewed limitation or recovery record. Closed actions
carry presentation intent only; feature state, retry, availability,
authorization, provider/model use, and artifact execution remain with their
owning modules.

The additive cross-module `provenance/v1` family defines closed owner-issued
references, two exact initial learning roots, bounded lineage graphs, explicit
incomplete links, and deterministic view digests. It contains no owner payload,
permission, identity, provider, storage, execution, grading, or financial
authority. See `docs/architecture/contracts/provenance-and-lineage-contract.md`.

The additive `provenance/v2` family defines a closed cross-domain owner-
reference catalog for Project snapshots and synthetic future financial,
dataset, model, execution, simulation, recommendation, and administrative
profiles. It changes no v1 schema and adds no lineage view, product adapter,
provider/model action, persistence, permission, or financial authority.

The additive cross-module `accountable-history/v1` family defines one safe,
purpose-limited learner inspection document and one ephemeral portable evidence
wrapper over an already authorized learning-lineage root. Server-bound purpose,
closed diagnostics, redaction summaries, deterministic disclosed-content
digests, and reviewed display text expose no owner payload, learner identity,
provider secret, storage detail, retained export, or new permission.
