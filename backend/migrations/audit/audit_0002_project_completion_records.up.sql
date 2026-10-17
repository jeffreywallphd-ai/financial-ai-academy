CREATE TABLE audit.project_completion_records (
    audit_id uuid PRIMARY KEY,
    event_id text NOT NULL UNIQUE,
    evidence_id text NOT NULL UNIQUE,
    submission_id text NOT NULL,
    actor_id uuid NOT NULL,
    action text NOT NULL,
    project_id text NOT NULL,
    snapshot_id text NOT NULL,
    snapshot_digest char(64) NOT NULL,
    brief_id text NOT NULL,
    brief_version text NOT NULL,
    brief_digest char(64) NOT NULL,
    placement_id text NOT NULL,
    placement_version text NOT NULL,
    placement_digest char(64) NOT NULL,
    policy_id text NOT NULL,
    policy_version text NOT NULL,
    occurrence integer NOT NULL,
    supersedes_submission_id text,
    occurred_at timestamptz NOT NULL,
    integrity_digest char(64) NOT NULL,
    recorded_at timestamptz NOT NULL,
    CONSTRAINT audit_project_completion_action
        CHECK (action = 'assessment.project.completed'),
    CONSTRAINT audit_project_completion_policy
        CHECK (
            policy_id = 'assessment-project-closure'
            AND policy_version = '1.0.0'
        ),
    CONSTRAINT audit_project_completion_occurrence
        CHECK (occurrence BETWEEN 1 AND 100),
    CONSTRAINT audit_project_completion_submission_identity
        UNIQUE (actor_id, submission_id),
    CONSTRAINT audit_project_completion_digests
        CHECK (
            snapshot_digest ~ '^[a-f0-9]{64}$'
            AND brief_digest ~ '^[a-f0-9]{64}$'
            AND placement_digest ~ '^[a-f0-9]{64}$'
            AND integrity_digest ~ '^[a-f0-9]{64}$'
        )
);

CREATE INDEX audit_project_completion_context
    ON audit.project_completion_records (
        actor_id, project_id, occurrence, event_id
    );

CREATE TRIGGER audit_project_completion_append_only
    BEFORE UPDATE OR DELETE ON audit.project_completion_records
    FOR EACH ROW EXECUTE FUNCTION audit.reject_record_mutation();

COMMENT ON TABLE audit.project_completion_records IS
    'Project completion integrity references; Assessment remains authority.';
