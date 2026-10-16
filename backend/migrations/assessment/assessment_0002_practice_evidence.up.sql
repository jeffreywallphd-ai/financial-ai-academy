CREATE TABLE assessment.practice_attempts (
    attempt_id uuid PRIMARY KEY,
    learner_id uuid NOT NULL,
    submission_id uuid NOT NULL,
    request_fingerprint char(64) NOT NULL,
    placement_id text NOT NULL,
    package_id text NOT NULL,
    package_version text NOT NULL,
    package_digest char(64) NOT NULL,
    definition_digest char(64) NOT NULL,
    practice_id text NOT NULL,
    practice_version text NOT NULL,
    attempt_policy_id text NOT NULL,
    attempt_policy_version text NOT NULL,
    score smallint NOT NULL,
    max_score smallint NOT NULL,
    outcome text NOT NULL,
    submitted_at timestamptz NOT NULL,
    CONSTRAINT assessment_practice_request_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_score_profile
        CHECK (
            score >= 0
            AND max_score >= 1
            AND score <= max_score
            AND outcome IN ('all_correct', 'review_needed')
            AND (outcome = 'all_correct') = (score = max_score)
        ),
    CONSTRAINT assessment_practice_submission_idempotency
        UNIQUE (learner_id, submission_id),
    CONSTRAINT assessment_one_placed_practice_completion
        UNIQUE (
            learner_id,
            placement_id,
            practice_id,
            practice_version
        )
);

CREATE TABLE assessment.practice_responses (
    attempt_id uuid NOT NULL
        REFERENCES assessment.practice_attempts (attempt_id)
        ON DELETE RESTRICT,
    item_position smallint NOT NULL,
    item_id text NOT NULL,
    item_version text NOT NULL,
    item_type text NOT NULL,
    scoring_policy_id text NOT NULL,
    scoring_policy_version text NOT NULL,
    response jsonb NOT NULL,
    PRIMARY KEY (attempt_id, item_position),
    UNIQUE (attempt_id, item_id),
    CONSTRAINT assessment_practice_response_position
        CHECK (item_position >= 0),
    CONSTRAINT assessment_practice_response_type
        CHECK (item_type IN ('single_select', 'multiple_select', 'numeric_entry')),
    CONSTRAINT assessment_practice_response_is_object
        CHECK (jsonb_typeof(response) = 'object')
);

CREATE TABLE assessment.practice_scores (
    attempt_id uuid NOT NULL
        REFERENCES assessment.practice_attempts (attempt_id)
        ON DELETE RESTRICT,
    item_position smallint NOT NULL,
    item_id text NOT NULL,
    score smallint NOT NULL,
    max_score smallint NOT NULL,
    correct boolean NOT NULL,
    feedback_id text NOT NULL,
    feedback_text text NOT NULL,
    review_reference_ids jsonb NOT NULL,
    PRIMARY KEY (attempt_id, item_position),
    UNIQUE (attempt_id, item_id),
    CONSTRAINT assessment_practice_score_position
        CHECK (item_position >= 0),
    CONSTRAINT assessment_practice_item_score
        CHECK (
            score IN (0, 1)
            AND max_score = 1
            AND correct = (score = 1)
        ),
    CONSTRAINT assessment_practice_review_references_are_array
        CHECK (jsonb_typeof(review_reference_ids) = 'array')
);

CREATE TABLE assessment.practice_completion_evidence (
    evidence_id uuid PRIMARY KEY,
    attempt_id uuid NOT NULL UNIQUE
        REFERENCES assessment.practice_attempts (attempt_id)
        ON DELETE RESTRICT,
    result jsonb NOT NULL,
    recorded_at timestamptz NOT NULL,
    CONSTRAINT assessment_practice_result_is_object
        CHECK (jsonb_typeof(result) = 'object')
);

CREATE TABLE assessment.practice_outbox (
    event_id uuid PRIMARY KEY,
    evidence_id uuid NOT NULL UNIQUE
        REFERENCES assessment.practice_completion_evidence (evidence_id)
        ON DELETE RESTRICT,
    event_type text NOT NULL,
    event_version text NOT NULL,
    event_payload jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT assessment_practice_completion_event_type
        CHECK (event_type = 'assessment.practice.completed'),
    CONSTRAINT assessment_practice_completion_event_version
        CHECK (event_version = '1.0.0'),
    CONSTRAINT assessment_practice_event_is_object
        CHECK (jsonb_typeof(event_payload) = 'object')
);

CREATE INDEX assessment_practice_attempt_provenance
    ON assessment.practice_attempts (
        learner_id,
        placement_id,
        package_id,
        package_version,
        practice_id,
        practice_version
    );

CREATE TRIGGER assessment_practice_attempts_append_only
    BEFORE UPDATE OR DELETE ON assessment.practice_attempts
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_practice_responses_append_only
    BEFORE UPDATE OR DELETE ON assessment.practice_responses
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_practice_scores_append_only
    BEFORE UPDATE OR DELETE ON assessment.practice_scores
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_practice_completion_append_only
    BEFORE UPDATE OR DELETE ON assessment.practice_completion_evidence
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_practice_outbox_append_only
    BEFORE UPDATE OR DELETE ON assessment.practice_outbox
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();

COMMENT ON TABLE assessment.practice_outbox IS
    'Atomic Assessment-owned practice completion event evidence; delivery is not implemented.';
