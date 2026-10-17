CREATE TABLE learner_model.preference_profiles (
    profile_id text PRIMARY KEY,
    learner_id uuid NOT NULL UNIQUE,
    revision integer NOT NULL,
    profile jsonb NOT NULL,
    profile_digest char(64) NOT NULL,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    CONSTRAINT learner_model_preference_profile_id
        CHECK (profile_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT learner_model_preference_revision CHECK (revision >= 2),
    CONSTRAINT learner_model_preference_digest
        CHECK (profile_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_preference_shape CHECK (
        jsonb_typeof(profile) = 'object'
        AND profile->>'schema_version' = '1.0.0'
        AND profile->>'profile_id' = profile_id
        AND profile->>'learner_id' = learner_id::text
        AND (profile->>'revision')::integer = revision
        AND profile->>'profile_digest' = profile_digest
    ),
    CONSTRAINT learner_model_preference_time CHECK (updated_at >= created_at)
);

CREATE TABLE learner_model.preference_changes (
    learner_id uuid NOT NULL
        REFERENCES learner_model.preference_profiles(learner_id)
        ON DELETE CASCADE,
    revision integer NOT NULL,
    change jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    resulting_profile_digest char(64) NOT NULL,
    PRIMARY KEY (learner_id, revision),
    CONSTRAINT learner_model_preference_change_revision CHECK (revision >= 2),
    CONSTRAINT learner_model_preference_change_digest
        CHECK (resulting_profile_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_preference_change_shape CHECK (
        jsonb_typeof(change) = 'object'
        AND change->>'schema_version' = '1.0.0'
        AND (change->>'revision')::integer = revision
        AND change->>'resulting_profile_digest' = resulting_profile_digest
    )
);

CREATE TABLE learner_model.preference_mutations (
    learner_id uuid NOT NULL
        REFERENCES learner_model.preference_profiles(learner_id)
        ON DELETE CASCADE,
    idempotency_key text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    accepted_profile jsonb NOT NULL,
    accepted_revision integer NOT NULL,
    PRIMARY KEY (learner_id, idempotency_key),
    CONSTRAINT learner_model_preference_mutation_key
        CHECK (idempotency_key ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT learner_model_preference_mutation_fingerprint
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_preference_mutation_revision
        CHECK (accepted_revision >= 2),
    CONSTRAINT learner_model_preference_mutation_shape CHECK (
        jsonb_typeof(accepted_profile) = 'object'
        AND accepted_profile->>'learner_id' = learner_id::text
        AND (accepted_profile->>'revision')::integer = accepted_revision
    )
);

COMMENT ON TABLE learner_model.preference_profiles IS
    'Current learner-entered goals, experience, and interests; not evidence.';
COMMENT ON TABLE learner_model.preference_changes IS
    'Bounded non-content preference change summaries.';
COMMENT ON TABLE learner_model.preference_mutations IS
    'Request fingerprints and exact accepted profile replays.';
