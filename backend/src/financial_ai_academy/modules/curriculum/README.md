# Curriculum Module

Curriculum owns lesson placement and retains only exact Content identifiers:
package ID, semantic version, and digest.

## Public operations

- `CurriculumService.create_lesson_placement(CreateLessonPlacementRequest) -> LessonPlacement`
- `CurriculumService.open_placed_lesson(OpenPlacedLessonRequest) -> LessonReadingResult`
- `CurriculumService.create_assessment_placement(CreateAssessmentPlacementRequest) -> AssessmentPlacement`
- `CurriculumService.resolve_placed_assessment(ResolvePlacedAssessmentRequest) -> AssessmentPlacement`
- `CurriculumService.register_lesson_opportunity(RegisterLessonOpportunityRequest) -> LessonOpportunityClassification`
- `CurriculumService.rebuild_learning_opportunity_projection(RebuildLearningOpportunityProjectionRequest) -> LearningOpportunityBrowse`
- `CurriculumService.browse_learning_opportunities(BrowseLearningOpportunitiesRequest) -> LearningOpportunityBrowse`
- `CurriculumService.query_learning_opportunities(QueryLearningOpportunitiesRequest) -> LearningOpportunityQueryPage`

The Content gateway imports only `financial_ai_academy.modules.content.public`.
Curriculum does not import Content internals, query Content tables, use object
keys, or silently resolve another version.

The module owns `curriculum.lesson_placements` through migration
`0002_curriculum_lesson_placements`. The table intentionally has no foreign key
to Content persistence; the application operation checks the exact reference
through the public Content facade.

The `curriculum_0001_assessment_placements` stream adds a separate exact
Assessment reference keyed by the existing lesson placement. It stores package,
definition, item, and policy versions/digests without interpreting the private
definition or reading Content/Assessment persistence.

## Discovery projection core

Curriculum owns bounded catalog classification, exact destination,
prerequisite summary, availability, and rebuild policy for learning
opportunities. Content remains authoritative for title, objectives, package
version/digest, publication state, and provenance; the Curriculum adapter reads
those facts only through Content's existing exact public operation.

Discovery v1 currently admits only exact approved lesson placements. It builds
every record in memory before calling one atomic repository replacement,
derives stable SHA-256 source and generation fingerprints, and uses normalized
title plus opportunity identity for the fixed browse order. Identity reuse with
different classification, a missing/mismatched exact source, corrupted
generation, or repository failure is bounded and fail closed. The projection
contains no learner/provider identity, storage reference, ranking score,
eligibility, recommendation, or execution promise.

`curriculum_0002_discovery_projection` persists immutable classifications and
one complete ordered generation in Curriculum-owned PostgreSQL tables. The
adapter serializes replacement with a transaction-scoped advisory lock and
publishes the state pointer and all records in the same transaction; readers
therefore see the prior or next complete generation, never a mixed one.

The protected queryless `GET /api/v1/curriculum/opportunities` operation
requires the server-issued `curriculum.discovery.read` permission and returns
the same closed v1 browse shape through the reviewed OpenAPI snapshot and
generated TypeScript client. Explicit local-fixture rebuild orchestration and
the same-origin browser catalog-to-lesson path are directly qualified for the
local single-profile deployment.

## Discovery query core

Discovery-query v1 leaves the queryless browse contract unchanged. Curriculum
normalizes bounded text with Unicode NFKC, whitespace collapse, and case-fold
semantics; applies conjunctive search terms, OR-within/AND-across metadata
filters, inclusive duration bounds, and closed deterministic sorts; and pages
only the already validated projection. The default sort preserves projection
order. Other sorts use normalized title and opportunity identity as stable
tie-breaks and never produce a relevance score.

An opaque continuation cursor binds the canonical query fingerprint,
projection generation, and next offset. Malformed, tampered, mismatched, or
generation-stale cursors fail closed without records. Cursors grant no
authority and are not durable learner evidence. The current 500-record
projection bound lets the shared application core enforce identical local and
future cloud semantics without a second index. The protected HTTP operation,
generated client, browser controls, and live qualification remain WRK-0049
through WRK-0051 work.
