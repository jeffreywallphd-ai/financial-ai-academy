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
`curriculum.discovery.read` and `curriculum.lesson.read` permissions. Hosts
enforce the permission for each protected operation. Both queryless discovery
browse and bounded discovery query use `curriculum.discovery.read`; neither
permission nor any actor or learner selector is accepted from the client, and
an opaque query cursor grants no authority.

Built-in credentials, OIDC, multiple learners, identity-mode migration, and
remote single-profile exposure are not implemented by this module.
