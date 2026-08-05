---
id: DEC-0002
kind: decision-request
planning_status: complete
authority: noncanonical
owner: unassigned
updated: 2026-08-04
parent: null
depends_on: []
decision_gates: []
decision_record: ../../adr/ADR-0006-setup-selectable-learner-identity.md
---

# Decision Request: Establish Local Learner Identity

## Decision Needed

Define a setup-selectable identity strategy that supports a stable single-profile mode, built-in credential authentication, and an external OIDC provider behind one shared learner-context contract.

## Why Now

Assessment attempts and retained completion evidence must belong to an unambiguous learner context. Candidate B cannot define authorization, duplicate-submission behavior, evidence ownership, or resumption until the local identity flow is decided. Selecting a convenient placeholder in implementation could create incompatible local and cloud contracts or unsafe shared-machine behavior.

## Current Authority and Constraints

- The [local open-source profile](../../architecture/deployment/local-open-source-profile.md) cannot require a commercial service for core learning and must support a reproducible local installation.
- The [managed-cloud profile](../../architecture/deployment/managed-cloud-profile.md) uses managed identity integration and application authorization.
- [ADR-0004](../../adr/ADR-0004-shared-core-local-cloud.md) requires both profiles to share domain rules, application operations, contract versions, and migrations while allowing different identity adapters.
- [ADR-0002](../../adr/ADR-0002-contract-driven-provider-architecture.md) requires identity providers to remain behind platform-owned contracts.
- [Security and privacy standards](../../standards/security-and-privacy-standards.md) require least privilege, explicit actors and authority, denial evidence, scoped learner context, and an accepted decision for new identity flows.
- CAP-0001 is limited to an individual learner; organization membership, tenancy, enterprise identity, and multi-user local administration are out of scope.

## Decision Classification

| Decision | Readiness | Viable options | Recommendation | Blocking DEC |
| --- | --- | --- | --- | --- |
| Setup identity strategy | ready | D. Setup-selectable single-profile, built-in, or OIDC mode | Use Option D accepted by ADR-0006 | none |
| Active provider cardinality | ready | D1. Exactly one active provider selected at setup | Use D1 accepted by ADR-0006 | none |
| Provider change after evidence exists | constrained | M1. Freeze the selected mode and require a later migration decision | Use M1; migration remains decision-required | none |
| Browser session model | ready | S1. Opaque server-side session referenced by a protected cookie | Use S1 accepted by ADR-0006 | none |
| Built-in password verifier | ready | P1. Versioned Argon2id password hashes | Use P1 accepted by ADR-0006 | none |
| Built-in recovery | ready | R1. One-time recovery codes plus a local operator CLI reset | Use R1 accepted by ADR-0006 | none |
| OIDC protocol profile | constrained | Authorization Code flow with PKCE S256, exact redirect matching, TLS, state, nonce, and issuer/audience/signature validation | Use the standards-constrained path | none |
| Learner-context semantics | ready | Stable opaque platform learner ID plus a private provider-subject mapping; no provider payload in domain/application consumers | Use the ADR-0006 provider-neutral contract | none |
| Authorization authority | ready | Application authorization receives validated actor/learner context and remains authoritative | Preserve application-owned authorization | none |

Canonical authority for the nonblocking rows:

- ADR-0002 requires provider-neutral platform contracts, and ADR-0004 requires local and cloud adapters to preserve the same application semantics.
- The managed-cloud profile makes application authorization authoritative; the security standards require explicit scoped context and denial evidence.
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0-18.html) defines issuer, subject, audience, signature, state, and nonce validation.
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) requires exact redirect handling, CSRF defenses, and modern authorization-code protections including PKCE.

## Options

