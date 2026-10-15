# Learning Discovery Query v1

Discovery-query v1 adds deterministic matching, metadata filters, closed sorts,
bounded pagination, and generation-bound cursors over validated discovery-v1
records. It does not change the discovery-v1 record or queryless browse
envelope, grant access, infer eligibility, or add relevance and personalized
ranking.

Raw text and filter arrays are bounded before canonicalization. Text is then
normalized with Unicode NFKC, collapsed whitespace, and Unicode case-folding;
each field permits no more than ten canonical terms. Repeated filters and
noncanonical input order are accepted within the raw bound, then projected to
sorted unique applied-query values. All general terms must match across title,
summary, objectives, topics, or prerequisite summary; prerequisite-query terms
match only the prerequisite summary. Repeated values in one filter dimension
use OR, while different dimensions use AND. Default order preserves the
projection; closed alternative sorts use opportunity identity as the final
tie-break.

Run the direct contract evidence from the repository root:

```powershell
uv run --project backend pytest backend/tests/contract/discovery_query
```
