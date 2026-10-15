# Curriculum Graph v1

Curriculum Graph v1 defines one provider-neutral, immutable approved curriculum
version. Curriculum owns objectives, competencies, activities, branches, and
typed relationships. Activities retain exact public lesson or assessment
placement references; the graph does not embed Content or Assessment payloads.

`presentation_order` is an optional partial hint. It cannot define
prerequisites, eligibility, completion, or advancement, and consumers must
remain correct when it is absent. Multiple entry activities, multiple optional
branches, activities shared across branches of the same kind, and unbranched
activities are valid. An activity cannot simultaneously acquire required and
optional meaning through different branches.

`published_at` uses a deliberately conservative timestamp profile: uppercase
`T`, uppercase `Z` or a numeric offset, seconds from `00` through `59`, and at
most six fractional digits. Calendar-invalid values and leap seconds are
rejected. This profile matches the precision retained by the public Python
type and prevents distinct accepted timestamps from collapsing to one digest.

`graph_digest` is SHA-256 over UTF-8 JSON with sorted object keys, compact
separators, and `graph_digest` removed. Before serialization, `published_at` is
normalized to UTC with a trailing `Z`, and empty arrays inside an explicitly
present `presentation_order` object are omitted. The object itself remains
present even when every hint is empty. No other collection is reordered or
removed.

The compatibility corpus in
[`../../../compatibility/curriculum-graph/v1/`](../../../compatibility/curriculum-graph/v1/README.md)
fixes canonical digest behavior, typed-edge validation, prerequisite cycle
denials, exact resource references, and flexible valid graph shapes.

Run the direct contract evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/curriculum_graph
```

This contract does not qualify persistence, publication commands, API
authorization, eligibility, activity launch, browser rendering, or adaptive
ranking.
