# Reusable Local Control Plane

This directory contains the dependency-free local automation control plane. Its
core is intentionally reusable across projects:

- `contracts.py` defines stable success and actionable-refusal envelopes.
- `state.py` is a pure work-item, lease, recovery, and submission kernel.
- `store.py` provides confined locking, compare-and-swap revisions, atomic JSON
  publication, and recoverable state/projection transactions.
- `ports.py` defines the project, projection, and candidate adapter interfaces.
- `engine.py` composes those ports without knowing this repository's planning
  vocabulary.
- `verification.py` supplies project-neutral check catalogs, deterministic
  affected selection, privacy-minimized execution results, append-only receipts,
  and freshness validation.
- `review.py` supplies independent disposition, finding/closure, open-finding,
  and corrected-descendant lineage contracts through a pluggable local ledger.
- `policy.py` supplies a stable rule inventory, profile-neutral evaluation,
  privacy-minimized evidence digests, and confined atomic reports.
- `operator_status.py` derives concise work status and one next legal action
  from a project adapter without becoming a source of truth.
- `operations.py` closes acceptance at packet start, routes completed-work
  corrections, and runs bounded allowlisted maintenance sessions.
- `capabilities.py` confines effects to exact command IDs and normalized paths.
- `provenance.py` binds machine results without copying their payloads.
- `telemetry.py` emits anonymous local events and deterministic friction metrics.
- `harness.py` evaluates the tracked multi-turn safety/friction corpus.
- `portfolio.py` defines project-neutral hierarchy and dependency-graph
  contracts with deterministic validation and diagnostics.
- `portfolio_ordering.py` derives hierarchy-aware ready sets, blocked reasons,
  explicit-priority ordering, and visible ties without inventing product value.
- `portfolio_conflicts.py` classifies dependency and coordination evidence as
  compatible, incompatible, or unknown and builds pairwise-safe groups.
- `file_leases.py` provides vocabulary-neutral, exact-file intent and renewable
  lease contracts with atomic all-or-nothing acquisition and explicit recovery.
- `portfolio_allocation.py` composes graph, readiness, compatibility, branch,
  and edit facts into proposal-only lanes with stable replanning evidence.
- `portfolio_harness.py` executes tracked synthetic scenarios through the real
  generic pipeline and evaluates hard safety separately from friction budgets.
- `roadmap_review.py` validates machine-readable candidate catalogs and composes
  inert plan documents, hierarchy, order, compatibility, diagnostics, and source
  fingerprints into a project-neutral read-only review contract.

`financial_academy.py` and `git_candidate.py` are adapters. They map this
repository's CAP/SLI/WRK package authority, frontmatter projection, scope, and
Git facts onto the reusable core. Another project can start with the core and
implement its own adapters without inheriting CAP/SLI/WRK names or approval
policy. `financial_academy_policy.py` and `financial_academy_status.py` are the
project-specific fact and status adapters; replace them in another project.
`financial_academy_portfolio.py` maps this repository's capability catalog and
CAP/SLI/WRK artifacts into the generic portfolio graph without granting
authority or inventing dependencies.
`financial_academy_editing.py` binds generic file coordination to one active
WRK claim and its declared scope while allowing that work, its parent slice, or
its parent capability to serve as the logical coordination lane.
`financial_academy_roadmap_review.py` maps the versioned product capability
catalog and planning artifacts onto the generic review contract. The Markdown
planning register remains a synchronized human index and is not the runtime
database.

For reuse, copy the project-neutral modules and supply project-owned node facts
to `portfolio.analyze`, current authority/priority to `portfolio_ordering.plan`,
coordination evidence to `portfolio_conflicts.analyze_compatibility`, and local
intent/lease records to `portfolio_allocation.allocate`. Implement repository
authority and filesystem scope checks outside those modules, as this repository
does in `financial_academy_portfolio.py` and `financial_academy_editing.py`.
Generic code and the portfolio evaluation corpus use no CAP/SLI/WRK identifier
assumption; adapters may retain whatever planning vocabulary their project owns.

## Commands

