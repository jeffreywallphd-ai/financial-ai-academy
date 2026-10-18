# Feature Guidance v1

This additive contract carries reviewed, read-only explanations for an exact
public feature condition. A record describes learner-safe status, reason,
protected or uncertain outcome, closed presentation actions, exact Help topic
references, applicability, publication, and canonical source facts. A mapping
correlates one exact `(surface_key, condition_key, mapping_version)` to one
exact record version.

The contract contains no route, URL, HTTP status, exception, learner identity,
request body, provider payload, command, credential, mutable feature state, or
promise of recovery. Only `open_help_topic` has a destination, and that
destination is one exact Help topic identity admitted in the same Guidance
composition. Other action kinds express presentation intent; the owning
feature decides whether its own action is currently available and safe.

Canonical digests use UTF-8 JSON with sorted keys, compact separators, and no
implicit Unicode rewriting. Each digest excludes only its own field. Published
meaning changes require a new exact version. Readers never select `latest` or
substitute another condition.
