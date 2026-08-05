# ADR-0005: First Learning Loop Module Ownership

- Status: accepted
- Date: 2026-08-04
- Decision request: [DEC-0001](../planning/decision-requests/DEC-0001-learning-module-ownership.md)

## Context

CAP-0001 needs one versioned lesson, deterministic assessment evidence, a derived completion view, and traceable provenance. Leaving these responsibilities in one broad Learning module would allow early persistence and API choices to establish accidental ownership and make later separation costly.

The accepted modular-monolith architecture requires one semantic owner for behavior and data, public application operations for synchronous coordination, and registered versioned events for asynchronous coordination.

## Decision

Use distinct bounded modules for the first learning loop:

- **Content** owns versioned learning resources, source provenance, publication state, and content storage references.
- **Curriculum** owns competencies, prerequisites, pathways, course structure, and immutable references to the required Content and Assessment versions.
- **Assessment** owns item definitions, attempts, responses, deterministic scores, review state, and bounded knowledge-check completion evidence.
- **Learner model** owns derived completion and progress projections plus their source-evidence references. It does not replace Assessment evidence or interpret completion as mastery.
- **Audit** owns append-oriented audit and provenance records, source-event references, actor/action metadata, and integrity metadata. It does not become a second source of Content, Curriculum, Assessment, or Learner-model business facts.

API and CLI hosts may compose published application operations but own no feature policy. Modules may retain stable identifiers owned elsewhere, but they may not import another module's internals or read or mutate its persistence. Assessment publishes versioned evidence events for idempotent Learner-model and Audit consumers; no reverse dependency is permitted.

The provisional public seams in DEC-0001 guide later contract design. Exact request fields, event schemas, HTTP operations, persistence models, and generated clients require approved vertical-slice planning and executable contract review.

## Consequences

- Every first-loop command, query, evidence record, and projection has one semantic owner.
- Evidence remains separate from derived learner state and is suitable for replay and explanation.
- Content, Curriculum, and Assessment versions remain explicit across module boundaries.
- The first implementation introduces more public seams than a broad Learning module, but those seams remain in one deployable application and are independently testable.
- Architecture checks must eventually enforce public surfaces, forbidden imports, event ownership, and absence of cross-module persistence access.
- Local and managed-cloud profiles use the same module semantics and public contract versions.

## Boundaries

This decision accepts the five named boundaries for the CAP-0001 learning loop. It does not settle identity, content-package representation, data protection and recovery, tenancy, adaptive ranking, AI authority, provider choices, or managed-cloud operations. It does not accept every remaining hypothesis in the module map and does not authorize implementation.

## Alternatives Rejected

- **Combine Content and Curriculum initially.** Rejected because reusable versioned resources and curriculum placement have different lifecycles and future reuse needs.
- **Use one broad Learning module initially.** Rejected because it would conflate content, grading evidence, and derived learner state and make later extraction cross persistence, events, and APIs.

## Verification Implications

- Add forbidden-import and public-surface checks when backend modules are introduced.
- Add contract ownership, schema, fixture, idempotency, and consumer conformance checks with the first evidence events.
- Prove that completion projections rebuild from Assessment evidence without mutating or replacing it.
- Prove that Audit retains trace references and integrity metadata without becoming the source of business state.
- Keep the current coverage classified as a gap until those executable checks exist.

## Supersession

None. A future change to these ownership boundaries requires a superseding ADR and migration analysis for contracts, persistence, events, and consumers.