Run from the repository root:

```text
python dev-tools/control-plane/control_plane.py status WRK-0010
python dev-tools/control-plane/control_plane.py claim WRK-0010 --owner <owner>
python dev-tools/control-plane/control_plane.py resume WRK-0010 --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py renew WRK-0010 --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py recover WRK-0010 --owner <owner>
python dev-tools/control-plane/control_plane.py submit WRK-0010 --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py release WRK-0010 --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py plan-checks WRK-0010
python dev-tools/control-plane/control_plane.py verify WRK-0010
python dev-tools/control-plane/control_plane.py validate-receipt <ignored-receipt-path>
python dev-tools/control-plane/control_plane.py review-status WRK-0010
python dev-tools/control-plane/control_plane.py record-review WRK-0010 --reviewer-label <independent-label> --from .local-codex/review-request.json
python dev-tools/control-plane/control_plane.py resubmit WRK-0010 --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py resubmit WRK-0010 --owner <owner> --claim-id <claim-id> --cleanup-only
python dev-tools/control-plane/control_plane.py policy-check --profile local --report-path artifacts/control-plane/policy.json
python dev-tools/control-plane/control_plane.py operator-status [WRK-0010]
python dev-tools/control-plane/control_plane.py packet-start WRK-0010
python dev-tools/control-plane/control_plane.py correction-route WRK-0010 --path docs/example.md --reason-code defect.fixed
python dev-tools/control-plane/control_plane.py maintenance-status
python dev-tools/control-plane/control_plane.py maintenance-start --defect-code transaction.interrupted --allow recover-interrupted-transaction
python dev-tools/control-plane/control_plane.py maintenance-action recover-interrupted-transaction
python dev-tools/control-plane/control_plane.py maintenance-finish
python dev-tools/control-plane/control_plane.py telemetry-report --report-path artifacts/control-plane/telemetry.json
python dev-tools/control-plane/control_plane.py harness-evaluate --report-path artifacts/control-plane/harness-evaluation.json
python dev-tools/control-plane/control_plane.py portfolio-graph
python dev-tools/control-plane/control_plane.py roadmap-review
python dev-tools/control-plane/control_plane.py portfolio-plan --level capability --priority CAP-0003
python dev-tools/control-plane/control_plane.py portfolio-compatibility --level capability
python dev-tools/control-plane/control_plane.py portfolio-allocate --level slice --priority SLI-0013
python dev-tools/control-plane/control_plane.py edit-intent --unit-id CAP-0003 --work-id WRK-0020 --owner <owner> --claim-id <claim-id> --path dev-tools/control-plane/file_leases.py
python dev-tools/control-plane/control_plane.py edit-acquire --unit-id SLI-0012 --work-id WRK-0020 --owner <owner> --claim-id <claim-id> --path dev-tools/control-plane/file_leases.py
python dev-tools/control-plane/control_plane.py edit-status --path dev-tools/control-plane/file_leases.py
python dev-tools/control-plane/control_plane.py edit-renew <lease-id> --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py edit-release <lease-id> --owner <owner> --claim-id <claim-id>
python dev-tools/control-plane/control_plane.py edit-recover --unit-id WRK-0020 --work-id WRK-0020 --owner <owner> --claim-id <claim-id> --path dev-tools/control-plane/file_leases.py
```

For the dynamic browser review of all product capability candidates, run:

```text
python dev-tools/roadmap-review-site/server.py
```

Open `http://127.0.0.1:8765`. The one command compiles its TypeScript client to
ignored local output and serves a loopback-only, GET/HEAD-only view over the
current `roadmap-review-v1` projection. See
`dev-tools/roadmap-review-site/README.md` for the dynamic candidate/CAP/slice/
work routes, missing-refinement behavior, inert plan rendering, safeguards,
focused checks, and the reuse seam.

Add `--json` before the subcommand for the stable machine result. Mutations
automatically finish an interrupted journal before proceeding. Submission
records an existing clean exact Git candidate; it never commits, pushes, merges,
publishes, deploys, or runs a repository-wide test suite.

