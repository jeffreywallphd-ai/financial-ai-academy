CREATE SCHEMA IF NOT EXISTS learner_model;

CREATE TABLE learner_model.lesson_completion_projections (
    learner_id uuid NOT NULL,
    placement_id text NOT NULL,
    completed boolean NOT NULL,
    history_count integer NOT NULL,
    source_digest char(64) NOT NULL,
    rebuilt_at timestamptz NOT NULL,
    PRIMARY KEY (learner_id, placement_id),
    CONSTRAINT learner_completion_history_count
        CHECK (history_count >= 0),
    CONSTRAINT learner_completion_state_matches_history
        CHECK (completed = (history_count > 0)),
    CONSTRAINT learner_completion_source_digest_profile
        CHECK (source_digest ~ '^[a-f0-9]{64}$')
);

CREATE TABLE learner_model.lesson_completion_history (
    event_id uuid PRIMARY KEY,
    learner_id uuid NOT NULL,
    placement_id text NOT NULL,
    attempt_id uuid NOT NULL UNIQUE,
    evidence_id uuid NOT NULL UNIQUE,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    assessment_id text NOT NULL,
    assessment_version text NOT NULL,
    definition_digest char(64) NOT NULL,
    item_id text NOT NULL,
    item_version text NOT NULL,
    scoring_policy_id text NOT NULL,
    scoring_policy_version text NOT NULL,
    score smallint NOT NULL,
    max_score smallint NOT NULL,
    completed_at timestamptz NOT NULL,
    CONSTRAINT learner_completion_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_completion_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT learner_completion_bounded_score
        CHECK (score IN (0, 1) AND max_score = 1)
);

CREATE INDEX learner_completion_history_context
    ON learner_model.lesson_completion_history (
        learner_id, placement_id, completed_at, event_id
    );

COMMENT ON TABLE learner_model.lesson_completion_projections IS
    'Rebuildable completion state derived from Assessment events; not mastery.';
COMMENT ON TABLE learner_model.lesson_completion_history IS
    'Rebuildable exact source references; Assessment remains authoritative.';
