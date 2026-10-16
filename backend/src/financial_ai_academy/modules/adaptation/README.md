# Adaptation Module

Adaptation owns deterministic learner-specific eligibility and policy
application before any advisory ranking. Curriculum remains authoritative for
the exact graph and prerequisite meaning; Learner model remains authoritative
for bounded completion; Assessment remains authoritative for source evidence.

## Public deterministic core

`public.py` publishes closed source, completion, eligibility,
requirement, reason, request, result, and error values; the provider-neutral
`AdaptationOperations` protocol; canonical digest helpers; and the pure
`evaluate_navigation_state` rule baseline.

The same public surface includes the pure `resolve_activity_launch` decision
and closed `activity-launch-v1` mapping. It accepts only an exact validated
Curriculum graph, its complete matching Navigation-state v1 projection, and
one activity ID. It rechecks graph/projection identity, state order and
closure, projection integrity, availability, and eligibility before deriving
`/learn/placements/{placement_id}` from the exact lesson reference. Completed
eligible lessons can be reopened for review. Locked, unavailable, unknown,
malformed, or assessment activities return bounded errors without a
destination.

The baseline accepts an already validated exact Curriculum graph plus exactly
one typed source fact per activity. It evaluates `activity_prerequisite` edges
from source prerequisite to dependent target, preserves graph activity and
relationship order, and keeps optionality independent from availability,
completion, and eligibility. Missing, duplicate, unknown, malformed, or
incomplete source closure fails before a partial projection is returned.

The framework-free application service opens one exact graph through the
Curriculum public facade, observes each exact activity source, maps lesson
completion through the Learner-model public facade, and evaluates the pure
policy once with an injected UTC clock. The two source dimensions degrade
independently: a failed activity read does not erase valid completion, and a
failed completion read does not rewrite activity availability. Because no
accepted assessment-activity completion projection exists, assessment
completion remains explicitly `unavailable` rather than inferred.

The module has no repository, random source, provider, model, host, web
framework, or database dependency. It stores nothing and makes no mastery,
competency, recommendation, ranking, credential, suitability, or advice claim.
The API host exposes only the public application operation. The reviewed
generated client and browser present the returned state, ordered reasons,
references, policy identity, and provenance without recomputing policy or
digests. Composed live qualification covers the exact retained-completion
transition, complete graph/API/UI parity, bounded missing-version and
authorization responses, accessible peer views, and isolated
PostgreSQL/Python/static-browser execution. Durable recommendations, model
ranking, experiments, managed-cloud adapters, and assessment completion remain
outside this implemented boundary. Application composition, HTTP,
authorization, generated clients, browser navigation, and return context also
remain separate from the current pure launch seam.
