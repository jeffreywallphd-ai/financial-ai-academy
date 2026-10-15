# Assessment Completion Event v1

`knowledge-check-completed.schema.json` defines the Assessment-owned
`assessment.knowledge-check.completed` event. Its `event_id` is the delivery
deduplication identity. Its `idempotency_key` is the stable evidence identity
and remains the same if a producer retries publication. `aggregate` identifies
the attempt, while `source.evidence_id` points to the durable Assessment
evidence.

The bounded payload carries the learning context and deterministic score
needed by future Learner-model and Audit consumers. It intentionally excludes
the selected option, correct option, feedback text, raw response, and private
definition. This contract establishes durable event meaning only; it does not
select a broker, queue, dispatcher, delivery guarantee, or consumer.

