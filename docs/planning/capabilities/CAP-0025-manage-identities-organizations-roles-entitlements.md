---
id: CAP-0025
kind: capability
planning_status: decision-blocked
authority: noncanonical
owner: unassigned
updated: 2026-10-15
parent: null
depends_on: ["CAP-0001", "CAP-0026"]
decision_gates: ["DEC-0016", "DEC-0019"]
approval_model: cap-package-v1
slice_ids: ["SLI-0102", "SLI-0103", "SLI-0104", "SLI-0105"]
---

# Capability: Manage Identities, Organizations, Roles, and Entitlements

## Outcome

An authorized administrator can manage identity bindings, organizations,
memberships, roles, permissions, and edition entitlements under explicit tenant
and commercial boundaries while all application operations receive the same
provider-neutral actor/learner authorization context.

## Users and Value

Learners, instructors, organization administrators, and operators need
predictable access and isolation across local and cloud profiles. Value is
observable when every permission and entitlement decision is deterministic,
auditable, revocable, and independent of a provider SDK or client assertion.

## Scope

### In Scope

- The organization/tenant, membership, role, database/object placement,
  lifecycle, isolation, and authorization model selected by DEC-0016.
- The edition entitlement expression permitted by DEC-0019 without embedding
  billing or license interpretation in domain rules.
- Provider-neutral actor/learner context, identity bindings, invitations or
  membership admission, role assignment, entitlement checks, revocation,
  session effects, and audit.
- Accessible administration and self-visible access explanations.

### Out of Scope

- Choosing an identity provider, billing system, legal licensing model, HR
  directory, consumer social identity, or policy-as-model output.
- Client-selected roles/tenant, cross-tenant administration, or contradictory
  local/cloud domain semantics.

## Canonical Context

- [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md)
- [Identity Provider Contract](../../architecture/contracts/identity-provider-contract.md)
- [Local Identity Security](../../security/local-identity-architecture.md)
- [Local and Cloud Capability Parity](../../architecture/deployment/local-cloud-capability-parity.md)
- [Community and Commercial Editions](../../product/community-and-commercial-editions.md)
- [Decision Readiness](../../adr/decision-readiness.md)

## Decision Gates and Constraints

- ADR-0006 fixes provider-neutral local learner context, but organization
  tenancy remains unresolved and is selected by DEC-0016.
- DEC-0019 determines the commercial/licensing boundary within which edition
  entitlements may be represented; it does not make authorization provider-owned.
- Authentication supplies verified context; application policy deterministically
  evaluates permissions and entitlements at every protected operation.

## Proposed Vertical Slices

| Slice ID | Observable increment | Dependencies and order constraints | Material-change boundary | Planning status |
| --- | --- | --- | --- | --- |
| SLI-0102 | The platform resolves the accepted organization/tenant and actor/learner context with explicit lifecycle and data-isolation semantics. | First after decisions and dependencies. | Client-selected tenant, cross-tenant shared state, or provider-owned authorization changes the CAP package. | captured |
| SLI-0103 | Authorized administrators manage memberships and roles with invitation/admission, change, suspension, removal, revocation, and audit behavior. | After SLI-0102. | HR automation, hidden roles, or retroactive history rewriting changes the CAP package. | captured |
| SLI-0104 | Protected operations evaluate versioned permissions and edition entitlements and explain allowed, denied, unavailable, and revoked outcomes. | After SLI-0103 and DEC-0019. | Billing, suitability, or client-authoritative entitlement changes the CAP package. | captured |
| SLI-0105 | Identity/organization administration is qualified for isolation, escalation, revocation, session effects, audit, recovery, accessibility, and local/cloud parity. | Last; depends on SLI-0102 through SLI-0104. | Selecting a provider, cloud platform, or billing product changes the CAP package. | captured |

## Capability Acceptance

- Tenant, actor, learner, membership, role, permission, and entitlement context
  is server-derived, versioned, deterministic, auditable, and revocable.
- Cross-tenant, stale-session, privilege-escalation, confused-deputy, missing,
  malformed, or conflicting cases fail closed without identity leakage.
- Local profiles continue to use the same application authorization contract and
  do not acquire fake organizations or contradictory domain behavior.
- Administration and access explanations meet security, accessibility, recovery,
  and audit requirements.

- Every slice includes focused failure and anti-rigidity tests; unavailable
  enterprise identity or commercial entitlement adapters do not weaken or block
  supported local identity behavior.

## Risks and Non-Goals

Identity and tenancy mistakes can expose all other domains. This CAP does not
choose a vendor, billing system, legal license, or allow roles and entitlements
to bypass application authorization.

## Documentation Impact

Delivery will add organization/tenant/role/entitlement vocabulary and contracts,
identity adapters, isolation and authorization policy, migrations, threat models,
session/recovery behavior, admin UI, operations, and verification evidence.

## Planning History

- 2026-10-15: Shaped from catalog candidate 22 with manifest SLI-0102 through
  SLI-0105. DEC-0016 and DEC-0019 block CAP approval and delivery.
