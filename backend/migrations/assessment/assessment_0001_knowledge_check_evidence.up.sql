CREATE SCHEMA IF NOT EXISTS assessment;

CREATE TABLE assessment.attempts (
    attempt_id uuid PRIMARY KEY,
    learner_id uuid NOT NULL,
    submission_id uuid NOT NULL,
    request_fingerprint char(64) NOT NULL,
    placement_id text NOT NULL,
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
    submitted_at timestamptz NOT NULL,
    CONSTRAINT assessment_request_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_submission_idempotency
        UNIQUE (learner_id, submission_id),
    CONSTRAINT assessment_one_placed_completion
        UNIQUE (
            learner_id,
            placement_id,
            assessment_id,
            assessment_version
        )
);

CREATE TABLE assessment.responses (
    attempt_id uuid PRIMARY KEY
        REFERENCES assessment.attempts (attempt_id) ON DELETE RESTRICT,
    selected_option_id text NOT NULL
);

CREATE TABLE assessment.scores (
    attempt_id uuid PRIMARY KEY
        REFERENCES assessment.attempts (attempt_id) ON DELETE RESTRICT,
    score smallint NOT NULL,
    max_score smallint NOT NULL,
    correct boolean NOT NULL,
    feedback_id text NOT NULL,
    feedback_text text NOT NULL,
    CONSTRAINT assessment_single_point_score
        CHECK (
            score IN (0, 1)
            AND max_score = 1
            AND correct = (score = 1)
        )
);

CREATE TABLE assessment.completion_evidence (
    evidence_id uuid PRIMARY KEY,
    attempt_id uuid NOT NULL UNIQUE
        REFERENCES assessment.attempts (attempt_id) ON DELETE RESTRICT,
    result jsonb NOT NULL,
    recorded_at timestamptz NOT NULL,
    CONSTRAINT assessment_result_is_object
        CHECK (jsonb_typeof(result) = 'object')
);

CREATE TABLE assessment.outbox (
    event_id uuid PRIMARY KEY,
    evidence_id uuid NOT NULL UNIQUE
        REFERENCES assessment.completion_evidence (evidence_id)
        ON DELETE RESTRICT,
    event_type text NOT NULL,
    event_version text NOT NULL,
    event_payload jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT assessment_completion_event_type
        CHECK (event_type = 'assessment.knowledge-check.completed'),
    CONSTRAINT assessment_completion_event_version
        CHECK (event_version = '1.0.0'),
    CONSTRAINT assessment_event_is_object
        CHECK (jsonb_typeof(event_payload) = 'object')
);

CREATE INDEX assessment_attempt_provenance
    ON assessment.attempts (
        learner_id,
        placement_id,
        package_id,
        package_version,
        assessment_id,
        assessment_version
    );

CREATE FUNCTION assessment.reject_evidence_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'accepted assessment evidence is append-only'
        USING ERRCODE = '55000';
END;
$$;

CREATE TRIGGER assessment_attempts_append_only
    BEFORE UPDATE OR DELETE ON assessment.attempts
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_responses_append_only
    BEFORE UPDATE OR DELETE ON assessment.responses
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_scores_append_only
    BEFORE UPDATE OR DELETE ON assessment.scores
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_completion_append_only
    BEFORE UPDATE OR DELETE ON assessment.completion_evidence
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_outbox_append_only
    BEFORE UPDATE OR DELETE ON assessment.outbox
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();

COMMENT ON TABLE assessment.outbox IS
    'Atomic Assessment-owned completion event evidence; delivery is not implemented.';

