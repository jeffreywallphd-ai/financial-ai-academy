# Personal Workspace Contract

- Status: accepted; v1 contract, persistence, and protected API implemented
- Owner: Personal workspace
- Decision: [ADR-0021](../../adr/ADR-0021-focused-personal-learning-workspace.md)
- Executable family: [`contracts/learning/personal-workspace/v1/`](../../../contracts/learning/personal-workspace/v1/README.md)

## Boundary

Personal workspace owns learner-authored notes, bookmarks, collections, their
order, and archive state. Curriculum continues to own a referenced learning
opportunity or placed lesson, while Project owns its shell, mutable workspace,
immutable snapshots, and inert artifact manifests. A workspace reference
therefore carries exact bounded public identity/provenance facts but never
copies target business state, grants permission, provides artifact content, or
creates a mutation or execution path into another module.

## v1 rules

- One workspace is revisioned, bounded to 200 records and 50 collections.
- A collection is bounded to 100 unique record references.
- Workspace, learner, record, collection, selector, and idempotency identities
  use the normalized 1-to-128-character platform profile. Retained Curriculum
  opportunity, placement, and package identities keep Curriculum's 3-to-64-
  character producer profile.
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
- Additive Project references are exactly `project_workspace`,
  `project_snapshot`, and `project_artifact`. They retain safe Project title,
  lifecycle and revisions; snapshot identity/digest/close time; or inert
  artifact identity/version/kind/path/media/inspection/size/content-digest
  facts. Safe same-origin destinations correlate every retained identity. A
  retained artifact logical path must remain canonical under Project's path
  profile; traversal, dot/empty segments, reserved aliases, surrounding
  whitespace, control characters, backslashes, over-240-character values, and
  non-NFC forms fail closed.
- The Project adapter calls only learner-bound `open_project`, `open_workspace`,
  and `open_snapshot` public operations. It cannot call artifact download,
  export, mutation, object storage, or persistence and maps missing, denied,
  unavailable, or mismatched targets to one confidential source-unavailable
  result.
- The public create-note and create-bookmark requests accept only the closed
  Curriculum and Project selectors. The server derives learner identity and
  validation time, dispatches to the selector owner's learner-bound public
  operations, and verifies exact returned identities before any write.
- Authorized Project browser views may construct only the three closed Project
  selectors and send them to the shared `/saved-learning/new` flow. The browser
  derives same-origin return anchors from validated identities, never accepts a
  caller-supplied Project return path, and exposes no learner, authorization,
  Project-content, artifact-download, or storage fields in the save request.
- Curriculum and Project records share the same ordering, archive, and
  collection operations. Mixing those reference kinds does not change the
  mutation contract or move target ownership into Personal workspace.
- Repeated empty reads project the same revision-one workspace without writing.
  The first accepted mutation atomically persists revision two. Exact retries
  return the accepted workspace; stale revisions and changed idempotency-key
  reuse fail without replacing it.
- `GET /api/v1/personal-workspace` and
  `POST /api/v1/personal-workspace/mutations` use server-owned learner context
  and explicit read/write permissions. Browser and authenticated headless
  consumers share these reviewed OpenAPI and generated-client contracts.
- Source-bearing create requests also require the referenced owner's public
  read permission and reject caller-selected learner query parameters before
  workspace access. Missing workspace-owned records and collections have a
  distinct bounded `not_found` result.

## Exclusions

The protected API, generated client, and `Saved learning` browser entry flow
cover Curriculum and Project references. Project lifecycle-event handling
remains later CAP-0017 work. The boundary has no collaboration, cloud
synchronization, artifact preview/download/execution, Project mutation,
Portfolio association, Assessment or Learner-model effect, AI authority, or
personalized financial advice.
