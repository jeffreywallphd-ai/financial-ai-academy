# Local Learner Identity Security Architecture

- Status: accepted
- Canonical for: local learner identity trust boundaries and minimum controls
- Related ADR: [ADR-0006](../adr/ADR-0006-setup-selectable-learner-identity.md)
- Contract: [Identity Provider and Learner-Context Contract](../architecture/contracts/identity-provider-contract.md)

## Protected Assets

- learner and evidence ownership;
- platform identity bindings;
- password and recovery verifiers;
- sessions and OIDC transactions;
- provider tokens and client secrets;
- setup configuration and installation identity; and
- authentication, denial, and recovery audit evidence.

## Trust Boundaries

- browser to API session and authorization context;
- setup CLI or launcher to persisted installation configuration;
- Identity module to PostgreSQL identity, binding, and session records;
- application to an external OIDC provider;
- host secret resolver to identity adapters;
- portable export or data-root copy to a destination installation; and
- normalized learner context to learning modules.

## Minimum Controls

### All Modes

- Exactly one identity mode is active and persisted with the installation identity.
- Actor and learner identifiers are server-issued opaque values; client-selected identifiers are ignored.
- Missing, expired, revoked, malformed, duplicate, or cross-learner context fails closed.
- Sessions are opaque server-side records referenced by protected cookies, rotate after authentication or recovery, expire, and support revocation.
- State-changing requests receive same-origin and anti-CSRF protection.
- Secrets remain outside portable configuration; diagnostics and logs redact identities, credentials, sessions, codes, tokens, hashes, and recovery material.
- Once bindings or evidence exist, an identity-mode mismatch fails safely and requires a separately approved migration.

### Single Profile

- Bind the local service to loopback by default.
- Require explicit acknowledgement that host access acts as the learner.
- Describe shared-machine and remotely exposed operation as unsupported without another accepted protection boundary.
- Generate stable installation, actor, learner, and binding identifiers on first setup.

### Built-In Credentials

- Create the primary account through a one-time setup transaction; do not enable open registration.
- Store versioned Argon2id password hashes with unique salts and upgradeable parameters.
- Accept long passphrases, screen common or compromised values, avoid arbitrary composition and periodic-change rules, return generic failures, and throttle online attempts.
- Hash one-time recovery codes, display them once, and revoke sessions after recovery.
- Require local host authority and explicit confirmation for CLI reset; never log replacement secrets.

### OIDC

- Use Authorization Code flow with PKCE S256 over TLS.
- Match redirects exactly and expose no open redirector.
- Bind one-time state, nonce, and PKCE values to the initiating transaction.
- Validate issuer, signature algorithm and key, audience, authorized party when applicable, expiry, not-before, nonce, and subject before creating a platform session.
- Admit only the setup-authorized primary subject for CAP-0001; do not enable open just-in-time admission.
- Treat provider outage, stale metadata, and key rotation as explicit unavailable or bounded retry states; never bypass validation.

## Threats and Required Outcomes

| Threat | Required outcome |
| --- | --- |
| Exposed single-profile service | Local-origin checks and documented limitation; no claim of remote authentication |
| Copied or readable data root | Host protection, stable installation identity, no silent merge, and secrets excluded from portable export |
| Missing or client-selected context | Denial without learning-evidence mutation |
| Duplicate or cross-profile binding | Transactional uniqueness failure and no ambiguous learner ownership |
| Session fixation, theft, replay, or stale privilege | Rotation, expiry, revocation, cookie protection, CSRF defense, and safe denial evidence |
| Password guessing or database disclosure | Throttling, generic responses, versioned memory-hard hashing, rehash path, and no verifier disclosure |
| Recovery takeover | Single-use hashed codes or host-authorized CLI reset followed by session revocation |
| OIDC redirect, mix-up, injection, or replay | Exact redirect, PKCE, state, nonce, issuer/audience/signature/time validation, and fail-closed handling |
| Provider outage or key rotation | Bounded unavailable/retry behavior with no authentication bypass |
| Secret or identity leakage | Structured allowlisted diagnostics and sentinel redaction tests |
| Mode change after evidence | Startup rejection and separately governed migration |

## Residual Risk

Local host administrators remain trusted in the community profile. Single-profile mode does not protect against another person who can reach the service. Passwords are not phishing-resistant. OIDC inherits provider availability and provider-account compromise risk.

Multiple users, MFA, organization tenancy, identity linking, and mode migration require additional decisions and threat models.

## Verification

The approved-lesson seam directly covers configured `single_profile` setup,
stable opaque binding, hashed session-token storage, idle/absolute expiry,
revocation, missing/tampered context denial, client-selected identity denial,
exact Host/Origin enforcement, generic redacted failures, HttpOnly
`SameSite=Strict` cookie issuance, loopback-only same-origin static/API
composition, and a live Chromium read path against PostgreSQL 18.4.

Built-in credentials, password hashing/throttling, recovery, OIDC transaction
and token validation, provider outage/key rotation, multiple learners,
identity-mode migration, export/import identity behavior, managed-cloud
adapters, and cross-provider conformance remain gaps. Direct `single_profile`
evidence must not be generalized to those modes.

## Standards Basis

- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0-18.html)
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
