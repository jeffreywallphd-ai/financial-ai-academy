# Learning Discovery v1

Discovery v1 defines a provider-neutral, read-only learning-opportunity record
and stable browse result. Content remains authoritative for exact package and
publication facts; Curriculum remains authoritative for placement,
classification, prerequisites, availability, and destination facts. The record
is a rebuildable projection and never grants enrollment, eligibility,
recommendation, or execution authority.

The current conformance profile qualifies only `lesson` records backed by an
exact approved Curriculum placement and Content version. The closed `course`,
`lab`, and `project` kind vocabulary reserves portable meanings without
claiming that those destinations are delivered.

Run the direct contract evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/discovery
```
