# Learner Presentation Preferences Contract

- Status: accepted and composed through the protected public API
- Canonical for: explicit learner-owned presentation choices
- Executable family: `contracts/learning/learner-presentation-preferences/v1/`

## Ownership and Meaning

Learner model owns the learner's explicit text-size, text-spacing,
reading-width, and motion choices. These values record presentation choices;
they are not a disability or medical diagnosis, an inferred accessibility need,
Assessment evidence, competency or mastery, Curriculum prerequisite,
Adaptation eligibility, recommendation, permission, financial suitability, or
irreversible instruction.

The platform design system owns how a validated choice maps to semantic root
attributes and tokens. Browser-local light, dark, or device theme remains a
separate platform setting. Theme is not part of the learner-owned profile,
history, export, digest, API, or headless meaning.

## Safe Values and Protective Precedence

The closed version-one values are:

- text size: `default` or `larger`;
- text spacing: `default` or `increased`;
- reading width: `standard` or `focused`; and
- motion: `system` or `reduce`.

`default` means the accepted accessible design-system baseline, not a request
to undo browser or operating-system protections. `system` motion follows the
device signal, while `reduce` can remove optional application motion. A
consumer must preserve content, actions, focus, contrast, targets, responsive
reflow, browser zoom and text scaling, forced colors, and any more-protective
reduced-motion signal. Arbitrary CSS, fonts, scales, smaller text, tighter
spacing, reduced contrast, wider-than-standard reading, forced motion, and
hidden content are not compatible additions.

## Versioned Record and Mutation

`learner-presentation-preference-profile-v1` is a closed learner-bound record
with one server-owned profile identity, positive revision, all four choices,
canonical UTC times, and a canonical SHA-256 digest. An absent stored profile
may later project revision-one `default`, `default`, `standard`, and `system`
without a read-side write.

A mutation intent contains an idempotency key, exact expected revision, and
either a complete four-choice replacement or `reset_profile`. Reset restores
the safe four-value baseline in a new revision. Partial updates are excluded so
clients and adapters never invent merge or precedence behavior. Callers cannot
select a learner or supply server identity, time, revision outcome, digest,
theme, CSS, medical labels, evidence, policy, provider, or model fields.

## History, Export, and Pure Core

History contains at most 100 non-content summaries with the resulting
revision, operation, time, and digest. It does not copy prior choices. Export
binds the exact current profile and bounded history to explicit purpose and
limitations. Neither shape contains session, permission, storage, provider,
model, inferred trait, evidence, recommendation, financial, or browser-local
theme data.

The profile digest is SHA-256 over compact sorted-key JSON encoded directly as
UTF-8 with `profile_digest` omitted. The pure contract adapter issues no
identity or time, persists nothing, and has no database, network, filesystem,
provider, model, browser, design-token, or cross-module effect.

## Persistence and Public API

The application boundary supplies learner identity from the opaque server
session, canonical time, deterministic profile identity, exact mutation
fingerprinting, optimistic revision checks, and safe public errors. The
Learner-model PostgreSQL adapter owns the current profile, replay records, and
newest 100 summaries in additive `learner_model_0005` tables. An absent row is
a side-effect-free virtual default. A per-learner advisory lock and one
transaction keep the profile, summary, and replay atomic; exact retry resolves
before revision comparison.

The reviewed API exposes profile, mutation, history, and export operations
under `learner_presentation_preferences.read|write`. All reject query-selected
learner authority and closed models reject unknown fields and values. The
OpenAPI-generated TypeScript client is the identical contract for browser,
command-line, service, and future headless clients. Browser-local theme remains
outside every public and stored learner-owned document.

## Failure and Compatibility

Unknown versions, operations, fields, values, malformed identity/time/digest,
incomplete replacement, stale revision, unchanged mutation, and mismatched
history/export fail closed with bounded codes. Any future value must still be
safe, explicit, reversible, and unable to weaken the accessibility baseline;
otherwise it requires a new governed contract version or a different owner.
