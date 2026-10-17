DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM assessment.project_submissions)
        OR EXISTS (SELECT 1 FROM assessment.project_outbox)
    THEN
        RAISE EXCEPTION
            'Cannot remove retained Project submission evidence or events.';
    END IF;
END
$$;

DROP TABLE IF EXISTS assessment.project_outbox;
DROP TABLE IF EXISTS assessment.project_submissions;
DROP TABLE IF EXISTS assessment.project_submission_scopes;
DROP TABLE IF EXISTS assessment.project_submission_identities;
DROP SEQUENCE IF EXISTS assessment.project_submission_accepted_sequence;
