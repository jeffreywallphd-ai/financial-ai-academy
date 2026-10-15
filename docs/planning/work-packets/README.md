# Agent Work Packets

An agent work packet is the smallest independently executable planning artifact. It gives one automated agent one objective, bounded write scope, current authority, dependencies, acceptance scenarios, verification commands, documentation impact, and stop conditions.

Name files `WRK-####-short-name.md` and start from [the work-packet template](../templates/work-packet-template.md).

A packet must not require the implementing agent to choose unresolved product meaning, architecture, identity, tenancy, licensing, model authority, financial policy, recovery posture, or external execution policy. If it does, create a decision request and mark the packet `decision-blocked`.

Packets may run in parallel only when each declares independent prerequisites, contracts, and write scopes. One agent owns a packet from `active` through handoff unless ownership is explicitly transferred.

Declare repository-relative `write_scope` paths and any `generated_artifacts` before claim. Parallel-safe relationships must be reciprocal and remain invalid when either declared scope overlaps. On activation, record `base_revision`, a unique `claim_id`, `claimed_by`, and UTC `claimed_at`. Use [the concurrent-work protocol](../concurrent-work.md) and the deterministic claim helper instead of coordinating ownership only in conversation.

Use `author-agent-work-packet` to prepare each bounded packet immediately before it starts. Work starts after deterministic validation, current CAP-package conformance, satisfied dependencies, and a successful claim. Execute and complete packets one at a time in dependency order unless scopes are explicitly parallel-safe. New or revised packets need no approval when they remain within the approved CAP and slice contracts; material CAP drift returns the CAP package to shaping.
