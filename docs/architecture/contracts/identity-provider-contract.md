# Identity Provider and Learner-Context Contract

- Status: accepted
- Canonical for: identity-provider capabilities and provider-neutral learner context
- Related ADR: [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md)

## Purpose

Identity adapters establish authenticated platform identity without exposing provider payloads to application or domain behavior. Local single-profile, built-in, OIDC, and managed-cloud adapters produce the same learner-context semantics.

## Learner Context

The shared application context carries:

| Semantic value | Invariant |
| --- | --- |
| `actor_id` | Stable opaque platform actor identifier issued by Identity, never accepted from a client |
| `learner_id` | Stable opaque learner identifier used for evidence ownership, independent of username, email, or provider subject |
| `session_id` | Opaque server-owned session reference used for revocation and audit correlation |
| `authenticated_at` | Time Identity accepted the authentication or bounded local bootstrap |
| `expires_at` | Absolute server-enforced context expiry |
| `authentication_method` | Normalized local-bootstrap, password, or OIDC method for evidence and policy |
| `permissions` | Application-issued capabilities for the operation; provider claims are not direct authorization |

Identity privately maps a normalized provider instance and provider subject to platform actor and learner identifiers. That binding is unique, status-bearing, and provenance-aware. Password material, recovery secrets, sessions, OIDC tokens, and raw claims never enter learner context.

Trusted host middleware resolves context for each request. Missing, malformed, expired, revoked, or client-selected context fails closed. Owning modules still enforce operation-level authorization against the normalized context.

## Setup Contract

Exactly one identity mode is configured per installation:

- `single_profile`
- `built_in`
- `oidc`

Interactive setup requires an explicit selection. Unattended setup supplies it explicitly. Configuration identifies required public values and secret references; secrets remain outside portable configuration. The selected mode and installation identity are persisted.

Provider capability metadata declares mode, contract version, offline/network needs, interactive behavior, configuration schema, required secrets, callback or egress needs, readiness behavior, and limitations.

## Provider Port

| Capability | Required semantics |
| --- | --- |
| `validate_setup` | Validate one mode, configuration, secret references, callback constraints, and safe deployment assumptions without authenticating, installing, or repairing |
| `begin_authentication` | Start the selected interactive flow or bounded local-bootstrap transaction |
| `complete_authentication` | Validate proof, resolve one private provider binding, and return normalized platform identity |
| `resolve_session` | Resolve an opaque session to current context or fail closed |
| `revoke_session` | Revoke one session or every session for a binding after logout, reset, recovery, deletion, or security action |
| `health` | Report readiness and redacted configuration failures without identity or secret material |

Hosts select the adapter from validated setup. Application and domain code never select adapters or receive provider SDK objects.

## Session Contract

Sessions are opaque, high-entropy, server-side records referenced by protected cookies. They rotate after authentication and recovery, enforce idle and absolute expiry, and support revocation. Authentication tokens and session identifiers are not stored in browser local or session storage.

State-changing requests require same-origin and anti-CSRF protection. OIDC transactions additionally bind one-time state, nonce, and PKCE values to the initiating user agent.

## Mode-Specific Requirements

- **Single profile:** one durable local binding, private-host and loopback-default boundary, explicit limitation acknowledgement, and no claim of shared-machine protection.
- **Built-in:** one setup-created primary account for CAP-0001, no open registration, versioned Argon2id password verifier, throttled generic failures, one-time recovery codes, and local CLI recovery.
- **OIDC:** one configured provider and one setup-authorized primary subject for CAP-0001; Authorization Code with PKCE S256; exact callback and complete issuer, signature, audience, authorized-party, time, state, nonce, and subject validation.
- **Managed cloud:** an adapter may use managed identity but must produce this same context and remain subject to application authorization.

## Lifecycle and Migration

Restart preserves installation, mode, platform identities, and bindings independently of session expiry. Portable exports omit all authentication secrets. Imports cannot overwrite or silently merge bindings.

After a binding or learner evidence exists, a configured mode mismatch fails startup safely. Identity-mode migration is not part of this contract; it requires a separate approved mapping, backup, verification, rollback, and conflict policy.

## Compatibility and Conformance

The contract family is versioned. Additive capabilities may evolve compatibly, but changes to identifier meaning, evidence ownership, provider cardinality, session ownership, authorization meaning, or mode migration are breaking.

Every adapter must pass reusable scenarios for setup, missing capability, authentication success, malformed or tampered proof, expired/revoked context, duplicate binding, cross-learner denial, provider outage, recovery, secret redaction, and local/cloud semantic parity.
