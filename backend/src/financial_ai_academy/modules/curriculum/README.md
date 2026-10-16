# Curriculum Module

Curriculum owns lesson placement and retains only exact Content identifiers:
package ID, semantic version, and digest.

## Public operations

- `CurriculumService.create_lesson_placement(CreateLessonPlacementRequest) -> LessonPlacement`
- `CurriculumService.open_placed_lesson(OpenPlacedLessonRequest) -> LessonReadingResult`
- `CurriculumService.create_assessment_placement(CreateAssessmentPlacementRequest) -> AssessmentPlacement`
- `CurriculumService.resolve_placed_assessment(ResolvePlacedAssessmentRequest) -> AssessmentPlacement`
- `CurriculumService.create_practice_placement(CreatePracticePlacementRequest) -> PracticePlacement`
- `CurriculumService.resolve_placed_practice(ResolvePlacedPracticeRequest) -> PracticePlacement`
- `CurriculumService.register_practice_review_target(RegisterPracticeReviewTargetRequest) -> PracticeReviewTarget`
- `CurriculumService.resolve_practice_review_targets(...) -> tuple[PracticeReviewTarget, ...]`
- `CurriculumService.register_lesson_opportunity(RegisterLessonOpportunityRequest) -> LessonOpportunityClassification`
- `CurriculumService.rebuild_learning_opportunity_projection(...) -> LearningOpportunityBrowse`
- `CurriculumService.browse_learning_opportunities(BrowseLearningOpportunitiesRequest) -> LearningOpportunityBrowse`
- `CurriculumService.query_learning_opportunities(QueryLearningOpportunitiesRequest) -> LearningOpportunityQueryPage`
- `CurriculumService.publish_curriculum_graph(PublishCurriculumGraphRequest) -> CurriculumGraph`
- `CurriculumService.open_curriculum_graph(OpenCurriculumGraphRequest) -> CurriculumGraph`

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

The additive `curriculum_0004_practice_placements` stream stores a separate
immutable package/practice/version/digest reference for an existing lesson
placement. It does not reuse the singular knowledge-check item/policy fields,
interpret private answers, or read Content/Assessment persistence.

`curriculum_0005_practice_review_targets` stores append-only mappings from an
exact practice placement and full review-resource identity/version/digest to
an available exact lesson destination or an explicit unavailable reason.
Registration is idempotent and conflicting reuse fails. Resolution preserves
declaration order, removes only exact duplicates, and represents a missing
mapping as `mapping_not_found`; it never falls forward, ranks resources, reads
Assessment evidence, or stores Content bytes.

The isolated live practice flow qualifies that a missing exact mapping remains
an explicit unavailable target in both the generated browser and a fresh
cookie-backed non-browser progress read. Focused contract and PostgreSQL suites
also cover available destinations, declaration-order preservation,
idempotency, changed-meaning refusal, and restart durability. Review routing
does not rank, personalize, or generate a recommendation.

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
bounds raw text and filter cardinality before it normalizes text with Unicode
NFKC, whitespace collapse, and case-fold semantics and reduces repeated
filters to sorted unique applied values. It applies no more than ten terms per
text field, OR-within/AND-across metadata filters, inclusive duration bounds,
and closed deterministic sorts, then pages only the already validated
projection. The default sort preserves projection order. Other sorts use
normalized title and opportunity identity as stable tie-breaks and never
produce a relevance score.

An opaque continuation cursor binds the canonical query fingerprint,
projection generation, and next offset. Malformed, checksum-corrupted,
query-mismatched, or generation-stale cursors fail closed without records.
Query mismatch is the bounded `invalid_query` case; projection-generation
drift is the bounded `stale_cursor` case. The
unkeyed checksum detects accidental corruption; it does not claim adversarial
integrity. Cursors grant no authority and are not durable learner evidence. The
current 500-record
projection bound lets the shared application core enforce identical local and
future cloud semantics without a second index. The protected
`GET /api/v1/curriculum/opportunities/query` operation maps bounded repeated
URL parameters directly into the public query request and returns the core's
canonical page through the reviewed OpenAPI snapshot and generated TypeScript
client. It shares the server-issued `curriculum.discovery.read` permission with
queryless browse. The URL-backed browser controls and isolated
PostgreSQL/Python/static/Chromium query path are directly qualified, including
combined filters, duration ordering across three one-record pages, opaque
cursor-query mismatch denial, context confidentiality, and axe accessibility.

## Curriculum graph validation

The public Curriculum surface exposes immutable `curriculum-graph-v1` records
and a pure validator/converter. Curriculum owns objective, competency,
activity, branch, and relationship meaning. Lesson and assessment activities
retain exact public placement and version/digest references without importing
Content or Assessment internals.

Validation rejects duplicate and dangling identities, incompatible typed
relationship endpoints, ambiguous required/optional branch membership,
prerequisite cycles,
activity/reference mismatches, unsupported versions, and stale graph digests.
Partial presentation order is only a hint: multiple entry activities, optional
branches, same-kind shared activities, sibling reordering, and unbranched
activities remain valid. Required-versus-optional reuse fails as ambiguous.

Graph admission now verifies every lesson and assessment activity against the
exact Curriculum-owned placement before idempotently inserting the immutable
version. `curriculum_0003_curriculum_graphs` stores the complete validated JSONB
aggregate behind `CurriculumRepositoryPort`, constrains root fields, and
rejects ordinary update/delete. Exact reads reconstruct and revalidate public
types and never fall forward to another version.

The protected
`GET /api/v1/curriculum/graphs/{curriculum_id}/versions/{curriculum_version}`
operation requires server-issued `curriculum.graph.read` and returns the closed
graph through the reviewed OpenAPI snapshot and generated client. It accepts no
learner, permission, or current-version selector. Learner map/list rendering,
eligibility, completion context, and activity launch remain later CAP-0005
packets.
