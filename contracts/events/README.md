# Event Contracts

Versioned event-envelope and event-family JSON Schemas live here. Each event
identifies its owner, compatibility policy, idempotency expectations, and
representative fixtures.

The first family is the
[`assessment.knowledge-check.completed@1.0.0`](assessment/v1/README.md) event.
It points to durable Assessment evidence and intentionally makes no event-
delivery or consumer-implementation claim.
