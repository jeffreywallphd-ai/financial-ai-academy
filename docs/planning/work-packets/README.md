# Agent Work Packets

An agent work packet is the smallest independently executable planning artifact. It gives one automated agent one objective, bounded write scope, current authority, dependencies, acceptance scenarios, verification commands, documentation impact, and stop conditions.

Name files `WRK-####-short-name.md` and start from [the work-packet template](../templates/work-packet-template.md).

A packet must not require the implementing agent to choose unresolved product meaning, architecture, identity, tenancy, licensing, model authority, financial policy, recovery posture, or external execution policy. If it does, create a decision request and mark the packet `decision-blocked`.

Packets may run in parallel only when each declares independent prerequisites, contracts, and write scopes. One agent owns a packet from `active` through handoff unless ownership is explicitly transferred.

Declare repository-relative `write_scope` paths and any `generated_artifacts` before planning approval. Parallel-safe relationships must be reciprocal and remain invalid when either declared scope overlaps. On activation, record `base_revision`, a unique `claim_id`, `claimed_by`, and UTC `claimed_at`. Use [the concurrent-work protocol](../concurrent-work.md) and the deterministic claim helper instead of coordinating ownership only in conversation.

Use `author-agent-work-packet` to prepare packets. Keep `planning_approval` and `implementation_approval` separate. Work starts only after both are approved, `implementation_authority` is recorded, and the user currently asks to implement the named work.
