# Development Tools

This directory contains narrowly scoped, testable repository checks and generators:

- contract generation and compatibility,
- module dependency enforcement,
- documentation/context integrity,
- agent-support evaluations,
- test orchestration.

Tools must be deterministic, avoid arbitrary command execution when an allowlist is sufficient, and report exact evidence.

Current entry points:

- `agent/check_ready.py` runs the fixed aggregate readiness allowlist, including the constrained CI workflow check;
- `planning/check_planning.py` validates planning identity, lifecycle, approvals, references, register state, and ownership;
- `planning/reserve_id.py` and `planning/claim_packet.py` perform constrained planning coordination mutations;
- `documentation/check_docs.py` verifies documentation and context-catalog integrity;
- `design/check_design_system.py` verifies semantic tokens and production icon assets.

Before changing a tool, follow applicable `AGENTS.md` and repository-root `docs/README.md`, inspect its callers and evidence consumers, and add deterministic positive and refusal-path tests. Tools do not grant approval or external-action authority.