| Option | Benefits | Costs and risks | Contracts and operations affected | Reversibility |
| --- | --- | --- | --- | --- |
| A. Single local profile with a stable opaque learner ID | Keeps the community baseline offline-capable and simple. A local identity adapter establishes one durable learner context without storing application passwords; the host and operating-system boundary protect access. Cloud adapters provide the same application-level learner-context semantics. | Anyone with access to the running local installation may act as that learner. Shared-machine and exposed-network use must be explicitly unsupported or separately protected. Profile reset, import, and cloning need defined identity behavior. | Identity-provider port, learner-context contract, local session bootstrap, evidence ownership, export/import identity mapping, API denial when context is absent. | High. A later credentialed local provider can implement the same identity contract if opaque identifiers and evidence ownership remain stable. |
| B. Built-in local username and password | Supports multiple local users and explicit authentication without an external provider. | Adds credential hashing, recovery, session security, rate limiting, migration, and administrative responsibilities before they are needed by CAP-0001. | Credential store, authentication API/UI, session/token lifecycle, recovery operations, security monitoring. | Medium. Credential semantics become durable and must migrate if replaced. |
| C. Require an external OIDC identity provider | Aligns local and cloud authentication protocols and delegates credential security. | Adds setup complexity, possible network or additional-service dependency, provider configuration, callback security, and a poor default for a simple local installation. | OIDC adapter, redirect/session contracts, secrets, deployment configuration, provider qualification. | Medium to high if the shared learner-context contract remains provider-neutral. |
| D. Support A, B, and C as setup-selectable provider modes | Gives local operators an offline single-profile default, an application-managed login option, or external identity integration while preserving one learner-context contract. | Expands the identity attack surface, setup validation, documentation, testing matrix, migrations, recovery behavior, and support burden. Each mode requires its own security qualification and denial tests. | Provider capability contract, setup schema and UI, active-provider configuration, credential/session contracts, OIDC configuration, evidence identity mapping, export/import, diagnostics, and provider-change migration. | Medium. Adding modes is straightforward behind the port; changing a populated installation's mode requires an explicit identity-mapping migration. |

## Recommendation

**Selected direction: Option D, supporting Options A, B, and C as provider modes chosen during setup.**

- **Verified:** local and cloud may use different identity infrastructure but must share application semantics; identity providers belong behind platform-owned contracts; core local learning cannot require a commercial service.
- **User direction:** setup must allow single-profile, built-in credential, or OIDC provider selection.
- **Assumption to validate:** one provider mode is active for an installation at a time, and changing modes after learner evidence exists requires a separately reviewed migration rather than an unguarded settings toggle.
- **Inference:** a common identity-provider capability contract can preserve evidence ownership while allowing the three modes, but each adapter needs independent security and conformance evidence.

## Canonical Direction

[ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md) records **Option D** together with D1, M1, S1, P1, R1, and the private-host limitation as the canonical direction.

## Evidence Package

### Bounded Identity Model

Option D is bounded as follows:

- Setup requires an explicit choice of `single_profile`, `built_in`, or `oidc`; exactly one mode is active for an installation.
- CAP-0001 admits one primary learner binding in every mode. Public registration, account administration, organization membership, and multi-user authorization remain future capabilities.
- Every mode resolves to the same platform-owned learner context. Learning modules never branch on provider type and never receive password material, OIDC tokens, raw claims, or provider SDK objects.
- The selected mode is stored with the installation identity. Once learner evidence exists, a mismatched configured mode fails closed; changing it requires a separately approved identity-mapping migration.
- The local setup default is not silent. Interactive setup asks for a mode; unattended setup must supply one explicitly.

### Provider-Neutral Learner-Context Contract

The exact wire shape remains deferred, but the shared application context must carry these semantics:

| Semantic field | Purpose and invariant |
| --- | --- |
| `actor_id` | Stable opaque platform identifier for the authenticated actor; never supplied or overridden by a client request |
| `learner_id` | Stable opaque platform learner identifier used to own attempts and evidence; independent of username, email, or OIDC subject |
| `session_id` | Opaque server-issued reference used for revocation and audit correlation; contains no business meaning |
| `authenticated_at` | Time of the successful authentication or local bootstrap event |
| `expires_at` | Absolute server-enforced session expiry |
| `authentication_method` | Normalized method such as local bootstrap, password, or OIDC; consumers may record it but cannot use provider claims as authorization |
| `permissions` | Application-issued capabilities for the current operation, initially limited to the primary learner's own learning and evidence operations |

Identity privately owns the binding from a provider instance and provider subject to `actor_id` and `learner_id`. The binding uses a uniqueness constraint, normalized provider identity, status, creation time, and provenance. Raw OIDC claims, access tokens, refresh tokens, password hashes, and recovery secrets are excluded from learner context.

Every authenticated API operation receives context from trusted host middleware. Missing, expired, revoked, malformed, or client-selected context fails closed and records safe denial evidence. Learning modules receive only the normalized context and remain responsible for their own operation-level authorization.

### Identity Provider Capability Contract

The provider port exposes common capabilities rather than a universal provider payload:

