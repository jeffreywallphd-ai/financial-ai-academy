---
id: WRK-0011
kind: work-packet
planning_status: complete
authority: noncanonical
owner: codex-control-plane
updated: 2026-10-15
parent: SLI-0003
capability: CAP-0002
depends_on: []
decision_gates: []
parallel_safe_with: []
write_scope: ["dev-tools/control-plane", "dev-tools/planning/claim_packet.py", "dev-tools/planning/README.md", "dev-tools/planning/test_planning_tools.py", "docs/context/packs/delivery-planning.pack.md", "docs/planning/concurrent-work.md", "docs/planning/register.md", "docs/planning/vertical-slices/SLI-0003-resume-submit-interrupted-work-packet.md", "docs/planning/work-packets/WRK-0011-deliver-interruption-safe-packet-lifecycle.md", "docs/standards/testing-and-verification-standards.md"]
generated_artifacts: []
base_revision: 204c9f14a18bcfd6d48d41bdb5dfe43be32c4b8a
claim_id: WRK-0011:a142da6d-5923-4cf4-9a91-f2d5646cd4c1
claimed_by: codex-control-plane
claimed_at: 2026-10-15T12:30:14Z
---

# Agent Work Packet: Deliver the Interruption-Safe Packet Lifecycle

## Objective and Deliverable

Deliver the repository-local lifecycle kernel, atomic operational store, lease
and recovery rules, exact Git submission binding, and command interface needed
to claim, renew, resume, submit, release, and inspect one work packet without
manual lifecycle edits or repeated approval prompts.

## Required Context

Before any file change, read and follow every applicable `AGENTS.md`, the
repository-root `docs/README.md`, CAP-0002, SLI-0003, the planning guide and
register, concurrent-work protocol, decision-readiness register, delivery and
testing context packs, affected planning tools and tests, and the nearest
README. Accepted ADRs and canonical repository guidance outrank this packet.

## Decisions and Assumptions

- The controller is local, dependency-free Python and uses the existing
  CAP/SLI/WRK vocabulary; it does not port Research Observatory's Wave model.
- Operational state is ignored local evidence. Tracked packet frontmatter
  remains the public planning projection, and a recoverable transaction journal
  prevents a partially published transition from becoming authoritative.
- Default leases are bounded and renewable; active ownership cannot be stolen.
  Expired ownership is recovered through a deterministic command, not hand edits.
- Submission records an existing Git candidate and never commits, pushes,
  merges, publishes, or broadens scope.

## In Scope

- Versioned lifecycle and result/refusal contracts.
- Confined atomic JSON persistence, compare-and-swap revisions, lock handling,
  transaction recovery, and packet projection synchronization.
- Claim, renew, resume, recover, submit, release, and status commands.
- Clean-worktree, ancestry, declared-scope, declared-input, and exact-candidate
  checks with actionable denials.
- Compatibility with existing packet metadata and the current CAP package.
- Unit, Git-fixture, fault, and Windows multi-process coverage.
- Anti-rigidity tests proving the minimal path has one CAP check, no slice/work
  approval prompt, optional renewal, no full-suite requirement, and bounded
  command-directed recovery.

## Out of Scope

- Affected-check selection or reusable verification receipts.
- Independent review findings or corrected-descendant review rounds.
- Hosted/remote coordination, automatic commits, or external actions.
- Product-domain behavior or a new approval stage.

## Expected File and Boundary Impact

| Area | Inspect | Allowed to change | Reason |
| --- | --- | --- | --- |
| Control plane | Research Observatory lifecycle patterns and current planning helpers | `dev-tools/control-plane/` | Add the small local lifecycle kernel, adapters, CLI, and focused tests |
| Existing claim compatibility | `dev-tools/planning/claim_packet.py`, planning tests | Named planning files in `write_scope` | Route legacy claim semantics through or keep them compatible with the new lifecycle |
| Planning operations | Planning and concurrent-work guides | Named documentation files | Document supported commands, migration, lease, recovery, and exact-candidate behavior |
| Evidence standards | Delivery/testing guidance | Named context and standard files | Require direct interruption and anti-rigidity evidence |

## Contracts and Interfaces

- State envelope: version, monotonic revision, packet ID, lifecycle state,
  owner/claim/lease, base revision, submission, history, and transaction ID.
- Mutation contract: caller supplies expected revision; mismatch refuses with
  `state.version-conflict` and a status/retry remediation.
- Result contract: stable code, outcome, message, observed evidence, remediation,
  state revision, and optional data; JSON is available for every command.
- Lease contract: renewal only by the live owner and claim; expired leases cannot
  renew and must use explicit recovery.
- Submission contract: clean exact descendant, declared path set confined to the
  packet scope, complete declared inputs, and immutable candidate identity.

