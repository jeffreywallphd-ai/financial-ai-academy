# Context Pack: Security and Risk

## Use When

Work affects identity, tenancy, privacy, financial claims, market-data terms, external sources, plugins, secrets, public exposure, executable inputs, or sensitive diagnostics.

## Preserve

- Least privilege and explicit request/job/tenant context
- Exactly one setup-selected identity provider resolves to a provider-neutral learner context and server-owned session
- Education/advice separation
- Source-backed provider permissions and claims
- Inspection without execution for untrusted plugins
- Schema, semantic, path, media, integrity, resource-bound, and renderer validation for untrusted lesson packages
- Revision-bound human review and atomic publication for platform-native
  authoring; preview, AI proposals, provider/import content, and future mappings
  remain untrusted and cannot become publication authority.
- Private-host community learner-evidence protection, confidential recovery sets, untrusted restore validation, external-secret exclusion, and restored-session/recovery revocation
- Safe diagnostics and explicit data/model egress
- Direct `single_profile` lesson evidence stays inside its loopback/private-host boundary and must not be generalized to built-in, OIDC, remote, or managed-cloud identity.
- Qualified review for legal, regulatory, tax, licensing, and investment-advice conclusions
- Treat applied-project datasets, notebooks, code, environments, and results as inert untrusted artifacts; the platform provides no kernel, subprocess, network, secret, or provider execution boundary
- Financial experiment export/import follows ADR-0016; a provider-neutral future
  execution seam remains optional and does not authorize a sandbox, provider
  job, network, secret, or active preview.
- ADR-0018 admits only exact allowlisted reviewed packaged adapters. Jobs contain
  no secrets, enforce current lease/fencing, and assume duplicate delivery and
  uncertain external outcomes through idempotency or reconciliation.
- ADR-0019 keeps instructor overrides as visible time-bounded append-only
  projection overlays with two-person activation; DEC-0016 remains required for
  tenant, membership, role, and permission isolation.
- Keep mutable Project workspaces, immutable snapshots, Assessment submissions, and linked domain-resource authorization distinct; a Project link never grants persistence, provider, or privileged-operation access

## Canonical Sources

- `docs/security/README.md`
- `docs/security/local-identity-architecture.md`
- `docs/adr/ADR-0006-setup-selectable-learner-identity.md`
- `docs/adr/ADR-0007-platform-owned-versioned-lesson-package.md`
- `docs/adr/ADR-0008-community-learner-evidence-protection-and-recovery.md`
- `docs/adr/ADR-0011-inert-applied-project-artifacts.md`
- `docs/adr/ADR-0012-reusable-project-workspace.md`
- `docs/adr/ADR-0016-learner-managed-experiment-execution.md`
- `docs/adr/ADR-0017-platform-native-human-reviewed-content-authoring.md`
- `docs/adr/ADR-0018-allowlisted-adapters-postgresql-at-least-once-jobs.md`
- `docs/architecture/deployment/provider-admission-and-job-delivery.md`
- `docs/architecture/contracts/job-delivery-contract.md`
- `docs/adr/ADR-0019-append-only-bounded-projection-overrides.md`
- `docs/architecture/learning/instructor-review-and-projection-override.md`
- `docs/architecture/contracts/content-authoring-workflow-contract.md`
- `docs/architecture/contracts/content-package-contract.md`
- `docs/security/community-learner-evidence-protection.md`
- `docs/risk-compliance/README.md`
- `docs/external-sources/README.md`
- `docs/standards/security-and-privacy-standards.md`

## Stop When

A trust, authority, license, privacy, financial-claims, external-execution, or managed-cloud protection/recovery decision is missing.
