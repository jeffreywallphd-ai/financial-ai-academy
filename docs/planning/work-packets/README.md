# Agent Work Packets

An agent work packet is the smallest independently executable planning artifact. It gives one automated agent one objective, bounded write scope, current authority, dependencies, acceptance scenarios, verification commands, documentation impact, and stop conditions.

Name files `WRK-####-short-name.md` and start from [the work-packet template](../templates/work-packet-template.md).

A packet must not require the implementing agent to choose unresolved product meaning, architecture, identity, tenancy, licensing, model authority, financial policy, recovery posture, or external execution policy. If it does, create a decision request and mark the packet `decision-blocked`.

Packets may run in parallel only when each declares independent prerequisites, contracts, and write scopes. One agent owns a packet from `active` through handoff unless ownership is explicitly transferred.

Declare repository-relative `write_scope` paths and any `generated_artifacts` before planning approval. Parallel-safe relationships must be reciprocal and remain invalid when either declared scope overlaps. On activation, record `base_revision`, a unique `claim_id`, `claimed_by`, and UTC `claimed_at`. Use [the concurrent-work protocol](../concurrent-work.md) and the deterministic claim helper instead of coordinating ownership only in conversation.

Use `author-agent-work-packet` to prepare the complete closed packet set for a slice. Keep planning and implementation stages separate in the ignored local ledger, while allowing one response per stage to cover every explicitly listed packet. Work starts only after both stages are approved locally with implementation scope exactly matching each current `write_scope` and the user currently asks to implement the named slice or work. Execute and complete packets one at a time in dependency order; new or materially revised packets require renewed approval.