## Dependencies and Parallel Safety

No packet dependency. This packet is intentionally serial and not parallel-safe
because it establishes the lifecycle contracts used by every later CAP-0002
slice.

## Acceptance Scenarios

| Scenario | Given | When | Then | Evidence |
| --- | --- | --- | --- | --- |
| Minimal happy path | Ready packet in the approved CAP | Operator claims then submits a clean candidate | One claim and one submission succeed without lower-level approval or mandatory full-suite work | Command integration and anti-rigidity test |
| Resume interruption | Live or expired prior claim | Same owner resumes, or a new owner explicitly recovers expiry | History is preserved and no metadata hand edit is requested | Time-controlled integration test |
| Concurrent mutation | Two writers share an expected revision | Both attempt a transition | Exactly one succeeds and the loser gets version-conflict remediation | Multi-process test |
| Active owner protected | Unexpired lease belongs to another owner | Resume/recover/release is attempted | Mutation is refused with owner and expiry evidence | Denial test |
| Interrupted publish | A fault occurs before publication | Recovery/status runs | Prior or completed successor state is valid; partial bytes are not authoritative | Fault-injection test |
| Exact candidate | Clean descendant within declared scope | Submit runs | Candidate, base, paths, inputs, and repository identity are recorded | Git fixture test |
| Invalid candidate | Dirty, forked, stale, or out-of-scope tree | Submit runs | State does not advance and exact remediation is returned | Git denial tests |
| Path confinement | Traversal, absolute, symlink, or replacement is presented | Store or scope check runs | Access is refused before state publication | Security test |

## Verification Commands

- `python dev-tools/control-plane/test_control_plane.py`
- `python dev-tools/planning/test_planning_tools.py`
- `python dev-tools/planning/check_planning.py --require-local-approvals`
- `python docs/planning/skills/author-agent-work-packet/scripts/validate_work_packet.py docs/planning/work-packets/WRK-0011-deliver-interruption-safe-packet-lifecycle.md`
- `python dev-tools/agent/check_ready.py`

## Documentation and Evidence Update

Update the operational command reference, concurrent-work semantics, delivery
and testing guidance, SLI completion evidence, packet state, and planning
register. Record focused command results and remaining portability limits; do
not put local approval or reviewer records in tracked files.

## Stop Conditions

Stop for material CAP drift, a required remote service or credential, a conflict
with accepted planning authority, inability to preserve existing packet history,
or failure to demonstrate Windows-safe atomic publication and active-owner
protection. Local implementation defects remain inside this packet.

## Required Handoff

Report the delivered state/command contracts, compatibility behavior, files and
boundaries changed, exact focused and aggregate checks, interruption/concurrency
and anti-rigidity evidence, documentation impact, assumptions, platform gaps,
and CAP conformance.

## Completion Evidence

- Delivered a project-neutral transition kernel, stable result/refusal contract,
  pluggable project/projection/candidate ports, confined journaled CAS store,
  Financial AI Academy planning adapter, exact Git candidate adapter, and one
  command interface for status, claim, resume, renew, recover, submit, and release.
- `python dev-tools/control-plane/test_control_plane.py` passed 10 tests. Direct
  evidence covers the two-command ordinary path, no lower-level approval prompt,
  no mandatory full suite, no manual metadata repair, lease expiry/recovery,
  active-owner denial, CAS conflict, two-process exclusion on Windows,
  interrupted publication, project-neutral adapter reuse, dirty Git refusal,
  exact candidate binding, scope escape, and path confinement.
- `python dev-tools/planning/test_planning_tools.py` passed the planning integrity,
  reservation, collision, stale-package, and claim behavior suite.
- `python dev-tools/planning/check_planning.py` passed for 16 artifacts.
- The WRK and SLI validators passed. `python
  dev-tools/documentation/check_docs.py` passed for 136 Markdown files and the
  context catalog. The first documentation command used the wrong `dev-tools/docs`
  path and failed before running; the canonical command above then passed.
- `python dev-tools/agent/check_ready.py` passed all 10 aggregate checks.
- No public product contract, learner data, external service, credential,
  commit, push, deployment, or production state was changed. The control-plane
  state and transaction journal remain ignored local data.
- Windows received direct multi-process qualification. Other operating systems
  are supported by portable standard-library semantics but were not executed in
  this environment.
- The implementation remains within CAP-0002 and SLI-0003. It reuses Research
  Observatory patterns rather than its Wave vocabulary or controller, and the
  reusable core has an explicit synthetic-adapter contract test.

## Planning History

- 2026-10-15: Authored just in time as the single bounded delivery packet for
  SLI-0003 under the current CAP-0002 package.
