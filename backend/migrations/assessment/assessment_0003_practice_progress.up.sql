ALTER TABLE assessment.practice_attempts
    ADD COLUMN attempt_order smallint NOT NULL DEFAULT 1;

ALTER TABLE assessment.practice_attempts
    ALTER COLUMN attempt_order DROP DEFAULT;

ALTER TABLE assessment.practice_attempts
    ADD CONSTRAINT assessment_practice_attempt_order_positive
        CHECK (attempt_order >= 1 AND attempt_order <= 10);

ALTER TABLE assessment.practice_attempts
    DROP CONSTRAINT assessment_one_placed_practice_completion;

ALTER TABLE assessment.practice_attempts
    ADD CONSTRAINT assessment_practice_attempt_order_unique
        UNIQUE (
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
        );

CREATE TABLE assessment.practice_retry_scopes (
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
    CONSTRAINT assessment_practice_retry_scope_pk PRIMARY KEY (
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
    CONSTRAINT assessment_practice_retry_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_retry_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$')
);

INSERT INTO assessment.practice_retry_scopes (
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
)
SELECT DISTINCT
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
FROM assessment.practice_attempts;

CREATE TABLE assessment.practice_drafts (
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
    responses jsonb NOT NULL,
    response_fingerprint char(64) NOT NULL,
    revision bigint NOT NULL,
    saved_at timestamptz NOT NULL,
    CONSTRAINT assessment_practice_draft_pk PRIMARY KEY (
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
    CONSTRAINT assessment_practice_draft_responses_array
        CHECK (jsonb_typeof(responses) = 'array'),
    CONSTRAINT assessment_practice_draft_fingerprint_profile
        CHECK (response_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_draft_revision_positive
        CHECK (revision >= 1),
    CONSTRAINT assessment_practice_draft_package_digest_profile
        CHECK (package_digest ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_practice_draft_definition_digest_profile
        CHECK (definition_digest ~ '^[a-f0-9]{64}$')
);

COMMENT ON TABLE assessment.practice_drafts IS
    'Mutable learner work for one exact practice scope; never completion evidence.';
COMMENT ON TABLE assessment.practice_retry_scopes IS
    'Assessment-owned transaction lock rows for exact formative retry scopes.';
