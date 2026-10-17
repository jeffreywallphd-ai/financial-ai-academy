# Personal Workspace Contract

- Status: accepted; v1 portable contract and pure core implemented
- Owner: Personal workspace
- Decision: [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md)
- Executable family: [`contracts/learning/personal-workspace/v1/`](../../../contracts/learning/personal-workspace/v1/README.md)

## Boundary

Personal workspace owns learner-authored notes, bookmarks, collections, their
order, and archive state. Curriculum continues to own the referenced learning
opportunity or placed lesson. A workspace reference therefore carries exact
public identity and provenance but never copies target business state, grants
permission, or provides a mutation path into another module.

## v1 rules

- One workspace is revisioned, bounded to 200 records and 50 collections.
- A collection is bounded to 100 unique record references.
- Notes and labels are bounded learner text; no rich markup or executable
  content is admitted.
- A mutation includes an idempotency key and expected revision. Creation needs
  an externally issued ID; the pure core does not own identity, time, or random
  generation.
- Canonical digests use compact sorted-key UTF-8 JSON so persistence and API
  adapters can detect changed meaning.
- Records retain exact Curriculum/package/publication provenance and a last
  validation time. Learning routes use Curriculum's canonical same-origin
  `/learn/placements/{placement_id}` shape and must correlate with the exact
  retained placement. Unavailable or inaccessible targets remain an adapter
  and presentation concern; the workspace cannot silently substitute a target.

## Exclusions

The first seam has no persistence, authentication, authorization, HTTP,
generated client, browser view, collaboration, cloud synchronization, artifact
execution, Project membership, Portfolio association, AI authority, or
personalized financial advice. Those concerns require their owning packets and
decision readiness.
