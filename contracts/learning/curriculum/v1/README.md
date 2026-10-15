# Curriculum Graph v1

Curriculum Graph v1 defines one provider-neutral, immutable approved curriculum
version. Curriculum owns objectives, competencies, activities, branches, and
typed relationships. Activities retain exact public lesson or assessment
placement references; the graph does not embed Content or Assessment payloads.

`presentation_order` is an optional partial hint. It cannot define
prerequisites, eligibility, completion, or advancement, and consumers must
remain correct when it is absent. Multiple entry activities, multiple optional
branches, activities shared across optional branches, and unbranched activities
are valid. An activity cannot simultaneously acquire required and optional
meaning through different branches.

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
