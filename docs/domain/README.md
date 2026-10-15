# Domain Documentation

- Status: proposed
- Canonical for: domain-document routing

## Initial Domain Areas

- Identity and organizations
- Learning content and curriculum
- Assessments and evidence
- Learner state and mastery
- Adaptive pathways
- Financial instruments and market data
- Simulated portfolios and backtesting
- AI orchestration
- Provenance and audit

The [initial glossary](glossary.md) and module boundaries not accepted by ADR remain starting hypotheses. [ADR-0005](../adr/ADR-0005-first-learning-loop-module-ownership.md) accepts the Content, Curriculum, Assessment, Learner model, and Audit boundaries for the first learning loop. Detailed rules should still be added through vertical-slice discovery rather than invented in advance.

Domain documents own meaning and invariants. Executable contracts own exact external shapes. Architecture documents own placement and dependencies.

## Implemented Introductory Lesson Read Core

The first executable domain seam preserves these terms:

- **Published lesson version:** one immutable package ID, semantic version, and
  digest owned by Content.
- **Lesson placement:** one Curriculum-owned identity retaining the exact
  published Content tuple without owning Content bytes or persistence.
- **Lesson reading result:** the placement identity plus the exact Content
  tuple, title, objectives, closed safe body nodes, educational sources,
  application-controlled passive assets, and publication provenance.
- **Admission:** Content validation, staged/finalized object storage, and
  publication metadata visibility. Invalid or unsafe packages never become
  visible; a metadata failure may leave only an unreferenced object for bounded
  reconciliation.

Content's public operations admit and read exact published versions. Curriculum's
public operations create and open exact placements. Missing or stale references
do not resolve a newer version. Knowledge-check meaning, attempts, scoring,
completion evidence, and mastery remain Assessment/Learner-model work and are
not implied by the packaged assessment file.

## Deterministic Knowledge-Check Contract Terms

The first executable Assessment contract establishes these terms without yet
claiming application behavior:

- **Private definition:** immutable Assessment-owned item, ordered options,
  correct option, exact-match policy, and reviewed feedback identified by an
  assessment/item/policy version chain and definition digest.
- **Learner presentation:** the public prompt and options plus exact version
  tokens, with correct-answer and feedback internals excluded.
- **Submission:** one opaque submission identity and one selected option tied
  to the exact placement, package, assessment, item, and policy versions.
- **Assessment evidence:** the append-oriented semantic record of learner,
  attempt, response, deterministic score, feedback, provenance, and server
  time. It is not a mastery or lesson-completion projection.
- **Knowledge-check completion event:** a bounded Assessment-owned reference
  to durable evidence for later idempotent consumers. Event delivery and
  projection behavior remain unimplemented.

## Implemented Deterministic Assessment Core

The private-host core implements the first contract terms through two public
Assessment operations: open one placed knowledge check and submit one exact
response. Curriculum resolves the exact placement reference; Content returns
the exact validated private definition bytes; Assessment alone produces the
safe presentation and score.

One learner may complete the exact placed assessment once. Repeating the same
submission identity and payload returns the original evidence. Reusing that
identity for different input is a conflict. A different submission after
accepted completion is `already_completed`; none of these paths creates a
retake. Evidence and its completion event append atomically. This behavior
still makes no lesson-completion or mastery projection.
