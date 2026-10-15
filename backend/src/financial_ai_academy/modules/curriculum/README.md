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

WRK-0043 establishes the public/application contract and repository port.
PostgreSQL storage, composition, protected HTTP/OpenAPI exposure, generated
client, and browser catalog remain subsequent SLI-0018 packets.
