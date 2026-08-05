# Curriculum Module

Curriculum owns lesson placement and retains only exact Content identifiers:
package ID, semantic version, and digest.

## Public operations

- `CurriculumService.create_lesson_placement(CreateLessonPlacementRequest) -> LessonPlacement`
- `CurriculumService.open_placed_lesson(OpenPlacedLessonRequest) -> LessonReadingResult`

The Content gateway imports only `financial_ai_academy.modules.content.public`.
Curriculum does not import Content internals, query Content tables, use object
keys, or silently resolve another version.

The module owns `curriculum.lesson_placements` through migration
`0002_curriculum_lesson_placements`. The table intentionally has no foreign key
to Content persistence; the application operation checks the exact reference
through the public Content facade.
