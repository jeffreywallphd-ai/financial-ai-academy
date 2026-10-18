# Contextual Help v1

`contextual-help/v1` maps one exact, versioned feature context to an ordered
set of exact approved `platform-help/v1` topics. Guidance owns the safe mapping;
the feature and each referenced canonical source retain behavior and meaning.

Exact reads require both `context_key` and `context_version`. There is no
`latest` substitution and no search-derived or browser-owned mapping. A record
contains only a feature label, applicability, exact topic identities, closed
purposes, safe link labels, approved publication facts, canonical-source facts,
and a canonical digest.

Canonical JSON uses UTF-8, sorted object keys, and compact separators. The
digest excludes only `context_digest`; admitted Unicode text is preserved. The
contract contains no route, URL, component, repository path, learner identity,
permission, prompt, provider/model payload, mutable feature state, command, or
external action.
