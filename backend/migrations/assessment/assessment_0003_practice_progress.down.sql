DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM assessment.practice_attempts
        GROUP BY
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
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION
            'Cannot remove practice retry support while retained retries exist.';
    END IF;
END
$$;

DROP TABLE IF EXISTS assessment.practice_drafts;
DROP TABLE IF EXISTS assessment.practice_retry_scopes;

ALTER TABLE assessment.practice_attempts
    DROP CONSTRAINT assessment_practice_attempt_order_unique;
ALTER TABLE assessment.practice_attempts
    DROP CONSTRAINT assessment_practice_attempt_order_positive;
ALTER TABLE assessment.practice_attempts
    DROP COLUMN attempt_order;
ALTER TABLE assessment.practice_attempts
    ADD CONSTRAINT assessment_one_placed_practice_completion
        UNIQUE (
            learner_id,
            placement_id,
            practice_id,
            practice_version
        );
