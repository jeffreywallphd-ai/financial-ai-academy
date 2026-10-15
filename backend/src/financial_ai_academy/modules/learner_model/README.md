# Learner Model Module

Learner model owns derived completion and progress projections plus their exact
source-evidence references. It never replaces Assessment evidence and never
interprets bounded completion as mastery, competency, certification, advice, or
investment performance.

## Public operation

- `open_lesson_completion(OpenLessonCompletionRequest) -> LessonCompletionView`

The operation obtains validated completion events through the Assessment
public facade, derives a stable source-set digest and ordered history, and
atomically replaces only its own PostgreSQL projection. Empty evidence produces
an explicit incomplete view. Invalid or unavailable evidence fails before a
false completion is stored.

## Persistence and replay

`learner_model_0001_completion_projection` owns the replaceable
`lesson_completion_projections` and `lesson_completion_history` tables. The
history rows retain event, attempt, evidence, lesson-package, Assessment, item,
policy, score, and completion-time provenance. Repeated replay replaces one
derived set; an interrupted transaction preserves the prior complete set.

These tables are rebuildable and intentionally contain no cross-schema foreign
keys. The synchronous replay query does not establish a queue, worker,
checkpoint, delivery guarantee, backup service, or managed-cloud posture.
