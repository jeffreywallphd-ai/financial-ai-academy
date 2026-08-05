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
