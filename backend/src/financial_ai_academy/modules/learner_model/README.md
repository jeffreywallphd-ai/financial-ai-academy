# Learner Model Module

Learner model owns derived completion and progress projections plus their exact
source-evidence references. It never replaces Assessment evidence and never
interprets bounded completion as mastery, competency, certification, advice, or
investment performance.

## Public operation

- `open_lesson_completion(OpenLessonCompletionRequest) -> LessonCompletionView`
- `open_practice_history(OpenPracticeHistoryRequest) -> PracticeHistoryView`
- `open_project_completion(OpenProjectCompletionRequest) -> ProjectCompletionView`
- `open_preferences(OpenLearnerPreferencesRequest) -> LearnerPreferenceProfile`
- `mutate_preferences(MutateLearnerPreferencesRequest) -> LearnerPreferenceProfile`
- `read_preference_history(ReadLearnerPreferenceHistoryRequest) -> PreferenceHistory`
- `export_preferences(ExportLearnerPreferencesRequest) -> PreferenceExport`

SLI-0074 adds a transport-neutral `learner-preferences/v1` contract core for
explicit learner-entered goals, self-described experience, interests, closed
revision-bound mutations, bounded non-content change summaries, reset, and
portable export. The pure domain and JSON Schema adapter issue no learner
identity, time, or ID; persist nothing; and call no provider, model, network,
filesystem, or other module. The application supplies those server facts and
exposes the same public operations to the protected API, generated browser
client, and authenticated headless clients. Browser feature UI remains outside
this module.

Preferences are not evidence, competency or mastery state, Curriculum
requirements, Adaptation eligibility, recommendations, permissions,
experiment consent, financial suitability, or inferred traits. Consumers must
use later public operations and cannot query Learner-model storage or treat a
learner's stated choice as another module's authority.

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

`learner_model_0004_preferences` owns the materialized current profile,
accepted mutation replays, and at most 100 newest non-content change summaries.
An absent row projects a deterministic revision-one empty profile without a
write. The first accepted mutation persists revision two. Per-learner advisory
locking, exact idempotency replay before revision comparison, and one database
transaction keep the profile, summary, and replay atomic. Stale revision and
changed-key reuse preserve current state; an interrupted write rolls back all
three records. The migration has no cross-module foreign key and refuses a
development down migration while retained preference data exists.

The protected HTTP boundary derives learner identity from the opaque session.
Reads, history, and export require `learner_preferences.read`; mutation requires
`learner_preferences.write`. The four reviewed operations accept no learner or
query selector and share the generated OpenAPI client with browser and headless
callers. Export contains the current closed profile and bounded history only;
it is not an import, recovery, evidence, permission, or recommendation record.

The isolated approved-lesson qualification drives the generated browser client
and ordinary headless HTTP clients through these same operations. It proves
exact profile/history/export parity, unchanged replay, same-key replay and
conflict races, stale-revision serialization, PostgreSQL row correlation,
normal host restart without reseeding, and unchanged unrelated learning state.
That evidence does not establish multiple real learners, managed-cloud
deployment, backup/restore, import, or a separate autonomous AI authority.

## Presentation preference contract core

Learner model also owns the additive pure
`learner-presentation-preferences/v1` family for four explicit presentation
choices: text size, text spacing, reading width, and motion. The profile is
complete and revision-bound; mutations replace all four values or reset them
to the safe baseline. Bounded history carries no prior values, and export
contains only the exact profile, correlated summaries, purpose, and
limitations.

These choices are not diagnoses, inferred accessibility needs, Assessment
evidence, competency, eligibility, permission, recommendations, or financial
signals. The pure domain and JSON Schema adapter issue no identity or time,
persist nothing, and have no UI, browser, database, provider, model, or cross-
module effect. Browser-local theme remains platform-owned and outside this
contract. A later presentation adapter must preserve browser zoom, forced
colors, and any more-protective reduced-motion behavior.
