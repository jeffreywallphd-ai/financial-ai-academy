# Agent Readiness

`check_ready.py` is the single deterministic repository-readiness entry point.
It runs a fixed allowlist of planning, skill, prompt-evaluation, documentation,
CI-workflow, and design-system checks without evaluating repository-provided shell commands.

Before changing this runner, read and follow every applicable `AGENTS.md`, the
repository-root `docs/README.md`, and the standards/testing context they route.

Run locally with:

```text
python dev-tools/agent/check_ready.py
```

Use `--base-ref <revision>` when lifecycle transitions must be compared with a
known base. CI uses `--profile ci` and supplies the pull-request base revision.
Use `--json` for automation evidence and `--verbose` for successful check output.

The runner is read-only. It does not install skills, approve plans, claim work,
commit, push, publish, deploy, or call external services. When local skill
discovery is installed, it verifies that installation has not drifted.

`check_ci_workflow.py` verifies the committed workflow's required triggers,
read-only permissions, full-history checkout, current official action majors,
base-revision pull-request check, and absence of higher-risk trigger/permission
tokens. Repository-host branch protection remains a separate administrator control.
