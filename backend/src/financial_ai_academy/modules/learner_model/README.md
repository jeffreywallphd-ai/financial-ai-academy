# Learner Model Module

Learner model owns derived completion and progress projections plus their exact
source-evidence references. It never replaces Assessment evidence and never
interprets bounded completion as mastery, competency, certification, advice, or
investment performance.

## Public operation

- `open_lesson_completion(OpenLessonCompletionRequest) -> LessonCompletionView`
- `open_practice_history(OpenPracticeHistoryRequest) -> PracticeHistoryView`
- `open_project_completion(OpenProjectCompletionRequest) -> ProjectCompletionView`

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

`learner_model_0002_practice_history` adds exact-scope projection roots and
ordered attempt summaries. The application consumes only Assessment's public
safe-history operation, validates zero through ten contiguous attempts,
deduplicates exact event replay, rejects identity collisions or changed item
signatures, and computes the contract's canonical source digest before one
transaction replaces the complete projection. Incorrect-item review IDs are
retained; responses, feedback text, answers, and raw Assessment documents are
not. Retry history remains evidence-only and never becomes mastery,
competency, eligibility, certification, recommendation, or advice.

The isolated local qualification submits one browser attempt, reads the same
ordered answer-free history from a fresh non-browser session, preserves its
source digest and review evidence while a next-attempt draft is saved, and
reopens the identical public progress meaning after normal host restart.
Focused PostgreSQL evidence owns idempotent rebuild, interrupted-rebuild
rollback, migration, and variable attempt-history cases; the live runner does
not reach into this module's tables or introduce another projection path.

`learner_model_0003_project_completion` adds one replaceable projection root
per learner and Project plus ordered public source references for every
accepted Project submission. The operation consumes only Assessment's typed
Project-event replay, validates contiguous occurrence and immediate
supersession, deduplicates exact event replay, and atomically replaces the
complete derived set with a stable source digest. Completion means only that
Assessment accepted structural Project evidence; the rows contain no workspace
content, artifact bytes, qualitative grade, mastery, competency, suitability,
recommendation, or advice meaning.

The isolated browser/headless Project qualification correlates two accepted
Assessment occurrences with two ordered history references and one rebuildable
completion root. The exact public history, source digest, and bounded activity-
completion meaning survive a normal application restart and deterministic
replay without introducing a browser-owned projection path.
