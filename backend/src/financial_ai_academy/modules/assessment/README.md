# Assessment Module

Assessment owns private definition interpretation, answer-safe presentation,
response validation, deterministic scoring, reviewed feedback selection,
attempt/response/score/completion evidence, and the bounded completion event.

The additive practice-v1 parser/projector accepts single-select,
multiple-select exact-set, and fixed-decimal numeric definitions and produces
an immutable answer-safe presentation. The application service resolves exact
Content bytes and the Curriculum placement through public-only gateways, then
exposes the same protected operation to browser and non-browser clients. Opening
has no persistence, clock, scoring, or learner-state side effect.

The additive practice submission adapter accepts a whole transport-neutral
response set, correlates it by item ID, canonicalizes semantically unordered
response and multiple-selection order for request identity, and scores every
item against the exact private definition. It returns immutable definition-
ordered outcomes, aggregate `all_correct|review_needed` meaning, only the
applicable reviewed feedback/references, and a safe correlated completion-event
document from supplied server metadata. It performs no identity lookup, clock,
persistence, publication, network, API, or UI action.

## Public operations

- `open_placed_knowledge_check(OpenPlacedKnowledgeCheckRequest) -> KnowledgeCheckPresentation`
- `open_placed_practice(OpenPlacedPracticeRequest) -> PracticePresentation`
- `submit_placed_practice(SubmitPlacedPracticeRequest) -> PracticeResult`
- `submit_placed_knowledge_check(SubmitPlacedKnowledgeCheckRequest) -> KnowledgeCheckResult`
- `read_completed_knowledge_checks(ReadCompletedKnowledgeChecksRequest) -> tuple[KnowledgeCheckCompletionEvent, ...]`

The open operation resolves Curriculum and Content only through their public
facades and returns no correct option, private scoring object, or feedback. The
submission operation requires server-resolved learner context and exact public
version tokens. Assessment alone validates the option, calculates `0|1`, and
selects reviewed feedback.

The practice-open operation resolves one immutable multi-item definition and
returns exact package/practice provenance, public prompts and choices, numeric
response constraints, attempt-policy metadata, and resource references. It
never returns correct option IDs, accepted numeric values/ranges, or feedback.
Practice submission/scoring contracts, the transport-neutral application
operation, and atomic evidence persistence are implemented. The operation
accepts server-resolved learner context, a route-bound placement ID, and the
exact versioned submission bytes; it supplies time and durable IDs itself. The
public HTTP POST, generated client, and browser result flow are not yet
implemented. Browser, command-line, and future headless clients must map this
same operation rather than create another scoring or persistence path.
The isolated local qualification admits the exact three-shape package through
Content, creates its placement through Curriculum, and reads this same operation
from non-browser and generated-browser clients. Repeated reads leave attempt,
response, score, completion, outbox, and learner projection/history counts
unchanged and retain identical answer-safe meaning after a normal restart.

## Persistence

The `assessment_0001_knowledge_check_evidence` stream owns
`assessment.attempts`, `responses`, `scores`, `completion_evidence`, and
`outbox`. One transaction appends all five records. Unique constraints enforce
learner/submission idempotency and one completion for the exact placed
assessment. Exact replay returns the original result; conflicting reuse and a
new post-completion submission fail distinctly. Update/delete triggers protect
accepted rows from ordinary mutation.

The additive `assessment_0002_practice_evidence` stream owns separate
`practice_attempts`, `practice_responses`, `practice_scores`,
`practice_completion_evidence`, and `practice_outbox` tables. One transaction
appends a complete definition-ordered aggregate and its confidential bounded
completion event. Unique constraints enforce learner/submission idempotency and
one completion for the exact placed practice version until the retry slice
adds policy. Exact canonical replay returns the original server IDs, time, and
result; conflicting reuse and a distinct post-completion submission fail
without partial rows. The tables use the same append-only trigger as existing
Assessment evidence and do not change knowledge-check storage.

The outbox row is durable event evidence only. No dispatcher, worker, broker,
consumer, or delivery guarantee is implemented.

The completion-event read operation is an explicit synchronous replay source.
It validates every stored envelope against the executable event v1 schema,
returns only the requested learner and placement, and uses occurrence/event ID
ordering. It never acknowledges, marks, deletes, or claims delivery of an
event. Later Learner-model and Audit consumers must remain idempotent and must
not read these tables directly.

