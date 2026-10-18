# Learner Assistance Preferences Contract

- Status: accepted for SLI-0076 contract core
- Canonical for: explicit learner-owned AI-help choice and separate local
  learning-reminder preference
- Executable family: `contracts/learning/learner-assistance-preferences/v1/`

## Ownership and Meaning

Learner model owns the learner's explicit `off` or `on_request` AI-help choice.
`on_request` means only that a later governed feature may offer an action that
the learner must deliberately start each time. It does not admit or select a
provider, grant a data-class permission, authorize egress, call a model, create
output, enable background work, or promise that AI help is available. Every
provider remains disabled by default under ADR-0013.

The platform browser adapter separately owns the local learning-reminder choice.
`off` is the default. `in_app_when_available` records future intent in this
browser only. It does not prompt for operating-system permission, create a
service worker, timer, schedule, queue, subscription, external destination, or
delivery claim. It has no learner identity, server authority, or headless
meaning.

Neither choice is inferred from activity. Neither is Assessment evidence,
competency or mastery, Curriculum prerequisite, Adaptation eligibility,
authorization, provider consent, experiment consent, recommendation, financial
suitability, or an irreversible instruction.

## Learner-Owned Versioned Record

`learner-assistance-preference-profile-v1` is a closed learner-bound record with
one server-owned profile identity, positive revision, `assistance_mode`,
canonical UTC times, and a canonical SHA-256 digest. An absent stored profile
may later project revision-one `off` without a read-side write.

A mutation intent contains one idempotency key, exact expected revision, and a
complete replacement or `reset_profile`. Reset returns to `off`. Callers cannot
select a learner or supply provider, model, credential, prompt, content, tool,
destination, data permission, evidence, policy, identity, time, revision
outcome, or digest fields.

History contains at most 100 ordered non-content summaries with the resulting
revision, operation, time, and digest. Export binds the exact current profile
and bounded history to explicit purpose and limitations. It is not provider
consent, execution authority, proof of availability, or evidence that AI help
was used.

The canonical digest is SHA-256 over compact sorted-key JSON encoded directly
as UTF-8 with `profile_digest` omitted. Unicode is not normalized implicitly.
The pure domain and JSON Schema adapter issue no learner identity or time,
persist nothing, and have no database, network, filesystem, provider, model,
browser, notification, or cross-module effect.

## Browser-Local Reminder Envelope

`local-learning-reminder-preference-v1` is one complete local envelope with a
positive revision, `off` or `in_app_when_available`, canonical update time,
newest 100 non-content summaries, and an integrity code over compact sorted-key
UTF-8 JSON. It contains no learner ID or server session. One allowlisted storage
key contains the entire envelope.

An absent value projects revision-one `off` without writing. Unknown versions,
fields, values, malformed times/history, integrity mismatch, invalid JSON, and
inaccessible storage fall back to an in-memory `off` projection without
overwriting the stored bytes during read. Replacement and reset each write one
complete validated envelope. Export is visibly browser-specific and contains
no learner identity or claim that a reminder was scheduled or sent.

This local contract is intentionally not part of the learner-owned API,
profile, history, digest, or portable export. A future notification delivery
capability must define and govern its own permission, scheduling, destination,
retry, revocation, and delivery contracts rather than reinterpret this setting
as execution authority.

## Persistence and Public API

`learner_model_0006_assistance_preferences` stores the current learner-owned
profile, accepted request replays, and newest 100 non-content change summaries
inside the Learner-model schema. An absent row projects deterministic revision
one `off` without a read-side write. A per-learner advisory lock and one
transaction keep profile, summary, and replay atomic; exact retry returns the
accepted profile, while changed-key reuse, stale revision, and interrupted
writes change nothing. Retained data blocks the development down migration.

The protected profile, mutation, history, and export operations use the opaque
server session as the only learner selector. Reads require
`learner_assistance_preferences.read`; mutation requires
`learner_assistance_preferences.write`. The reviewed OpenAPI and generated
TypeScript client serve browser, command-line, service, and future headless
clients without a second authority path. Public requests cannot carry learner,
provider, model, credential, data permission, prompt, content, tool, output,
evidence, policy, local reminder, or generated server facts.

The public boundary records a choice only. No accepted request admits a
provider, grants egress, calls a model, creates output, schedules work, prompts
for notification permission, or sends a reminder. Those effects require later
governed capabilities and cannot be inferred from `on_request`.

## Failure and Compatibility

Unknown versions, operations, fields, values, invalid identity/time/digest,
stale or unchanged learner mutation, history/export mismatch, and provider,
model, permission, execution, evidence, or delivery fields fail closed with
bounded codes. Compatible technical metadata cannot be added inside either
closed v1 document; meaning-changing additions require a later governed version
or a differently owned contract.

A consumer must use a public Learner-model operation for the portable choice
and the platform adapter for the local choice. It may not query Learner-model
storage, inspect unrelated browser storage, treat either value as permission or
evidence, or make an unavailable downstream feature block viewing, changing,
resetting, or exporting an otherwise valid choice.
