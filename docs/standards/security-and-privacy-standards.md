# Security and Privacy Standards

- Status: proposed
- Canonical for: baseline security and privacy behavior

Apply a proportional security and privacy screen to every change.

At minimum, identify:

- protected data and assets,
- actors and authority,
- trust boundaries,
- untrusted inputs and external outputs,
- provider/model/data egress,
- abuse and failure cases,
- owning controls and denial evidence,
- logging/redaction implications,
- retention, rollback, and residual risk.

Keep learner context, provider secrets, market-data licenses, model inputs, prompts, diagnostics, and tenant identity least-privileged and explicitly scoped. New public exposure, executable plugins, identity flows, encryption, or external processing requires an accepted threat/architecture decision.

Learner identity flows must preserve [ADR-0006](../adr/ADR-0006-setup-selectable-learner-identity.md) and the [local identity security architecture](../security/local-identity-architecture.md), including provider-neutral context, server-owned sessions, exactly-one-mode setup, fail-closed authorization context, and redacted diagnostics.

Versioned lesson packages must preserve [ADR-0007](../adr/ADR-0007-platform-owned-versioned-lesson-package.md) and the [content-package contract](../architecture/contracts/content-package-contract.md). Treat imported content as untrusted; fail closed on unsupported versions or capabilities, unsafe paths and URLs, active content, media or integrity mismatches, resource-limit violations, and immutable-version conflicts. Provider approval or signatures do not bypass validation.

Community retained learner evidence must preserve [ADR-0008](../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) and the [community learner-evidence protection boundary](../security/community-learner-evidence-protection.md). Treat recovery sets as confidential and restore input as untrusted; require coordinated cross-store capture, external-secret exclusion, empty-target validation, restored-session and recovery-credential revocation, and honest disclosure that the community profile provides no RPO, RTO, hostile-host protection, or managed-cloud recovery posture.
