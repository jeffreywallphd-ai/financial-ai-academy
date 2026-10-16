# Adaptation Module

Adaptation owns deterministic learner-specific eligibility and policy
application before any advisory ranking. Curriculum remains authoritative for
the exact graph and prerequisite meaning; Learner model remains authoritative
for bounded completion; Assessment remains authoritative for source evidence.

## Public deterministic core

`public.py` currently publishes closed source, completion, eligibility,
requirement, reason, request, result, and error values; the provider-neutral
`AdaptationOperations` protocol; canonical digest helpers; and the pure
`evaluate_navigation_state` rule baseline.

The baseline accepts an already validated exact Curriculum graph plus exactly
one typed source fact per activity. It evaluates `activity_prerequisite` edges
from source prerequisite to dependent target, preserves graph activity and
relationship order, and keeps optionality independent from availability,
completion, and eligibility. Missing, duplicate, unknown, malformed, or
incomplete source closure fails before a partial projection is returned.

The core has no repository, clock, random source, provider, model, host, web
framework, or database dependency. It stores nothing and makes no mastery,
competency, recommendation, ranking, credential, suitability, or advice claim.
Application gateways, protected transport, browser presentation, and composed
qualification are later SLI-0023 packets.
