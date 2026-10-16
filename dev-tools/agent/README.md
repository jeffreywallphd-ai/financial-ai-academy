# Agent Readiness

`check_ready.py` is the single deterministic repository-readiness entry point.
It runs a fixed allowlist of planning, skill, prompt-evaluation, control-plane,
documentation, CI-workflow, learner-language, and design-system checks without
evaluating repository-provided shell commands. A focused readiness-catalog test
protects command construction without recursively starting readiness.

Before changing this runner, read and follow every applicable `AGENTS.md`, the
repository-root `docs/README.md`, and the standards/testing context they route.

Run locally with:

```text
python dev-tools/agent/check_ready.py
```

Use `--base-ref <revision>` when lifecycle transitions must be compared with a
known base. The runner forwards that exact revision to both planning lifecycle
validation and the changed-copy learner-language check. It never promotes the
language check to full-scope mode. CI uses `--profile ci` and supplies the
pull-request base revision.
Use `--json` for privacy-minimized automation evidence and `--verbose` for
successful interactive output. `--report-path
artifacts/control-plane/agent-readiness.json` atomically retains the same
machine report. Machine records contain output hashes and byte counts, never raw
subprocess output or local command paths.

The fixed allowlist also runs control-plane capability/provenance/telemetry
tests and the tracked deterministic multi-turn corpus. These checks enforce hard
safety/privacy constraints and explicit friction budgets without using a model
grader or reading local telemetry.

The runner is read-only. It does not install skills, approve plans, claim work,
commit, push, publish, deploy, or call external services. When local skill
discovery is installed, it verifies that installation has not drifted.

`check_ci_workflow.py` verifies the committed workflow's required triggers,
read-only permissions, full-history checkout, current official action majors,
base-revision pull-request check, and absence of higher-risk trigger/permission
tokens. CI uploads the report even when readiness fails, with read-only
repository permissions and bounded retention. Repository-host branch protection
remains a separate administrator control.