| Capability | Required behavior |
| --- | --- |
| `validate_setup` | Validate exactly one selected mode, required configuration, secret references, callback constraints, and safe deployment assumptions without authenticating or repairing |
| `begin_authentication` | Start the selected interactive flow or establish the bounded single-profile bootstrap transaction |
| `complete_authentication` | Validate proof, resolve one private provider binding, and return normalized platform identity |
| `resolve_session` | Resolve an opaque session to current actor, learner, expiry, and permissions or fail closed |
| `revoke_session` | Revoke one session or all sessions for a binding after logout, password reset, recovery, deletion, or security action |
| `health` | Report readiness and actionable redacted configuration failures without identities, secrets, tokens, or credentials |

Provider capability metadata declares the mode, offline/network needs, interactive behavior, configuration schema, secret names, and limitations. Hosts select adapters from validated setup; application and domain code never select them.

### Setup and Lifecycle Behavior

| Mode | First setup | Normal restart and login | Supported boundary |
| --- | --- | --- | --- |
| Single profile | Generate installation, actor, learner, and binding identifiers; require acknowledgement that host access acts as the learner | Resolve the durable binding and issue a fresh server session only when the supported local-origin checks pass | Offline and private-host use; loopback binding by default; shared-machine or remotely exposed use is unsupported without an additional protection boundary |
| Built-in | Create one primary account through a one-time setup transaction; reject open registration; issue offline recovery codes | Verify the password, throttle failures, rotate the session, and retain the same platform IDs | One primary learner for CAP-0001; additional account administration and MFA require later capabilities |
| OIDC | Validate issuer metadata, client configuration, exact callbacks, TLS, and secret references; bind the first successful setup-authorized subject to the primary learner | Use Authorization Code flow with PKCE S256 and validate state, nonce, issuer, audience, signature, time claims, and subject before issuing a platform session | One configured OIDC provider and one primary learner binding for CAP-0001; no open just-in-time admission of other subjects |

Lifecycle rules:

- **Restart:** installation identity, selected mode, platform learner ID, and provider binding remain stable; sessions may expire independently.
- **Portable export:** include stable platform learner and evidence references plus format/version metadata, but exclude password hashes, recovery secrets, sessions, OIDC tokens, and client secrets.
- **Import:** never overwrite an existing provider binding or silently merge learner IDs. Binding imported evidence to a new identity requires an explicit reviewed import or migration operation.
- **Deletion:** revoke sessions and disable or remove the provider binding. Evidence retention or deletion follows a separately accepted learner-data policy and cannot be inferred from identity deletion.
- **Data-root copy or clone:** treat the copy as the same installation identity and learner data until an explicit clone/import workflow assigns a new installation identity; never merge diverged evidence automatically.
- **Mode mismatch:** if persisted evidence or bindings exist and setup selects another mode, startup fails with a redacted migration-required diagnostic.

### Session, Password, Recovery, and OIDC Requirements

- Use an opaque, high-entropy, server-side session referenced by an `HttpOnly`, `Secure` cookie when HTTPS is used, with the narrowest practical `SameSite`, path, and lifetime settings. Do not store session IDs, OIDC tokens, or credentials in browser local or session storage.
- Rotate the session identifier after authentication and recovery; enforce idle and absolute expiry; revoke on logout, password reset, recovery, binding deletion, and provider-security failure.
- Apply CSRF protection to state-changing operations through same-origin checks and a server-bound anti-CSRF mechanism; OIDC transactions additionally use one-time state, nonce, and PKCE values.
- Built-in passwords use versioned Argon2id hashes with a unique salt and upgradeable cost parameters. Accept long passphrases, screen against common or compromised values, avoid arbitrary composition and periodic-change rules, use generic failure messages, and throttle online attempts.
- Recovery codes are high-entropy, single-use, hashed at rest, displayed once, and invalidate existing sessions when used. A local operator reset requires filesystem/host authority and an explicit CLI confirmation; it creates audit evidence without logging the new secret.
- OIDC uses Authorization Code flow with PKCE S256. Validate discovery and issuer configuration, exact redirect URIs, TLS, signature algorithm policy, signing keys, issuer, audience and authorized party where applicable, expiry and not-before, state, nonce, and subject. Reject implicit-flow tokens and unvalidated claims.
- Provider and session diagnostics disclose mode, capability, health, and redacted error categories only. They exclude usernames, emails, subjects, cookies, codes, tokens, secrets, hashes, and recovery material.

### Local Identity Threat Model

