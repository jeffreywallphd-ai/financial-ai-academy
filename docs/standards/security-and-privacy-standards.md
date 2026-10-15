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

Content authoring must preserve [ADR-0017](../adr/ADR-0017-platform-native-human-reviewed-content-authoring.md) and the [content-authoring workflow contract](../architecture/contracts/content-authoring-workflow-contract.md). Bind review and publication to one exact draft revision; edits invalidate prior publication authority. Treat preview, imported/provider content, AI proposals, and future interoperability mappings as untrusted non-published input. Adapter or validation success cannot replace human review or bypass native safety, accessibility, ownership, provenance, and package validation.

Provider and background-job execution must preserve [ADR-0018](../adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md), the [provider-admission architecture](../architecture/deployment/provider-admission-and-job-delivery.md), and the [durable job-delivery contract](../architecture/contracts/job-delivery-contract.md). Activate only exact allowlisted reviewed packages; do not dynamically discover or install executable code. Exclude secrets and unbounded sensitive/provider payloads from job metadata, enforce current lease/fencing at commit, and require effect-level idempotency or reconciliation because timeout, cancellation, and at-least-once delivery can leave uncertain external outcomes.

Instructor review and learner-projection overrides must preserve [ADR-0019](../adr/ADR-0019-append-only-bounded-projection-overrides.md) and the [review/override architecture](../architecture/learning/instructor-review-and-projection-override.md). Keep source evidence and base projections immutable; require an exact registered field/policy, distinct proposal and confirmation actors, current authorization/source checks, time bounds, learner-visible reason/history, reversal, and audit. Do not implement evidence visibility or override authority until DEC-0016 defines tenant and permission isolation.

Community retained learner evidence must preserve [ADR-0008](../adr/ADR-0008-community-learner-evidence-protection-and-recovery.md) and the [community learner-evidence protection boundary](../security/community-learner-evidence-protection.md). Treat recovery sets as confidential and restore input as untrusted; require coordinated cross-store capture, external-secret exclusion, empty-target validation, restored-session and recovery-credential revocation, and honest disclosure that the community profile provides no RPO, RTO, hostile-host protection, or managed-cloud recovery posture.