The focused qualification commands are:

```text
python dev-tools/control-plane/test_control_plane.py
python dev-tools/control-plane/test_verification.py
python dev-tools/control-plane/test_review.py
python dev-tools/control-plane/test_policy.py
python dev-tools/control-plane/test_operations.py
python dev-tools/control-plane/test_qualification.py
python dev-tools/control-plane/evaluate_harness.py
python dev-tools/control-plane/test_portfolio.py
python dev-tools/control-plane/test_portfolio_ordering.py
python dev-tools/control-plane/test_portfolio_conflicts.py
python dev-tools/control-plane/test_file_leases.py
python dev-tools/control-plane/test_portfolio_allocation.py
python dev-tools/control-plane/test_portfolio_qualification.py
python dev-tools/control-plane/evaluate_portfolio.py
python dev-tools/control-plane/test_roadmap_review.py
```

Tests include a synthetic adapter with no Financial AI Academy vocabulary,
interrupted publication recovery, Windows multi-process exclusion, exact Git
scope checks, and anti-rigidity assertions for the two-command claim/submit path.
Verification tests cover narrow-versus-full selection, deterministic plan
digests, failed and timed-out attempts, append-only receipt chains, candidate
drift, stale evidence, raw-output minimization, and disabled optimistic reuse.
The Financial AI Academy catalog classifies web source, production-build,
generated-client, mocked-browser, roadmap-review, local-runtime, local-script,
and documentation paths separately. Each class selects only the prepared Node
24/npm 10.8.2, Python, Chromium, or live PostgreSQL behavior needed for that
impact. Approved-lesson browser and runner changes select the existing live
PostgreSQL/Python/static-browser qualification; documentation-only and
Python-only changes do not inherit unrelated TypeScript or aggregate-readiness
work.

Roadmap-review implementation paths are also divided by their owning boundary:
TypeScript source selects qualification, typecheck, DOM unit, and Chromium
behavior; server/static-shell changes select the server and Chromium checks;
test-only changes select their owning suite; and the roadmap README remains a
documentation-only impact. When the web wrapper is given explicit
`FINANCIAL_AI_ACADEMY_NODE_EXECUTABLE` and `FINANCIAL_AI_ACADEMY_NPM_CLI`
values, it prepends that Node directory and exports the current Python
executable to child processes. Nested compilation and test servers therefore
use the prepared runtime without requiring a global Node or Python command.

The production-build and live wrappers copy the exact tracked candidate into an
isolated temporary snapshot, omit any tracked `apps/web/dist` output, and link
the already prepared web dependencies. Production build and live qualification
then run entirely inside that snapshot. They never read, replace, restore, or
remove the working tree's `apps/web/dist`, including when that path is absent, a
file, a link, or is being changed concurrently. Temporary output is deleted
with the snapshot, while the controller's post-run clean-HEAD check remains
authoritative.
The roadmap-review browser check likewise runs from an isolated candidate
snapshot and substitutes an ephemeral loopback port only in that snapshot, so
an already running review site cannot block qualification or be reused as
evidence.
Review tests cover independent one-round acceptance, self-review denial,
immutable candidate rounds, blocking findings, explicit closure, stale-receipt
denial, strict-descendant corrections, fresh-verification requirements,
root-cause escalation, append-only ignored-ledger storage, and proportionate
cleanup findings. Cleanup cannot cause an adverse disposition. A strict
cleanup-only descendant of an accepted candidate inherits that review only
when Git proves the incremental delta changes whitespace or blank lines and the
descendant has its own qualifying affected-verification receipt. Repeated
cleanup descendants retain the original accepted basis. Semantic formatting,
styling, functionality, accessibility, security, data, contract, policy, and
evidence changes retain the ordinary review path; repository policy may defer
non-functional styling rather than interrupt the current functional CAP.
Policy/status tests cover local/CI rule parity, explicit unavailable evidence,
report confinement and privacy, stale-local reconciliation, one-command
read-only status, bounded remediation, and absence of approval or full-suite
requirements on the ordinary status path.
Portfolio tests cover deterministic hierarchy projection, missing and
superseded dependencies, cycles, invalid ancestry, future just-in-time slice
bindings, authority separation, and read-only CLI behavior.
Ordering tests cover CAP/SLI/WRK readiness, current parent authority, completed
dependencies, explicit priority, unresolved ties, precise refusals, and
read-only behavior.
Compatibility tests cover dependency paths, normalized scope and generated
output overlap, contracts, exclusive resources, active branches, reciprocal WRK
declarations, safe-set closure, and unknown-evidence anti-rigidity.
File coordination tests cover process races, path aliases, atomic multi-file
acquisition, non-blocking intent, prompt release, live-owner protection,
complete-set recovery lineage, active-WRK authorization, and the absence of read
or directory locks.
Allocation tests use non-CAP/SLI/WRK identifiers against the generic core and
cover priority-preserving lanes, dependency blocking, narrow unknown isolation,
active descendants, `codex/*` branch observations, live edit facts, deterministic
replanning, explicit non-authority, and read-only repository CLI behavior.
The real-core portfolio corpus covers active containers, cycles, dependencies,
slice/work parallelism, exact overlap, and narrow unknown evidence. Its report
contains only scenario IDs, digests, categorical metrics, and violation codes.
Roadmap-review tests cover exact machine-catalog accounting, explicit formal
mapping, unplanned candidates, internal capabilities, refined and missing
children, dynamic source fingerprints, inert Markdown, path confinement,
privacy, generic vocabulary, and one-command read-only behavior.

