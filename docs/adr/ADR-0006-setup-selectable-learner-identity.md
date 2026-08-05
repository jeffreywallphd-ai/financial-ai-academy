# ADR-0006: Setup-Selectable Learner Identity

- Status: accepted
- Date: 2026-08-04
- Decision request: [DEC-0002](../planning/decision-requests/DEC-0002-local-learner-identity.md)

## Context

Local community installations must work without a commercial identity service, while operators may need explicit local login or an external OpenID Connect provider. Managed cloud uses managed identity, but every deployment must establish the same platform-owned actor and learner meaning before learning evidence is read or written.

A single hard-coded mode would either weaken the local default, impose unnecessary credentials, or require external infrastructure. Supporting several modes without one contract would leak provider payloads into application behavior and make evidence ownership ambiguous.

## Decision

Support three identity adapters selected explicitly during setup:

- `single_profile` establishes one durable local actor and learner without application credentials.
- `built_in` authenticates one primary local learner with a password and offline recovery.
- `oidc` authenticates one setup-authorized external subject through OpenID Connect.

Exactly one provider mode is active for an installation. Interactive setup asks for it; unattended setup supplies it explicitly. CAP-0001 supports one primary learner binding in every mode. Public registration, multiple local accounts, organization membership, MFA administration, and enterprise federation management remain outside this boundary.

Every adapter resolves to one provider-neutral application context containing opaque platform actor, learner, and session identifiers; authentication and expiry times; a normalized method; and application-issued permissions. Identity privately owns provider-subject bindings. Learning modules never receive passwords, hashes, recovery secrets, OIDC tokens, raw claims, or provider SDK objects and never trust client-selected actor or learner identifiers.

Use opaque server-side sessions referenced by protected cookies. Sessions rotate after authentication and recovery, expire server-side, and are revoked on logout, reset, recovery, deletion, or a security action.

Built-in passwords use versioned Argon2id hashes with unique salts and upgradeable parameters. Recovery uses hashed single-use codes plus an explicitly confirmed local operator CLI reset. Online failures are throttled and do not reveal account existence.

OIDC uses Authorization Code flow with PKCE S256, TLS, exact redirect matching, one-time state and nonce, and validation of issuer, signature, audience, authorized party where applicable, time claims, and subject before a platform session is issued.

The selected mode and installation identity are persisted. Once a binding or learner evidence exists, a configured mode mismatch fails closed. Any identity-mode change requires a separately approved mapping migration with backup, verification, and rollback.

Single-profile mode is supported only for documented private-host operation, with loopback binding by default. Anyone who can reach an unsafely exposed installation may act as the learner; shared-machine or remote exposure requires built-in, OIDC, or another separately accepted protection boundary.

## Consequences

- Community installations retain an offline-capable identity path without preventing credentialed or federated setups.
- Local and cloud deployments share learner-context and application-authorization semantics while using different adapters.
- Identity adapters require reusable setup, session, denial, recovery, diagnostics, and conformance tests.
- The identity attack surface and support matrix are larger than a single-mode system.
- OIDC mode depends on provider availability; password mode is not phishing-resistant; single-profile mode trusts the local host boundary.
- Exact session lifetimes, Argon2id cost calibration, throttling thresholds, metadata caching, and user experience remain implementation parameters that must satisfy the accepted boundary.

## Boundaries

This decision does not authorize multiple simultaneous providers, open registration, multi-user local administration, organization tenancy, MFA, identity-mode migration, or provider-specific cloud identity selection. It does not define learner-data deletion or retention policy and does not authorize implementation.

## Alternatives Rejected

- **Only single profile.** Rejected because some local installations require explicit authentication.
- **Only built-in credentials.** Rejected because it imposes password and recovery operations on simple private-host use.
- **Only external OIDC.** Rejected because core community learning must not require networked identity infrastructure.
- **Multiple simultaneous providers.** Rejected for the initial boundary because account linking and collision policy would broaden identity and recovery semantics.
- **Stateless browser sessions.** Rejected because revocation and recovery behavior are clearer with server-owned sessions.
- **In-place mode switching.** Rejected until a separately reviewed identity-mapping migration exists.

## Verification Implications

- Prove exactly-one-mode setup validation and reject mode mismatch after bindings or evidence exist.
- Run the same learner-context and application-authorization conformance scenarios for all local modes and managed-cloud adapters.
- Test missing, tampered, expired, revoked, duplicate, and cross-learner context denial.
- Test password hashing, throttling, generic failures, session rotation/revocation, and single-use recovery.
- Test OIDC state, nonce, PKCE, issuer, audience, signature, subject, callback, time, key-rotation, and outage failures.
- Use sentinel secrets and identities to prove diagnostic and logging redaction.
- Keep coverage classified as a gap until executable checks exist.

## Standards Basis

- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0-18.html)
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## Supersession

None. A future change to provider cardinality, session ownership, identity mapping, or populated-installation mode migration requires a superseding ADR or a separately scoped migration decision.
