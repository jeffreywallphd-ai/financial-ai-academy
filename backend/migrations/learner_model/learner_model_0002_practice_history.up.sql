CREATE TABLE learner_model.practice_history_projections (
    learner_id uuid NOT NULL,
    placement_id text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    definition_digest char(64) NOT NULL,
    practice_id text NOT NULL,
    practice_version text NOT NULL,
    attempt_policy_id text NOT NULL,
    attempt_policy_version text NOT NULL,
    source_digest char(64) NOT NULL,
    attempt_count integer NOT NULL,
    rebuilt_at timestamptz NOT NULL,
    PRIMARY KEY (
        learner_id,
        placement_id,
        package_id,
        package_version,
        package_digest,
        definition_digest,
        practice_id,
        practice_version,
        attempt_policy_id,
        attempt_policy_version
    ),
    CONSTRAINT learner_model_practice_projection_placement_profile
        CHECK (placement_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT learner_model_practice_projection_package_profile
        CHECK (package_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'),
    CONSTRAINT learner_model_practice_projection_package_version_profile
        CHECK (
            package_version ~
            '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
        ),
    CONSTRAINT learner_model_practice_projection_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_practice_projection_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_practice_projection_practice_profile
        CHECK (
            practice_id ~ '^[a-z0-9][a-z0-9._-]{2,63}$'
            AND practice_version = '1.0.0'
        ),
    CONSTRAINT learner_model_practice_projection_policy_profile
        CHECK (
            attempt_policy_id = 'formative-retry'
            AND attempt_policy_version = '1.0.0'
        ),
    CONSTRAINT learner_model_practice_projection_source_digest_profile
        CHECK (source_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_model_practice_projection_attempt_count
        CHECK (attempt_count BETWEEN 0 AND 10)
);

CREATE TABLE learner_model.practice_history_attempts (
    learner_id uuid NOT NULL,
    placement_id text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    definition_digest char(64) NOT NULL,
    practice_id text NOT NULL,
    practice_version text NOT NULL,
    attempt_policy_id text NOT NULL,
    attempt_policy_version text NOT NULL,
    attempt_order integer NOT NULL,
    event_id uuid NOT NULL,
    attempt_id uuid NOT NULL,
    evidence_id uuid NOT NULL,
    submission_id uuid NOT NULL,
    score integer NOT NULL,
    max_score integer NOT NULL,
    outcome text NOT NULL,
    item_summaries jsonb NOT NULL,
    completed_at timestamptz NOT NULL,
    PRIMARY KEY (
        learner_id,
        placement_id,
        package_id,
        package_version,
        package_digest,
        definition_digest,
        practice_id,
        practice_version,
        attempt_policy_id,
        attempt_policy_version,
        attempt_order
    ),
    CONSTRAINT learner_model_practice_history_projection_fk
        FOREIGN KEY (
            learner_id,
            placement_id,
            package_id,
            package_version,
            package_digest,
            definition_digest,
            practice_id,
            practice_version,
            attempt_policy_id,
            attempt_policy_version
        ) REFERENCES learner_model.practice_history_projections (
            learner_id,
            placement_id,
            package_id,
            package_version,
            package_digest,
            definition_digest,
            practice_id,
            practice_version,
            attempt_policy_id,
            attempt_policy_version
        ) ON DELETE CASCADE,
    CONSTRAINT learner_model_practice_history_attempt_order
        CHECK (attempt_order BETWEEN 1 AND 10),
    CONSTRAINT learner_model_practice_history_score
        CHECK (
            score BETWEEN 0 AND 20
            AND max_score BETWEEN 1 AND 20
            AND score <= max_score
        ),
    CONSTRAINT learner_model_practice_history_outcome
        CHECK (outcome IN ('all_correct', 'review_needed')),
    CONSTRAINT learner_model_practice_history_items
        CHECK (
            jsonb_typeof(item_summaries) = 'array'
            AND jsonb_array_length(item_summaries) BETWEEN 1 AND 20
        ),
    UNIQUE (event_id),
    UNIQUE (attempt_id),
    UNIQUE (evidence_id),
    UNIQUE (submission_id)
);

COMMENT ON TABLE learner_model.practice_history_projections IS
    'Replaceable exact-scope practice history roots rebuilt from Assessment.';
COMMENT ON TABLE learner_model.practice_history_attempts IS
    'Replaceable ordered safe practice summaries; not mastery or eligibility.';
