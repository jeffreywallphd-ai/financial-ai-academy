# Assessment Module

Assessment owns private definition interpretation, answer-safe presentation,
response validation, deterministic scoring, reviewed feedback selection,
attempt/response/score/completion evidence, and the bounded completion event.

The additive practice-v1 parser/projector accepts single-select,
multiple-select exact-set, and fixed-decimal numeric definitions and produces
an immutable answer-safe presentation. It is transport-neutral and has no
persistence, clock, network, scoring, or learner-state side effect. The
protected public operation and API that will compose Content and Curriculum
are introduced in a later packet; browser and headless clients must use that
same operation rather than importing this adapter.

## Public operations

- `open_placed_knowledge_check(OpenPlacedKnowledgeCheckRequest) -> KnowledgeCheckPresentation`
- `submit_placed_knowledge_check(SubmitPlacedKnowledgeCheckRequest) -> KnowledgeCheckResult`
- `read_completed_knowledge_checks(ReadCompletedKnowledgeChecksRequest) -> tuple[KnowledgeCheckCompletionEvent, ...]`

The open operation resolves Curriculum and Content only through their public
facades and returns no correct option, private scoring object, or feedback. The
submission operation requires server-resolved learner context and exact public
version tokens. Assessment alone validates the option, calculates `0|1`, and
selects reviewed feedback.

## Persistence

The `assessment_0001_knowledge_check_evidence` stream owns
`assessment.attempts`, `responses`, `scores`, `completion_evidence`, and
`outbox`. One transaction appends all five records. Unique constraints enforce
learner/submission idempotency and one completion for the exact placed
assessment. Exact replay returns the original result; conflicting reuse and a
new post-completion submission fail distinctly. Update/delete triggers protect
accepted rows from ordinary mutation.

The outbox row is durable event evidence only. No dispatcher, worker, broker,
consumer, or delivery guarantee is implemented.

The completion-event read operation is an explicit synchronous replay source.
It validates every stored envelope against the executable event v1 schema,
returns only the requested learner and placement, and uses occurrence/event ID
ordering. It never acknowledges, marks, deletes, or claims delivery of an
event. Later Learner-model and Audit consumers must remain idempotent and must
not read these tables directly.