Protected assets include learner/evidence ownership, platform identity bindings, password and recovery verifiers, sessions, OIDC transactions and tokens, client secrets, setup configuration, and diagnostic records. Actors include the primary learner, local operator, another host user, an unauthenticated network client, a malicious website, a credential attacker, and a compromised or misconfigured identity provider.

| Threat or failure | Boundary and impact | Required controls | Residual boundary |
| --- | --- | --- | --- |
| Single-profile installation exposed beyond the private host | Browser to API; anyone reaching it may act as the learner | Loopback default, explicit setup acknowledgement, origin/host validation, fail-closed diagnostics, and no claim of shared-machine safety | Host compromise or deliberate unsafe exposure remains outside single-profile protection |
| Another user can read a copied data root | Host filesystem to application data; learner evidence and bindings may be disclosed or cloned | Host permissions, documented data root, secrets outside portable configuration, clone detection through installation identity, and backup guidance | Host administrators and compromised hosts remain trusted for the community profile |
| Missing or client-selected learner context | Browser to API; evidence could be written to or read from the wrong learner | Server-issued context only, ignore client identity fields, operation authorization, ownership checks, and denial evidence | None accepted; ambiguous context fails closed |
| Cross-profile or duplicate provider binding | Identity adapter to platform mapping; one external subject could map incorrectly | Unique provider-instance and subject binding, transactional creation, stable platform IDs, and explicit conflict errors | Binding repair requires an approved administrative or migration operation |
| Session fixation, theft, replay, or stale privilege | Browser session to API; attacker impersonates the learner | High-entropy opaque sessions, post-auth rotation, secure cookie attributes, expiry, revocation, CSRF controls, and no browser storage of credentials | Active browser or host compromise can still act within a valid session |
| Password guessing or credential stuffing | Built-in login; account takeover and denial of service | Long passphrases, compromised-value screening, generic errors, progressive throttling, safe monitoring, and recovery independent of login | Passwords are not phishing-resistant; MFA is outside CAP-0001 |
| Password database disclosure | Database boundary; offline guessing | Salted versioned Argon2id, cost calibration, rehash-on-login, least-privileged access, and no password logging | Weak learner-chosen passwords may still be cracked; recovery and notification policy remain operational work |
| Recovery takeover | Recovery code or CLI boundary; account and evidence takeover | Hashed one-time codes, host-authority check for CLI reset, explicit confirmation, session revocation, and audit evidence | Anyone with both host authority and data access is trusted in the local profile |
| OIDC redirect, mix-up, code injection, or token replay | Browser, application, and external provider | Exact redirects, no open redirector, state, nonce, PKCE S256, issuer binding, signature/audience/time validation, and one-time transaction storage | Compromised provider or stolen provider account remains an upstream risk |
| OIDC outage or signing-key rotation | Application to provider; login unavailable or valid keys appear stale | Bounded metadata/key cache, refresh and retry policy, last-known-key safeguards, redacted health, and no authentication bypass | OIDC mode may be unavailable offline; existing session policy must remain explicit |
| Secret or identity leakage through configuration and logs | Host configuration and diagnostics | Secret references outside portable config, structured redaction, allowlisted diagnostics, and tests using sentinel secrets | Local administrators can inspect runtime memory and secret stores |
| Mode changed after evidence exists | Setup configuration to persisted identity; evidence becomes orphaned or misattributed | Persist selected mode and installation identity, reject mismatch, require separately approved mapping migration with backup and rollback | Migration remains unavailable until separately planned and approved |

### Required Verification Scenarios

- Setup accepts each supported mode separately and rejects a missing, unknown, or multiply configured mode.
- Restart preserves installation, actor, learner, mode, and binding identifiers while expiring sessions according to policy.
- A populated installation rejects an identity-mode mismatch without changing bindings or evidence.
- Missing, expired, revoked, malformed, or client-selected context denies access and creates no evidence.
- A client-supplied learner ID is ignored; cross-learner reads and writes fail; duplicate provider bindings fail transactionally.
- Single-profile bootstrap works only within its documented local-origin boundary and communicates its shared-host limitation.
- Built-in login uses the approved hash envelope, returns generic failures, throttles repeated attempts, rotates sessions, and never emits credentials or verifiers.
- A recovery code succeeds once, revokes existing sessions, and is unusable afterward; CLI recovery requires host authority and redacts secrets.
- OIDC success validates the complete transaction. Wrong state, nonce, PKCE verifier, issuer, audience, authorized party, signature, callback, subject, or time claims fail.
- OIDC key rotation and temporary provider outage produce bounded retry or unavailable outcomes without accepting an unverified identity.
- Logout, password reset, recovery, binding deletion, and security revocation invalidate the expected sessions.
- Export excludes authentication secrets; import and cloned data roots cannot silently create or merge bindings.
- Diagnostics and logs remain useful with sentinel usernames, subjects, tokens, cookies, client secrets, password hashes, and recovery codes fully redacted.
- The same learner-context contract and application authorization scenarios pass for local single-profile, built-in, OIDC, and managed-cloud adapters.