CI deliberately evaluates the same policy inventory while marking ignored
local authority and lifecycle facts `not-evaluated`. That absence never becomes
a fabricated pass and does not block public checks. Reports contain digests and
counts rather than raw command or review content.

`packet-start` is idempotent for the same claim and semantic plan. It freezes
acceptance and scope digests, not prose history, timestamps, or completion
evidence, so normal documentation updates do not create false drift. Low- and
medium-risk routes remain affected-check plus one-review paths; only explicit
shared/control impact adds aggregate readiness.

Completed work is never reopened in place. `correction-route` creates an
ignored, scope-confined route to one descendant WRK under the same slice; that
just-in-time packet does not need a new approval while it conforms to the CAP.
Maintenance accepts only registered action IDs, pauses normal CLI mutations,
preserves append-only event evidence, and exits only after an action succeeds
and local health passes. It has no arbitrary shell or metadata-edit surface.

Affected verification executes through a `capability-grant-v1` containing exact
catalog command IDs, matched repository paths, and the `subprocess` effect; argv
never belongs to a grant. CLI results and new receipts carry
`control-provenance-v1` digests. Every CLI invocation also attempts one
`control-event-v1` record containing only categorical result fields, duration,
and remediation count. Aggregates distinguish portfolio attempts/refusals and
file-edit contention/recovery/release counts without recording work or path
identifiers. Telemetry failure is intentionally non-blocking.

The tracked `evals/scenarios.json` corpus deterministically checks thirteen
multi-turn flows and hard safety assertions. Friction budgets can fail an
evaluation but cannot offset a safety violation. Neither telemetry nor the
evaluator grants authority, changes lifecycle state, or sends data remotely.
The separate `evals/portfolio-scenarios.json` corpus runs seven scenarios through
the actual project-neutral implementation and enforces useful-concurrency,
isolation, blockage, and unresolved-evidence budgets after safety assertions.

`portfolio-allocate` always selects exactly one hierarchy level. Ancestors are
reported as context and active descendants, never as duplicate editing owners.
The output is a proposal: it cannot create agents, claims, branches, or file
leases. Pass `--previous-plan .local-codex/...json` to compare with an earlier
allocation and receive categorical lane/group changes while preserving the
earlier plan digest. Unknown compatibility isolates only the affected lanes.

Review request files must remain under `.local-codex/`. Reviewer labels,
dispositions, findings, closures, notes, candidate/evidence bindings, and review
history are written only to `.local-codex/approvals/ledger.json`; tracked files
must never summarize or copy those records.
