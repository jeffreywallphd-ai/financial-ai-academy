# Guidance Resources

`platform-help/v1/` is the checked-in immutable starter corpus admitted at
application composition time. Every JSON file must satisfy the executable v1
topic schema and Guidance validation rules as one atomic corpus.

The versioned manifest in the immutable-corpus adapter identifies the required
starter topic identities and binds safe source keys to the reviewed source
fingerprints. Admission fails when a required starter topic is absent or a
source binding is stale. Additional valid topics remain supported when they use
a manifest-bound source and satisfy the same corpus rules.

Contributors must derive plain-language explanations from current canonical
sources, update the safe source fingerprint, create a new exact topic version
when published meaning changes, and run the contract, corpus, API, and generated
client checks. The corpus test binds manifest fingerprints to current canonical
sources; runtime code never parses or serves the source Markdown. The
resource contains no repository path, approval/reviewer data, learner data,
prompt, credential, arbitrary URL, active content, or provider payload.

Run `python dev-tools/guidance/check_guidance_quality.py` from the repository
root for one fast source, registry-link, exact-read, and deterministic-search
result. Repository-only source locations live in
`dev-tools/guidance/source_authority.json`; do not add local paths to these
runtime resources. A valid additional record may change corpus size, wording,
references, or file order without weakening exact identity and provenance.

`contextual-help/v1/` is the checked-in immutable exact-context registry. Each
record maps a delivered feature context to ordered exact topics already
admitted from `platform-help/v1/`. The complete registry fails closed for a
missing context, stale source binding, invalid digest, or dangling topic.

Context resources are reviewed product data rather than feature state or
canonical source content. Add a new exact context version instead of rewriting
published meaning. Do not add routes, external URLs, private paths, learner
selectors, provider/model payloads, commands, or mutable feature data.

`feature-guidance/v1/` contains exact reviewed limitation/recovery records and
exact surface-condition mappings. The complete registry is admitted only after
the Help corpus, and every record reference must resolve to an admitted exact
topic. Closed actions express presentation intent only. They do not authorize
or perform a feature retry, reload, download, provider/model call, artifact
execution, or other state change. Feature modules retain all runtime state,
availability, authorization, retry, and execution authority.

Published meaning changes require a new record or mapping version. Do not add
routes, URLs, HTTP statuses, exception text, request bodies, private state,
commands, credentials, guarantees, or learner identifiers. Safe recovery text
must preserve uncertainty rather than claim whether an unconfirmed write was
accepted.
