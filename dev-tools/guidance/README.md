# Guidance Quality Gate

Run the fast contributor gate after changing Platform Help, contextual Help,
feature guidance, a bound canonical source, or shared Help rendering:

```text
python dev-tools/guidance/check_guidance_quality.py
```

The command compares current canonical source bytes with the safe fingerprints
used by the runtime, loads all three checked-in registries through production
adapters, resolves every exact record, and traverses deterministic browse and
filter results through contract cursors. It starts no host, browser, database,
network client, or model provider.

`source_authority.json` is repository-only build metadata. Its safe keys must
exactly match the runtime source manifest, and each value must be a unique
repository-relative Markdown file inside this checkout. Paths never enter
runtime Guidance values or public responses.

When a canonical source changes, review whether learner-facing meaning changed.
Update the relevant versioned Guidance resource and its canonical digest, then
update the runtime fingerprint. Do not change a fingerprint merely to silence
the gate. Published meaning receives a new exact version.

The gate intentionally accepts valid corpus growth, changed safe prose, and
different file order. It protects current source binding, exact internal links,
closed records, complete traversal, and deterministic results; it does not
freeze starter counts, whole wording, or layout. External URLs, remote crawling,
semantic search, AI grading, and hosted support remain outside this command.

Run focused behavior tests with:

```text
python dev-tools/guidance/test_guidance_quality.py
```