### Standards Consulted

- [NIST SP 800-63B-4, Authenticators](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/) for password, recovery, throttling, and session guidance.
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0-18.html) for issuer, subject, audience, signature, state, nonce, and token validation.
- [OAuth 2.0 Security Best Current Practice, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) for exact redirects, CSRF protection, PKCE, mix-up defense, and token/code injection defenses.
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) for slow salted password hashing and Argon2id guidance.
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) for password handling, generic failures, and authentication controls.
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) for session entropy, cookie protection, fixation defense, expiry, and revocation.

### Security Review Conclusion

- **Verified:** the proposed contract keeps provider payloads and secrets out of learning modules and preserves one local/cloud application meaning.
- **Verified:** the three setup modes can share one learner-context and server-session boundary without making a commercial service mandatory.
- **Verified:** exactly-one-provider validation and a frozen populated-installation mode prevent ambiguous evidence ownership until a separate migration is approved.
- **Approved:** Option D with D1, M1, S1, P1, and R1 as the bounded sub-decisions in the classification table.
- **Residual risks:** host access acts as the learner in single-profile mode; passwords are not phishing-resistant; OIDC inherits provider/account compromise and network availability; local host administrators remain trusted.
- **Known gaps:** exact session lifetimes, hash cost calibration, rate limits, recovery UX, provider metadata cache duration, and executable schemas must be selected and tested in later approved work packets without weakening this boundary.
- **Scope limit:** this decision does not authorize multiple local users, open registration, organization tenancy, MFA, enterprise federation administration, or identity-mode migration.

The evidence supported canonical promotion of DEC-0002. The resulting ADR does not select a slice or authorize authentication implementation.

## Evidence Required

- **Prepared:** local identity threat model covering shared hosts, browser/API access, exposed ports, copied data roots, recovery, absent context, credentials, sessions, OIDC, and mode mismatch.
- **Prepared:** provider-neutral learner-context and private identity-binding contract sketches.
- **Prepared:** provider capability and setup contract with exactly-one-active-provider validation, explicit unattended configuration, mode capabilities, secret references, and redacted diagnostics.
- **Prepared:** first setup, restart, export/import, deletion, cloning, and populated-installation mode-mismatch behavior.
- **Prepared:** password hashing, recovery, throttling, session, CSRF, callback, issuer, audience, state, nonce, PKCE, secret handling, and OIDC validation requirements.
- **Prepared:** verification scenarios for success, denial, tampering, replay, duplication, outage, key rotation, recovery, redaction, and local/cloud parity.
- **Satisfied:** ADR-0006 records Option D, D1, M1, S1, P1, R1, and the documented private-host limitation as canonical authority.

## Required Authority

Product and architecture decision authority informed by security review of the local identity threat model. Approval evidence is retained only in the ignored local ledger.

## Decision Record and Promotion

The accepted boundary is recorded in [ADR-0006](../../adr/ADR-0006-setup-selectable-learner-identity.md), the [identity-provider contract](../../architecture/contracts/identity-provider-contract.md), the [local identity security architecture](../../security/local-identity-architecture.md), deployment profiles, and decision readiness.

## Dependent Planning Updates

- DEC-0002 has been removed from CAP-0001's unresolved decision gates.
- Refine Candidate B and Candidate C authorization, evidence ownership, and resumption scenarios.
- Keep organization tenancy and enterprise identity as separate future decisions.

## Planning History

- 2026-08-04: Decision request captured from CAP-0001's local identity gate.
- 2026-08-04: The provider-neutral context, setup contract, three mode lifecycles, threat model, security requirements, standards review, migration boundary, verification scenarios, and residual risks were prepared.
- 2026-08-04: ADR-0006 and affected identity, security, deployment, context, verification, capability, and register documents were synchronized; DEC-0002 moved to `complete`.
