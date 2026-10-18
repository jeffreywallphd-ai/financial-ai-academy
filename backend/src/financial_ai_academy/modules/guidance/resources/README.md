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
