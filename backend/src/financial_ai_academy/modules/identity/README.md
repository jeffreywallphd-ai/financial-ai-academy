# Identity Module: Single Profile

WRK-0003 implements only the explicitly configured `single_profile` adapter.
Identity owns stable opaque installation, binding, actor, learner, and session
identifiers. Browser cookies contain one random opaque token; PostgreSQL stores
only its SHA-256 digest.

The public `LearnerContext` contains normalized platform identifiers,
authentication/expiry times, `single_profile` as the method, and
application-issued permissions. Learning modules never receive the cookie,
token digest, provider subject, or client-selected identity headers.

The current single-profile context issues separate
`adaptation.navigation.read`, `curriculum.discovery.read`,
`curriculum.graph.read`, and `curriculum.lesson.read` permissions. Hosts
enforce the permission for each protected operation. Both discovery operations
use `curriculum.discovery.read`; the exact-version graph GET uses
`curriculum.graph.read`; and the exact-version navigation-state GET uses
`adaptation.navigation.read`. No permission, actor, learner, policy, provider,
or fallback-version selector is accepted from the client, and an opaque query
cursor grants no authority.

Built-in credentials, OIDC, multiple learners, identity-mode migration, and
remote single-profile exposure are not implemented by this module.
