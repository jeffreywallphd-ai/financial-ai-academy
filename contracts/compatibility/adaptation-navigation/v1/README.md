# Adaptation Navigation State v1 Compatibility Corpus

The approved pair binds the implemented Curriculum graph fixture to one
explicit source-fact closure and its deterministic navigation-state result. It
contains a completed required entry, an unlocked required dependent activity,
an eligible optional entry, an unavailable optional entry, and an eligible
unbranched entry.

The `flexible/case.json` fixture records a second executable shape with absent
presentation hints, reversed activity and source-fact order, same-kind branch
sharing, optional-but-locked activities, multiple entry activities, an
unbranched activity, and two ordered unmet prerequisites. Tests materialize it
against the versioned Curriculum graph and validate it through both independent
contract runners and the public domain policy. Additional denial cases are
derived for missing, duplicate, unknown, malformed, or conflicting facts.

The flexible case intentionally records transformations and facts instead of a
second complete copy of the Curriculum graph. This keeps Curriculum as the
single owner of pathway meaning while making the permitted variations durable
and reviewable without freezing one pathway size or visual order.

The corpus is synthetic and contains no learner identity, private response,
provider payload, model output, mastery claim, recommendation, or approval
record.
