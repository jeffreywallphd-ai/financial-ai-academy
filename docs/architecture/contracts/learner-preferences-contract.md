# Learner Preferences Contract

- Status: accepted for SLI-0074 contract core
- Canonical for: explicit learner-entered goals, experience, and interests
- Executable family: `contracts/learning/learner-preferences/v1/`

## Ownership and Meaning

Learner model owns the learner's explicit learning goals, self-described
experience, and interests. These values record what a learner chose to say.
They are not Assessment evidence, a competency or mastery estimate, a
Curriculum prerequisite, Adaptation eligibility, a recommendation, permission,
experiment consent, financial suitability, or an irreversible instruction.

No value may be inferred from activity, assessment, engagement, browser,
provider, model, or third-party data under this contract. A future inferred or
model-derived profile would be a different governed boundary and cannot be
added as compatible learner-preference metadata.

## Versioned Record

`learner-preference-profile-v1` is a closed learner-bound record with one
server-owned profile identity, positive revision, ordered goals, ordered
experience entries, ordered interests, canonical UTC times, and a canonical
SHA-256 digest.

- Goals are learner intentions with bounded title, optional detail, and an
  active or archived state.
- Experience entries pair a learner-named subject with the learner's explicit
  `new`, `some_experience`, or `experienced` self-description and optional
  detail. The label is not a score or verified level.
- Interests are bounded learner-authored labels. The platform does not assign
  a taxonomy or semantic category in this version.

Initial limits are 20 goals, 20 experience entries, and 50 interests. Empty
sections are valid. All entry identities and times are server facts.

## Mutation, History, and Export

Mutation intents carry one idempotency key, exact expected revision, and one
closed goal, experience, interest, ordering, or reset operation. A create
intent contains learner text but no learner identity, entry identity, canonical
time, next revision, or digest. Reset clears only this profile in a new
revision; it does not erase Assessment evidence, completion, projects, saved
learning, or another module's data.

Change history contains at most 100 non-content summaries. A summary identifies
the resulting revision, operation, affected profile-owned object when
applicable, time, and resulting digest. It does not retain prior private text
and is not a legal-consent or Assessment evidence ledger.

The export binds the exact current profile and bounded history to a clear
purpose, limitations, schema version, and export time. It contains no session,
permission, storage, provider, hidden profile, inferred trait, evidence,
scoring, recommendation, experiment, or financial field.

## Canonicalization and Pure Core

The profile digest is SHA-256 over compact sorted-key JSON encoded directly as
UTF-8 with `profile_digest` omitted. Unicode is not normalized implicitly.
Fixed ASCII and non-ASCII vectors protect this rule.

The contract adapter and domain mutation rules are pure. They do not resolve
identity or permission; issue time or IDs; persist state; call Curriculum,
Assessment, Adaptation, a provider, or a model; access network or filesystem;
or create another durable effect. The later application boundary supplies
server facts and exact replay behavior under one protected public API for
browser and supported headless clients.

## Failure and Compatibility

Unknown versions, operations, fields, invalid text/identity/time, duplicate or
incomplete order, quota overflow, stale revision, digest mismatch, and
history/export mismatch fail closed with bounded codes. Additive compatible
technical metadata is not accepted inside the closed v1 document; it belongs
in a later schema version when it changes portable shape.

A preference consumer must use a public Learner-model operation and declare
its purpose. It may not query Learner-model storage, reinterpret a preference
as evidence or permission, or make an unsupported downstream capability block
viewing, changing, resetting, or exporting otherwise valid preferences.
