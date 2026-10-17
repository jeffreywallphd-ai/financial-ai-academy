CREATE SEQUENCE assessment.project_submission_accepted_sequence AS bigint;

CREATE TABLE assessment.project_submission_identities (
    learner_id uuid NOT NULL,
    submission_id text NOT NULL,
    CONSTRAINT assessment_project_submission_identity_pk
        PRIMARY KEY (learner_id, submission_id),
    CONSTRAINT assessment_project_submission_identity_profile
        CHECK (submission_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$')
);

CREATE TABLE assessment.project_submission_scopes (
    learner_id uuid NOT NULL,
    project_id text NOT NULL,
    CONSTRAINT assessment_project_submission_scope_pk
        PRIMARY KEY (learner_id, project_id),
    CONSTRAINT assessment_project_submission_scope_profile
        CHECK (project_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$')
);

CREATE TABLE assessment.project_submissions (
    evidence_id text PRIMARY KEY,
    learner_id uuid NOT NULL,
    submission_id text NOT NULL,
    project_id text NOT NULL,
    snapshot_id text NOT NULL,
    request_fingerprint char(64) NOT NULL,
    occurrence integer NOT NULL,
    accepted_sequence bigint NOT NULL,
    supersedes_submission_id text,
    candidate jsonb NOT NULL,
    submission jsonb NOT NULL,
    evidence jsonb NOT NULL,
    submitted_at timestamptz NOT NULL,
    CONSTRAINT assessment_project_submission_identity_unique
        UNIQUE (learner_id, submission_id),
    CONSTRAINT assessment_project_submission_occurrence_unique
        UNIQUE (learner_id, project_id, occurrence),
    CONSTRAINT assessment_project_submission_sequence_unique
        UNIQUE (accepted_sequence),
    CONSTRAINT assessment_project_evidence_identity_profile
        CHECK (evidence_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT assessment_project_id_profile
        CHECK (project_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT assessment_project_snapshot_id_profile
        CHECK (snapshot_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT assessment_project_fingerprint_profile
        CHECK (request_fingerprint ~ '^[a-f0-9]{64}$'),
    CONSTRAINT assessment_project_occurrence_positive CHECK (occurrence >= 1),
    CONSTRAINT assessment_project_sequence_positive CHECK (accepted_sequence >= 1),
    CONSTRAINT assessment_project_candidate_object
        CHECK (jsonb_typeof(candidate) = 'object'),
    CONSTRAINT assessment_project_submission_object
        CHECK (jsonb_typeof(submission) = 'object'),
    CONSTRAINT assessment_project_evidence_object
        CHECK (jsonb_typeof(evidence) = 'object')
);

CREATE TABLE assessment.project_outbox (
    event_id text PRIMARY KEY,
    evidence_id text NOT NULL UNIQUE,
    event_type text NOT NULL,
    event_version text NOT NULL,
    event_payload jsonb NOT NULL,
    occurred_at timestamptz NOT NULL,
    CONSTRAINT assessment_project_outbox_evidence_fk
        FOREIGN KEY (evidence_id)
        REFERENCES assessment.project_submissions (evidence_id),
    CONSTRAINT assessment_project_event_identity_profile
        CHECK (event_id ~ '^[a-z0-9][a-z0-9._-]{0,127}$'),
    CONSTRAINT assessment_project_event_type_exact
        CHECK (event_type = 'assessment.project.completed'),
    CONSTRAINT assessment_project_event_version_exact
        CHECK (event_version = '1.0.0'),
    CONSTRAINT assessment_project_event_object
        CHECK (jsonb_typeof(event_payload) = 'object')
);

CREATE TRIGGER assessment_project_identities_append_only
    BEFORE UPDATE OR DELETE ON assessment.project_submission_identities
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_project_scopes_append_only
    BEFORE UPDATE OR DELETE ON assessment.project_submission_scopes
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_project_submissions_append_only
    BEFORE UPDATE OR DELETE ON assessment.project_submissions
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();
CREATE TRIGGER assessment_project_outbox_append_only
    BEFORE UPDATE OR DELETE ON assessment.project_outbox
    FOR EACH ROW EXECUTE FUNCTION assessment.reject_evidence_mutation();

COMMENT ON TABLE assessment.project_submissions IS
    'Immutable structurally complete Project snapshot learning evidence.';
COMMENT ON TABLE assessment.project_outbox IS
    'Safe Project completion events committed atomically with Assessment evidence.';
