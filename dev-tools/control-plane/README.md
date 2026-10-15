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

`financial_academy.py` and `git_candidate.py` are adapters. They map this
repository's CAP/SLI/WRK package authority, frontmatter projection, scope, and
Git facts onto the reusable core. Another project can start with the core and
implement its own adapters without inheriting CAP/SLI/WRK names or approval
policy. `financial_academy_policy.py` and `financial_academy_status.py` are the
project-specific fact and status adapters; replace them in another project.

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
```

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
```

Tests include a synthetic adapter with no Financial AI Academy vocabulary,
interrupted publication recovery, Windows multi-process exclusion, exact Git
scope checks, and anti-rigidity assertions for the two-command claim/submit path.
Verification tests cover narrow-versus-full selection, deterministic plan
digests, failed and timed-out attempts, append-only receipt chains, candidate
drift, stale evidence, raw-output minimization, and disabled optimistic reuse.
Review tests cover independent one-round acceptance, self-review denial,
immutable candidate rounds, blocking findings, explicit closure, stale-receipt
denial, strict-descendant corrections, fresh-verification requirements,
root-cause escalation, and append-only ignored-ledger storage.
Policy/status tests cover local/CI rule parity, explicit unavailable evidence,
report confinement and privacy, stale-local reconciliation, one-command
read-only status, bounded remediation, and absence of approval or full-suite
requirements on the ordinary status path.

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
and remediation count. Telemetry failure is intentionally non-blocking.

The tracked `evals/scenarios.json` corpus deterministically checks seven
multi-turn flows and hard safety assertions. Friction budgets can fail an
evaluation but cannot offset a safety violation. Neither telemetry nor the
evaluator grants authority, changes lifecycle state, or sends data remotely.

Review request files must remain under `.local-codex/`. Reviewer labels,
dispositions, findings, closures, notes, candidate/evidence bindings, and review
history are written only to `.local-codex/approvals/ledger.json`; tracked files
must never summarize or copy those records.
